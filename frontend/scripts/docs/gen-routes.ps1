<#
.SYNOPSIS
  Route table from react-router usage: object routes `{ path: '...', element: <X/> }` and JSX `<Route path="..." element={<X/>}>`.
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/routes.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$rows = New-Object System.Collections.Generic.List[object]
foreach ($f in Get-SourceFiles $Root @('*.tsx','*.ts') | Where-Object { $_.Name -notmatch '\.(test|spec)\.' }) {
    $t = Read-Text $f.FullName
    if ($t -notmatch '\bpath\s*[:=]') { continue }
    $rel = Get-RelPath $Root $f.FullName
    foreach ($m in [regex]::Matches($t, 'path:\s*[''"`]([^''"`]+)[''"`][^}]*?element:\s*<(\w+)')) {
        $rows.Add([pscustomobject]@{ Path = $m.Groups[1].Value; Component = $m.Groups[2].Value; Loc = "$rel`:$(Get-LineNumber $t $m.Index)" })
    }
    foreach ($m in [regex]::Matches($t, '<Route\s+[^>]*?path=[''"]([^''"]+)[''"][^>]*?element=\{<(\w+)')) {
        $rows.Add([pscustomobject]@{ Path = $m.Groups[1].Value; Component = $m.Groups[2].Value; Loc = "$rel`:$(Get-LineNumber $t $m.Index)" })
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Routes (FE)' 'react-router route objects / <Route> elements'))
[void]$sb.AppendLine("$($rows.Count) route(s). Component -> feature: see codebase-map.md public exports.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Path | Component | Location |')
[void]$sb.AppendLine('|---|---|---|')
foreach ($r in $rows | Sort-Object Path) {
    [void]$sb.AppendLine("| ``$($r.Path)`` | ``$($r.Component)`` | ``$($r.Loc)`` |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "routes: $($rows.Count) route(s) -> $Out"
