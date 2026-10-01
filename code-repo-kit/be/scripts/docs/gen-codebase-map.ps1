<#
.SYNOPSIS
  Codebase map for a Maven/Kotlin multi-module repo: module -> purpose -> entry points. One line per module.
.EXAMPLE
  ./gen-codebase-map.ps1 -Root . -Out docs/_generated/codebase-map.md
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/codebase-map.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$rootPom = Join-Path $Root 'pom.xml'
if (-not (Test-Path $rootPom)) { throw "No pom.xml in $Root" }
[xml]$pom = Read-Text $rootPom
$ns = @{ m = 'http://maven.apache.org/POM/4.0.0' }
$modules = @(Select-Xml -Xml $pom -Namespace $ns -XPath '//m:modules/m:module' | ForEach-Object { $_.Node.InnerText })
if ($modules.Count -eq 0) { $modules = @('.') }

$rows = foreach ($m in $modules) {
    $mDir = Join-Path $Root $m
    $desc = ''
    $mPom = Join-Path $mDir 'pom.xml'
    if (Test-Path $mPom) {
        [xml]$mx = Read-Text $mPom
        $d = Select-Xml -Xml $mx -Namespace $ns -XPath '/m:project/m:description'
        if ($d) { $desc = $d.Node.InnerText }
    }
    $srcMain = Join-Path $mDir 'src/main'
    $files = @(); if (Test-Path $srcMain) { $files = @(Get-SourceFiles $srcMain @('*.kt','*.java')) }

    $entry = [ordered]@{ facades = @(); controllers = @(); listeners = @(); jobs = @() }
    $packages = New-Object System.Collections.Generic.HashSet[string]
    foreach ($f in $files) {
        $t = Read-Text $f.FullName
        $pm = [regex]::Match($t, '(?m)^package\s+([\w.]+)')
        if ($pm.Success) { [void]$packages.Add($pm.Groups[1].Value) }
        $rel = Get-RelPath $Root $f.FullName
        if ($f.Name -match '(Facade|UseCase|Service)\.kt$' -and $t -match '(?m)^\s*/\*\*') { $entry.facades += $rel }
        if ($t -match '@RestController') { $entry.controllers += $rel }
        if ($t -match '@KafkaListener') { $entry.listeners += $rel }
        if ($t -match '@Scheduled') { $entry.jobs += $rel }
    }
    $basePkg = ($packages | Sort-Object { $_.Length } | Select-Object -First 1)
    $ep = @()
    foreach ($k in $entry.Keys) { if ($entry[$k].Count) { $ep += "$k`: " + (($entry[$k] | ForEach-Object { '`' + $_ + '`' }) -join ', ') } }
    [pscustomobject]@{ Module = $m; Desc = $desc; Pkg = $basePkg; Files = $files.Count; Entry = ($ep -join '<br>') }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Codebase map (BE)' 'pom.xml modules + annotation scan'))
[void]$sb.AppendLine('Read the **facade** file of a module first; open `calc/`, `messaging/`, repositories only when the facade is not enough.')
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Module | Purpose | Base package | Files | Entry points |')
[void]$sb.AppendLine('|---|---|---|---|---|')
foreach ($r in $rows) {
    [void]$sb.AppendLine("| ``$($r.Module)`` | $(Escape-Cell $r.Desc) | ``$($r.Pkg)`` | $($r.Files) | $($r.Entry) |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "codebase-map: $($rows.Count) module(s) -> $Out"
