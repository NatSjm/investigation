<#
.SYNOPSIS
  Migration status per bounded context: which runs of the spec lifecycle are still due (skeleton, legacy merge,
  calculation audit, owner decision) and the exact command for each. Deterministic input for the `migration-lead`
  agent; writes migration/<scope>.md (OKF Document) or prints with -Print.
.DESCRIPTION
  Sources (all inside the docs repo, no source code): contexts.yml, features/<ctx>/*.md frontmatter,
  domain/calculations/*.md (status, used_by, `## Audit` section), generated/be/docs-tags.md (every @docs tag with its
  code location), generated/graph/REPO_MAP.md (spec coverage), confluence-import/<SPACE>/*.md not yet in _done/
  (header status; a page is assigned to a context when its text mentions the context name, its spec prefix or a spec
  ID of the context; otherwise it is listed as unassigned).
.EXAMPLE
  ./scripts/migration-status.ps1 -Scope all
  ./scripts/migration-status.ps1 -Scope product2 -Print
#>
param(
    [string]$Scope = 'all',
    [string]$Out = '',
    [switch]$Print
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[cultureinfo]::CurrentCulture = [cultureinfo]::InvariantCulture   # identical sort order on every machine (ICU + machine culture otherwise)
$Utf8 = New-Object System.Text.UTF8Encoding($false)
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).ProviderPath
function Read-File([string]$p) { if (Test-Path $p) { [IO.File]::ReadAllText($p, $Utf8) } else { '' } }
function Rel([string]$p) { $p.Substring($repo.Length).TrimStart('\', '/').Replace('\', '/') }
function Get-Fm([string]$text) { if ($text -match '(?s)\A﻿?---\r?\n(.*?)\r?\n---') { $Matches[1] } else { '' } }
function Get-Val([string]$fm, [string]$k) { if ($fm -match "(?m)^$k`:\s*(.+?)\s*$") { ($Matches[1] -replace '\s+#.*$', '').Trim().Trim('"').Trim("'") } else { '' } }
function Get-List([string]$fm, [string]$k) {
    $v = Get-Val $fm $k
    if ($v -match '^\[(.*)\]$') { return @($Matches[1] -split ',' | ForEach-Object { $_.Trim().Trim('"', "'") } | Where-Object { $_ }) }
    return @()
}
$bt = [char]96
function Code([string]$s) { $bt + $s + $bt }

# ---------- contexts ----------
$contexts = [ordered]@{}
foreach ($line in ((Read-File (Join-Path $repo 'contexts.yml')) -split "`r?`n")) {
    if ($line -notmatch '^\s{2}([\w-]+):\s*\{(.*)\}') { continue }
    $c = $Matches[1]; $body = $Matches[2]
    $spec = if ($body -match 'spec:\s*([A-Z][A-Z0-9]*)') { $Matches[1] } else { '' }
    $fe = if ($body -match 'fe:\s*"?([\w-]*)"?') { $Matches[1] } else { '' }
    $be = @(); if ($body -match 'be:\s*\[([^\]]*)\]') { $be = @($Matches[1] -split ',' | ForEach-Object { $_.Trim().Trim('"', "'") } | Where-Object { $_ }) }
    $contexts[$c] = [pscustomobject]@{ Name = $c; Spec = $spec; Fe = $fe; Be = $be }
}
if ($contexts.Count -eq 0) { throw 'contexts.yml has no contexts' }
$prefixes = @($contexts.Values | ForEach-Object { $c = $_; $_.Be | ForEach-Object { [pscustomobject]@{ Ctx = $c.Name; Prefix = $_ } } } | Sort-Object { $_.Prefix.Length } -Descending)
function Context-Of([string]$cls) { foreach ($p in $prefixes) { if ($cls.StartsWith($p.Prefix, [StringComparison]::Ordinal)) { return $p.Ctx } }; return 'shared' }
function Context-OfSpecId([string]$id) { $pfx = ($id -split '-')[0]; foreach ($c in $contexts.Values) { if ($c.Spec -eq $pfx) { return $c.Name } }; return '' }

$selected = @(if ($Scope -eq 'all') { $contexts.Keys } else { $Scope -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $contexts.Contains($_) } })
if ($selected.Count -eq 0) { throw "Unknown context '$Scope'. Known: $($contexts.Keys -join ', ')" }

# ---------- specs ----------
$specs = @{}   # ctx -> list of {Id, Status, Badge, Open, File}
foreach ($f in @(Get-ChildItem (Join-Path $repo 'features') -Recurse -Filter '*.md' | Where-Object { $_.Name -match '^[A-Z][A-Z0-9]*-\d{3}\.md$' })) {
    $t = Read-File $f.FullName; $fm = Get-Fm $t
    $id = Get-Val $fm 'id'; if (-not $id) { $id = $f.BaseName }
    $ctx = Get-Val $fm 'context'; if (-not $ctx) { $ctx = Context-OfSpecId $id }
    $open = 0; if ($t -match '(?s)## Open questions\r?\n(.*?)(\r?\n## |\z)') { $open = ([regex]::Matches($Matches[1], '(?m)^\s*- \[ \]')).Count }
    $verified = [bool](Get-Val $fm 'verified')
    if (-not $specs.ContainsKey($ctx)) { $specs[$ctx] = New-Object System.Collections.Generic.List[object] }
    $specs[$ctx].Add([pscustomobject]@{ Id = $id; Status = (Get-Val $fm 'status'); Verified = $verified; Open = $open; File = (Rel $f.FullName) })
}

# ---------- calculations: tags from code vs concepts ----------
$calcs = @{}   # name -> {Name, Location, Ctx, Concept, Status, Audited, UsedBy}
$tagsText = Read-File (Join-Path $repo 'generated/be/docs-tags.md')
foreach ($m in [regex]::Matches($tagsText, '(?m)^\|\s*`([a-z][a-z0-9_]*)`\s*\|\s*`(?:object|class)\s+(\w+)[^`]*`\s*\|[^|]*\|\s*`([^`]+)`\s*\|')) {
    $name = $m.Groups[1].Value; $cls = $m.Groups[2].Value
    $calcs[$name] = [pscustomobject]@{ Name = $name; Class = $cls; Location = $m.Groups[3].Value; Ctx = (Context-Of $cls); Concept = ''; Status = ''; Audited = $false; UsedBy = @() }
}
foreach ($f in @(Get-ChildItem (Join-Path $repo 'domain/calculations') -Filter '*.md' | Where-Object { $_.Name -notin 'index.md', '_template.md' })) {
    $t = Read-File $f.FullName; $fm = Get-Fm $t
    $name = Get-Val $fm 'name'; if (-not $name) { $name = $f.BaseName }
    if (-not $calcs.ContainsKey($name)) { $calcs[$name] = [pscustomobject]@{ Name = $name; Class = ''; Location = ''; Ctx = ''; Concept = ''; Status = ''; Audited = $false; UsedBy = @() } }
    $c = $calcs[$name]
    $c.Concept = Rel $f.FullName; $c.Status = Get-Val $fm 'status'; $c.Audited = ($t -match '(?m)^## Audit '); $c.UsedBy = @(Get-List $fm 'used_by')
    if (-not $c.Ctx) { $tags = @(Get-List $fm 'tags' | Where-Object { $contexts.Contains($_) }); if ($tags) { $c.Ctx = $tags[0] } }
}
# a calculation is OWNED by the context of its class-name prefix (fallback: first context tag) - its Run 3 is listed
# there only; contexts whose specs merely use it (used_by) show it as a dependency
function Calcs-Of([string]$ctx) { @($calcs.Values | Where-Object { $_.Ctx -eq $ctx } | Sort-Object Name) }
function Calcs-UsedBy([string]$ctx) {
    $ids = @(if ($specs.ContainsKey($ctx)) { $specs[$ctx] | ForEach-Object { $_.Id } })
    $c = $contexts[$ctx]
    @($calcs.Values | Where-Object { $_.Ctx -ne $ctx -and ($_.UsedBy | Where-Object { $_ -in $ids -or $_ -like "$($c.Spec)-*" }) } | Sort-Object Name)
}

# ---------- REPO_MAP spec coverage ----------
$codeOnly = @{}
foreach ($m in [regex]::Matches((Read-File (Join-Path $repo 'generated/graph/REPO_MAP.md')), '(?m)^- `spec:([\w-]+)`: code only')) { $codeOnly[$m.Groups[1].Value] = $true }

# ---------- legacy pages not yet migrated ----------
$pages = New-Object System.Collections.Generic.List[object]
$impDir = Join-Path $repo 'confluence-import'
if (Test-Path $impDir) {
    foreach ($f in @(Get-ChildItem $impDir -Recurse -Filter '*.md' | Where-Object { $_.FullName -notmatch '[\\/]_done[\\/]' -and $_.Name -ne 'README.md' })) {
        $t = Read-File $f.FullName; $fm = Get-Fm $t
        $status = Get-Val $fm 'status'; if (-not $status) { $status = 'imported' }
        if ($status -in 'migrated', 'obsolete') { continue }
        # context of a page: explicit header `target: <ctx | spec ID>`, else its title (header `source` or first H1,
        # spaces removed, so "Product 1 overview" matches product1), else spec IDs cited in the body
        $hits = New-Object System.Collections.Generic.List[string]
        $target = Get-Val $fm 'target'
        $title = Get-Val $fm 'source'; if ($t -match '(?m)^# (.+)$') { $title += ' ' + $Matches[1] }
        $titleKey = ($title -replace '[^A-Za-z0-9]', '').ToLower()
        foreach ($c in $contexts.Values) {
            $byTarget = $target -and ($target -eq $c.Name -or ($c.Spec -and $target -like "$($c.Spec)-*"))
            $stem = ($c.Name.ToLower() -replace 's$', '')   # "meetings" also matches "Meeting flow"
            $byTitle = $titleKey.Contains($stem) -or ($c.Fe -and $titleKey.Contains($c.Fe.ToLower()))
            $byId = $c.Spec -and ($t -match ('\b' + [regex]::Escape($c.Spec) + '-\d{3}\b'))
            if ($byTarget -or $byTitle -or $byId) { $hits.Add($c.Name) }
        }
        $kind = if ($t -match '(?i)formula|threshold|calculation|rounding') { 'calculation?' } else { 'feature?' }
        $pages.Add([pscustomobject]@{ File = (Rel $f.FullName); Modified = (Get-Val $fm 'last_modified'); Status = $status; Kind = $kind; Ctx = @($hits) })
    }
}

# ---------- render ----------
$today = (Get-Date).ToString('yyyy-MM-dd')
$sb = [System.Text.StringBuilder]::new()
$title = if ($Scope -eq 'all') { 'Migration status (all contexts)' } else { "Migration status ($Scope)" }
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('type: Document')
[void]$sb.AppendLine("title: $title")
[void]$sb.AppendLine('description: Which runs of the spec lifecycle (skeleton, legacy merge, calculation audit, owner decision) are still due per bounded context, with the command for each; generated by scripts/migration-status.ps1.')
[void]$sb.AppendLine('tags: [migration, plan]')
[void]$sb.AppendLine('status: stable')
[void]$sb.AppendLine("generated: { by: process:migration-status, at: ${today}T00:00:00Z }")
[void]$sb.AppendLine('---')
[void]$sb.AppendLine()
[void]$sb.AppendLine("# $title")
[void]$sb.AppendLine()
[void]$sb.AppendLine('> Generated by ' + (Code 'scripts/migration-status.ps1') + " on $today from contexts.yml, features/, domain/calculations/, generated/be/docs-tags.md, generated/graph/REPO_MAP.md and confluence-import/. Lifecycle: " + (Code '.github/skills/spec-lifecycle/SKILL.md') + '. Regenerate instead of editing.')
[void]$sb.AppendLine()

$totals = [ordered]@{ run1 = 0; run2 = 0; run3 = 0; run4 = 0; ready = 0 }
$summary = New-Object System.Collections.Generic.List[string]
$detail = [System.Text.StringBuilder]::new()
foreach ($ctxName in $selected) {
    $c = $contexts[$ctxName]
    $ctxSpecs = @(if ($specs.ContainsKey($ctxName)) { $specs[$ctxName] | Sort-Object Id })
    $ctxCalcs = @(Calcs-Of $ctxName)
    $ctxPages = @($pages | Where-Object { $_.Ctx -contains $ctxName })
    $runs = New-Object System.Collections.Generic.List[string]
    $firstId = "$($c.Spec)-001"
    if ($ctxSpecs.Count -eq 0) {
        $totals.run1++
        $runs.Add("- [ ] **Run 1 - skeleton** " + (Code $firstId) + ': ' + (Code "/spec-skeleton-from-graph $ctxName $firstId") + ' (agent ' + (Code 'spec-writer') + "; REPO_MAP: $(if ($codeOnly.ContainsKey($firstId)) { 'code only' } else { 'not listed' }))")
    }
    foreach ($p in $ctxPages) {
        $totals.run2++
        $who = if ($p.Kind -eq 'calculation?') { 'looks like a formula page: ' + (Code "/audit-calculation $($p.File)") + ' (agent ' + (Code 'calc-auditor') + ')' } else { (Code "@confluence-migrator $($p.File)") }
        $runs.Add("- [ ] **Run 2 - legacy merge** " + (Code $p.File) + " (last_modified $($p.Modified), status $($p.Status)): $who")
    }
    foreach ($k in $ctxCalcs) {
        if (-not $k.Concept) {
            $totals.run3++
            $runs.Add("- [ ] **Run 3 - calculation concept** " + (Code $k.Name) + " (code only, $($k.Location)): " + (Code "/audit-calculation $($k.Name)") + ' creates ' + (Code "domain/calculations/$($k.Name).md") + ' from ' + (Code 'domain/calculations/_template.md') + ' with worked examples from the unit test')
        } elseif (-not $k.Audited) {
            $totals.run3++
            $runs.Add("- [ ] **Run 3 - calculation audit** " + (Code $k.Name) + " (no audit table, status $($k.Status)): " + (Code "/audit-calculation $($k.Name)"))
        } elseif ($k.Status -ne 'stable') {
            # audited but not stable: the auditor found drift or the concept is new - the owner decides, not the auditor again
            $totals.run4++
            $runs.Add("- [ ] **Run 4 - owner decision** " + (Code $k.Name) + " (audited, status $($k.Status)): decide the open questions in " + (Code $k.Concept) + ", set " + (Code "status: stable") + " and " + (Code "verified: { by: human:<id>, at }"))
        }
    }
    foreach ($s in $ctxSpecs) {
        if ($s.Status -ne 'stable' -or -not $s.Verified) {
            $totals.run4++
            $what = @(); if ($s.Open -gt 0) { $what += "$($s.Open) open question(s)" }; if ($s.Status -ne 'stable') { $what += "status $($s.Status)" }; if (-not $s.Verified) { $what += 'no verified.by' }
            $runs.Add("- [ ] **Run 4 - owner decision** " + (Code $s.Id) + " ($($what -join ', ')): decide the open questions in " + (Code $s.File) + ', record them in the Change log, add ' + (Code 'verified: { by: human:<id>, at }') + ' and ' + (Code 'stale_after'))
        }
    }
    $state = if ($runs.Count -eq 0) { $totals.ready++; 'ready' } else { "$($runs.Count) run(s) due" }
    $specCell = if ($ctxSpecs.Count) { ($ctxSpecs | ForEach-Object { (Code $_.Id) + " ($($_.Status)$(if ($_.Verified) { ', verified' }))" }) -join ', ' } else { 'none' }
    $calcCell = if ($ctxCalcs.Count) { ($ctxCalcs | ForEach-Object { (Code $_.Name) + $(if (-not $_.Concept) { ' (code only)' } elseif (-not $_.Audited) { " ($($_.Status), unaudited)" } else { " ($($_.Status))" }) }) -join ', ' } else { 'none' }
    $used = @(Calcs-UsedBy $ctxName)
    if ($used.Count) { $calcCell += '; uses ' + (($used | ForEach-Object { Code $_.Name }) -join ', ') }
    $summary.Add("| $ctxName | $($c.Spec) | $specCell | $calcCell | $($ctxPages.Count) | $state |")

    [void]$detail.AppendLine("## $ctxName")
    [void]$detail.AppendLine()
    [void]$detail.AppendLine("Spec prefix $(Code $c.Spec); BE class prefixes $(($c.Be | ForEach-Object { Code $_ }) -join ', '); FE feature $(if ($c.Fe) { Code "src/features/$($c.Fe)" } else { 'none' }). Graph: " + (Code "generated/graph/$ctxName.md") + '.')
    [void]$detail.AppendLine()
    if ($runs.Count -eq 0) { [void]$detail.AppendLine('Ready for the analyst agent: spec stable and verified, calculations audited, no legacy page pending.') }
    else { foreach ($r in $runs) { [void]$detail.AppendLine($r) } }
    [void]$detail.AppendLine()
}

[void]$sb.AppendLine('## Summary')
[void]$sb.AppendLine()
[void]$sb.AppendLine("Runs due: skeleton $($totals.run1), legacy merge $($totals.run2), calculation $($totals.run3), owner decision $($totals.run4). Contexts ready for the analyst: $($totals.ready) of $($selected.Count).")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Context | Spec prefix | Specs | Calculations | Legacy pages pending | State |')
[void]$sb.AppendLine('|---|---|---|---|---|---|')
foreach ($row in $summary) { [void]$sb.AppendLine($row) }
[void]$sb.AppendLine()
$unassigned = @($pages | Where-Object { $_.Ctx.Count -eq 0 })
if ($unassigned.Count) {
    [void]$sb.AppendLine('Legacy pages that mention no context (classify by hand, then run ' + (Code '@confluence-migrator <page>') + '):')
    foreach ($p in $unassigned) { [void]$sb.AppendLine('- ' + (Code $p.File) + " (last_modified $($p.Modified), $($p.Kind))") }
    [void]$sb.AppendLine()
}
[void]$sb.AppendLine('Order of work: Run 1 for every context without a spec first (code is the truth, pages are merged into a skeleton), then Run 2 page by page, Run 3 as the handoff after each spec, Run 4 by the owner. One run, one review, one commit.')
[void]$sb.AppendLine()
[void]$sb.Append($detail.ToString())

$text = $sb.ToString()
if ($Print) { Write-Output $text }
if (-not $Out) { $Out = "migration/$Scope.md" }
if (-not $Print -or $Out) {
    $outPath = if ([IO.Path]::IsPathRooted($Out)) { $Out } else { Join-Path $repo $Out }
    $dir = Split-Path $outPath -Parent; if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
    [IO.File]::WriteAllText($outPath, $text, $Utf8)
    Write-Host "migration-status: $($selected.Count) context(s), runs due: $($totals.run1 + $totals.run2 + $totals.run3 + $totals.run4) -> $(Rel $outPath)"
}
