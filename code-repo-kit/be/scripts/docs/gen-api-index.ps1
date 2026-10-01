<#
.SYNOPSIS
  REST API index from Spring annotations (no app start, no springdoc): method | path | handler | file:line.
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/api-index.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$verbs = 'Get','Post','Put','Patch','Delete'
$rows = New-Object System.Collections.Generic.List[object]

foreach ($f in Get-SourceFiles $Root @('*.kt')) {
    $t = Read-Text $f.FullName
    if ($t -notmatch '@RestController') { continue }
    $rel = Get-RelPath $Root $f.FullName
    $base = ''
    $cm = [regex]::Match($t, '@RequestMapping\(\s*(?:value\s*=\s*)?\[?"([^"]*)"')
    if ($cm.Success) { $base = $cm.Groups[1].Value }
    $cls = [regex]::Match($t, '(?m)^\s*class\s+(\w+)').Groups[1].Value

    $rx = '@(' + ($verbs -join '|') + ')Mapping\s*(?:\(\s*(?:value\s*=\s*)?\[?"([^"]*)"[^)]*\))?\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:override\s+|suspend\s+)*fun\s+(\w+)\s*\(([^)]*)\)'
    foreach ($m in [regex]::Matches($t, $rx)) {
        $verb = $m.Groups[1].Value.ToUpper()
        $path = ($base.TrimEnd('/') + '/' + $m.Groups[2].Value.TrimStart('/')).TrimEnd('/')
        if (-not $path) { $path = '/' }
        $params = ($m.Groups[4].Value -replace '@\w+(\([^)]*\))?\s*', '' -replace '\s+', ' ').Trim()
        $rows.Add([pscustomobject]@{
            Verb = $verb; Path = $path; Handler = "$cls.$($m.Groups[3].Value)"; Params = $params
            Loc = "$rel`:$(Get-LineNumber $t $m.Index)"
        })
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'REST API index (BE)' '@RestController / @*Mapping scan'))
[void]$sb.AppendLine("$($rows.Count) endpoint(s). DTO field lists: open the DTO file, not the controller.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Method | Path | Handler | Params | Location |')
[void]$sb.AppendLine('|---|---|---|---|---|')
foreach ($r in $rows | Sort-Object Path, Verb) {
    [void]$sb.AppendLine("| $($r.Verb) | ``$($r.Path)`` | ``$($r.Handler)`` | $(Escape-Cell $r.Params) | ``$($r.Loc)`` |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "api-index: $($rows.Count) endpoint(s) -> $Out"
