<#
.SYNOPSIS
  Parameter catalogue: every key of the `ParameterKey` enum with the values seeded by the Flyway migrations
  (`INSERT INTO parameter_set`), the classes that read it and the validator that bounds it. Lets agents answer
  "which admin parameters exist, what is the default, who reads it" without opening the enum, the migrations and
  the services. The MEANING of a key is documentation, not code: `docs-repo/domain/calculations/*.md`
  (`## Parameters`) and the admin feature spec; `validate-frontmatter.ps1` cross-checks both against this file.
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/parameters.md',
    [string]$EnumName = 'ParameterKey',
    [string]$Table = 'parameter_set'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

# 1. keys: enum constants with their string key
$enumFile = Get-SourceFiles $Root @("$EnumName.kt") | Select-Object -First 1
$keys = [ordered]@{}
$enumRel = ''
if ($enumFile) {
    $enumRel = Get-RelPath $Root $enumFile.FullName
    $et = Read-Text $enumFile.FullName
    foreach ($m in [regex]::Matches($et, '(?m)^\s*(?<const>[A-Z][A-Z0-9_]*)\s*\(\s*"(?<key>[^"]+)"\s*\)')) {
        $keys[$m.Groups['key'].Value] = @{
            Const = $m.Groups['const'].Value; Line = Get-LineNumber $et $m.Index
            Seeds = New-Object System.Collections.Generic.List[string]; Readers = @{}; Validators = @{}
        }
    }
}

# 2. seeds: INSERT INTO <table> (...) VALUES (...), (...) in the migrations; column order taken from the column list
$unknownSeeds = @{}
$seedCount = 0
$insertRx = "(?is)INSERT\s+INTO\s+$([regex]::Escape($Table))\s*\((?<cols>[^)]*)\)\s*VALUES\s*(?<vals>.*?);"
foreach ($f in Get-SourceFiles $Root @('*.sql') | Where-Object { $_.FullName -match '[\\/]db[\\/]migration[\\/]' } | Sort-Object Name) {
    $t = Read-Text $f.FullName
    $rel = Get-RelPath $Root $f.FullName
    foreach ($ins in [regex]::Matches($t, $insertRx)) {
        $cols = @($ins.Groups['cols'].Value -split ',' | ForEach-Object { $_.Trim().ToLowerInvariant() })
        $ix = @{}; for ($i = 0; $i -lt $cols.Count; $i++) { $ix[$cols[$i]] = $i }
        if (-not $ix.ContainsKey('key') -or -not $ix.ContainsKey('value')) { continue }
        foreach ($tup in [regex]::Matches($ins.Groups['vals'].Value, '\((?<tuple>(?:[^()]|\([^()]*\))*)\)')) {
            $cells = @($tup.Groups['tuple'].Value -split ',' | ForEach-Object { ($_.Trim() -replace '^DATE\s+', '').Trim("'") })
            $cell = { param($col) if ($ix.ContainsKey($col) -and $ix[$col] -lt $cells.Count) { $v = $cells[$ix[$col]]; if ($v -eq 'NULL') { '' } else { $v } } else { '' } }
            $key = & $cell 'key'
            $scope = @(@((& $cell 'scope_product_group'), (& $cell 'scope_country'), (& $cell 'scope_value')) | Where-Object { $_ })
            $scopeText = if ($scope.Count) { $scope -join '/' } else { 'global' }
            $from = & $cell 'valid_from'
            $seed = "$scopeText = $(& $cell 'value')" + $(if ($from) { " (from $from)" } else { '' })
            $seedCount++
            if ($keys.Contains($key)) { $keys[$key].Seeds.Add($seed) }
            else { $unknownSeeds[$key] = "$rel`:$(Get-LineNumber $t ($ins.Groups['vals'].Index + $tup.Index))" }
        }
    }
}

# 3. readers and validators: `ParameterKey.CONST` references outside the enum
$constToKey = @{}; foreach ($k in $keys.Keys) { $constToKey[$keys[$k].Const] = $k }
foreach ($f in Get-SourceFiles $Root @('*.kt') | Where-Object { -not $enumFile -or $_.FullName -ne $enumFile.FullName }) {
    $t = Read-Text $f.FullName
    if ($t -notmatch "$EnumName\.") { continue }
    $cls = [regex]::Match($t, '(?m)^\s*(?:class|object|interface)\s+(\w+)').Groups[1].Value
    if (-not $cls) { $cls = [IO.Path]::GetFileNameWithoutExtension($f.Name) }
    $bucket = if ($f.FullName -match '[\\/]validator[\\/]') { 'Validators' } else { 'Readers' }
    foreach ($m in [regex]::Matches($t, "$([regex]::Escape($EnumName))\.(?<const>[A-Z][A-Z0-9_]*)\b")) {
        $c = $m.Groups['const'].Value
        if ($constToKey.ContainsKey($c)) { $keys[$constToKey[$c]][$bucket][$cls] = $true }
    }
}

# 4. render
$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Parameters (BE)' "$EnumName + $Table seeds" "Generated catalogue of the admin parameters: every $EnumName key with its seeded defaults per scope, the classes that read it and the validator that bounds it; the meaning of a key is documented in domain/calculations and the admin spec."))
[void]$sb.AppendLine("$($keys.Count) key(s), $seedCount seeded value(s). Scope = product group / country / scope value; ``global`` = no scope. Lookups take the most specific scope in force, then the newest ``valid_from``.")
[void]$sb.AppendLine("Meaning, unit and business rule of each key: ``domain/calculations/*.md`` (``## Parameters``) and the admin feature spec; ``scripts/validate-frontmatter.ps1`` checks that every key below is documented there and that documents name only keys that exist here.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Key | Constant | Seeded defaults | Read by | Validated by | Location |')
[void]$sb.AppendLine('|---|---|---|---|---|---|')
foreach ($k in ($keys.Keys | Sort-Object)) {
    $e = $keys[$k]
    $seeds = if ($e.Seeds.Count) { ($e.Seeds | Sort-Object) -join '; ' } else { '(no seed - must be created on the admin page)' }
    $readers = if ($e.Readers.Count) { (($e.Readers.Keys | Sort-Object | ForEach-Object { "``$_``" }) -join ', ') } else { '(no reader)' }
    $validators = if ($e.Validators.Count) { (($e.Validators.Keys | Sort-Object | ForEach-Object { "``$_``" }) -join ', ') } else { '' }
    [void]$sb.AppendLine("| ``$k`` | ``$($e.Const)`` | $(Escape-Cell $seeds) | $readers | $validators | ``$enumRel`:$($e.Line)`` |")
}
if ($unknownSeeds.Count) {
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('## Seeded keys without an enum constant')
    [void]$sb.AppendLine("Rows in the migrations whose key is not in ``$EnumName`` - unreadable by the application until the constant exists.")
    [void]$sb.AppendLine()
    foreach ($k in ($unknownSeeds.Keys | Sort-Object)) { [void]$sb.AppendLine("- ``$k`` - ``$($unknownSeeds[$k])``") }
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "parameters: $($keys.Count) key(s), $seedCount seed(s), $($unknownSeeds.Count) unknown seeded key(s) -> $Out"
