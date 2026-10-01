<#
.SYNOPSIS
  Maps changed code paths (relative to FE/BE repo roots) to affected docs using docs-map.yml.
.EXAMPLE
  .\map-paths.ps1 be/hedge/src/main/kotlin/Foo.kt fe/src/features/hedge/Bar.tsx
  git diff --name-only origin/main | .\map-paths.ps1
.OUTPUTS
  Objects { Path; Specs } ; unmapped paths have Specs = @('UNMAPPED')
#>
param([Parameter(ValueFromPipeline, ValueFromRemainingArguments)][string[]]$ChangedPaths)

begin {
    $repo = Split-Path $PSScriptRoot -Parent
    # Minimal YAML reader for docs-map.yml (paths/specs lists only) — avoids external modules.
    $lines = Get-Content (Join-Path $repo 'docs-map.yml')
    $mappings = @(); $ignore = @(); $cur = $null; $section = ''
    foreach ($l in $lines) {
        if ($l -match '^\s*#' -or $l.Trim() -eq '') { continue }
        if ($l -match '^mappings:') { $section = 'map'; continue }
        if ($l -match '^ignore:') { $section = 'ignore'; continue }
        if ($section -eq 'ignore' -and $l -match '^\s*-\s*"?([^"#]+)"?') { $ignore += $Matches[1].Trim(); continue }
        if ($section -eq 'map' -and $l -match '^\s*-\s*paths:\s*\[(.*)\]') {
            $cur = [pscustomobject]@{ Paths = @(); Specs = @() }; $mappings += $cur
            $cur.Paths = ($Matches[1] -split ',') | ForEach-Object { $_.Trim().Trim('"') } | Where-Object { $_ }
            continue
        }
        if ($section -eq 'map' -and $l -match '^\s*specs:\s*\[(.*?)\]') {
            $cur.Specs = ($Matches[1] -split ',') | ForEach-Object { $_.Trim().Trim('"') } | Where-Object { $_ }
        }
    }
    function Test-Glob([string]$glob, [string]$path) {
        $rx = '^' + [regex]::Escape($glob).Replace('\*\*/', '(.*/)?').Replace('\*\*', '.*').Replace('\*', '[^/]*') + '$'
        return $path -match $rx
    }
    $all = @()
}
process { $all += $ChangedPaths }
end {
    foreach ($p in $all | Where-Object { $_ }) {
        $p = $p -replace '\\', '/'
        if ($ignore | Where-Object { Test-Glob $_ $p }) { continue }
        $specs = @()
        foreach ($m in $mappings) { if ($m.Paths | Where-Object { Test-Glob $_ $p }) { $specs += $m.Specs } }
        [pscustomobject]@{ Path = $p; Specs = if ($specs) { $specs | Select-Object -Unique } else { @('UNMAPPED') } }
    }
}
