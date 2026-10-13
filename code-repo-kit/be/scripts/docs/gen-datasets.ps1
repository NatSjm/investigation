<#
.SYNOPSIS
  Dataset catalogue: every named dataset (local seed under scripts/db/seed, integration-test fixture under
  src/test/resources/datasets) with its purpose, tables and row counts, dependencies, the tests that load it and
  one sample row per table. Lets analysts and test designers cite a setup by name ("Given dataset "x" is loaded")
  instead of describing rows, without opening the code repository. Names and shape only: the sample row is the
  first tuple of each table and is included only when the header declares `synthetic: yes`.

  Header contract (first comment block of the .sql file):
    -- dataset: <kebab-name>      -- purpose: <one sentence>      -- tables: a, b (optional)
    -- depends: x, y (optional)   -- synthetic: yes|no
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/datasets.md',
    [int]$SampleChars = 140
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$rows = New-Object System.Collections.Generic.List[object]
$unnamed = 0
$tupleRx = '\((?<tuple>(?:[^()]|\([^()]*\))*)\)'
foreach ($f in Get-SourceFiles $Root @('*.sql') | Where-Object { $_.FullName -notmatch '[\\/]db[\\/]migration[\\/]' } | Sort-Object FullName) {
    $t = Read-Text $f.FullName
    $rel = Get-RelPath $Root $f.FullName
    # header: leading `-- key: value` lines
    $hdr = @{}
    foreach ($line in ($t -split '\r?\n')) {
        if ($line -match '^\s*--\s*([a-z_]+)\s*:\s*(.*)$') { $hdr[$Matches[1]] = $Matches[2].Trim() }
        elseif ($line.Trim() -and $line -notmatch '^\s*--') { break }
    }
    if (-not $hdr.ContainsKey('dataset')) { $unnamed++; continue }
    $kind = if ($f.FullName -match '[\\/]test[\\/]') { 'fixture' } else { 'seed' }
    $synthetic = ($hdr['synthetic'] -eq 'yes')

    # tables and row counts from INSERT statements; DELETE/UPDATE targets count as touched
    $counts = [ordered]@{}
    $samples = [ordered]@{}
    foreach ($ins in [regex]::Matches($t, '(?is)INSERT\s+INTO\s+(?<table>[a-z_][a-z0-9_]*)\s*\((?<cols>[^)]*)\)\s*VALUES\s*(?<vals>.*?);')) {
        $tbl = $ins.Groups['table'].Value
        $vals0 = $ins.Groups['vals'].Value -replace '(?is)\s+ON\s+CONFLICT.*$', ''   # upsert clause is not a row
        $tuples = [regex]::Matches($vals0, $tupleRx)
        if (-not $counts.Contains($tbl)) { $counts[$tbl] = 0 }
        $counts[$tbl] += $tuples.Count
        if ($synthetic -and $tuples.Count -and -not $samples.Contains($tbl)) {
            $cols = @($ins.Groups['cols'].Value -split ',' | ForEach-Object { $_.Trim() })
            $vals = @($tuples[0].Groups['tuple'].Value -split ',(?=(?:[^'']*''[^'']*'')*[^'']*$)' | ForEach-Object { $_.Trim() })
            $pairs = for ($i = 0; $i -lt [Math]::Min($cols.Count, $vals.Count); $i++) {
                $v = $vals[$i] -replace '^DATE\s+', '' -replace '::jsonb$', ''
                if ($v -match '^gen_random_uuid\(\)$|^now\(\)$|^''?[0-9a-f]{8}-[0-9a-f]{4}-' -or $v.Length -gt 40) { continue }   # skip generated and long values
                "$($cols[$i])=$($v.Trim(''''))"
            }
            $s = ($pairs -join ', ')
            if ($s.Length -gt $SampleChars) { $s = $s.Substring(0, $SampleChars - 1) + '…' }
            $samples[$tbl] = $s
        }
    }
    foreach ($m in [regex]::Matches($t, '(?i)\b(?:DELETE\s+FROM|UPDATE)\s+([a-z_][a-z0-9_]*)')) { if (-not $counts.Contains($m.Groups[1].Value)) { $counts[$m.Groups[1].Value] = 0 } }
    $tables = if ($hdr.ContainsKey('tables')) { @($hdr['tables'] -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }) } else { @($counts.Keys) }
    $tablesText = ($tables | ForEach-Object { if ($counts.Contains($_) -and $counts[$_]) { "``$_`` ($($counts[$_]))" } else { "``$_``" } }) -join ', '

    $rows.Add([pscustomobject]@{
        Name = $hdr['dataset']; Kind = $kind; Purpose = $hdr['purpose']; Tables = $tablesText; TableList = $tables
        Depends = $(if ($hdr.ContainsKey('depends') -and $hdr['depends'] -ne '-') { $hdr['depends'] } else { '' })
        Synthetic = $synthetic; Samples = $samples; Rel = $rel; File = $f.Name; Users = @{}
    })
}

