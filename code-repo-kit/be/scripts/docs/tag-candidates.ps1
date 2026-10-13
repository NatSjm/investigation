<#
.SYNOPSIS
  Lists every manager and calculation class with its current `@docs` tag and, where it is missing, the tag it should get.
  Deterministic input for the `docs-tagger` agent (prompt /tag-docs): the agent adds the comment lines, a human reviews the table.
.DESCRIPTION
  Reads docs/_generated/components.md (run gen-all.ps1 first) and the docs repo contexts.yml:
    - layer `manager`: context = longest class-name prefix in contexts.yml; proposed tag = `<spec prefix>-<next free NNN>`
      (NNN from the IDs already used in docs-tags.md, 001 when none). No matching prefix -> BLOCKED (add the prefix first).
    - layer `utils`: proposed tag = snake_case of the class name; the agent refines it from the KDoc (e.g. `monthly_projection`).
  Status: tagged | PROPOSE | REVIEW (utils class without a context prefix: shared helper or calculation?) | BLOCKED.
  A second table lists the public functions of the `utils` classes: a reusable sub-calculation is an entry point and
  needs its own tag (status REVIEW when it has none and the class has several public functions).
  Nothing is written to the source files.
.EXAMPLE
  ./tag-candidates.ps1 -Root . -Contexts ../harbor-docs/contexts.yml
  ./tag-candidates.ps1 -Root . -Out docs/_generated/tag-candidates.md
#>
param(
    [string]$Root = '.',
    [string]$Contexts = '',
    [string]$Components = 'docs/_generated/components.md',
    [string]$DocsTags = 'docs/_generated/docs-tags.md',
    [string]$Out = ''
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

if (-not $Contexts) {
    $Contexts = @('../harbor-docs/contexts.yml', '../docs-repo/contexts.yml') | ForEach-Object { Join-Path $Root $_ } | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $Contexts) { throw 'contexts.yml not found next to the repo; pass -Contexts <path>' }
}
$compPath = Join-Path $Root $Components
if (-not (Test-Path $compPath)) { throw "$Components missing; run scripts/docs/gen-all.ps1 first" }

# ---- contexts.yml: name -> { Spec; Prefixes } (one line per context, flow style) ----
$ctxs = @{}
foreach ($m in [regex]::Matches((Read-Text $Contexts), '(?m)^\s*([\w-]+):\s*\{\s*spec:\s*(\w+)\s*,\s*fe:\s*[^,]*,\s*be:\s*\[([^\]]*)\]')) {
    $ctxs[$m.Groups[1].Value] = @{ Spec = $m.Groups[2].Value; Prefixes = @($m.Groups[3].Value -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }) }
}
function Resolve-Context([string]$className) {
    $best = ''; $bestLen = 0
    foreach ($c in $ctxs.Keys) { foreach ($p in $ctxs[$c].Prefixes) { if ($className.StartsWith($p) -and $p.Length -gt $bestLen) { $best = $c; $bestLen = $p.Length } } }
    return $best
}

# ---- IDs already in use per spec prefix (docs-tags.md, Spec ID column) ----
$used = @{}
$tagsPath = Join-Path $Root $DocsTags
if (Test-Path $tagsPath) {
    foreach ($m in [regex]::Matches((Read-Text $tagsPath), '(?m)^\|\s*`([A-Z][A-Z0-9]*)-(\d{3})[a-z]?`')) {
        $p = $m.Groups[1].Value; $n = [int]$m.Groups[2].Value
        if (-not $used[$p] -or $used[$p] -lt $n) { $used[$p] = $n }
    }
}
function Next-Id([string]$prefix) {
    $n = if ($used[$prefix]) { $used[$prefix] + 1 } else { 1 }
    $used[$prefix] = $n
    return ('{0}-{1:000}' -f $prefix, $n)
}
function To-Snake([string]$s) { return ([regex]::Replace($s, '(?<=[a-z0-9])([A-Z])|(?<=[A-Z])([A-Z][a-z])', '_$1$2')).ToLower() }

# ---- components.md rows: | `Class` | Layer | Module | Kind | Depends on | Tables | @docs | `Location` | ----
$rows = New-Object System.Collections.Generic.List[object]
foreach ($line in (Read-Text $compPath) -split '\r?\n') {
    if ($line -notmatch '^\|\s*`([\w.]+)`\s*\|\s*(\w+|\(root\))\s*\|') { continue }
    $cells = @($line.Trim('|') -split '\|' | ForEach-Object { $_.Trim() })
    if ($cells.Count -lt 8) { continue }
    $name = $cells[0].Trim('`'); $layer = $cells[1]; $kind = $cells[3]; $tag = ($cells[6] -replace '`', ''); $loc = $cells[7].Trim('`')
    if ($layer -notin @('manager', 'utils')) { continue }
    if ($layer -eq 'utils' -and $kind -notmatch '^(object|class)$') { continue }   # enums, data classes, interfaces are not calculations
    $ctx = ''; $proposed = ''; $status = ''
    if ($layer -eq 'manager') {
        $ctx = Resolve-Context $name
        if ($tag) { $status = 'tagged' }
        elseif (-not $ctx) { $status = 'BLOCKED: no class-name prefix in contexts.yml' }
        else { $proposed = Next-Id $ctxs[$ctx].Spec; $status = 'PROPOSE' }
    } else {
        $ctx = Resolve-Context $name
        if ($tag) { $status = 'tagged' }
        elseif (-not $ctx) { $status = 'REVIEW: shared helper? tag only if it computes a business quantity' }
        else { $proposed = To-Snake $name; $status = 'PROPOSE (confirm name from the KDoc formula)' }
    }
    $rows.Add([pscustomobject]@{ Class = $name; Layer = $layer; Context = $(if ($ctx) { $ctx } else { 'shared' }); Current = $tag; Proposed = $proposed; Status = $status; Loc = $loc })
}

