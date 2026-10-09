<#
.SYNOPSIS
  REST API index: method | path | operationId | handler | params | file:line. No app start, no build.

  Contract-first mode (default when api/openapi.yaml exists): operations are read from the OpenAPI document
  (the contract both FE and BE are generated from) and joined to the implementing `override fun <operationId>(`
  in a `@RestController` class. Endpoints without an implementation are listed as `_not implemented_`.

  Annotation mode (fallback): `@RestController` + `@*Mapping` scan, for repos that are not contract-first.
.EXAMPLE
  ./gen-api-index.ps1 -Root . -Out docs/_generated/api-index.md
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/api-index.md',
    # path of OUR OpenAPI contract relative to -Root; empty = auto-detect: api/openapi.yaml, else the first
    # */src/main/resources/openapi/*.y*ml that is an OpenAPI document with paths (AsyncAPI files are skipped)
    [string]$OpenApi = ''
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath
$rows = New-Object System.Collections.Generic.List[object]
if (-not $OpenApi) {
    if (Test-Path (Join-Path $Root 'api/openapi.yaml')) { $OpenApi = 'api/openapi.yaml' }
    else {
        $cand = @(Get-SourceFiles $Root @('*.yaml', '*.yml') | Where-Object { $_.FullName -match '[\\/]src[\\/]main[\\/]resources[\\/]openapi[\\/]' } |
            Where-Object { $x = Read-Text $_.FullName; $x -match '(?m)^openapi:' -and $x -match '(?m)^paths:' } | Sort-Object FullName | Select-Object -First 1)
        if ($cand) { $OpenApi = Get-RelPath $Root $cand[0].FullName }
    }
}
$specPath = if ($OpenApi) { Join-Path $Root $OpenApi } else { Join-Path $Root '__none__' }

if (Test-Path $specPath) {
    # ---------- contract-first: parse the OpenAPI document (indentation-based, no YAML library) ----------
    $text = Read-Text $specPath
    $base = ''
    $sm = [regex]::Match($text, '(?ms)^servers:\s*\r?\n\s*-\s*url:\s*(\S+)')
    if ($sm.Success) {
        $base = $sm.Groups[1].Value.Trim('"', "'").TrimEnd('/')
        if ($base -match '^https?://[^/]+(/.*)?$') { $base = $Matches[1] }
    }
    $ops = New-Object System.Collections.Generic.List[object]
    $inPaths = $false; $curPath = $null; $op = $null; $pendingName = $null; $tagsList = $false
    foreach ($line in ($text -split "`r?`n")) {
        if ($line -match '^paths:\s*$') { $inPaths = $true; continue }
        if ($inPaths -and $line -match '^\S') { $inPaths = $false }
        if (-not $inPaths) { continue }
        if ($line -match '^  (/\S*):\s*$') { $curPath = $Matches[1]; $op = $null; continue }
        if ($line -match '^    (get|post|put|patch|delete|head|options):\s*$') {
            $op = [ordered]@{ Verb = $Matches[1].ToUpper(); Path = $curPath; OpId = ''; Tag = ''; Query = @(); Session = $false; Summary = '' }
            $ops.Add($op); $tagsList = $false; continue
        }
        if ($null -eq $op) { continue }
        if ($line -match '^      operationId:\s*(\S+)') { $op.OpId = $Matches[1].Trim('"', "'") }
        elseif ($line -match '^      summary:\s*(.+)$') { $op.Summary = $Matches[1].Trim().Trim('"', "'") }
        elseif ($line -match '^      tags:\s*\[([^\]]*)\]') { $op.Tag = ($Matches[1] -split ',')[0].Trim().Trim('"', "'") }
        elseif ($line -match '^      tags:\s*$') { $tagsList = $true }
        elseif ($tagsList -and $line -match '^\s+-\s*(\S+)') { $op.Tag = $Matches[1].Trim('"', "'"); $tagsList = $false }
        elseif ($line -match 'SessionHeader') { $op.Session = $true }
        elseif ($line -match '^\s+-\s+name:\s*(\S+)') { $pendingName = $Matches[1].Trim('"', "'") }
        elseif ($line -match '^\s+in:\s*query' -and $pendingName) { $op.Query += $pendingName; $pendingName = $null }
        elseif ($line -match '^\s+in:\s*(path|header)') { $pendingName = $null }
    }
    # implementations: override fun <operationId>( inside @RestController classes
    $impls = @{}
    foreach ($f in Get-SourceFiles $Root @('*.kt')) {
        $t = Read-Text $f.FullName
        if ($t -notmatch '@RestController') { continue }
        $rel = Get-RelPath $Root $f.FullName
        $cls = [regex]::Match($t, '(?m)^\s*class\s+(\w+)').Groups[1].Value
        foreach ($m in [regex]::Matches($t, 'override\s+fun\s+(\w+)\s*\(')) {
            $impls[$m.Groups[1].Value] = @{ Handler = "$cls.$($m.Groups[1].Value)"; Loc = "$rel`:$(Get-LineNumber $t $m.Index)" }
        }
    }
    foreach ($o in $ops) {
        $pathParams = @([regex]::Matches($o.Path, '\{(\w+)\}') | ForEach-Object { $_.Groups[1].Value })
        $params = @($pathParams + ($o.Query | ForEach-Object { "${_}?" }))
        if ($o.Session) { $params += 'X-Harbor-Session' }
        $impl = $impls[$o.OpId]
        $rows.Add([pscustomobject]@{
            Verb = $o.Verb; Path = ($base + $o.Path); OpId = $o.OpId; Tag = $o.Tag
            Handler = $(if ($impl) { $impl.Handler } else { '_not implemented_' })
            Params = ($params -join ', '); Loc = $(if ($impl) { $impl.Loc } else { "$OpenApi" })
        })
    }
    $source = "$OpenApi (contract) + override fun <operationId> lookup in @RestController classes"
    $note = "$($rows.Count) operation(s) from the contract; $(@($rows | Where-Object { $_.Handler -ne '_not implemented_' }).Count) implemented. Request/response schemas: open the contract ``components/schemas``, not the DTO files."
} else {
    # ---------- annotation mode ----------
    $verbs = 'Get','Post','Put','Patch','Delete'
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
            $path = ($base.TrimEnd('/') + '/' + $m.Groups[2].Value.TrimStart('/')).TrimEnd('/')
            if (-not $path) { $path = '/' }
            $rows.Add([pscustomobject]@{
                Verb = $m.Groups[1].Value.ToUpper(); Path = $path; OpId = $m.Groups[3].Value; Tag = ''
                Handler = "$cls.$($m.Groups[3].Value)"
                Params = ($m.Groups[4].Value -replace '@\w+(\([^)]*\))?\s*', '' -replace '\s+', ' ').Trim()
                Loc = "$rel`:$(Get-LineNumber $t $m.Index)"
            })
        }
    }
    $source = '@RestController / @*Mapping scan'
    $note = "$($rows.Count) endpoint(s). DTO field lists: open the DTO file, not the controller."
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'REST API index (BE)' $source))
[void]$sb.AppendLine($note)
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Method | Path | operationId | Tag | Handler | Params | Location |')
[void]$sb.AppendLine('|---|---|---|---|---|---|---|')
foreach ($r in $rows | Sort-Object Path, Verb) {
    [void]$sb.AppendLine("| $($r.Verb) | ``$($r.Path)`` | ``$($r.OpId)`` | $($r.Tag) | ``$($r.Handler)`` | $(Escape-Cell $r.Params) | ``$($r.Loc)`` |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "api-index: $($rows.Count) endpoint(s) -> $Out"
