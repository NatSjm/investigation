<#
.SYNOPSIS
  Scheduled jobs catalogue: every `@Scheduled` method with its trigger (cron / fixedDelay / fixedRate), the
  first KDoc line and file:line. Lets agents answer "what runs when" without opening the job classes.
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/jobs.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$rows = New-Object System.Collections.Generic.List[object]
$rx = '(?:/\*\*(?<doc>.*?)\*/\s*)?@Scheduled\((?<args>[^)]*)\)\s*(?:@\w+(?:\([^)]*\))?\s*)*fun\s+(?<fn>\w+)'
foreach ($f in Get-SourceFiles $Root @('*.kt')) {
    $t = Read-Text $f.FullName
    if ($t -notmatch '@Scheduled') { continue }
    $rel = Get-RelPath $Root $f.FullName
    $cls = [regex]::Match($t, '(?m)^\s*class\s+(\w+)').Groups[1].Value
    # class-level KDoc is the fallback summary when the @Scheduled method itself has none
    $classDoc = [regex]::Match($t, '(?s)/\*\*(.*?)\*/\s*(?:@\w+(?:\([^)]*\))?\s*)*class\s+\w+').Groups[1].Value
    function First-Line([string]$doc) { (($doc -split '\r?\n' | ForEach-Object { ($_ -replace '^\s*\*\s?', '').Trim() } | Where-Object { $_ -and $_ -notmatch '^@' }) | Select-Object -First 1) }
    foreach ($m in [regex]::Matches($t, $rx, 'Singleline')) {
        $args = $m.Groups['args'].Value
        $trigger = if ($args -match 'cron\s*=\s*"([^"]+)"') { "cron ``$($Matches[1])``" }
                   elseif ($args -match '(fixedDelay|fixedRate|initialDelay)\w*\s*=\s*([^,)]+)') { "$($Matches[1]) $($Matches[2].Trim())" }
                   else { $args.Trim() }
        $doc = $m.Groups['doc'].Value
        $summary = if ($doc) { First-Line $doc } elseif ($classDoc) { First-Line $classDoc } else { '' }
        $rows.Add([pscustomobject]@{ Job = "$cls.$($m.Groups['fn'].Value)"; Trigger = $trigger; Summary = $summary; Loc = "$rel`:$(Get-LineNumber $t $m.Groups['fn'].Index)" })
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Scheduled jobs (BE)' '@Scheduled scan'))
[void]$sb.AppendLine("$($rows.Count) job(s). Cron expressions are Spring 6-field (seconds first).")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Job | Trigger | Summary | Location |')
[void]$sb.AppendLine('|---|---|---|---|')
foreach ($r in $rows | Sort-Object Job) {
    [void]$sb.AppendLine("| ``$($r.Job)`` | $($r.Trigger) | $(Escape-Cell $r.Summary) | ``$($r.Loc)`` |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "jobs: $($rows.Count) job(s) -> $Out"
