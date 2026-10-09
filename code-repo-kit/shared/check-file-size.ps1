<#
.SYNOPSIS
  Token-budget lint: fails when source files exceed a line cap (Copilot pulls whole files on #file / open editor).
  No external tools. Put in CI as a warn-first, then blocking gate. Grandfather existing offenders via -Baseline.
  Used by harbor-backend (400 lines, *.kt) and harbor-frontend (300 lines, *.ts/*.tsx); copied to scripts/ by apply-kit.ps1.
.EXAMPLE
  ./check-file-size.ps1 -Root . -MaxLines 400 -Include *.kt -Baseline .filesize-baseline.txt
.EXAMPLE
  ./check-file-size.ps1 -Root . -MaxLines 300 -Include *.ts,*.tsx -Baseline .filesize-baseline.txt -WriteBaseline
#>
param(
    [string]$Root = '.',
    [int]$MaxLines = 400,
    [string[]]$Include = @('*.kt','*.java','*.ts','*.tsx'),
    [string[]]$ExcludeDirs = @('target','build','node_modules','.git','dist','coverage','generated','_generated'),
    [string]$Baseline = '',
    [switch]$WriteBaseline
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path $Root).ProviderPath
$rx = '[\\/](' + (($ExcludeDirs | ForEach-Object { [regex]::Escape($_) }) -join '|') + ')[\\/]'
$known = @{}
if ($Baseline -and (Test-Path (Join-Path $Root $Baseline))) {
    Get-Content (Join-Path $Root $Baseline) | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object { $known[$_.Trim()] = $true }
}

$offenders = foreach ($f in Get-ChildItem $Root -Recurse -File -Include $Include | Where-Object { $_.FullName -notmatch $rx }) {
    $n = ([IO.File]::ReadAllLines($f.FullName)).Count
    if ($n -gt $MaxLines) {
        $rel = $f.FullName.Substring($Root.Length + 1).Replace('\','/')
        [pscustomobject]@{ File = $rel; Lines = $n; Grandfathered = $known.ContainsKey($rel) }
    }
}
$offenders = @($offenders | Sort-Object Lines -Descending)

if ($WriteBaseline) {
    $out = @("# files allowed to exceed $MaxLines lines (shrink over time; do not add)") + ($offenders | ForEach-Object { $_.File })
    [IO.File]::WriteAllLines((Join-Path $Root $Baseline), $out)
    Write-Host "baseline written: $($offenders.Count) file(s)"; exit 0
}

foreach ($o in $offenders) { Write-Host ("{0,6}  {1}{2}" -f $o.Lines, $o.File, $(if ($o.Grandfathered) { '  (baseline)' })) }
$new = @($offenders | Where-Object { -not $_.Grandfathered })
if ($new.Count) { Write-Error "$($new.Count) file(s) exceed $MaxLines lines (not in baseline). Split them - large files cost tokens on every Copilot read."; exit 1 }
Write-Host "file-size: OK ($($offenders.Count) grandfathered)"
