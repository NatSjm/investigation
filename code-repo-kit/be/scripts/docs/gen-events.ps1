<#
.SYNOPSIS
  Kafka topic catalogue: consumers (@KafkaListener) and producers (KafkaTemplate.send) with constant resolution.
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/events.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$files = @(Get-SourceFiles $Root @('*.kt'))
$consts = @{}
foreach ($f in $files) {
    foreach ($m in [regex]::Matches((Read-Text $f.FullName), 'const\s+val\s+(\w+)\s*=\s*"([^"]+)"')) {
        $consts[$m.Groups[1].Value] = $m.Groups[2].Value
    }
}
function Resolve-Topic([string]$expr) {
    $e = $expr.Trim()
    if ($e -match '^"([^"]+)"$') { return $Matches[1] }
    $name = ($e -split '\.')[-1]
    if ($consts.ContainsKey($name)) { return $consts[$name] }
    return "<$e>"
}

$topics = @{}
function Add-Usage([string]$topic, [string]$kind, [string]$who) {
    if (-not $topics.ContainsKey($topic)) { $topics[$topic] = @{ consumers = @(); producers = @() } }
    $topics[$topic][$kind] += $who
}

foreach ($f in $files) {
    $t = Read-Text $f.FullName
    if ($t -notmatch 'KafkaListener|KafkaTemplate') { continue }
    $rel = Get-RelPath $Root $f.FullName
    foreach ($m in [regex]::Matches($t, '@KafkaListener\(([^)]*)\)\s*(?:@\w+\s*)*fun\s+(\w+)')) {
        $args = $m.Groups[1].Value
        $tm = [regex]::Match($args, 'topics\s*=\s*(\[[^\]]*\]|"[^"]*"|[\w.]+)')
        if (-not $tm.Success) { continue }
        $list = $tm.Groups[1].Value.Trim('[',']') -split ','
        $grp = [regex]::Match($args, 'groupId\s*=\s*"([^"]*)"').Groups[1].Value
        foreach ($x in $list) {
            Add-Usage (Resolve-Topic $x) 'consumers' "``$($m.Groups[2].Value)`` ($rel`:$(Get-LineNumber $t $m.Index)$(if ($grp) { ", group $grp" }))"
        }
    }
    foreach ($m in [regex]::Matches($t, '\.send\(\s*([^,)]+)')) {
        $cls = [regex]::Match($t.Substring(0, $m.Index), '(?s).*class\s+(\w+)').Groups[1].Value
        Add-Usage (Resolve-Topic $m.Groups[1].Value) 'producers' "``$cls`` ($rel`:$(Get-LineNumber $t $m.Index))"
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Kafka events (BE)' '@KafkaListener / KafkaTemplate.send scan'))
[void]$sb.AppendLine("$($topics.Count) topic(s). Payload schema: open the event class named in the handler signature.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Topic | Producers (this repo) | Consumers (this repo) |')
[void]$sb.AppendLine('|---|---|---|')
foreach ($k in $topics.Keys | Sort-Object) {
    $p = if ($topics[$k].producers.Count) { $topics[$k].producers -join '<br>' } else { '_external_' }
    $c = if ($topics[$k].consumers.Count) { $topics[$k].consumers -join '<br>' } else { '_external_' }
    [void]$sb.AppendLine("| ``$k`` | $p | $c |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "events: $($topics.Count) topic(s) -> $Out"
