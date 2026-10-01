<#
.SYNOPSIS
  PowerShell port of the OKF v0.2 conformance checker core (okf_validate.py, MIT, scaccogatto/okf-skills).
  Runs without Python. ERRORs = §11 hard failures; warnings = soft guidance.
.EXAMPLE
  .\okf-validate.ps1                    # whole repo bundle
  .\okf-validate.ps1 -Path features -Strict
  .\okf-validate.ps1 -MaxWarnings 5
#>
param(
    [string]$Path = (Split-Path $PSScriptRoot -Parent),
    [switch]$Strict,
    [int]$MaxWarnings = -1,
    [string[]]$Exclude = @('.github', 'scripts', 'ci-examples', 'third-party', 'node_modules', '.git', 'confluence-import', 'work-items', 'test-design')
)
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$root = (Resolve-Path $Path).Path
$errors = New-Object System.Collections.Generic.List[string]
$warns  = New-Object System.Collections.Generic.List[string]
$now = [DateTime]::UtcNow
$actorRx = '^(human:[^\s/]+|process:[^\s/]+|[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)$'
$isoRx = '^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(Z|[+\-]\d{2}:\d{2}))?$'

function Get-Frontmatter([string]$text) {
    if ($text -match '(?s)\A\uFEFF?---\r?\n(.*?)\r?\n---(\r?\n|\z)') { return $Matches[1] }
    return $null
}
function Get-TopKeys([string]$fm) {
    ($fm -split "`r?`n") | Where-Object { $_ -match '^([A-Za-z_][\w\-]*):' } | ForEach-Object { $Matches[1] }
}
function Get-Scalar([string]$fm, [string]$key) {
    if ($fm -match "(?m)^$key`:\s*(.+?)\s*$") {
        $v = $Matches[1] -replace '\s+#.*$', ''   # drop inline YAML comment
        return $v.Trim().Trim('"').Trim("'")
    }
    return $null
}
function Test-IsTemplate([string]$rel) { return ($rel -match '(^|/)_?template\.md$') }

