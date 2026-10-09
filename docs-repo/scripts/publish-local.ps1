<#
.SYNOPSIS
  Local stand-in for the code repositories' CI publish job (code-repo-kit/ci/docs-maps.yml): copies the generated
  maps and the contracts from ../backend and ../frontend into generated/be, generated/fe, generated/openapi,
  generated/asyncapi of this docs repo. Run gen-all.ps1 in both repos first.
.EXAMPLE
  .\publish-local.ps1
  .\publish-local.ps1 -Backend D:\src\harbor-backend -Frontend D:\src\harbor-frontend
#>
param(
    [string]$Backend = (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'backend'),
    [string]$Frontend = (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'frontend')
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
function Copy-Into([string]$src, [string]$dstDir, [string]$filter = '*') {
    if (-not (Test-Path $src)) { Write-Host "skip (missing): $src" -ForegroundColor Yellow; return }
    if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Force -Path $dstDir | Out-Null }
    Get-ChildItem $src -File -Filter $filter | ForEach-Object { Copy-Item $_.FullName (Join-Path $dstDir $_.Name) -Force; Write-Host "  $($_.Name) -> $($dstDir.Substring($repo.Length + 1))" }
}
Write-Host "BE maps"; Copy-Into (Join-Path $Backend 'docs/_generated') (Join-Path $repo 'generated/be') '*.md'
Copy-Into (Join-Path $Backend 'docs/_generated') (Join-Path $repo 'generated/be') 'graph-export-be.json'
Write-Host "FE maps"; Copy-Into (Join-Path $Frontend 'docs/_generated') (Join-Path $repo 'generated/fe') '*.md'
Copy-Into (Join-Path $Frontend 'docs/_generated') (Join-Path $repo 'generated/fe') 'graph-export-fe.json'
Write-Host "Contracts"
$res = Join-Path $Backend 'core/src/main/resources'
$oa = Join-Path $res 'openapi/harbor-api.yaml'; if (-not (Test-Path $oa)) { $oa = Join-Path $Backend 'api/openapi.yaml' }; if (Test-Path $oa) { New-Item -ItemType Directory -Force -Path (Join-Path $repo 'generated/openapi') | Out-Null; Copy-Item $oa (Join-Path $repo 'generated/openapi/backend.yaml') -Force; Write-Host '  harbor-api.yaml -> generated/openapi/backend.yaml' }
$aa = Join-Path $res 'openapi/harbor-events.yaml'; if (Test-Path $aa) { New-Item -ItemType Directory -Force -Path (Join-Path $repo 'generated/asyncapi') | Out-Null; Copy-Item $aa (Join-Path $repo 'generated/asyncapi/backend.yaml') -Force; Write-Host '  harbor-events.yaml -> generated/asyncapi/backend.yaml' }
Copy-Into (Join-Path $res 'api') (Join-Path $repo 'generated/openapi/external') '*.yaml'
# the generated/be and generated/fe index.md files are reserved OKF files; the bundle index builder owns them
Remove-Item (Join-Path $repo 'generated/be/index.md'), (Join-Path $repo 'generated/fe/index.md') -ErrorAction SilentlyContinue
Write-Host "done - now run gen-graph.ps1 and build-index.ps1" -ForegroundColor Green