# ---- public functions of the calculation classes: a reusable sub-calculation is an entry point of its own ----
$funRx = '(?s)(?:/\*\*(?<doc>(?:(?!\*/).)*)\*/\s*)?(?:@\w+(?:\([^)]*\))?\s*)*(?<mods>(?:(?:private|internal|protected|public|override|operator|inline|infix|suspend|tailrec|open|abstract)\s+)*)fun\s+(?:<[^>]*>\s*)?(?<name>\w+)\s*\('
$funs = New-Object System.Collections.Generic.List[object]
foreach ($r in $rows | Where-Object { $_.Layer -eq 'utils' }) {
    $file = ($r.Loc -split ':')[0]
    $src = Read-Text (Join-Path $Root $file)
    $public = @([regex]::Matches($src, $funRx) | Where-Object { $_.Groups['mods'].Value -notmatch 'private|internal|protected|override' })
    foreach ($m in $public) {
        $fname = $m.Groups['name'].Value
        $ftags = @([regex]::Matches($m.Groups['doc'].Value, '@docs\s+([\w.-]+)') | ForEach-Object { $_.Groups[1].Value })
        $status = if ($ftags) { 'tagged' }
                  elseif ($r.Current -and $public.Count -eq 1) { "covered by class tag" }
                  elseif ($r.Status -like 'REVIEW*') { 'helper (see class row)' }
                  else { 'REVIEW: entry point? tag if it has a business name and its own test cases' }
        $funs.Add([pscustomobject]@{ Function = "$($r.Class).$fname"; Class = $r.Class; Current = ($ftags -join ', '); Status = $status; Loc = "$file`:$(Get-LineNumber $src $m.Groups['name'].Index)" })
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header '@docs tag candidates (BE)' "$Components + contexts.yml" 'Managers and calculations with their current @docs tag and the proposed one where missing; input for the docs-tagger agent.'))
$n = $rows.Count; $todo = @($rows | Where-Object { $_.Status -like 'PROPOSE*' }).Count; $blocked = @($rows | Where-Object { $_.Status -like 'BLOCKED*' }).Count
$review = @($rows | Where-Object { $_.Status -like 'REVIEW*' }).Count
$ctxShown = (Resolve-Path $Contexts).ProviderPath; if ($ctxShown.StartsWith($Root)) { $ctxShown = Get-RelPath $Root $ctxShown }
[void]$sb.AppendLine("$n class(es): $($n - $todo - $blocked - $review) tagged, $todo to tag, $review to review, $blocked blocked. Spec IDs come from ``$ctxShown``; the spec file itself may not exist yet.")
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Class | Layer | Context | Current | Proposed | Status | Location |')
[void]$sb.AppendLine('|---|---|---|---|---|---|---|')
foreach ($r in $rows | Sort-Object Layer, Context, Class) {
    $cur = if ($r.Current) { '`' + $r.Current + '`' } else { '' }
    $pro = if ($r.Proposed) { '`@docs ' + $r.Proposed + '`' } else { '' }
    [void]$sb.AppendLine("| ``$($r.Class)`` | $($r.Layer) | $($r.Context) | $cur | $pro | $($r.Status) | ``$($r.Loc)`` |")
}
if ($funs.Count) {
    $fReview = @($funs | Where-Object { $_.Status -like 'REVIEW*' }).Count
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('## Public functions of the calculation classes')
    [void]$sb.AppendLine("$($funs.Count) function(s), $fReview to review. A sub-calculation reused by other calculations or cited by a spec is an entry point and carries its own ``@docs``; private steps and helpers do not.")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('| Function | Current | Status | Location |')
    [void]$sb.AppendLine('|---|---|---|---|')
    foreach ($f in $funs | Sort-Object Class, Function) {
        $cur = if ($f.Current) { '`' + $f.Current + '`' } else { '' }
        [void]$sb.AppendLine("| ``$($f.Function)`` | $cur | $($f.Status) | ``$($f.Loc)`` |")
    }
}
if ($blocked) {
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('## Blockers')
    foreach ($r in $rows | Where-Object { $_.Status -like 'BLOCKED*' }) { [void]$sb.AppendLine("- ``$($r.Class)``: add its name prefix to a context in contexts.yml, then rerun.") }
}
$text = $sb.ToString()
if ($Out) { Write-Text (Resolve-Out $Root $Out) $text; Write-Host "tag-candidates: $n class(es), $todo to tag, $blocked blocked -> $Out" } else { Write-Output $text }
