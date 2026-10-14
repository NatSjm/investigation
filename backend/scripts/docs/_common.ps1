<#
.SYNOPSIS
  Shared helpers for the lib-free doc generators. Dot-source from the gen-*.ps1 scripts.
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[cultureinfo]::CurrentCulture = [cultureinfo]::InvariantCulture   # identical sort order on every machine (ICU + machine culture otherwise)

$script:Utf8 = [System.Text.UTF8Encoding]::new($false)

function Read-Text([string]$Path) { [IO.File]::ReadAllText($Path, $script:Utf8) }

function Write-Text([string]$Path, [string]$Content) {
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [IO.File]::WriteAllText($Path, $Content, $script:Utf8)
}

function Get-SourceFiles([string]$Root, [string[]]$Include, [string[]]$ExcludeDirs = @('target','build','node_modules','.git','dist','coverage','generated')) {
    $rx = '[\\/](' + (($ExcludeDirs | ForEach-Object { [regex]::Escape($_) }) -join '|') + ')[\\/]'
    Get-ChildItem -Path $Root -Recurse -File -Include $Include | Where-Object { $_.FullName -notmatch $rx }
}

function Resolve-Out([string]$Root, [string]$Out) {
    if ([IO.Path]::IsPathRooted($Out)) { return $Out } else { return (Join-Path $Root $Out) }
}

function Get-RelPath([string]$Root, [string]$Full) {
    $r = [IO.Path]::GetFullPath($Root).TrimEnd('\','/')
    return $Full.Substring($r.Length + 1).Replace('\','/')
}

function Get-LineNumber([string]$Text, [int]$Index) {
    return ([regex]::Matches($Text.Substring(0, $Index), "`n")).Count + 1
}

function New-Header([string]$Title, [string]$Source, [string]$Description = "") {
    if (-not $Description) { $Description = "Generated map: $Title, derived from $Source; read instead of source files." }
    $date = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd')
@"
---
type: Document
title: "$($Title -replace '"', '\"')"
description: "$($Description -replace '"', '\"')"
generated:
  by: process:gen-docs
  at: $date
status: stable
---
# $Title

> Generated from ``$Source`` by ``scripts/docs`` (regex scan, no build required). Do not edit by hand.

"@
}

function Escape-Cell([string]$s) { ($s -replace '\|', '\|' -replace '\r?\n', ' ').Trim() }
