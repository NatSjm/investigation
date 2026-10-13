<#
.SYNOPSIS
  Validates frontmatter of feature specs and calculation docs.
.EXAMPLE
  .\validate-frontmatter.ps1                       # all specs
  .\validate-frontmatter.ps1 features\product1\P1-001.md
#>
param([string[]]$Paths)

$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
if (-not $Paths) {
    $Paths = Get-ChildItem (Join-Path $repo 'features'), (Join-Path $repo 'domain\calculations') -Recurse -Filter '*.md' |
        Where-Object { $_.Name -notmatch '^(_template|README|INDEX)\.md$' } | ForEach-Object FullName
}

$requiredFeature = 'id','title','context','status','owners','last_verified','code_refs','api','events','tables','calculations','flows','jira','tests'
$requiredCalc    = 'name','title','used_by','code_refs','last_verified'
$errors = @()

foreach ($p in $Paths) {
    $full = if ([IO.Path]::IsPathRooted($p)) { $p } else { Join-Path $repo $p }
    $text = [IO.File]::ReadAllText($full, [Text.UTF8Encoding]::new($false))
    if ($text -notmatch '(?s)^\uFEFF?---\r?\n(.*?)\r?\n---') { $errors += "$p : missing frontmatter"; continue }
    $fm = $Matches[1]
    $keys = ($fm -split "`r?`n") | Where-Object { $_ -match '^([A-Za-z_]+):' } | ForEach-Object { $Matches[1] }

    # Only the two repo-specific OKF types carry the extended schema; other concepts (Document,
    # Architecture View, ...) and reserved files (index.md/log.md) are covered by okf-validate.ps1.
    $type = if ($fm -match '(?m)^type:\s*"?([^"\r\n#]+?)"?\s*(#.*)?$') { $Matches[1].Trim() } else { '' }
    if ($type -notin 'Feature Spec', 'Attested Computation') { continue }

    $isCalc = ($type -eq 'Attested Computation')
    $required = if ($isCalc) { $requiredCalc } else { $requiredFeature }
    foreach ($k in $required) { if ($keys -notcontains $k) { $errors += "$p : missing key '$k'" } }

    if (-not $isCalc) {
        if ($fm -match 'id:\s*([A-Z][A-Z0-9]*-\d{3}[a-z]?)') {
            $id = $Matches[1]
            if ((Split-Path $full -Leaf) -ne "$id.md") { $errors += "$p : filename must be $id.md" }
            if ($text -notmatch "BR-$id-1") { $errors += "$p : no business rule BR-$id-1 found" }
        } else { $errors += "$p : id must match ^[A-Z][A-Z0-9]*-\d{3}$" }
        if ($fm -match '(?m)^status:\s*(\w+)' -and $Matches[1] -notin 'draft','stable','deprecated') { $errors += "$p : bad status (OKF §5.4: draft|stable|deprecated)" }
    }

    # referenced calculation and flow files must exist
    [regex]::Matches($fm, 'domain/calculations/[\w\-]+\.md') | ForEach-Object {
        if (-not (Test-Path (Join-Path $repo $_.Value))) { $errors += "$p : missing $($_.Value)" }
    }
    [regex]::Matches($fm, 'flows/[\w\-]+\.md') | ForEach-Object {
        if (-not (Test-Path (Join-Path $repo $_.Value))) { $errors += "$p : missing $($_.Value)" }
    }
}

# flows: every spec a flow names in `specs:` must exist (the other direction of the spec's `flows:` key)
$specIds = @(Get-ChildItem (Join-Path $repo 'features') -Recurse -Filter '*.md' | Where-Object { $_.Name -match '^[A-Z][A-Z0-9]+-\d{3}\.md$' } | ForEach-Object { $_.BaseName })
$flowDir = Join-Path $repo 'flows'
if (Test-Path $flowDir) {
    foreach ($ff in Get-ChildItem $flowDir -Filter '*.md' | Where-Object { $_.Name -notmatch '^(_template|index)\.md$' }) {
        $ft = [IO.File]::ReadAllText($ff.FullName, [Text.UTF8Encoding]::new($false))
        if ($ft -match '(?m)^specs:\s*\[(.*?)\]') {
            foreach ($sid in ($Matches[1] -split ',' | ForEach-Object { $_.Trim().Trim('"') } | Where-Object { $_ })) {
                if ($specIds -notcontains $sid) { $errors += "flows/$($ff.Name) : specs[] names $sid, no features/*/$sid.md" }
            }
        } else { $errors += "flows/$($ff.Name) : no specs[] list (a flow must name the specs it composes)" }
    }
}

if ($errors) { $errors | ForEach-Object { Write-Host "ERROR $_" -ForegroundColor Red }; exit 1 }
Write-Host "OK: $($Paths.Count) file(s) valid" -ForegroundColor Green
