<#
.SYNOPSIS
  Component library map for a React/TS repo: one row per exported component under src/shared/** (the in-house UI
  library: tables, modals, charts, form controls) with its props (names from the `<Name>Props` interface), the first
  JSDoc line, the features that render it and file:line. Lets an analyst or a coding agent name the library component a
  story should use, and lets the graph link features to the shared components they depend on.
.EXAMPLE
  ./gen-components.ps1 -Root . -Out docs/_generated/components.md
#>
param(
    [string]$Root = '.',
    [string]$SharedDir = 'src/shared',
    [string]$FeaturesDir = 'src/features',
    [string]$Out = 'docs/_generated/components.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath
$sharedRoot = Join-Path $Root $SharedDir
if (-not (Test-Path $sharedRoot)) { throw "No $SharedDir under $Root" }

# usage index: component name -> features whose files reference `<Name` (JSX) or `Name(` (render helpers)
$featureFiles = @{}
$featRoot = Join-Path $Root $FeaturesDir
if (Test-Path $featRoot) {
    foreach ($d in Get-ChildItem $featRoot -Directory) {
        $featureFiles[$d.Name] = @(Get-SourceFiles $d.FullName @('*.ts', '*.tsx') | Where-Object { $_.Name -notmatch '\.(test|spec|stories)\.' } | ForEach-Object { Read-Text $_.FullName })
    }
    # app shell counts as a pseudo-feature
    $appDir = Join-Path $Root 'src/app'
    if (Test-Path $appDir) { $featureFiles['fe-app'] = @(Get-SourceFiles $appDir @('*.ts', '*.tsx') | ForEach-Object { Read-Text $_.FullName }) }
}

$rows = New-Object System.Collections.Generic.List[object]
$files = @(Get-SourceFiles $sharedRoot @('*.tsx', '*.ts') | Where-Object { $_.Name -notmatch '\.(test|spec|stories)\.' -and $_.Name -notmatch '^index\.' })
foreach ($f in $files) {
    $t = Read-Text $f.FullName
    $rel = Get-RelPath $Root $f.FullName
    $group = (($rel -replace ("^" + [regex]::Escape($SharedDir) + "/"), "") -split "/")[0]
    # exported components: `export function Name(` / `export const Name = (` / `export const Name: React.FC` with a capitalised name
    foreach ($m in [regex]::Matches($t, '(?m)^export\s+(?:default\s+)?(?:function\s+([A-Z]\w*)\s*(?:<[^>]*>)?\s*\(|const\s+([A-Z]\w*)\s*(?::\s*[^=]+)?=\s*(?:React\.)?(?:memo\()?(?:forwardRef\()?\s*(?:\([^)]*\)|\w+)\s*=>|const\s+([A-Z]\w*)\s*:\s*(?:React\.)?FC\b)')) {
        $name = @($m.Groups[1].Value, $m.Groups[2].Value, $m.Groups[3].Value) | Where-Object { $_ } | Select-Object -First 1
        if (-not $name) { continue }
        # props: fields of `interface <Name>Props` / `type <Name>Props = {` (names only, optional marked with ?)
        $props = @()
        $pm = [regex]::Match($t, '(?s)(?:interface|type)\s+' + [regex]::Escape($name) + 'Props(?:<[^>]*>)?\s*(?:=\s*)?\{(.*?)\n\}')
        if ($pm.Success) {
            $props = @([regex]::Matches($pm.Groups[1].Value, '(?m)^\s*(\w+\??)\s*:') | ForEach-Object { $_.Groups[1].Value })
        } elseif ($m.Value -match '\(\s*\{([^}]*)\}') {
            $props = @(($Matches[1] -split ',') | ForEach-Object { ($_ -replace '=.*$', '' -replace ':.*$', '').Trim() } | Where-Object { $_ })
        }
        # first JSDoc line directly above the declaration
        $before = $t.Substring(0, $m.Index)
        $doc = ''
        $jd = [regex]::Match($before, '(?s)/\*\*((?:(?!\*/).)*)\*/\s*$')
        if ($jd.Success) { $doc = (($jd.Groups[1].Value -split '\r?\n' | ForEach-Object { ($_ -replace '^\s*\*\s?', '').Trim() } | Where-Object { $_ -and $_ -notmatch '^@' }) | Select-Object -First 1) }
        $usedBy = @($featureFiles.Keys | Where-Object { $feat = $_; ($featureFiles[$feat] | Where-Object { $_ -match ('<' + [regex]::Escape($name) + '\b') -or $_ -match ('\b' + [regex]::Escape($name) + '\(') }) } | Sort-Object)
        $rows.Add([pscustomobject]@{ Name = $name; Group = $group; Doc = $doc; Props = $props; UsedBy = $usedBy; Loc = "$rel`:$(Get-LineNumber $t $m.Index)" })
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Component library (FE)' "$SharedDir/** exported components" 'One row per shared UI component: props, purpose, which features render it, file:line; name these in stories instead of inventing new components.'))
[void]$sb.AppendLine("$($rows.Count) component(s) under ``$SharedDir/``. Features must compose these; a new shared component is a change to this library, not to a feature.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Component | Group | Purpose | Props | Used by | Location |')
[void]$sb.AppendLine('|---|---|---|---|---|---|')
foreach ($r in $rows | Sort-Object Group, Name) {
    $props = if ($r.Props) { ($r.Props | ForEach-Object { '`' + $_ + '`' }) -join ', ' } else { '' }
    $used = if ($r.UsedBy) { ($r.UsedBy | ForEach-Object { '`' + $_ + '`' }) -join ', ' } else { '_unused_' }
    [void]$sb.AppendLine("| ``$($r.Name)`` | $($r.Group) | $(Escape-Cell $r.Doc) | $props | $used | ``$($r.Loc)`` |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "components: $($rows.Count) component(s) -> $Out"
