<#
.SYNOPSIS
  Runs all BE generators and writes docs/_generated/index.md (OKF-style reserved index for progressive disclosure).
.PARAMETER Check
  Exit 1 if any generated file would change (CI freshness gate).
#>
param(
    [string]$Root = '.',
    [string]$OutDir = 'docs/_generated',
    [switch]$Check
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$target = Join-Path $Root $OutDir
$work = if ($Check) { Join-Path ([IO.Path]::GetTempPath()) ("gen-docs-" + [guid]::NewGuid().ToString('N')) } else { $target }
New-Item -ItemType Directory -Force -Path $work | Out-Null
$rel = if ($Check) { $work } else { $OutDir }

& (Join-Path $PSScriptRoot 'gen-codebase-map.ps1') -Root $Root -Out (Join-Path $rel 'codebase-map.md')
& (Join-Path $PSScriptRoot 'gen-components.ps1')   -Root $Root -Out (Join-Path $rel 'components.md')
& (Join-Path $PSScriptRoot 'gen-api-index.ps1')    -Root $Root -Out (Join-Path $rel 'api-index.md')
& (Join-Path $PSScriptRoot 'gen-events.ps1')       -Root $Root -Out (Join-Path $rel 'events.md')
& (Join-Path $PSScriptRoot 'gen-db-schema.ps1')    -Root $Root -Out (Join-Path $rel 'db-schema.md')
& (Join-Path $PSScriptRoot 'gen-jobs.ps1')         -Root $Root -Out (Join-Path $rel 'jobs.md')
& (Join-Path $PSScriptRoot 'gen-docs-tags.ps1')    -Root $Root -Out (Join-Path $rel 'docs-tags.md')
& (Join-Path $PSScriptRoot 'gen-parameters.ps1')   -Root $Root -Out (Join-Path $rel 'parameters.md')

$index = @"
# Generated code maps

Read these before opening source. Each file is a few hundred tokens.
Contracts: ``core/src/main/resources/openapi/harbor-api.yaml`` (REST; FE client and BE interfaces are generated from it),
``core/src/main/resources/openapi/harbor-events.yaml`` (Kafka), ``core/src/main/resources/api/*.yaml`` (external services).

- [codebase-map.md](codebase-map.md): modules, technical layers with their classes, resource folders
- [components.md](components.md): one row per class - layer, stereotype, injected dependencies, tables, @docs, file:line
- [api-index.md](api-index.md): REST operations from the contract (method, path, operationId, handler, file:line)
- [events.md](events.md): Kafka topics with producers/consumers
- [db-schema.md](db-schema.md): tables and columns from migrations, ER diagram
- [jobs.md](jobs.md): scheduled jobs with their cron triggers
- [docs-tags.md](docs-tags.md): spec ID (``@docs``) to code location
- [parameters.md](parameters.md): admin parameter catalogue - every ``ParameterKey`` with seeded defaults per scope, readers and validator
"@
Write-Text (Join-Path $work 'index.md') $index

if ($Check) {
    $diff = 0
    foreach ($f in Get-ChildItem $work -File) {
        $cur = Join-Path $target $f.Name
        $a = if (Test-Path $cur) { (Read-Text $cur) -replace '(?m)^  at: .*$', '' } else { '' }
        $b = (Read-Text $f.FullName) -replace '(?m)^  at: .*$', ''
        if ($a -ne $b) { Write-Host "STALE: $OutDir/$($f.Name)"; $diff++ }
    }
    Remove-Item $work -Recurse -Force
    if ($diff) { Write-Error "$diff generated file(s) out of date. Run scripts/docs/gen-all.ps1"; exit 1 }
    Write-Host 'generated docs up to date'
}
