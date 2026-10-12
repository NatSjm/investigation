<#
.SYNOPSIS
  Deprecated name. The local publish step is now the single evidence collector: scripts/collect-evidence.ps1
  (same inputs, plus validation, deletion handling and generated/manifest.yml). This wrapper forwards to it.
.EXAMPLE
  .\publish-local.ps1                      # == .\collect-evidence.ps1
  .\publish-local.ps1 -Backend D:\src\harbor-backend -Frontend D:\src\harbor-frontend
#>
param(
    [string]$Backend,
    [string]$Frontend
)
Write-Host "publish-local.ps1 is deprecated: use scripts/collect-evidence.ps1 (forwarding)" -ForegroundColor Yellow
& (Join-Path $PSScriptRoot 'collect-evidence.ps1') @PSBoundParameters
exit $LASTEXITCODE
