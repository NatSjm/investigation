<#
.SYNOPSIS
  Lists every feature folder with the `@docs` tag of its barrel, types file and data hooks and, where missing, the tag
  it should get. Deterministic input for the `docs-tagger` agent (prompt /tag-docs); nothing is written to the sources.
.DESCRIPTION
  For each src/features/<name>/: context = the contexts.yml entry whose `fe` equals the folder name; the feature's ID is
  the barrel's existing `@docs` tag, else `<spec prefix>-<next free NNN>` (NNN from docs-tags.md, 001 when none).
  Files checked: index.ts (needs `@module <name>` + `@docs <ID>`), <name>.types.ts, api/use*.ts.
  Status per file: tagged | PROPOSE | BLOCKED (folder not in contexts.yml).
.EXAMPLE
  ./tag-candidates.ps1 -Root . -Contexts ../harbor-docs/contexts.yml
#>
param(
    [string]$Root = '.',
    [string]$Contexts = '',
    [string]$FeaturesDir = 'src/features',
    [string]$DocsTags = 'docs/_generated/docs-tags.md',
    [string]$Out = ''
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

if (-not $Contexts) {
    $Contexts = @('../harbor-docs/contexts.yml', '../docs-repo/contexts.yml') | ForEach-Object { Join-Path $Root $_ } | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $Contexts) { throw 'contexts.yml not found next to the repo; pass -Contexts <path>' }
}
$featRoot = Join-Path $Root $FeaturesDir
if (-not (Test-Path $featRoot)) { throw "No $FeaturesDir under $Root" }

# ---- contexts.yml: fe folder -> spec prefix ----
$byFolder = @{}
foreach ($m in [regex]::Matches((Read-Text $Contexts), '(?m)^\s*([\w-]+):\s*\{\s*spec:\s*(\w+)\s*,\s*fe:\s*"?([\w-]*)"?\s*,')) {
    if ($m.Groups[3].Value) { $byFolder[$m.Groups[3].Value] = @{ Context = $m.Groups[1].Value; Spec = $m.Groups[2].Value } }
}
$used = @{}
$tagsPath = Join-Path $Root $DocsTags
if (Test-Path $tagsPath) {
    foreach ($m in [regex]::Matches((Read-Text $tagsPath), '(?m)^\|\s*`([A-Z][A-Z0-9]*)-(\d{3})[a-z]?`')) {
        $p = $m.Groups[1].Value; $n = [int]$m.Groups[2].Value
        if (-not $used[$p] -or $used[$p] -lt $n) { $used[$p] = $n }
    }
}
function Next-Id([string]$prefix) { $n = if ($used[$prefix]) { $used[$prefix] + 1 } else { 1 }; $used[$prefix] = $n; return ('{0}-{1:000}' -f $prefix, $n) }
function First-Doc-Tags([string]$path) {
    $t = Read-Text $path
    $doc = [regex]::Match($t, '(?s)\A\s*/\*\*(.*?)\*/')      # the file-level JSDoc, before any code
    if (-not $doc.Success) { $doc = [regex]::Match($t, '(?s)/\*\*(.*?)\*/') }   # else the first block (hooks)
    if (-not $doc.Success) { return @() }
    return @([regex]::Matches($doc.Groups[1].Value, '@docs\s+([\w.-]+)') | ForEach-Object { $_.Groups[1].Value })
}

$rows = New-Object System.Collections.Generic.List[object]
foreach ($d in Get-ChildItem $featRoot -Directory | Sort-Object Name) {
    $feature = $d.Name
    $ctx = $byFolder[$feature]
    $files = @()
    $idx = Get-ChildItem $d.FullName -File -Filter 'index.ts*' | Select-Object -First 1
    if ($idx) { $files += $idx }
    $files += @(Get-ChildItem $d.FullName -File -Filter "$feature.types.ts")
    $apiDir = Join-Path $d.FullName 'api'
    if (Test-Path $apiDir) { $files += @(Get-ChildItem $apiDir -File -Filter 'use*.ts' | Where-Object { $_.Name -notmatch '\.(test|spec)\.' }) }
    $barrelTags = if ($idx) { @(First-Doc-Tags $idx.FullName) } else { @() }
    $id = ''
    if ($barrelTags) { $id = $barrelTags[0] } elseif ($ctx) { $id = Next-Id $ctx.Spec }
    if (-not $idx) {
        $rows.Add([pscustomobject]@{ File = "$FeaturesDir/$feature/index.ts"; Feature = $feature; Context = $(if ($ctx) { $ctx.Context } else { '-' }); Current = ''; Proposed = $(if ($ctx) { "@module $feature + @docs $id" } else { '' }); Status = $(if ($ctx) { 'PROPOSE (create the barrel)' } else { 'BLOCKED: folder not in contexts.yml' }) })
    }
    foreach ($f in $files) {
        $tags = @(First-Doc-Tags $f.FullName)
        $rel = Get-RelPath $Root $f.FullName
        $status = ''; $proposed = ''
        if ($tags) { $status = 'tagged' }
        elseif (-not $ctx) { $status = 'BLOCKED: folder not in contexts.yml' }
        else { $proposed = $(if ($f.Name -like 'index.*') { "@module $feature + @docs $id" } else { "@docs $id" }); $status = 'PROPOSE' }
        $rows.Add([pscustomobject]@{ File = $rel; Feature = $feature; Context = $(if ($ctx) { $ctx.Context } else { '-' }); Current = ($tags -join ', '); Proposed = $proposed; Status = $status })
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header '@docs tag candidates (FE)' "$FeaturesDir/*/{index.ts, <name>.types.ts, api/use*.ts} + contexts.yml" 'Feature files with their current @docs tag and the proposed one where missing; input for the docs-tagger agent.'))
$n = $rows.Count; $todo = @($rows | Where-Object { $_.Status -like 'PROPOSE*' }).Count; $blocked = @($rows | Where-Object { $_.Status -like 'BLOCKED*' }).Count
$ctxShown = (Resolve-Path $Contexts).ProviderPath; if ($ctxShown.StartsWith($Root)) { $ctxShown = Get-RelPath $Root $ctxShown }
[void]$sb.AppendLine("$n file(s): $($n - $todo - $blocked) tagged, $todo to tag, $blocked blocked. Spec IDs come from ``$ctxShown``; the spec file itself may not exist yet.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| File | Feature | Context | Current | Proposed | Status |')
[void]$sb.AppendLine('|---|---|---|---|---|---|')
foreach ($r in $rows) {
    $cur = if ($r.Current) { '`' + $r.Current + '`' } else { '' }
    $pro = if ($r.Proposed) { '`' + $r.Proposed + '`' } else { '' }
    [void]$sb.AppendLine("| ``$($r.File)`` | $($r.Feature) | $($r.Context) | $cur | $pro | $($r.Status) |")
}
if ($blocked) {
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('## Blockers')
    foreach ($f in ($rows | Where-Object { $_.Status -like 'BLOCKED*' } | Select-Object -ExpandProperty Feature -Unique)) { [void]$sb.AppendLine("- ``$f``: add a context with ``fe: $f`` to contexts.yml, then rerun.") }
}
$text = $sb.ToString()
if ($Out) { Write-Text (Resolve-Out $Root $Out) $text; Write-Host "tag-candidates: $n file(s), $todo to tag, $blocked blocked -> $Out" } else { Write-Output $text }
