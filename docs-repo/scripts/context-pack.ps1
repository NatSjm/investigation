<#
.SYNOPSIS
  Builds a task-scoped, budgeted context pack for an agent (analyst, spec-writer, test-designer, calc-auditor):
  spec + trust badge, linked calculations (formula + worked examples), the flows the spec takes part in, depth-2 graph neighbourhood, contract
  operations, tables, related work items / tests and legacy pages that mention the subject. No libraries.

  The pack is the only thing an agent should read for a task; everything else is reachable through the
  file:line references it contains. Section order / truncation ranks: .github/skills/task-context/references/pack-anatomy.md

.PARAMETER Task
  Spec ID (P1-001), calculation name (stress_test_monthly), graph node id (topic:..., context:product2,
  feature:stress, table:...), or free text (matched against title/description/tags/aliases of specs and calculations).
.PARAMETER Budget
  Maximum lines in the pack (default 500). Lower-ranked sections are truncated first.
.EXAMPLE
  .\context-pack.ps1 -Task P1-001
  .\context-pack.ps1 -Task "transport mode toggle on the stress table" -Budget 300 -Print
#>
param(
    [Parameter(Mandatory)][string]$Task,
    [int]$Budget = 500,
    [string]$OutDir = '.context',
    [int]$Depth = 2,
    [switch]$Print
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[cultureinfo]::CurrentCulture = [cultureinfo]::InvariantCulture   # identical sort order on every machine (ICU + machine culture otherwise)
$Utf8 = [Text.UTF8Encoding]::new($false)
$repo = Split-Path $PSScriptRoot -Parent
$now = [DateTime]::UtcNow
function Read-File([string]$p) { if (Test-Path $p) { [IO.File]::ReadAllText($p, $Utf8) } else { '' } }
function Rel([string]$p) { $p.Substring($repo.Length).TrimStart('\', '/').Replace('\', '/') }
function Get-Fm([string]$text) { if ($text -match '(?s)\A﻿?---\r?\n(.*?)\r?\n---') { $Matches[1] } else { '' } }
function Get-Val([string]$fm, [string]$k) { if ($fm -match "(?m)^$k`:\s*(.+?)\s*$") { ($Matches[1] -replace '\s+#.*$', '').Trim().Trim('"').Trim("'") } else { '' } }
function Get-List([string]$fm, [string]$k) {
    # inline [a, b] or block list; returns trimmed strings
    if ($fm -match "(?m)^$k`:\s*\[([^\]]*)\]") { return @($Matches[1] -split ',' | ForEach-Object { $_.Trim().Trim('"').Trim("'") } | Where-Object { $_ }) }
    if ($fm -match "(?ms)^$k`:\s*\r?\n((?:\s+-\s+.*\r?\n?)+)") { return @([regex]::Matches($Matches[1], '(?m)^\s+-\s+(.+?)\s*$') | ForEach-Object { $_.Groups[1].Value.Trim().Trim('"').Trim("'") }) }
    return @()
}
function Get-Badge([string]$fm) {
    $b = @(); $status = Get-Val $fm 'status'; if ($status -and $status -ne 'stable') { $b += $status }
    if ($fm -match '(?m)^verified:') { $b += $(if ($fm -match 'verified:[\s\S]*?by:\s*human:') { 'human-reviewed' } else { 'machine-confirmed' }) } else { $b += 'unverified' }
    $sa = Get-Val $fm 'stale_after'; if ($sa) { try { if ([DateTime]::Parse($sa, $null, 'AdjustToUniversal') -le $now) { $b += 'STALE' } } catch {} }
    return ($b -join ' · ')
}
function Get-Section([string]$text, [string]$heading) {
    $m = [regex]::Match($text, '(?ms)^##\s+' + [regex]::Escape($heading) + '[^\r\n]*\r?\n(.*?)(?=^##\s|\z)')
    if ($m.Success) { $m.Groups[1].Value.TrimEnd() } else { '' }
}
function Body([string]$text) { ($text -replace '(?s)\A﻿?---\r?\n.*?\r?\n---\r?\n', '').Trim() }

# ---------- 1. resolve the subject ----------
$specs = @(Get-ChildItem (Join-Path $repo 'features') -Recurse -Filter '*.md' | Where-Object { $_.Name -notmatch '^(_?template|index|conventions)\.md$' })
$calcs = @(Get-ChildItem (Join-Path $repo 'domain/calculations') -Filter '*.md' | Where-Object { $_.Name -notmatch '^(_?template|index)\.md$' })
$kind = ''; $file = $null; $node = ''; $candidates = @()
if ($Task -match '^[A-Z][A-Z0-9]*-\d{3}[a-z]?$') {
    $kind = 'spec'; $file = $specs | Where-Object { $_.BaseName -eq $Task } | Select-Object -First 1; $node = "spec:$Task"
    if (-not $file) { Write-Host "no spec file for $Task - packing graph neighbourhood only" -ForegroundColor Yellow }
} elseif ($Task -match '^[a-z][a-z0-9_]+$' -and (Test-Path (Join-Path $repo "domain/calculations/$Task.md"))) {
    $kind = 'calculation'; $file = Get-Item (Join-Path $repo "domain/calculations/$Task.md"); $node = "spec:$Task"
} elseif ($Task -match '^(context|feature|endpoint|route|class|hook|component|topic|table|spec):') {
    $kind = 'node'; $node = $Task
    if ($Task -match '^(context|feature):(\w+)$') { $community = $Matches[2] }
} else {
    # free text: score concepts by token hits in title / description / tags / aliases / id
    $tokens = @($Task.ToLower() -split '[^a-z0-9_\-]+' | Where-Object { $_.Length -ge 4 })
    $scored = foreach ($f in @($specs + $calcs)) {
        $fm = Get-Fm (Read-File $f.FullName)
        $hay = ((Get-Val $fm 'title') + ' ' + (Get-Val $fm 'description') + ' ' + (Get-Val $fm 'tags') + ' ' + (Get-Val $fm 'aliases') + ' ' + $f.BaseName).ToLower()
        $s = 0; foreach ($t in $tokens) { if ($hay.Contains($t)) { $s++ } }
        [pscustomobject]@{ File = $f; Score = $s }
    }
    $best = @($scored | Where-Object { $_.Score -gt 0 } | Sort-Object Score -Descending)
    if ($best.Count -eq 0) { Write-Error "nothing matches '$Task' - give a spec ID, calculation name or graph node id" }
    $file = $best[0].File
    $kind = if ($file.DirectoryName -match 'calculations$') { 'calculation' } else { 'spec' }
    $node = "spec:$($file.BaseName)"
    $candidates = @($best | Select-Object -Skip 1 -First 2 | ForEach-Object { "$(Rel $_.File.FullName) (score $($_.Score))" })
}

# ---------- 2. assemble sections (rank = truncation priority, 1 never) ----------
$sections = New-Object System.Collections.Generic.List[object]
function Add-Section([string]$title, [string]$content, [int]$rank, [string]$seeAlso = '') {
    if (-not $content) { $content = '_(none)_' }
    $sections.Add([pscustomobject]@{ Title = $title; Content = $content.TrimEnd(); Rank = $rank; See = $seeAlso })
}
$sources = New-Object System.Collections.Generic.List[string]
$fm = ''; $text = ''
if ($file) { $text = Read-File $file.FullName; $fm = Get-Fm $text; $sources.Add((Rel $file.FullName)) }

# Subject
$subj = @("- task: ``$Task``", "- resolved: **$kind** $(if ($file) { '`' + (Rel $file.FullName) + '`' } else { '`' + $node + '`' })")
if ($file) {
    $subj += "- title: $(Get-Val $fm 'title')"
    $subj += "- badge: **$(Get-Badge $fm)** · status: $(Get-Val $fm 'status') · last_verified: $(Get-Val $fm 'last_verified') · stale_after: $(Get-Val $fm 'stale_after') · generated: $(Get-Val $fm 'generated')"
    $own = Get-Val $fm 'owners'; if ($own) { $subj += "- owners: $own" }
}
if ($candidates) { $subj += "- candidates: $($candidates -join '; ')  <- free text matched several concepts; confirm the subject" }
Add-Section 'Subject' ($subj -join "`n") 1

# Spec / calculation body
if ($file) {
    $body = Body $text
    $lines = @($body -split "`r?`n")
    if ($kind -eq 'spec' -and ($lines.Count -gt 200 -or $lines.Count -gt ($Budget * 0.6))) {
        $keep = foreach ($h in 'Summary', 'Actors', 'Business rules', 'API', 'Data', 'Calculations', 'Edge cases', 'Open questions') {
            $m = [regex]::Match($body, '(?ms)^(##\s+' + [regex]::Escape($h) + '[^\r\n]*)\r?\n(.*?)(?=^##\s|\z)')
            if ($m.Success) { $m.Groups[1].Value + "`n" + $m.Groups[2].Value.TrimEnd() }
        }
        Add-Section 'Spec' (($keep -join "`n`n") + "`n`n... (reduced to key sections: see ``$(Rel $file.FullName)``)") 1 (Rel $file.FullName)
    } elseif ($kind -eq 'calculation') {
        $keep = foreach ($h in 'Purpose', 'Inputs', 'Outputs', 'Formula', 'Conventions', 'Worked examples', 'Audit', 'Open questions') {
            $m = [regex]::Match($body, '(?ms)^(##\s+' + [regex]::Escape($h) + '[^\r\n]*)\r?\n(.*?)(?=^#{1,2}\s|\z)')
            if ($m.Success) { $m.Groups[1].Value + "`n" + $m.Groups[2].Value.TrimEnd() }
        }
        Add-Section 'Calculation' (($keep -join "`n`n") + "`n`n(sanctioned code shape: ``# Computation`` block in ``$(Rel $file.FullName)``)") 1 (Rel $file.FullName)
    } else {
        Add-Section 'Spec' $body 1 (Rel $file.FullName)
    }
}

# Calculations linked from the spec
if ($kind -eq 'spec' -and $file) {
    $calcRefs = @(Get-List $fm 'calculations' | ForEach-Object { ($_ -replace '^/', '') })
    $parts = foreach ($c in $calcRefs) {
        $cp = Join-Path $repo $c
        if (-not (Test-Path $cp)) { "### $c`n_(missing file)_"; continue }
        $ct = Read-File $cp; $cfm = Get-Fm $ct; $sources.Add($c)
        $pieces = foreach ($h in 'Purpose', 'Formula', 'Conventions', 'Worked examples', 'Audit') { $s = Get-Section $ct $h; if ($s) { "**$h**`n$s" } }
        "### $(Get-Val $cfm 'title') (``$c``) - badge: $(Get-Badge $cfm)`n" + ($pieces -join "`n`n")
    }
    Add-Section 'Calculations' ($parts -join "`n`n") 2 'domain/calculations/'
}

# Flows this spec takes part in: listed in the spec (`flows:`) or naming the spec in their own `specs:` (both directions)
if ($kind -eq 'spec' -and $file) {
    $specId = [IO.Path]::GetFileNameWithoutExtension($file.Name)
    $flowRefs = @(Get-List $fm 'flows' | ForEach-Object { ($_ -replace '^/', '') })
    $flowDir = Join-Path $repo 'flows'
    if (Test-Path $flowDir) {
        foreach ($ff in Get-ChildItem $flowDir -Filter '*.md' | Where-Object { $_.Name -notmatch '^(_template|index)\.md$' }) {
            if (@(Get-List (Get-Fm (Read-File $ff.FullName)) 'specs') -contains $specId) { $flowRefs += Rel $ff.FullName }
        }
    }
    $flowRefs = @($flowRefs | Select-Object -Unique)
    if ($flowRefs.Count) {
        $parts = foreach ($f in $flowRefs) {
            $fp = Join-Path $repo $f
            if (-not (Test-Path $fp)) { "### $f`n_(missing file)_"; continue }
            $ft = Read-File $fp; $ffm = Get-Fm $ft; $sources.Add($f)
            $pieces = foreach ($h in 'Purpose', 'Trigger', 'Participants', 'Steps', 'Invariants and assumptions') { $s = Get-Section $ft $h; if ($s) { "**$h**`n$s" } }
            "### $(Get-Val $ffm 'title') (``$f``) - badge: $(Get-Badge $ffm) - specs: $(@(Get-List $ffm 'specs') -join ', ')`n" + ($pieces -join "`n`n")
        }
        Add-Section 'Flows' ($parts -join "`n`n") 3 'flows/'
    }
}

# Graph neighbourhood
$graphJson = Join-Path $repo 'generated/graph/graph.json'
if (Test-Path $graphJson) {
    $q = Join-Path $PSScriptRoot 'graph-query.ps1'
    $startNode = $node
    if ($kind -eq 'node' -and $node -match '^(context|feature):') { $startNode = $node }
    $gout = & $q -Graph $graphJson -Node $startNode -Depth $Depth -MaxLines 80 2>&1 | Out-String
    if ($gout -match 'no node matches' -and $file) {
        # a spec without @docs tags: fall back to its context community
        $ctx = Get-Val $fm 'context'
        if ($ctx) {
            # BE contexts have a `context:` node (located at the manager); FE-only contexts (e.g. presentation) only a `feature:` node
            $ctxNode = "context:$ctx"
            if (((Read-File $graphJson) -notmatch ('"id"\s*:\s*"' + [regex]::Escape($ctxNode) + '"'))) { $ctxNode = "feature:$ctx" }
            $gout = "(``$node`` not in graph - no ``@docs`` tag in code; neighbourhood of ``$ctxNode`` instead)`n" + (& $q -Graph $graphJson -Node $ctxNode -Depth $Depth -MaxLines 80 2>&1 | Out-String)
        }
    }
    $sources.Add('generated/graph/graph.json')
    $gout = $gout -replace '(?m)^#', '###'   # demote the query's headings under this section
    Add-Section 'Graph neighbourhood' ("``scripts/graph-query.ps1 -Node $startNode -Depth $Depth``:`n`n" + $gout.TrimEnd() + "`n`nMore: ``generated/graph/REPO_MAP.md``, ``generated/graph/<community>.md``") 2 'generated/graph/REPO_MAP.md'
} else {
    Add-Section 'Graph neighbourhood' '_(generated/graph/graph.json missing - run scripts/gen-graph.ps1)_' 2
}

# Contracts
if ($file) {
    $apiRefs = @(Get-List $fm 'api'); $eventRefs = @(Get-List $fm 'events')
    $oa = Join-Path $repo 'generated/openapi/backend.yaml'
    $parts = @()
    if ($apiRefs.Count -and (Test-Path $oa)) {
        $oaText = Read-File $oa; $sources.Add('generated/openapi/backend.yaml')
        foreach ($a in $apiRefs) {
            $p = ($a -split '\s+')[-1] -replace '^/api/v\d+', ''
            $m = [regex]::Match($oaText, '(?ms)^  ' + [regex]::Escape($p) + ':\s*\r?\n(.*?)(?=^  /|^\S)')
            if ($m.Success) {
                $block = $m.Groups[1].Value -split "`r?`n" | Where-Object { $_ -match '^\s{4}(get|post|put|patch|delete):|operationId|summary:|\$ref: .#/components/(schemas|parameters)|in: (query|path)|- name:' } | ForEach-Object { $_.TrimEnd() }
                $parts += "### ``$a``" + "`n```````yaml`n" + ($block -join "`n") + "`n``````"
            } else { $parts += "### ``$a`` - _not found in the contract (verify the path)_" }
        }
    }
    if ($eventRefs.Count) { $parts += "**Kafka**: " + (($eventRefs | ForEach-Object { "``$_``" }) -join ', ') + " - channels in ``generated/asyncapi/backend.yaml``; producers/consumers in ``generated/be/events.md``" }
    Add-Section 'Contracts' ($parts -join "`n`n") 4 'generated/openapi/backend.yaml'
}

# Data
if ($file) {
    $tables = @(Get-List $fm 'tables'); $schema = Join-Path $repo 'generated/be/db-schema.md'
    $parts = @()
    if ($tables.Count -and (Test-Path $schema)) {
        $st = Read-File $schema; $sources.Add('generated/be/db-schema.md')
        foreach ($t in $tables) {
            $m = [regex]::Match($st, '(?ms)^## `' + [regex]::Escape($t) + '`\s*\r?\n(.*?)(?=^## |\z)')
            $parts += if ($m.Success) { "### ``$t```n" + $m.Groups[1].Value.Trim() } else { "### ``$t`` - _not in db-schema.md_" }
        }
    }
    # named datasets (seeds, test fixtures) that touch these tables - cite them by name instead of describing rows
    $dsFile = Join-Path $repo 'generated/be/datasets.md'
    if ($tables.Count -and (Test-Path $dsFile)) {
        $dsRows = foreach ($line in ((Read-File $dsFile) -split '\r?\n' | Where-Object { $_ -match '^\| `[a-z0-9\-]+` \| (seed|fixture) \|' })) {
            $cells = $line.TrimStart('|') -split '\|'
            $touched = @([regex]::Matches($cells[3], '`([a-z_]+)`') | ForEach-Object { $_.Groups[1].Value })
            if ($touched | Where-Object { $tables -contains $_ }) { "- $($cells[0].Trim()) ($($cells[1].Trim())): $($cells[2].Trim()) - tables $($cells[3].Trim())" }
        }
        $dsRows = @($dsRows | Select-Object -First 8)
        if ($dsRows.Count) { $sources.Add('generated/be/datasets.md'); $parts += "### Datasets touching these tables`n(cite by name: ``Given dataset `"<name>`" is loaded``; full list and sample rows in ``generated/be/datasets.md``)`n" + ($dsRows -join "`n") }
    }
    Add-Section 'Data' ($parts -join "`n`n") 4 'generated/be/db-schema.md'
}

# Related work items and tests
if ($file -and $kind -eq 'spec') {
    $id = $file.BaseName; $parts = @()
    $wi = Join-Path $repo "work-items/$id.yml"
    if (Test-Path $wi) { $sources.Add("work-items/$id.yml"); $parts += "**work-items/$id.yml**`n" + ((Select-String -Path $wi -Pattern '^\s*(- id:|\s+summary:|^questions:|^\s+- ")' | ForEach-Object { $_.Line.TrimEnd() }) -join "`n") }
    $ft = Join-Path $repo "test-design/features/$id.feature"
    if (Test-Path $ft) { $sources.Add("test-design/features/$id.feature"); $parts += "**test-design/features/$id.feature**`n" + ((Select-String -Path $ft -Pattern '^\s*(@|Scenario)' | ForEach-Object { $_.Line.Trim() }) -join "`n") }
    Add-Section 'Related work items and tests' ($parts -join "`n`n") 3
}

# Legacy pages
$legacyDir = Join-Path $repo 'confluence-import'
if (Test-Path $legacyDir) {
    $needle = @(); if ($file) { $needle += $file.BaseName; $needle += @((Get-Val $fm 'title').ToLower() -split '[^a-z0-9]+' | Where-Object { $_.Length -ge 5 }) } else { $needle += ($Task -replace '^\w+:', '') }
    $parts = foreach ($p in Get-ChildItem $legacyDir -Recurse -Filter '*.md' | Where-Object { $_.Name -ne 'README.md' -and $_.FullName -notmatch '[\\/]_done[\\/]' }) {
        $pt = Read-File $p.FullName; $hits = @($needle | Where-Object { $_ -and $pt.ToLower().Contains($_.ToLower()) })
        if ($hits.Count -ge [Math]::Min(2, $needle.Count)) {
            $head = @($pt -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -First 5)
            "### ``$(Rel $p.FullName)`` (matches: $($hits -join ', ')) - legacy, UNVERIFIED`n" + (($head | ForEach-Object { "> $_" }) -join "`n")
        }
    }
    Add-Section 'Legacy pages' ($parts -join "`n`n") 5 'confluence-import/'
}

# ---------- 3. budget ----------
$header = "# Context pack: $Task - $(if ($file) { Rel $file.FullName } else { $node }) - $(if ($fm) { Get-Badge $fm } else { 'n/a' }) - built $($now.ToString('yyyy-MM-ddTHH:mm:ssZ'))`n"
$fixed = 12  # header + footer allowance
$truncated = @()
$budgetLeft = $Budget - $fixed
foreach ($s in $sections | Sort-Object Rank) {
    $n = @($s.Content -split "`r?`n").Count + 2
    if ($n -le $budgetLeft) { $budgetLeft -= $n; continue }
    $allow = [Math]::Max(0, $budgetLeft - 2)
    $s.Content = ((@($s.Content -split "`r?`n") | Select-Object -First $allow) -join "`n") + "`n... (truncated: see ``$(if ($s.See) { $s.See } else { 'the files listed under Sources' })``)"
    $truncated += $s.Title; $budgetLeft = 0
}
$order = 'Subject', 'Spec', 'Calculation', 'Calculations', 'Flows', 'Graph neighbourhood', 'Contracts', 'Data', 'Related work items and tests', 'Legacy pages'
$out = New-Object System.Text.StringBuilder
[void]$out.AppendLine($header)
foreach ($t in $order) { $s = $sections | Where-Object { $_.Title -eq $t }; if ($s) { [void]$out.AppendLine("## $t"); [void]$out.AppendLine($s.Content); [void]$out.AppendLine() } }
[void]$out.AppendLine('## Sources and limits')
[void]$out.AppendLine("- files: " + (($sources | Select-Object -Unique | ForEach-Object { "``$_``" }) -join ', '))
[void]$out.AppendLine("- truncated sections: $(if ($truncated) { $truncated -join ', ' } else { 'none' }) (budget $Budget lines)")
[void]$out.AppendLine('- rule: open nothing else unless a question above is unanswered; then open only the `file:line` named above in `../backend` or `../frontend`. Record new facts as Open questions / Change log, never as silent assumptions.')

$slug = ($Task.ToLower() -replace '[^a-z0-9]+', '-').Trim('-'); if ($slug.Length -gt 60) { $slug = $slug.Substring(0, 60) }
$outPath = Join-Path (Join-Path $repo $OutDir) "$slug.md"
$dir = Split-Path $outPath -Parent; if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
[IO.File]::WriteAllText($outPath, $out.ToString(), $Utf8)
$lineCount = @($out.ToString() -split "`r?`n").Count
if ($Print) { Write-Output $out.ToString() }
Write-Host "context pack: $(Rel $outPath) ($lineCount lines, budget $Budget$(if ($truncated) { ', truncated: ' + ($truncated -join ', ') }))" -ForegroundColor Green
