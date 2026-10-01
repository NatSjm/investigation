<#
.SYNOPSIS
  Exported TypeScript types/interfaces index (names + fields, no implementation) - the cheapest FE context for agents.
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/types-index.md',
    [string]$Pattern = '*.types.ts'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Types index (FE)' $Pattern))
[void]$sb.AppendLine('Exported `interface`/`type` declarations verbatim (types only, ~1 line per field). Mirrors BE DTOs - compare with `api-index.md`.')
[void]$sb.AppendLine()
$count = 0
foreach ($f in Get-SourceFiles $Root @($Pattern) | Sort-Object FullName) {
    $t = Read-Text $f.FullName
    $rel = Get-RelPath $Root $f.FullName
    $decls = [regex]::Matches($t, '(?ms)^export\s+(?:interface|type|enum)\s+\w+[^{;=]*(?:\{[^{}\r\n]*\}|\{.*?^\}|=[^;]*;)')
    if ($decls.Count -eq 0) { continue }
    [void]$sb.AppendLine("## ``$rel``")
    [void]$sb.AppendLine('```ts')
    foreach ($d in $decls) { [void]$sb.AppendLine(($d.Value -replace '(?m)^\s*//.*$', '' -replace '(?m)^\s*$\r?\n', '').TrimEnd()); $count++ }
    [void]$sb.AppendLine('```')
    [void]$sb.AppendLine()
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "types-index: $count declaration(s) -> $Out"
