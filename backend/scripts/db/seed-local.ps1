<#
.SYNOPSIS
  Loads the named datasets of scripts/db/seed/*.sql into the local database (docker compose postgres by default).
.PARAMETER Dataset
  One or more dataset names (`-- dataset:` header). Default: every seed file, in file-name order.
.PARAMETER Fixtures
  Also load the integration-test fixtures from core/src/test/resources/datasets (same header convention).
.EXAMPLE
  .\scripts\db\seed-local.ps1
  .\scripts\db\seed-local.ps1 -Dataset reference-clients, p1-baseline-12m
  .\scripts\db\seed-local.ps1 -Fixtures -Database harbor_test
#>
param(
    [string[]]$Dataset,
    [switch]$Fixtures,
    [string]$Database = 'harbor',
    [string]$ComposeFile = (Join-Path $PSScriptRoot '..\..\init_docker_compose\docker-compose.yml'),
    [switch]$DryRun
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).ProviderPath

$files = @(Get-ChildItem (Join-Path $PSScriptRoot 'seed') -Filter '*.sql' | Sort-Object Name)
if ($Fixtures) { $files += @(Get-ChildItem (Join-Path $root 'core\src\test\resources\datasets') -Filter '*.sql' | Sort-Object Name) }

$selected = foreach ($f in $files) {
    $head = (Get-Content $f.FullName -TotalCount 10) -join "`n"
    $name = if ($head -match '(?m)^--\s*dataset:\s*(\S+)') { $Matches[1] } else { $f.BaseName }
    if (-not $Dataset -or $Dataset -contains $name) { [pscustomobject]@{ Name = $name; File = $f.FullName } }
}
if (-not $selected) { Write-Error "no dataset matched: $($Dataset -join ', ')"; exit 1 }

foreach ($s in $selected) {
    $rel = $s.File.Substring($root.Length + 1).Replace('\', '/')
    if ($DryRun) { Write-Host "would load $($s.Name)  ($rel)"; continue }
    Write-Host "loading $($s.Name)  ($rel)"
    # psql inside the compose container: no client installation needed on the developer machine
    Get-Content $s.File -Raw | docker compose -f $ComposeFile exec -T postgres psql -v ON_ERROR_STOP=1 -q -U harbor -d $Database
    if ($LASTEXITCODE) { Write-Error "psql failed for $($s.Name)"; exit $LASTEXITCODE }
}
Write-Host "done: $($selected.Count) dataset(s) into $Database"
