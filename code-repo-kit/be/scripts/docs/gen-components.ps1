<#
.SYNOPSIS
  Component index for a layered (package-by-layer) Kotlin backend: one row per top-level class / object /
  interface with its layer (package segment after the base package), Spring stereotype, constructor-injected
  dependencies, tables it touches, @docs tags and file:line. This is the map that replaces "one module per business
  area": agents and the docs graph read layer + name prefix + dependencies instead of walking folders.

  Tables: `@Table(name = "x")` on entities, SQL literals (`from|into|update|join <table>`) in DAOs, and for
  Spring Data DAOs (`: JpaRepository<Entity, Id>`) the table of the entity.
.EXAMPLE
  ./gen-components.ps1 -Root . -Out docs/_generated/components.md
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/components.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

# known tables from migrations (same source as db-schema.md)
$tables = New-Object System.Collections.Generic.HashSet[string]
foreach ($f in @(Get-SourceFiles $Root @('V*.sql') | Where-Object { $_.FullName -match '[\\/](migration|db)[\\/]' })) {
    foreach ($m in [regex]::Matches((Read-Text $f.FullName), '(?i)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)')) { [void]$tables.Add($m.Groups[1].Value.ToLower()) }
}

$files = @(Get-SourceFiles $Root @('*.kt') | Where-Object { $_.FullName -match '[\\/]src[\\/]main[\\/]' })
# base package per Maven module = shortest package found in that module
$basePkg = @{}
foreach ($f in $files) {
    $mod = ((Get-RelPath $Root $f.FullName) -split '/')[0]
    $pm = [regex]::Match((Read-Text $f.FullName), '(?m)^package\s+([\w.]+)')
    if ($pm.Success -and (-not $basePkg.ContainsKey($mod) -or $pm.Groups[1].Value.Length -lt $basePkg[$mod].Length)) { $basePkg[$mod] = $pm.Groups[1].Value }
}