$files = Get-ChildItem $root -Recurse -File -Filter '*.md' | Where-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart('\')
    -not ($Exclude | Where-Object { $rel -like "$_\*" -or $rel -eq $_ })
}
$conceptIds = @{}
foreach ($f in $files) { $rel = $f.FullName.Substring($root.Length).TrimStart('\') -replace '\\', '/'; $conceptIds[$rel] = $true }

foreach ($f in $files) {
    $rel = $f.FullName.Substring($root.Length).TrimStart('\') -replace '\\', '/'
    try { $text = [IO.File]::ReadAllText($f.FullName, [Text.UTF8Encoding]::new($false, $true)) }
    catch { $errors.Add("$rel : not readable as UTF-8"); continue }
    $fm = Get-Frontmatter $text
    $isReserved = $f.Name -in 'index.md', 'log.md'
    $isRootIndex = ($rel -eq 'index.md')

    if ($isReserved) {
        if ($fm) {
            $keys = Get-TopKeys $fm
            if ($isRootIndex) {
                $extra = $keys | Where-Object { $_ -ne 'okf_version' }
                if ($extra) { $warns.Add("$rel : root index carries unexpected keys: $($extra -join ', ') (§8/§12)") }
                $v = Get-Scalar $fm 'okf_version'
                if ($v -and $v -ne '0.2') { $warns.Add("$rel : okf_version '$v' differs from 0.2 (§12)") }
            } else { $warns.Add("$rel : reserved file must not carry frontmatter (§8/§9)") }
        }
        if ($f.Name -eq 'log.md') {
            [regex]::Matches($text, '(?m)^## (.+)$') | ForEach-Object {
                if ($_.Groups[1].Value.Trim() -notmatch '^\d{4}-\d{2}-\d{2}$') { $warns.Add("$rel : log heading '$($_.Groups[1].Value)' is not ISO YYYY-MM-DD (§9)") }
            }
        }
        continue
    }

    if (-not $fm) { $errors.Add("$rel : no YAML frontmatter (§11)"); continue }
    $type = Get-Scalar $fm 'type'
    if (-not $type) { $errors.Add("$rel : missing or empty 'type' (§11)"); continue }

    # Templates hold placeholders (<ISO>, [^id]); §11 checks apply, value-level warnings do not.
    if (Test-IsTemplate $rel) { continue }

    foreach ($k in 'title', 'description') { if (-not (Get-Scalar $fm $k)) { $warns.Add("$rel : missing recommended '$k'") } }

    $status = Get-Scalar $fm 'status'
    if ($status -and $status -notin 'draft', 'stable', 'deprecated') { $warns.Add("$rel : status '$status' not in draft|stable|deprecated (§5.4)") }

    $stale = Get-Scalar $fm 'stale_after'
    if ($stale) {
        if ($stale -notmatch $isoRx) { $warns.Add("$rel : stale_after '$stale' is not ISO 8601 (§5.5)") }
        elseif ([DateTime]::Parse($stale, $null, 'AdjustToUniversal') -le $now -and $status -ne 'deprecated') { $warns.Add("$rel : STALE since $stale (§5.5)") }
    }

    if ($fm -match '(?m)^timestamp:') { $warns.Add("$rel : v0.1 'timestamp' → use generated.at (§13.1)") }
    if ($text -match '(?m)^# Citations') { $warns.Add("$rel : v0.1 '# Citations' → use sources[] (§13.1)") }

    # actors in generated.by / verified[].by / sources[].author
    [regex]::Matches($fm, '(?m)\b(?:by|author):\s*([^\s,}\]]+)') | ForEach-Object {
        $a = $_.Groups[1].Value.Trim('"', "'")
        if ($a -notmatch $actorRx) {
            $hint = if ($a -match '^(?i)human[:/]') { ' — trust tier needs exact lowercase "human:<id>"' } else { '' }
            $warns.Add("$rel : actor '$a' does not match §7 shapes$hint")
        }
    }
    [regex]::Matches($fm, '(?m)\bat:\s*([^\s,}\]]+)') | ForEach-Object {
        $d = $_.Groups[1].Value.Trim('"', "'"); if ($d -notmatch $isoRx) { $warns.Add("$rel : datetime '$d' is not ISO 8601") }
    }

    if ($type -eq 'Attested Computation' -and -not (Get-Scalar $fm 'runtime')) { $warns.Add("$rel : Attested Computation without 'runtime' (§10.2)") }

    # footnote labels must match a sources[].id
    $sourceIds = [regex]::Matches($fm, '(?m)^\s*-\s*(?:\{\s*)?id:\s*([^\s,}]+)') | ForEach-Object { $_.Groups[1].Value.Trim('"', "'") }
    [regex]::Matches($text, '\[\^([^\]]+)\]') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique | ForEach-Object {
        if ($sourceIds -notcontains $_) { $warns.Add("$rel : footnote [^$_] names no sources[].id (§5.1)") }
    }

    # internal links (spec-tolerated → warn)
    [regex]::Matches($text, '\]\((/[^)#\s]+\.md|(?:\./|\.\./)[^)#\s]+\.md)') | ForEach-Object {
        $link = $_.Groups[1].Value
        $target = if ($link.StartsWith('/')) { $link.TrimStart('/') } else {
            $dir = Split-Path $rel -Parent
            $combined = if ($dir) { "$dir/$link" } else { $link }
            # normalise ./ and ../
            $parts = New-Object System.Collections.Generic.List[string]
            foreach ($p in ($combined -split '/')) { if ($p -eq '.' -or $p -eq '') { continue } elseif ($p -eq '..') { if ($parts.Count) { $parts.RemoveAt($parts.Count - 1) } } else { $parts.Add($p) } }
            $parts -join '/'
        }
        if (-not $conceptIds.ContainsKey($target) -and -not (Test-Path (Join-Path $root $target))) { $warns.Add("$rel : broken link $link (§6.1, tolerated)") }
    }
}

$errors | ForEach-Object { Write-Host "ERROR $_" -ForegroundColor Red }
$warns  | ForEach-Object { Write-Host "warn  $_" -ForegroundColor Yellow }
Write-Host ("{0} concept file(s) checked: {1} error(s), {2} warning(s)" -f $files.Count, $errors.Count, $warns.Count)

$gate = if ($Strict) { 0 } elseif ($MaxWarnings -ge 0) { $MaxWarnings } else { [int]::MaxValue }
if ($errors.Count -gt 0 -or $warns.Count -gt $gate) { exit 1 }
exit 0
