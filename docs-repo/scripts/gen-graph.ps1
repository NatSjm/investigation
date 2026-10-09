<#
.SYNOPSIS
  Joins the lib-free generated maps (BE + FE + @docs tags) into an architectural knowledge graph.
  No libraries: nodes/edges from the Markdown tables, communities = BE modules / FE features,
  connected components for cross-repo flows, a tiny PageRank for the budgeted REPO_MAP.

  Inputs  (default: generated/be, generated/fe as pushed by the code-repo CI):
    api-index.md, events.md, db-schema.md, codebase-map.md, docs-tags.md     (BE)
    codebase-map.md, routes.md, docs-tags.md                                  (FE)
    optional graph-export-be.json / graph-export-fe.json  -> precise edges from
      GraphExportTest.kt (Spring context) / gen-graph-fe.ts (TS compiler API); merged, win over regex.
    features/**/<ID>.md, domain/calculations/<id>.md  -> spec nodes get path + status.

  Outputs (-Out, default generated/graph):
    graph.json              machine view (extension #impact tool, graph-query.ps1, CI analytics)
    <community>.md          one neighbourhood per module/feature (what Copilot reads, ~30 lines)
    REPO_MAP.md             ranked, budgeted overview (-Budget lines) + flows + spec coverage
    index.md                written by scripts/build-index.ps1 (OKF reserved file) - run it after this script

.EXAMPLE
  .\gen-graph.ps1
  .\gen-graph.ps1 -BeMaps ..\backend\docs\_generated -FeMaps ..\frontend\docs\_generated -Out generated\graph
  .\gen-graph.ps1 -Check        # exit 1 if outputs are stale (CI)
#>
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [string]$BeMaps = 'generated/be',
    [string]$FeMaps = 'generated/fe',
    [string]$Out = 'generated/graph',
    [int]$Budget = 120,
    [switch]$Check
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Utf8 = [System.Text.UTF8Encoding]::new($false)
$Root = (Resolve-Path $Root).ProviderPath
function Abs([string]$p) { if ([IO.Path]::IsPathRooted($p)) { $p } else { Join-Path $Root $p } }
$BeMaps = Abs $BeMaps; $FeMaps = Abs $FeMaps; $OutDir = Abs $Out
$date = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd')

# ---------- helpers ----------
function Read-Text([string]$Path) { if (Test-Path $Path) { [IO.File]::ReadAllText($Path, $Utf8) } else { '' } }
function Write-Text([string]$Path, [string]$Content) {
    $d = Split-Path -Parent $Path; if ($d -and -not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
    [IO.File]::WriteAllText($Path, $Content, $Utf8)
}
function Strip([string]$s) { $s.Trim().Trim('`').Trim() }
# Parses every Markdown table in a file into rows (hashtable header -> cell), ignoring separator rows.
function Get-TableRows([string]$Text) {
    $rows = @(); $hdr = $null
    foreach ($line in ($Text -split "`r?`n")) {
        if ($line -notmatch '^\s*\|') { $hdr = $null; continue }
        $cells = @($line.Trim().Trim('|') -split '(?<!\\)\|' | ForEach-Object { $_.Trim() })
        if ($null -eq $hdr) { $hdr = $cells; continue }
        if (($cells -join '') -match '^[-:\s]+$') { continue }
        $r = @{}; for ($i = 0; $i -lt $hdr.Count -and $i -lt $cells.Count; $i++) { $r[$hdr[$i]] = $cells[$i] }
        $rows += , $r
    }
    return $rows
}
function Get-Section([string]$Text, [string]$Heading) {
    $m = [regex]::Match($Text, '(?ms)^## ' + [regex]::Escape($Heading) + '\s*$(.*?)(?=^## |\z)')
    if ($m.Success) { $m.Groups[1].Value } else { '' }
}

$nodes = [ordered]@{}   # id -> node
$edges = @{}            # key -> edge
function Add-Node([string]$Id, [string]$Kind, [string]$Label, [string]$Community, [string]$Repo, [string]$Location = '', [string]$Note = '') {
    if (-not $nodes.Contains($Id)) {
        $nodes[$Id] = [ordered]@{ id = $Id; kind = $Kind; label = $Label; community = $Community; repo = $Repo; location = $Location; note = $Note }
    } else {
        $n = $nodes[$Id]
        if (-not $n.location -and $Location) { $n.location = $Location }
        if (-not $n.note -and $Note) { $n.note = $Note }
        if ($n.community -eq 'external' -and $Community -ne 'external') { $n.community = $Community; $n.repo = $Repo }
    }
    return $nodes[$Id]
}
function Add-Edge([string]$From, [string]$To, [string]$Rel, [string]$Source = 'regex-map') {
    $k = "$From|$Rel|$To"
    if (-not $edges.ContainsKey($k)) { $edges[$k] = [ordered]@{ from = $From; to = $To; rel = $Rel; source = $Source } }
    elseif ($Source -ne 'regex-map') { $edges[$k].source = $Source }
}
function Feature-Of([string]$Location) {
    if ($Location -match 'src/features/([^/]+)/') { return $Matches[1] }
    return 'fe-app'
}
function File-Of([string]$Location) { ($Location -split ':')[0] }
function Class-Of([string]$Location) { [IO.Path]::GetFileNameWithoutExtension((File-Of $Location)) }
function Path-Tokens([string]$p) {
    $p = $p -replace '^<BASE>', '' -replace '^/api/v\d+', '' -replace '\{[^}]*\}', '{*}' -replace ':[A-Za-z_]+', '{*}'
    return @($p.Trim('/') -split '/' | Where-Object { $_ })   # callers wrap the result in @() (single token unrolls to a string)
}
# FE call "/clients/{*}/overview" matches BE "/api/v1/clients/{clientId}/overview" when FE tokens are a suffix of BE tokens.
function Url-Matches([string]$FeUrl, [string]$BePath) {
    $f = @(Path-Tokens $FeUrl); $b = @(Path-Tokens $BePath)
    if ($f.Count -eq 0 -or $f.Count -gt $b.Count) { return $false }
    for ($i = 1; $i -le $f.Count; $i++) {
        $ft = $f[$f.Count - $i]; $bt = $b[$b.Count - $i]
        # wildcards only match wildcards; a literal must match literally (prevents {*}/x matching every /{id})
        if ($ft -ne $bt) { return $false }
    }
    return $true
}

# ---------- bounded contexts (contexts.yml) ----------
# Layered backend: the business context of a class is its NAME PREFIX (longest match wins), not its folder.
$ctxPrefixes = @(); $ctxOfFeature = @{}; $ctxNames = @()
foreach ($line in ((Read-Text (Join-Path $Root 'contexts.yml')) -split "`r?`n")) {
    if ($line -notmatch '^\s{2}([\w-]+):\s*\{(.*)\}') { continue }
    $c = $Matches[1]; $body = $Matches[2]; $ctxNames += $c
    if ($body -match 'be:\s*\[([^\]]*)\]') { foreach ($p in ($Matches[1] -split ',')) { $p = $p.Trim().Trim('"', "'"); if ($p) { $ctxPrefixes += [pscustomobject]@{ Ctx = $c; Prefix = $p } } } }
    if ($body -match 'fe:\s*"?([\w-]*)"?') { if ($Matches[1]) { $ctxOfFeature[$Matches[1]] = $c } }
}
$ctxPrefixes = @($ctxPrefixes | Sort-Object { $_.Prefix.Length } -Descending)
function Context-Of([string]$Class) {
    foreach ($p in $ctxPrefixes) { if ($Class.StartsWith($p.Prefix, [StringComparison]::Ordinal)) { return $p.Ctx } }
    return 'shared'
}

# ---------- BE (components.md: one row per class with layer, deps, tables) ----------
$graphLayers = @('api', 'manager', 'service', 'dao', 'event', 'job', 'client', 'utils', 'validator', 'component')
$classInfo = @{}
foreach ($r in Get-TableRows (Read-Text (Join-Path $BeMaps 'components.md'))) {
    $cls = Strip $r['Class']; if (-not $cls) { continue }
    $classInfo[$cls] = [pscustomobject]@{
        Layer = Strip $r['Layer']; Loc = Strip $r['Location']; Kind = Strip $r['Kind']
        Deps = @([regex]::Matches([string]$r['Depends on'], '`(\w+)`') | ForEach-Object { $_.Groups[1].Value })
        Tables = @([regex]::Matches([string]$r['Tables'], '`(\w+)`') | ForEach-Object { $_.Groups[1].Value })
    }
}
foreach ($cls in $classInfo.Keys) {
    $ci = $classInfo[$cls]; if ($ci.Layer -notin $graphLayers) { continue }
    $ctx = Context-Of $cls
    $null = Add-Node "class:$cls" 'class' $cls $ctx 'be' $ci.Loc "$($ci.Layer)$(if ($ci.Kind) { '; ' + $ci.Kind })"
    if ($ctx -ne 'shared') {
        $null = Add-Node "context:$ctx" 'context' $ctx $ctx 'be'
        Add-Edge "context:$ctx" "class:$cls" 'contains'
        if ($ci.Layer -eq 'manager') { $nodes["context:$ctx"].location = File-Of $ci.Loc; $nodes["context:$ctx"].note = "entry point $cls (manager)" }
    }
}
# constructor injection between architectural classes (controller -> manager -> service -> dao / utils / client)
foreach ($cls in $classInfo.Keys) {
    if (-not $nodes.Contains("class:$cls")) { continue }
    foreach ($d in $classInfo[$cls].Deps) { if ($nodes.Contains("class:$d")) { Add-Edge "class:$cls" "class:$d" 'depends-on' } }
}
foreach ($r in Get-TableRows (Read-Text (Join-Path $BeMaps 'api-index.md'))) {
    $path = Strip $r['Path']; if (-not $path) { continue }
    $loc = Strip $r['Location']; $handler = Strip $r['Handler']
    if ($handler -match '^_') { $cls = ''; $ctx = if ($r['Tag']) { Strip $r['Tag'] } else { 'shared' } } else { $cls = ($handler -split '\.')[0]; $ctx = Context-Of $cls }
    $id = "endpoint:$($r['Method']) $path"
    $null = Add-Node $id 'endpoint' "$($r['Method']) $path" $ctx 'be' $loc "operationId $(Strip $r['operationId']); handler $handler; params $($r['Params'])"
    if ($cls) { $null = Add-Node "class:$cls" 'class' $cls $ctx 'be' (File-Of $loc) 'api'; Add-Edge $id "class:$cls" 'handled-by' }
    if ($ctx -ne 'shared') { $null = Add-Node "context:$ctx" 'context' $ctx $ctx 'be'; Add-Edge "context:$ctx" $id 'exposes' }
}
foreach ($r in Get-TableRows (Read-Text (Join-Path $BeMaps 'events.md'))) {
    $t = Strip $r['Topic']; if (-not $t) { continue }
    $tid = "topic:$t"
    $null = Add-Node $tid 'topic' $t 'external' 'kafka'
    foreach ($m in [regex]::Matches($r['Producers (this repo)'], '`?(\w+)`?\s*\(([^,)]+)')) {
        $loc = $m.Groups[2].Value.Trim(); $cls = Class-Of $loc; $ctx = Context-Of $cls
        $null = Add-Node "class:$cls" 'class' $cls $ctx 'be' (File-Of $loc) 'event; producer'
        Add-Edge "class:$cls" $tid 'produces'
        $nodes[$tid].community = $ctx; $nodes[$tid].repo = 'be'
    }
    foreach ($m in [regex]::Matches($r['Consumers (this repo)'], '`?(\w+)`?\s*\(([^,)]+)')) {
        $loc = $m.Groups[2].Value.Trim(); $cls = Class-Of $loc; $ctx = Context-Of $cls
        $null = Add-Node "class:$cls" 'class' $cls $ctx 'be' (File-Of $loc) 'event; listener'
        Add-Edge $tid "class:$cls" 'consumed-by'
        if ($nodes[$tid].community -eq 'external') { $nodes[$tid].community = $ctx; $nodes[$tid].repo = 'be' }
    }
    if ($r['Producers (this repo)'] -match '_external_') { $nodes[$tid].note = 'produced outside this repo' }
    if ($r['Consumers (this repo)'] -match '_external_') { $nodes[$tid].note = (($nodes[$tid].note, 'consumed outside this repo') | Where-Object { $_ }) -join '; ' }
}
$schema = Read-Text (Join-Path $BeMaps 'db-schema.md')
foreach ($m in [regex]::Matches($schema, '(?m)^## `(\w+)`\s*\r?\nCreated in `([^`]+)`')) {
    $t = $m.Groups[1].Value; $loc = $m.Groups[2].Value
    $section = Get-Section $schema "``$t``"
    $cols = @((Get-TableRows $section) | ForEach-Object { Strip $_['Column'] })
    # classes touching the table: components.md (exact: @Table, SQL, Spring Data entity) first, db-schema "Used in" second
    $touch = @($classInfo.Keys | Where-Object { $classInfo[$_].Tables -contains $t })
    if (-not $touch) { $touch = @([regex]::Matches(([regex]::Match($section, '(?m)^Used in:\s*(.+)$').Groups[1].Value), '`(\w+)`') | ForEach-Object { $_.Groups[1].Value }) }
    $daos = @($touch | Where-Object { $classInfo.ContainsKey($_) -and $classInfo[$_].Layer -eq 'dao' })
    $ownerCls = @($daos + $touch | Where-Object { (Context-Of $_) -ne 'shared' } | Select-Object -First 1)
    $ctx = if ($ownerCls) { Context-Of $ownerCls[0] } else { 'shared' }
    $null = Add-Node "table:$t" 'table' $t $ctx 'be' $loc "$($cols.Count) columns: $($cols -join ', ')"
    if ($ctx -ne 'shared') { $null = Add-Node "context:$ctx" 'context' $ctx $ctx 'be'; Add-Edge "context:$ctx" "table:$t" 'owns' }
    foreach ($c in $touch) { if ($nodes.Contains("class:$c")) { Add-Edge "class:$c" "table:$t" 'persists-to' } }
}
foreach ($m in [regex]::Matches($schema, '(?m)^\s*(\w+)\s*\|[|o}{\-]+\s*(\w+)\s*:\s*(\w+)')) {
    Add-Edge "table:$($m.Groups[2].Value)" "table:$($m.Groups[1].Value)" "fk $($m.Groups[3].Value)"
}

# ---------- FE ----------
$feExports = @{}
foreach ($r in Get-TableRows (Read-Text (Join-Path $FeMaps 'codebase-map.md'))) {
    $f = Strip $r['Feature']; if (-not $f) { continue }
    $null = Add-Node "feature:$f" 'feature' $f $f 'fe' (Strip $r['Entry']) (Strip $r['Purpose'])
    $feExports[$f] = @(($r['Public exports'] -split ',\s*') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    foreach ($url in (($r['API calls'] -split '<br>') | ForEach-Object { $_.Trim() } | Where-Object { $_ })) {
        $hits = @($nodes.Values | Where-Object { $_.kind -eq 'endpoint' -and (Url-Matches $url ($_.label -replace '^\w+\s+', '')) })
        if ($hits.Count -eq 0) {
            $null = Add-Node "url:$url" 'url' $url $f 'fe' '' 'no BE endpoint matched (external service or stale map?)'
            Add-Edge "feature:$f" "url:$url" 'calls'
        }
        foreach ($h in $hits) { Add-Edge "feature:$f" $h.id 'calls' }
    }
}
foreach ($r in Get-TableRows (Read-Text (Join-Path $FeMaps 'routes.md'))) {
    $p = Strip $r['Path']; if (-not $p) { continue }
    $comp = Strip $r['Component']; $loc = Strip $r['Location']
    $feat = ($feExports.Keys | Where-Object { $feExports[$_] -contains $comp } | Select-Object -First 1)
    if (-not $feat) { $feat = Feature-Of $loc }
    $null = Add-Node "route:$p" 'route' $p $feat 'fe' $loc "renders $comp"
    Add-Edge "route:$p" "feature:$feat" 'renders'
}

# ---------- @docs tags (both repos) + spec files ----------
function Add-Tags([string]$File, [string]$Repo) {
    foreach ($r in Get-TableRows (Read-Text $File)) {
        $id = Strip $r['Spec ID']; if (-not $id) { continue }
        $loc = Strip $r['Location']
        $comm = if ($Repo -eq 'be') { Context-Of (Class-Of $loc) } else { Feature-Of $loc }
        $kind = if ($id -match '^[a-z][a-z0-9_]+$') { 'calculation' } else { 'spec' }
        $null = Add-Node "spec:$id" $kind $id 'docs' 'docs'
        $target = if ($Repo -eq 'be') { "class:$(Class-Of $loc)" } else { "feature:$comm" }
        if ($Repo -eq 'be') { $null = Add-Node $target 'class' (Class-Of $loc) $comm 'be' (File-Of $loc) }
        Add-Edge "spec:$id" $target 'implemented-by'
        $nodes["spec:$id"].note = (($nodes["spec:$id"].note, "$Repo $loc") | Where-Object { $_ }) -join '; '
    }
}
Add-Tags (Join-Path $BeMaps 'docs-tags.md') 'be'
Add-Tags (Join-Path $FeMaps 'docs-tags.md') 'fe'
$specFiles = @()
foreach ($d in @('features', 'domain')) { $p = Join-Path $Root $d; if (Test-Path $p) { $specFiles += Get-ChildItem $p -Recurse -File -Filter '*.md' | Where-Object { $_.Name -notin 'index.md', 'log.md' } } }
foreach ($f in $specFiles) {
    $id = [IO.Path]::GetFileNameWithoutExtension($f.Name)
    if ($id -like '_*' -or $id -eq 'conventions' -or $id -like '*template*') { continue }
    $fm = Read-Text $f.FullName
    $status = if ($fm -match '(?m)^status:\s*(\S+)') { $Matches[1] } else { '' }
    $rel = $f.FullName.Substring($Root.Length + 1).Replace('\', '/')
    $kind = if ($rel -like 'domain/calculations/*') { 'calculation' } elseif ($rel -like 'features/*') { 'spec' } else { 'doc' }
    if ($kind -eq 'doc') { continue }
    $n = Add-Node "spec:$id" $kind $id 'docs' 'docs' $rel
    $n.location = $rel
    if ($status) { $n.note = (("status $status", $n.note) | Where-Object { $_ }) -join '; ' }
}

# ---------- precise exports (optional) ----------
foreach ($x in @(@{ f = 'graph-export-be.json'; d = $BeMaps }, @{ f = 'graph-export-fe.json'; d = $FeMaps })) {
    $p = Join-Path $x.d $x.f
    if (-not (Test-Path $p)) { continue }
    $j = Read-Text $p | ConvertFrom-Json
    foreach ($n in @($j.nodes)) {
        # the BE export leaves the community empty: the bounded context comes from the class-name prefix (contexts.yml)
        $comm = [string]$n.community
        if (-not $comm) { $comm = if ($n.kind -eq 'class') { Context-Of $n.label } elseif ($n.kind -eq 'topic') { 'external' } else { 'shared' } }
        $null = Add-Node $n.id $n.kind $n.label $comm $n.repo ([string]$n.location) ([string]$n.note)
    }
    foreach ($e in @($j.edges)) { Add-Edge $e.from $e.to $e.rel 'export' }
}
# Fold exported FE "url:METHOD path" nodes onto the matching BE endpoint (method + suffix match); unmatched ones stay as url nodes.
foreach ($u in @($nodes.Values | Where-Object { $_.kind -eq 'url' -and $_.label -match '^(GET|POST|PUT|PATCH|DELETE) (.+)$' })) {
    $m = [regex]::Match($u.label, '^(\w+) (.+)$'); $method = $m.Groups[1].Value; $url = $m.Groups[2].Value
    $hit = @($nodes.Values | Where-Object { $_.kind -eq 'endpoint' -and $_.label -like "$method *" -and (Url-Matches $url ($_.label -replace '^\w+\s+', '')) }) | Select-Object -First 1
    if (-not $hit) { continue }
    foreach ($k in @($edges.Keys)) {
        $e = $edges[$k]
        if ($e.to -eq $u.id) { $edges.Remove($k); Add-Edge $e.from $hit.id 'calls' 'export' }
    }
    $nodes.Remove($u.id)
}

# ---------- analytics: components, PageRank ----------
$adj = @{}
foreach ($id in $nodes.Keys) { $adj[$id] = New-Object System.Collections.Generic.List[string] }
foreach ($e in $edges.Values) {
    if (-not $nodes.Contains($e.from)) { $null = Add-Node $e.from 'unknown' $e.from 'external' '?' ; $adj[$e.from] = New-Object System.Collections.Generic.List[string] }
    if (-not $nodes.Contains($e.to))   { $null = Add-Node $e.to 'unknown' $e.to 'external' '?' ; $adj[$e.to] = New-Object System.Collections.Generic.List[string] }
    $adj[$e.from].Add($e.to); $adj[$e.to].Add($e.from)
}
$component = @{}; $cid = 0
foreach ($id in $nodes.Keys) {
    if ($component.ContainsKey($id)) { continue }
    $cid++; $q = New-Object System.Collections.Generic.Queue[string]; $q.Enqueue($id); $component[$id] = $cid
    while ($q.Count) { $c = $q.Dequeue(); foreach ($n in $adj[$c]) { if (-not $component.ContainsKey($n)) { $component[$n] = $cid; $q.Enqueue($n) } } }
}
$total = $nodes.Count; $pr = @{}; foreach ($id in $nodes.Keys) { $pr[$id] = 1.0 / $total }
for ($it = 0; $it -lt 25; $it++) {
    $next = @{}
    foreach ($id in $nodes.Keys) {
        $sum = 0.0
        foreach ($nb in $adj[$id]) { if ($adj[$nb].Count) { $sum += $pr[$nb] / $adj[$nb].Count } }
        $next[$id] = 0.15 / $total + 0.85 * $sum
    }
    $pr = $next
}
foreach ($id in $nodes.Keys) { $nodes[$id].component = $component[$id]; $nodes[$id].rank = [math]::Round($pr[$id] * 1000, 2); $nodes[$id].degree = $adj[$id].Count }

# ---------- render ----------
$nodeObjs = @($nodes.Values | ForEach-Object { [pscustomobject]$_ })
$edgeObjs = @($edges.Values | ForEach-Object { [pscustomobject]$_ })
$communities = @($nodeObjs | Where-Object { $_.community -notin 'docs', 'external' } | Group-Object -Property community | Sort-Object Name)
function Header([string]$Title, [string]$Desc) {
@"
---
type: Document
title: $Title
description: $Desc
generated:
  by: process:gen-graph
  at: $date
status: stable
---
# $Title

> Generated by ``scripts/gen-graph.ps1`` from ``generated/be``, ``generated/fe`` and ``@docs`` tags. Do not edit by hand.

"@
}
function Ticks([string[]]$Ids) { (@($Ids) | ForEach-Object { '`' + $_ + '`' }) -join ', ' }
function Fmt([object]$n) { $loc = if ($n.location) { " - ``$($n.location)``" } else { '' }; $note = if ($n.note) { " - $($n.note)" } else { '' }; "``$($n.id)``$loc$note" }
function Cross([object]$e, [string]$comm) {
    $o = if ($e.from -like "*" -and $nodes[$e.from].community -eq $comm) { $nodes[$e.to] } else { $nodes[$e.from] }
    if ($o.community -ne $comm) { " (-> $($o.community))" } else { '' }
}

$files = [ordered]@{}
foreach ($g in $communities) {
    $comm = $g.Name; $repo = (@($g.Group | ForEach-Object { $_.repo } | Sort-Object -Unique)) -join '+'
    $members = @($g.Group | Sort-Object @{ e = { -$_.rank } }, id)
    $ids = @($members | ForEach-Object { $_.id })
    $sb = New-Object System.Text.StringBuilder
    $head = $members | Where-Object { $_.kind -in 'context', 'feature' } | Select-Object -First 1
    $desc = if ($head -and $head.note) { $head.note } else { "Neighbourhood of $comm" }
    [void]$sb.Append((Header "Graph: $comm ($repo)" $desc))
    [void]$sb.AppendLine("$($members.Count) nodes. Read this file instead of walking the module; open only the ``file:line`` you need.")
    [void]$sb.AppendLine()
    foreach ($kg in ($members | Group-Object -Property kind | Sort-Object { @('context','feature','endpoint','route','class','topic','table','url','unknown').IndexOf($_.Name) })) {
        $plural = if ($kg.Name -eq 'class') { 'classes' } else { "$($kg.Name)s" }
        [void]$sb.AppendLine("## $plural")
        foreach ($n in $kg.Group) { [void]$sb.AppendLine("- $(Fmt $n)") }
        [void]$sb.AppendLine()
    }
    [void]$sb.AppendLine('## Edges')
    $own = @($edgeObjs | Where-Object { $ids -contains $_.from -or $ids -contains $_.to } | Sort-Object rel, from, to)
    foreach ($e in $own) {
        $flag = if ($e.source -eq 'name-heuristic') { ' (heuristic)' } elseif ($e.source -eq 'export') { ' (exact)' } else { '' }
        [void]$sb.AppendLine("- ``$($e.from)`` -$($e.rel)-> ``$($e.to)``$(Cross $e $comm)$flag")
    }
    [void]$sb.AppendLine()
    $specs = @($own | Where-Object { $_.from -like 'spec:*' } | ForEach-Object { $_.from } | Sort-Object -Unique)
    [void]$sb.AppendLine('## Specs touching this community')
    if ($specs.Count) { foreach ($s in $specs) { [void]$sb.AppendLine("- $(Fmt $nodes[$s])") } } else { [void]$sb.AppendLine('- none (add `@docs <ID>` tags)') }
    $files["$comm.md"] = $sb.ToString()
}

# REPO_MAP: ranked within budget
$sb = New-Object System.Text.StringBuilder
[void]$sb.Append((Header 'REPO_MAP' 'Ranked architectural map of BE + FE + docs; read first, then one graph/<community>.md'))
[void]$sb.AppendLine("$($nodes.Count) nodes, $($edges.Count) edges, $($communities.Count) communities, $cid connected component(s). Budget $Budget lines; lower-ranked nodes live only in ``<community>.md`` / ``graph.json``.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('## Communities')
foreach ($g in $communities) { $h = $g.Group | Where-Object { $_.kind -in 'context','feature' } | Select-Object -First 1; $d = if ($h -and $h.note) { " - $($h.note)" } else { '' }; $rp = (@($g.Group | ForEach-Object { $_.repo } | Sort-Object -Unique)) -join '+'; [void]$sb.AppendLine("- [$($g.Name)]($($g.Name).md) ($rp, $($g.Count) nodes)$d") }
[void]$sb.AppendLine()
[void]$sb.AppendLine('## Top nodes (PageRank)')
$used = $sb.ToString().Split("`n").Count
$ranked = @($nodeObjs | Where-Object { $_.kind -ne 'unknown' } | Sort-Object @{ e = { -$_.rank } }, id)
$left = [math]::Max(10, $Budget - $used - 30)
foreach ($n in ($ranked | Select-Object -First $left)) { [void]$sb.AppendLine("- $($n.rank) ``$($n.id)`` [$($n.community)] deg $($n.degree)" + $(if ($n.location) { " - ``$($n.location)``" } else { '' })) }
[void]$sb.AppendLine()
[void]$sb.AppendLine('## Cross-repo flows (route -> feature -> endpoint -> class -> topic/table)')
foreach ($e in @($edgeObjs | Where-Object { $_.rel -eq 'calls' -and $_.to -like 'endpoint:*' } | Sort-Object from, to)) {
    $ep = $nodes[$e.to]; $cls = @($edges.Values | Where-Object { $_.from -eq $ep.id -and $_.rel -eq 'handled-by' } | ForEach-Object { $_.to })
    $down = @($edges.Values | Where-Object { $cls -contains $_.from -and $_.rel -in 'produces', 'persists-to' } | ForEach-Object { $_.to })
    $routes = @($edges.Values | Where-Object { $_.to -eq $e.from -and $_.rel -eq 'renders' } | ForEach-Object { $_.from })
    $line = '- ' + (Ticks ($routes + @($e.from))) + ' -> ' + (Ticks @($ep.id)) + ' -> ' + (Ticks $cls)
    if ($down.Count) { $line += ' -> ' + (Ticks $down) }
    [void]$sb.AppendLine($line)
}
[void]$sb.AppendLine()
[void]$sb.AppendLine('## Spec coverage')
$specNodes = @($nodeObjs | Where-Object { $_.kind -in 'spec', 'calculation' } | Sort-Object id)
$impl = @($edges.Values | Where-Object { $_.rel -eq 'implemented-by' } | ForEach-Object { $_.from } | Sort-Object -Unique)
foreach ($s in $specNodes) {
    $hasFile = [bool]$s.location; $hasCode = $impl -contains $s.id
    $state = if ($hasFile -and $hasCode) { 'spec + code' } elseif ($hasFile) { 'spec only - no @docs tag in code' } else { 'code only - no spec file in docs repo' }
    [void]$sb.AppendLine("- ``$($s.id)``: $state" + $(if ($s.note) { " ($($s.note))" } else { '' }))
}
$files['REPO_MAP.md'] = $sb.ToString()

# graph.json
$json = [ordered]@{
    generated = [ordered]@{ by = 'process:gen-graph'; at = $date }
    communities = @($communities | ForEach-Object { [ordered]@{ id = $_.Name; repo = ((@($_.Group | ForEach-Object { $_.repo } | Sort-Object -Unique)) -join '+'); nodes = $_.Count } })
    nodes = @($nodes.Values)
    edges = @($edgeObjs | Sort-Object from, rel, to)
}
$files['graph.json'] = ($json | ConvertTo-Json -Depth 6) + "`n"

# index.md is an OKF reserved file: scripts/build-index.ps1 owns it (run after this script / in CI).

# ---------- write / check ----------
function Norm([string]$s) { ($s -replace '(?m)^\s*at: .*$', '' -replace '(?m)^\s*"at":\s*".*"\s*,?$', '') -replace '\r', '' }
if ($Check) {
    $stale = @()
    foreach ($k in $files.Keys) {
        $p = Join-Path $OutDir $k
        if (-not (Test-Path $p) -or (Norm (Read-Text $p)) -ne (Norm $files[$k])) { $stale += $k }
    }
    # community files of contexts that no longer exist are stale too
    if (Test-Path $OutDir) { $stale += @(Get-ChildItem $OutDir -File -Filter '*.md' | Where-Object { $_.Name -ne 'index.md' -and -not $files.Contains($_.Name) } | ForEach-Object { "$($_.Name) (orphan)" }) }
    if ($stale.Count) { Write-Host "STALE: $($stale -join ', ')  (run scripts/gen-graph.ps1)" -ForegroundColor Red; exit 1 }
    Write-Host "graph up to date ($($nodes.Count) nodes, $($edges.Count) edges)"; exit 0
}
foreach ($k in $files.Keys) { Write-Text (Join-Path $OutDir $k) $files[$k] }
# prune community files of contexts that disappeared (renamed/merged contexts, restructured repos)
if (Test-Path $OutDir) { Get-ChildItem $OutDir -File -Filter '*.md' | Where-Object { $_.Name -ne 'index.md' -and -not $files.Contains($_.Name) } | ForEach-Object { [IO.File]::Delete($_.FullName); Write-Host "  removed orphan $($_.Name)" } }
Write-Host "graph: $($nodes.Count) nodes, $($edges.Count) edges, $($communities.Count) communities -> $OutDir"
