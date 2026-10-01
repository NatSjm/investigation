<#
.SYNOPSIS
  Approximate DB schema from Flyway SQL migrations (CREATE TABLE / ALTER TABLE ADD|DROP COLUMN). No database needed.
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/db-schema.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$tables = [ordered]@{}
$migrations = @(Get-SourceFiles $Root @('V*.sql','R*.sql') | Where-Object { $_.FullName -match '[\\/](migration|db)[\\/]' }) |
    Sort-Object { if ($_.Name -match '^V(\d+(?:[._]\d+)*)__') { [version]($Matches[1] -replace '_','.' -replace '^(\d+)$','$1.0') } else { [version]'9999.0' } }, Name

foreach ($f in $migrations) {
    $sql = Read-Text $f.FullName
    $rel = Get-RelPath $Root $f.FullName
    foreach ($m in [regex]::Matches($sql, '(?is)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*?)\)\s*;')) {
        $name = $m.Groups[1].Value.ToLower()
        $cols = [ordered]@{}
        foreach ($line in ($m.Groups[2].Value -split ',\s*\r?\n')) {
            $l = $line.Trim()
            if ($l -match '^(PRIMARY\s+KEY|CONSTRAINT|UNIQUE|FOREIGN\s+KEY|CHECK)') { continue }
            $cm = [regex]::Match($l, '^(\w+)\s+(\w+(?:\s*\([^)]*\))?)(.*)$')
            if ($cm.Success) {
                $colName = $cm.Groups[1].Value.ToLower(); $colType = $cm.Groups[2].Value; $rest = $cm.Groups[3].Value
                $flags = @()
                if ($rest -match 'PRIMARY\s+KEY') { $flags += 'PK' }
                if ($rest -match 'NOT\s+NULL') { $flags += 'NN' }
                $fk = [regex]::Match($rest, 'REFERENCES\s+(\w+)')
                if ($fk.Success) { $flags += "FK->$($fk.Groups[1].Value.ToLower())" }
                $cols[$colName] = "$colType $($flags -join ' ')".Trim()
            }
        }
        $tables[$name] = @{ cols = $cols; src = $rel }
    }
    foreach ($m in [regex]::Matches($sql, '(?i)ALTER\s+TABLE\s+(\w+)\s+ADD\s+(?:COLUMN\s+)?(\w+)\s+([^,;]+)')) {
        $tn = $m.Groups[1].Value.ToLower()
        if ($tables.Contains($tn)) { $tables[$tn].cols[$m.Groups[2].Value.ToLower()] = ($m.Groups[3].Value -replace '\s+', ' ').Trim() + " (+$rel)" }
    }
    foreach ($m in [regex]::Matches($sql, '(?i)ALTER\s+TABLE\s+(\w+)\s+DROP\s+(?:COLUMN\s+)?(\w+)')) {
        $tn = $m.Groups[1].Value.ToLower()
        if ($tables.Contains($tn)) { $tables[$tn].cols.Remove($m.Groups[2].Value.ToLower()) }
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'DB schema (approximate, from migrations)' 'Flyway V*.sql'))
[void]$sb.AppendLine("$($tables.Count) table(s). Derived by regex from migrations - types/constraints are indicative; verify against a real DB for DDL work.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('```mermaid')
[void]$sb.AppendLine('erDiagram')
foreach ($tn in $tables.Keys) {
    foreach ($c in $tables[$tn].cols.Keys) {
        if ($tables[$tn].cols[$c] -match 'FK->(\w+)') { [void]$sb.AppendLine("  $($Matches[1]) ||--o{ $tn : $c") }
    }
}
[void]$sb.AppendLine('```')
[void]$sb.AppendLine()
foreach ($tn in $tables.Keys) {
    [void]$sb.AppendLine("## ``$tn``")
    [void]$sb.AppendLine("Created in ``$($tables[$tn].src)``")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('| Column | Type / flags |')
    [void]$sb.AppendLine('|---|---|')
    foreach ($c in $tables[$tn].cols.Keys) { [void]$sb.AppendLine("| ``$c`` | $(Escape-Cell $tables[$tn].cols[$c]) |") }
    [void]$sb.AppendLine()
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "db-schema: $($tables.Count) table(s) -> $Out"