# who loads it: @Sql("/datasets/<file>") or the dataset name / file name quoted in test sources, and the seed runner
foreach ($f in Get-SourceFiles $Root @('*.kt', '*.java', '*.ps1')) {
    if ($f.FullName -match '[\\/]scripts[\\/]docs[\\/]') { continue }
    $t = Read-Text $f.FullName
    foreach ($r in $rows) {
        if ($t -match [regex]::Escape($r.File) -or $t -match ('"' + [regex]::Escape($r.Name) + '"')) {
            $who = if ($f.Extension -eq '.ps1') { $f.Name } else { [regex]::Match($t, '(?m)^\s*(?:class|object)\s+(\w+)').Groups[1].Value }
            if ($who) { $r.Users[$who] = $true }
        }
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Datasets (BE)' 'scripts/db/seed + src/test/resources/datasets headers' 'Generated catalogue of the named synthetic datasets - local seeds and integration-test fixtures - with purpose, tables and row counts, dependencies, the tests that load them and one sample row per table; cite a dataset by name in Gherkin instead of describing rows.'))
$seeds = @($rows | Where-Object Kind -eq 'seed').Count; $fix = @($rows | Where-Object Kind -eq 'fixture').Count
[void]$sb.AppendLine("$($rows.Count) dataset(s): $seeds seed(s) for the developer database (``scripts/db/seed-local.ps1``), $fix integration-test fixture(s) (``@Sql(""/datasets/<name>.sql"")``). Row counts are tuples in ``INSERT`` statements; samples are the first row per table, shown only for datasets declared ``synthetic: yes``.")
[void]$sb.AppendLine("Use in test design: ``Given dataset ""<name>"" is loaded`` (step vocabulary in the docs repo, ``test-design/README.md``); add explicit ``Given`` rows only for the values a scenario asserts on.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Dataset | Kind | Purpose | Tables (rows) | Depends on | Loaded by | Location |')
[void]$sb.AppendLine('|---|---|---|---|---|---|---|')
foreach ($r in $rows | Sort-Object Name) {
    $users = if ($r.Users.Count) { (($r.Users.Keys | Sort-Object | ForEach-Object { "``$_``" }) -join ', ') } else { '(nothing yet)' }
    $flag = if ($r.Synthetic) { '' } else { ' **not declared synthetic - values withheld**' }
    [void]$sb.AppendLine("| ``$($r.Name)`` | $($r.Kind) | $(Escape-Cell $r.Purpose)$flag | $($r.Tables) | $($r.Depends) | $users | ``$($r.Rel)`` |")
}
$withSamples = @($rows | Where-Object { $_.Samples.Count })
if ($withSamples.Count) {
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('## Sample rows')
    [void]$sb.AppendLine('First row of each table, synthetic datasets only; `id` columns and generated values omitted when long.')
    [void]$sb.AppendLine()
    foreach ($r in $withSamples | Sort-Object Name) {
        foreach ($tbl in $r.Samples.Keys) { [void]$sb.AppendLine("- ``$($r.Name)`` / ``$tbl``: $(Escape-Cell $r.Samples[$tbl])") }
    }
}
if ($unnamed) { [void]$sb.AppendLine(); [void]$sb.AppendLine("_$unnamed SQL file(s) outside the migrations have no ``-- dataset:`` header and are not catalogued._") }
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "datasets: $($rows.Count) dataset(s) ($seeds seed, $fix fixture), $unnamed unnamed sql file(s) -> $Out"
