<#
.SYNOPSIS
  CI gate for FE/BE PRs: if a mapped code path changed, the linked spec must have last_verified >= PR base date,
  unless the PR carries label 'docs-not-affected'.
.EXAMPLE
  .\check-freshness.ps1 -ChangedPaths (git diff --name-only origin/main) -SinceDate (Get-Date).AddDays(-14)
#>
param(
    [Parameter(Mandatory)][string[]]$ChangedPaths,
    [datetime]$SinceDate = (Get-Date).AddDays(-30),
    [switch]$AllowUnmapped
)
$repo = Split-Path $PSScriptRoot -Parent
$hits = $ChangedPaths | & (Join-Path $PSScriptRoot 'map-paths.ps1')
$stale = @(); $unmapped = @()

foreach ($h in $hits) {
    if ($h.Specs -contains 'UNMAPPED') { $unmapped += $h.Path; continue }
    foreach ($spec in $h.Specs) {
        Get-ChildItem (Join-Path $repo $spec) -ErrorAction SilentlyContinue | ForEach-Object {
            $fm = (Get-Content $_.FullName -Raw)
            $lv = if ($fm -match 'last_verified:\s*(\d{4}-\d{2}-\d{2})') { [datetime]$Matches[1] } else { $null }
            if (-not $lv -or $lv -lt $SinceDate) { $stale += "$($h.Path) -> $spec (last_verified=$lv)" }
        }
    }
}

$stale | Select-Object -Unique | ForEach-Object { Write-Host "STALE  $_" -ForegroundColor Yellow }
$unmapped | ForEach-Object { Write-Host "UNMAPPED $_" -ForegroundColor Magenta }
if ($stale -or ($unmapped -and -not $AllowUnmapped)) { exit 1 }
Write-Host 'Freshness OK' -ForegroundColor Green