$rows = New-Object System.Collections.Generic.List[object]
$declRx = '(?m)^(?:@[\w.]+(?:\([^)]*\))?\s+)*(?:(?:public|internal|private|data|abstract|open|sealed|enum|annotation|value|fun)\s+)*(class|object|interface)\s+(\w+)'
foreach ($f in $files) {
    $t = Read-Text $f.FullName
    $rel = Get-RelPath $Root $f.FullName
    $mod = ($rel -split '/')[0]
    $pkg = [regex]::Match($t, '(?m)^package\s+([\w.]+)').Groups[1].Value
    $layer = ''
    if ($basePkg[$mod] -and $pkg.StartsWith($basePkg[$mod])) { $layer = ($pkg.Substring($basePkg[$mod].Length).TrimStart('.') -split '\.')[0] }
    if (-not $layer) { $layer = '(root)' }
    # comments blanked for the dependency / table scan (keeps offsets for line numbers)
    $code = [regex]::Replace($t, '(?s)/\*.*?\*/|//[^\r\n]*', { param($m) ($m.Value -replace '[^\r\n]', ' ') })
    foreach ($d in [regex]::Matches($code, $declRx)) {
        $name = $d.Groups[2].Value
        $start = $d.Index
        # annotations directly above the declaration, then the KDoc block directly above those (any length)
        $prefix = $t.Substring(0, $start)
        $annBlock = [regex]::Match($prefix, '(?:@[\w.]+(?:\([^)]*\))?\s*)*$').Value
        $kdocBlock = ''
        $beforeAnns = $prefix.Substring(0, $prefix.Length - $annBlock.Length).TrimEnd()
        if ($beforeAnns.EndsWith('*/')) {
            $kdOpen = $beforeAnns.LastIndexOf('/**')
            if ($kdOpen -ge 0) { $kdocBlock = $beforeAnns.Substring($kdOpen + 3, $beforeAnns.Length - $kdOpen - 5) }
        }
        $anns = @([regex]::Matches($annBlock + $d.Value, '@(RestControllerAdvice|RestController|Service|Component|Configuration|Repository|Entity|SpringBootApplication)\b') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
        $kind = @($anns)
        if ($code -match '@KafkaListener') { $kind += 'KafkaListener' }
        if ($code -match '@Scheduled') { $kind += 'Scheduled' }
        if ($code -match 'kafkaTemplate\.send\(|\.send\(\s*Topics\.') { $kind += 'KafkaProducer' }
        if (-not $kind) { $kind = @($d.Groups[1].Value) }
        # primary constructor dependencies: class Name(...) up to the matching ')'
        $deps = @()
        $after = $code.Substring($d.Index + $d.Length)
        if ($after -match '^\s*(?:<[^>]*>)?\s*(?:@\w+\s*)*(?:constructor\s*)?\(') {
            $open = $after.IndexOf('('); $depth = 0; $end = -1
            for ($i = $open; $i -lt $after.Length; $i++) { if ($after[$i] -eq '(') { $depth++ } elseif ($after[$i] -eq ')') { $depth--; if ($depth -eq 0) { $end = $i; break } } }
            if ($end -gt $open) {
                $params = $after.Substring($open + 1, $end - $open - 1)
                $deps = @([regex]::Matches($params, '(?:val|var)\s+\w+\s*:\s*([A-Z]\w*)') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
            }
        }
        $super = ''
        $sm = [regex]::Match($after, '^[^{\r\n]*?:\s*(?:JpaRepository|CrudRepository|PagingAndSortingRepository|ListCrudRepository)<\s*(\w+)')
        if ($sm.Success) { $super = $sm.Groups[1].Value }
        $tbl = New-Object System.Collections.Generic.List[string]
        $tm = [regex]::Match($annBlock + $d.Value, '@Table\(\s*name\s*=\s*"(\w+)"')
        if ($tm.Success) { $tbl.Add($tm.Groups[1].Value.ToLower()) }
        foreach ($sq in [regex]::Matches($t, '(?i)\b(?:from|into|update|join)\s+(\w+)')) { $x = $sq.Groups[1].Value.ToLower(); if ($tables.Contains($x) -and -not $tbl.Contains($x)) { $tbl.Add($x) } }
        $docs = @([regex]::Matches($kdocBlock, '@docs\s+([\w.-]+)') | ForEach-Object { $_.Groups[1].Value })
        $rows.Add([pscustomobject]@{ Name = $name; Layer = $layer; Module = $mod; Kind = ($kind | Select-Object -Unique) -join ', '; Deps = $deps; Super = $super; Tables = $tbl; Docs = $docs; Loc = "$rel`:$(Get-LineNumber $t $start)" })
    }
}
# Spring Data DAOs inherit the table of their entity; dependencies limited to classes of this repo
$byName = @{}; foreach ($r in $rows) { $byName[$r.Name] = $r }
foreach ($r in $rows) {
    if ($r.Super -and $byName.ContainsKey($r.Super)) { foreach ($x in $byName[$r.Super].Tables) { if (-not $r.Tables.Contains($x)) { $r.Tables.Add($x) } } }
    $r.Deps = @($r.Deps | Where-Object { $byName.ContainsKey($_) -and $_ -ne $r.Name })
}

$layers = @($rows | Group-Object Layer | Sort-Object Name | ForEach-Object { "$($_.Name) $($_.Count)" })
$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Components (BE)' 'top-level Kotlin declarations per layer' 'One row per class: layer, stereotype, injected dependencies, tables, @docs tags and file:line; business context = class-name prefix.'))
[void]$sb.AppendLine("$($rows.Count) declaration(s). Per layer: $($layers -join ', '). Business context of a class = its name prefix (docs repo ``contexts.yml``).")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Class | Layer | Module | Kind | Depends on | Tables | @docs | Location |')
[void]$sb.AppendLine('|---|---|---|---|---|---|---|---|')
foreach ($r in $rows | Sort-Object Layer, Name) {
    $deps = if ($r.Deps) { ($r.Deps | ForEach-Object { '`' + $_ + '`' }) -join ', ' } else { '' }
    $tb = if ($r.Tables.Count) { ($r.Tables | ForEach-Object { '`' + $_ + '`' }) -join ', ' } else { '' }
    [void]$sb.AppendLine("| ``$($r.Name)`` | $($r.Layer) | $($r.Module) | $($r.Kind) | $deps | $tb | $(($r.Docs | ForEach-Object { '`' + $_ + '`' }) -join ', ') | ``$($r.Loc)`` |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "components: $($rows.Count) declaration(s) -> $Out"
