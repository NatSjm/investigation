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
& (Join-Path $PSScriptRoot 'gen-api-index.ps1')    -Root $Root -Out (Join-Path $rel 'api-index.md')
& (Join-Path $PSScriptRoot 'gen-events.ps1')       -Root $Root -Out (Join-Path $rel 'events.md')
& (Join-Path $PSScriptRoot 'gen-db-schema.ps1')    -Root $Root -Out (Join-Path $rel 'db-schema.md')
& (Join-Path $PSScriptRoot 'gen-docs-tags.ps1')    -Root $Root -Out (Join-Path $rel 'docs-tags.md')

$index = @"
# Generated code maps

Read these before opening source. Each file is a few hundred tokens.

- [codebase-map.md](codebase-map.md): modules, purpose, facade/controller/listener/job entry points
- [api-index.md](api-index.md): REST endpoints (method, path, handler, file:line)
- [events.md](events.md): Kafka topics with producers/consumers
- [db-schema.md](db-schema.md): tables and columns from migrations, ER diagram
- [docs-tags.md](docs-tags.md): spec ID (``@docs``) to code location
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
