<#
.SYNOPSIS
  Traceability index: every KDoc/JSDoc `@docs <ID>` tag -> declaration signature + first summary line + file:line.
  Lets agents jump from a spec ID (HEDGE-001, hedge_monthly_cashflow) straight to the code without searching.
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/docs-tags.md',
    [string[]]$Include = @('*.kt','*.java','*.ts','*.tsx')
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$rows = New-Object System.Collections.Generic.List[object]
# KDoc/JSDoc block followed by the declaration line (annotations skipped)
$rx = '/\*\*(?<doc>.*?)\*/\s*(?:@\w+(?:\([^)]*\))?\s*)*(?<decl>[^\r\n{=]*?(?:fun|class|object|interface|function|const|export)\s[^\r\n{=]*)'
foreach ($f in Get-SourceFiles $Root $Include) {
    $t = Read-Text $f.FullName
    if ($t -notmatch '@docs\s') { continue }
    $rel = Get-RelPath $Root $f.FullName
    foreach ($m in [regex]::Matches($t, $rx, 'Singleline')) {
        $doc = $m.Groups['doc'].Value
        $ids = [regex]::Matches($doc, '@docs\s+([\w.-]+)') | ForEach-Object { $_.Groups[1].Value }
        if (-not $ids) { continue }
        $summary = (($doc -split '\r?\n' | ForEach-Object { ($_ -replace '^\s*\*\s?', '' -replace '@docs\s+[\w.-]+', '').Trim() } | Where-Object { $_ -and $_ -notmatch '^@' }) | Select-Object -First 1)
        $decl = ($m.Groups['decl'].Value -replace '\s+', ' ').Trim()
        if ($decl -match '^export(\s+type)?$') { $decl = "(module) $($f.Name)" }
        foreach ($id in $ids) {
            $rows.Add([pscustomobject]@{ Id = $id; Decl = $decl; Summary = $summary; Loc = "$rel`:$(Get-LineNumber $t $m.Groups['decl'].Index)" })
        }
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Spec-to-code traceability (@docs tags)' '@docs <ID> tags in KDoc/JSDoc'))
[void]$sb.AppendLine("$($rows.Count) tag(s). Resolve a spec/calculation ID here, then open only the listed location.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Spec ID | Declaration | Summary | Location |')
[void]$sb.AppendLine('|---|---|---|---|')
foreach ($r in $rows | Sort-Object Id, Loc) {
    [void]$sb.AppendLine("| ``$($r.Id)`` | ``$(Escape-Cell $r.Decl)`` | $(Escape-Cell $r.Summary) | ``$($r.Loc)`` |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "docs-tags: $($rows.Count) tag(s) -> $Out"
