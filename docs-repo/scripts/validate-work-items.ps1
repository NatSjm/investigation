<#
.SYNOPSIS
  Validates work-items/<ID>.yml against the rules documented in work-items/_schema.yml, without a YAML library:
  feature matches file name and spec exists; every story has summary / estimate (Fibonacci) / acceptance criteria;
  every cited BR exists in the spec; subtasks <= 8 h; jira_key present; no `depends_on` to unknown story ids.
.EXAMPLE
  .\validate-work-items.ps1                       # all files
  .\validate-work-items.ps1 work-items/P1-001.yml
#>
param([string[]]$Paths)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
if (-not $Paths) { $Paths = Get-ChildItem (Join-Path $repo 'work-items') -Filter '*.yml' | Where-Object { $_.Name -notmatch '^_' } | ForEach-Object FullName }
$errors = @(); $count = 0
foreach ($p in $Paths) {
    $full = if ([IO.Path]::IsPathRooted($p)) { $p } else { Join-Path $repo $p }
    if (-not (Test-Path $full)) { $errors += "$p : not found"; continue }
    $count++
    $y = [IO.File]::ReadAllText($full, [Text.UTF8Encoding]::new($false))
    $name = [IO.Path]::GetFileNameWithoutExtension($full)
    $feature = if ($y -match '(?m)^feature:\s*(\S+)') { $Matches[1] } else { '' }
    if ($feature -ne $name) { $errors += "$p : feature '$feature' must equal file name '$name'" }
    $spec = Get-ChildItem (Join-Path $repo 'features') -Recurse -Filter "$feature.md" | Select-Object -First 1
    $specText = if ($spec) { [IO.File]::ReadAllText($spec.FullName) } else { $errors += "$p : spec features/**/$feature.md not found"; '' }
    if ($y -notmatch '(?m)^epic:') { $errors += "$p : missing epic" }
    if ($y -notmatch '(?m)^\s+jira_key:') { $errors += "$p : missing jira_key (leave null)" }
    # split stories by '  - id:' blocks
    $storyBlocks = [regex]::Split(($y -split '(?m)^stories:')[-1], '(?m)^\s{2}-\s+id:') | Select-Object -Skip 1
    $ids = @($storyBlocks | ForEach-Object { ($_ -split "`r?`n")[0].Trim() })
    if ($ids.Count -eq 0) { $errors += "$p : no stories" }
    foreach ($b in $storyBlocks) {
        $sid = ($b -split "`r?`n")[0].Trim()
        $block = ($b -split '(?m)^questions:')[0]
        if ($block -notmatch '(?m)^\s+summary:\s*"?(.+?)"?\s*$') { $errors += "$p : story $sid missing summary" } elseif ($Matches[1].Length -gt 80) { $errors += "$p : story $sid summary > 80 chars" }
        if ($block -match '(?m)^\s{4}estimate:\s*(\d+)') { if ([int]$Matches[1] -notin 1, 2, 3, 5, 8) { $errors += "$p : story $sid estimate must be 1,2,3,5,8" } } else { $errors += "$p : story $sid missing estimate" }
        $rules = @([regex]::Matches($block, 'rule:\s*(BR-[A-Z0-9]+-\d{3}-\d+)') | ForEach-Object { $_.Groups[1].Value })
        if ($rules.Count -eq 0) { $errors += "$p : story $sid has no acceptance criterion citing a BR" }
        foreach ($r in $rules) { if ($specText -and $specText -notmatch [regex]::Escape($r)) { $errors += "$p : story $sid cites $r which is not in the spec" } }
        foreach ($m in [regex]::Matches($block, 'estimate_hours:\s*(\d+)')) { if ([int]$m.Groups[1].Value -gt 8) { $errors += "$p : story $sid subtask > 8 h" } }
        foreach ($m in [regex]::Matches($block, 'depends_on:\s*\[([^\]]*)\]')) { foreach ($d in ($m.Groups[1].Value -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })) { if ($d -notin $ids) { $errors += "$p : story $sid depends_on unknown $d" } } }
    }
}
if ($errors) { $errors | ForEach-Object { Write-Host "ERROR $_" -ForegroundColor Red }; exit 1 }
Write-Host "OK: $count work-item file(s) valid" -ForegroundColor Green
