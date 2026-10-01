<#
.SYNOPSIS
  Feature map for a React/TS repo organised as src/features/<name>: purpose (from @module JSDoc in index.ts),
  public exports, hooks/components counts, API calls. One line per feature.
#>
param(
    [string]$Root = '.',
    [string]$FeaturesDir = 'src/features',
    [string]$Out = 'docs/_generated/codebase-map.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$featRoot = Join-Path $Root $FeaturesDir
if (-not (Test-Path $featRoot)) { throw "No $FeaturesDir under $Root" }

$rows = foreach ($d in Get-ChildItem $featRoot -Directory | Sort-Object Name) {
    $files = @(Get-SourceFiles $d.FullName @('*.ts','*.tsx') | Where-Object { $_.Name -notmatch '\.(test|spec|stories)\.' })
    $idx = Get-ChildItem $d.FullName -File -Filter 'index.ts*' | Select-Object -First 1
    $desc = ''; $exports = @()
    if ($idx) {
        $t = Read-Text $idx.FullName
        $doc = [regex]::Match($t, '(?s)/\*\*(.*?)\*/')
        if ($doc.Success) {
            $desc = (($doc.Groups[1].Value -split '\r?\n' | ForEach-Object { ($_ -replace '^\s*\*\s?', '').Trim() } | Where-Object { $_ -and $_ -notmatch '^@' }) | Select-Object -First 1)
        }
        $exports = [regex]::Matches($t, '(?m)^export\s+(?:type\s+)?\{([^}]*)\}') | ForEach-Object { ($_.Groups[1].Value -split ',') | ForEach-Object { ($_ -replace '\s+as\s+.*', '').Trim() } | Where-Object { $_ } }
    }
    $hooks = @($files | Where-Object { $_.Name -match '^use[A-Z]' }).Count
    $components = @($files | Where-Object { $_.Extension -eq '.tsx' -and $_.Name -notmatch '^(index|routes?)\.' }).Count
    $apis = New-Object System.Collections.Generic.HashSet[string]
    foreach ($f in $files) {
        foreach ($m in [regex]::Matches((Read-Text $f.FullName), '(?:fetch|axios\.\w+|api\.\w+)\(\s*`([^`]*)`|(?:fetch|axios\.\w+|api\.\w+)\(\s*[''"]([^''"]*)[''"]')) {
            $u = if ($m.Groups[1].Success) { $m.Groups[1].Value } else { $m.Groups[2].Value }
            [void]$apis.Add(($u -replace '\$\{BASE\}', '<BASE>' -replace '\$\{[^}]+\}', '{*}'))
        }
    }
    [pscustomobject]@{
        Feature = $d.Name; Desc = $desc; Files = $files.Count; Components = $components; Hooks = $hooks
        Exports = ($exports -join ', '); Apis = (($apis | Sort-Object) -join '<br>')
        Entry = "$FeaturesDir/$($d.Name)/$(if ($idx) { $idx.Name } else { '-' })"
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Codebase map (FE)' "$FeaturesDir/* + index.ts barrels"))
[void]$sb.AppendLine('Read the feature `index.ts` (public surface) and `*.types.ts` first; open components only for UI-level questions.')
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Feature | Purpose | Entry | Files | Components | Hooks | Public exports | API calls |')
[void]$sb.AppendLine('|---|---|---|---|---|---|---|---|')
foreach ($r in $rows) {
    [void]$sb.AppendLine("| ``$($r.Feature)`` | $(Escape-Cell $r.Desc) | ``$($r.Entry)`` | $($r.Files) | $($r.Components) | $($r.Hooks) | $(Escape-Cell $r.Exports) | $($r.Apis) |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "codebase-map: $(@($rows).Count) feature(s) -> $Out"
