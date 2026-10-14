<#
.SYNOPSIS
  Runs all FE generators and writes docs/_generated/index.md. -Check: exit 1 if any output is stale (CI gate).
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
& (Join-Path $PSScriptRoot 'gen-routes.ps1')       -Root $Root -Out (Join-Path $rel 'routes.md')
& (Join-Path $PSScriptRoot 'gen-types-index.ps1')  -Root $Root -Out (Join-Path $rel 'types-index.md')
& (Join-Path $PSScriptRoot 'gen-docs-tags.ps1')    -Root $Root -Out (Join-Path $rel 'docs-tags.md') -Include @('*.ts','*.tsx')

$index = @"
# Generated code maps

Read these before opening source. Each file is a few hundred tokens.

- [codebase-map.md](codebase-map.md): features, purpose, public exports, API calls
- [components.md](components.md): shared component library (src/shared/**): props, purpose, used by which features
- [routes.md](routes.md): URL -> component
- [types-index.md](types-index.md): exported types/interfaces (DTO mirrors)
- [docs-tags.md](docs-tags.md): spec ID (``@docs``) to code location
"@
Write-Text (Join-Path $work 'index.md') $index

if ($Check) {
    $diff = 0
    foreach ($f in Get-ChildItem $work -File) {
        $cur = Join-Path $target $f.Name
        $a = if (Test-Path $cur) { (Read-Text $cur) -replace '(?m)^  at: .*$', '' -replace "`r", '' } else { '' }
        $b = (Read-Text $f.FullName) -replace '(?m)^  at: .*$', '' -replace "`r", ''
        if ($a -ne $b) { Write-Host "STALE: $OutDir/$($f.Name)"; $diff++ }
    }
    Remove-Item $work -Recurse -Force
    if ($diff) { Write-Error "$diff generated file(s) out of date. Run scripts/docs/gen-all.ps1"; exit 1 }
    Write-Host 'generated docs up to date'
}
