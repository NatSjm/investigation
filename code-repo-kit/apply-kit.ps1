<#
.SYNOPSIS
  Copies the code-repo-kit files for one flavour into a code repository (harbor-backend or harbor-frontend).
.DESCRIPTION
  Copied (relative to the kit):
    <flavour>/.github/**          -> <Target>/.github/**           (copilot-instructions, instructions, agents, prompts, hooks, workflows)
    <flavour>/AGENTS.md           -> <Target>/AGENTS.md
    <flavour>/scripts/docs/**     -> <Target>/scripts/docs/**      (generators, gen-all.ps1, FE graph exporter)
    shared/check-file-size.ps1    -> <Target>/scripts/check-file-size.ps1
    ci/docs-maps.yml              -> <Target>/.github/workflows/docs-maps.yml
  Existing files are overwritten (the kit is the source of truth). Supports -WhatIf / -Confirm.
.EXAMPLE
  ./apply-kit.ps1 -Flavour be -Target ..\backend -WhatIf
.EXAMPLE
  ./apply-kit.ps1 -Flavour fe -Target ..\frontend
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][ValidateSet('be', 'fe')][string]$Flavour,
    [Parameter(Mandatory)][string]$Target
)
$ErrorActionPreference = 'Stop'
$kit = $PSScriptRoot
if (-not (Test-Path $Target)) { throw "Target '$Target' does not exist (expected the root of the harbor-$(if ($Flavour -eq 'be') { 'backend' } else { 'frontend' }) checkout)." }
$Target = (Resolve-Path $Target).ProviderPath

$skipDirs = '[\\/](node_modules|out)[\\/]'
$plan = New-Object System.Collections.Generic.List[object]
function Add-Tree([string]$srcDir, [string]$dstDir) {
    if (-not (Test-Path $srcDir)) { return }
    foreach ($f in Get-ChildItem $srcDir -Recurse -File | Where-Object { $_.FullName -notmatch $skipDirs }) {
        $rel = $f.FullName.Substring($srcDir.Length).TrimStart('\', '/')
        $plan.Add([pscustomobject]@{ Source = $f.FullName; Dest = (Join-Path $dstDir $rel) })
    }
}
function Add-File([string]$src, [string]$dst) {
    if (-not (Test-Path $src)) { throw "Kit file missing: $src" }
    $plan.Add([pscustomobject]@{ Source = (Resolve-Path $src).ProviderPath; Dest = $dst })
}

Add-Tree (Join-Path $kit "$Flavour\.github")      (Join-Path $Target '.github')
Add-File (Join-Path $kit "$Flavour\AGENTS.md")    (Join-Path $Target 'AGENTS.md')
Add-Tree (Join-Path $kit "$Flavour\scripts\docs") (Join-Path $Target 'scripts\docs')
Add-File (Join-Path $kit 'shared\check-file-size.ps1') (Join-Path $Target 'scripts\check-file-size.ps1')
Add-File (Join-Path $kit 'ci\docs-maps.yml')      (Join-Path $Target '.github\workflows\docs-maps.yml')

$copied = 0
foreach ($p in $plan) {
    $relDest = $p.Dest.Substring($Target.Length).TrimStart('\', '/').Replace('\', '/')
    if ($PSCmdlet.ShouldProcess($relDest, "Copy from kit ($Flavour)")) {
        New-Item -ItemType Directory -Force -Path (Split-Path $p.Dest) | Out-Null
        Copy-Item $p.Source $p.Dest -Force
        Write-Host "  copied  $relDest"
        $copied++
    }
}
if (-not $WhatIfPreference) {
    Write-Host "apply-kit ($Flavour): $copied file(s) -> $Target"
    Write-Host "Next: pwsh scripts/docs/gen-all.ps1  |  pwsh scripts/check-file-size.ps1 -Root . -MaxLines $(if ($Flavour -eq 'be') { 400 } else { 300 }) -Baseline .filesize-baseline.txt -WriteBaseline"
    Write-Host "Then set the repo variable REPO_KIND=$Flavour (docs-maps.yml) and configure content exclusion from shared/copilot-content-exclusion.yml."
}
