<#
.SYNOPSIS
  Single evidence collector of the docs repository: pulls the generated code maps and the contracts from the
  backend and frontend checkouts into generated/, as one coherent snapshot, with a manifest of source commits and
  file hashes. Replaces per-repository "publisher" CI jobs (one owner of publication; see ci-examples/collect-evidence.yml).

.DESCRIPTION
  1. Resolves each source checkout to a commit (git rev-parse), its branch, remote and whether the working copy is dirty.
  2. Optionally regenerates the maps in both repos (-Generate runs scripts/docs/gen-all.ps1 there).
  3. Stages the collector-owned artifact sets in a temporary directory:
       generated/be/*.md (+ graph-export-be.json)      from <backend>/docs/_generated
       generated/fe/*.md (+ graph-export-fe.json)      from <frontend>/docs/_generated
       generated/openapi/backend.yaml, external/*.yaml  from <backend>/core/src/main/resources/{openapi,api}
       generated/asyncapi/backend.yaml                  from <backend>/core/src/main/resources/openapi/harbor-events.yaml
  4. Validates the candidate snapshot (every map has frontmatter, every contract parses as an OpenAPI/AsyncAPI document,
     nothing empty). A failed validation publishes nothing; the previous snapshot stays.
  5. Compares the candidate with the current generated/ ignoring volatile timestamps; when nothing changed it stops
     without touching a file (idempotent: a second run against unchanged inputs produces no diff).
  6. Replaces each artifact set completely (files the sources no longer produce are deleted), never touching
     hand-written concepts, index.md files or the graph, and writes generated/manifest.yml.
  7. With -Graph also runs gen-graph.ps1 and build-index.ps1 so the snapshot is ready to commit.

  Lib-free PowerShell 7. In CI the source repositories are checked out into separate directories and passed as
  -Backend / -Frontend; locally the sibling checkouts are used by default.

.EXAMPLE
  .\collect-evidence.ps1                                   # sibling checkouts, maps as they are on disk
  .\collect-evidence.ps1 -Generate -Graph                   # regenerate maps in both repos, collect, rebuild graph + indexes
  .\collect-evidence.ps1 -Backend D:\ci\harbor-backend -Frontend D:\ci\harbor-frontend -Graph
  .\collect-evidence.ps1 -DryRun                            # report what would change, write nothing
#>
param(
    [string]$Backend = (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'backend'),
    [string]$Frontend = (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'frontend'),
    [switch]$Generate,
    [switch]$Graph,
    [switch]$DryRun,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'
[cultureinfo]::CurrentCulture = [cultureinfo]::InvariantCulture   # identical sort order on every machine (ICU + machine culture otherwise)
$CollectorVersion = '1.0'
$repo = Split-Path $PSScriptRoot -Parent
$gen = Join-Path $repo 'generated'
$now = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')

function Read-Text([string]$p) { [IO.File]::ReadAllText($p) }
function Write-Text([string]$p, [string]$s) { $d = Split-Path $p -Parent; if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }; [IO.File]::WriteAllText($p, $s, [Text.UTF8Encoding]::new($false)) }
function Rel([string]$p) { $p.Substring($repo.Length + 1).Replace('\', '/') }
function Norm([string]$s) { ($s -replace '(?m)at:\s*[0-9T:\-Z.+]+', 'at: <t>') -replace '\r', '' }
function Sha([string]$p) { (Get-FileHash -Algorithm SHA256 -Path $p).Hash.ToLower() }

# ---------- 1. sources ----------
function Git-Info([string]$path, [string]$name) {
    if (-not (Test-Path $path)) { throw "$name checkout not found: $path" }
    $inRepo = (& git -C $path rev-parse --is-inside-work-tree 2>$null) -eq 'true'
    if (-not $inRepo) { return [ordered]@{ name = $name; path = $path.Replace('\', '/'); remote = ''; branch = ''; commit = 'unknown'; dirty = $true } }
    $commit = (& git -C $path rev-parse HEAD).Trim()
    $branch = (& git -C $path rev-parse --abbrev-ref HEAD).Trim()
    $remote = (& git -C $path config --get remote.origin.url 2>$null); if (-not $remote) { $remote = '' }
    $dirty = [bool]((& git -C $path status --porcelain) | Where-Object { $_ })
    return [ordered]@{ name = $name; path = $path.Replace('\', '/'); remote = "$remote".Trim(); branch = $branch; commit = $commit; dirty = $dirty }
}
$sources = @((Git-Info $Backend 'backend'), (Git-Info $Frontend 'frontend'))
foreach ($s in $sources) { Write-Host ("source {0,-8} {1} {2}{3}" -f $s.name, $s.commit.Substring(0, [Math]::Min(7, $s.commit.Length)), $s.branch, $(if ($s.dirty) { ' (dirty working copy)' } else { '' })) }

# ---------- 2. optional regeneration ----------
if ($Generate) {
    foreach ($s in $sources) {
        $g = Join-Path $s.path 'scripts/docs/gen-all.ps1'
        if (Test-Path $g) { Write-Host "regenerate maps: $($s.name)"; & pwsh -NoProfile -File $g -Root $s.path | Out-Null; if ($LASTEXITCODE) { throw "gen-all failed in $($s.name)" } }
        else { Write-Host "skip regenerate (no scripts/docs/gen-all.ps1): $($s.name)" -ForegroundColor Yellow }
    }
}

# ---------- 3. stage ----------
$stage = Join-Path ([IO.Path]::GetTempPath()) ("harbor-collect-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $stage | Out-Null
# artifact set -> { Dir (relative, collector-owned), Keep (files never deleted there) }
$sets = [ordered]@{
    be       = @{ Dir = 'generated/be';               Source = 'backend' }
    fe       = @{ Dir = 'generated/fe';               Source = 'frontend' }
    openapi  = @{ Dir = 'generated/openapi';          Source = 'backend' }
    asyncapi = @{ Dir = 'generated/asyncapi';         Source = 'backend' }
}
$staged = @()   # { Set, Rel, Path }
function Stage([string]$set, [string]$src, [string]$relName) {
    if (-not (Test-Path $src)) { return }
    $dst = Join-Path $stage (Join-Path $sets[$set].Dir $relName)
    $d = Split-Path $dst -Parent; if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
    Copy-Item $src $dst -Force
    $script:staged += [pscustomobject]@{ Set = $set; Rel = ($sets[$set].Dir + '/' + $relName); Path = $dst }
}
foreach ($x in @(@{ s = 'be'; p = $Backend }, @{ s = 'fe'; p = $Frontend })) {
    $d = Join-Path $x.p 'docs/_generated'
    if (-not (Test-Path $d)) { throw "no generated maps in $($x.p)/docs/_generated (run scripts/docs/gen-all.ps1 there or pass -Generate)" }
    Get-ChildItem $d -File | Where-Object { ($_.Extension -eq '.md' -and $_.Name -ne 'index.md') -or $_.Name -like 'graph-export-*.json' } | ForEach-Object { Stage $x.s $_.FullName $_.Name }
}
$res = Join-Path $Backend 'core/src/main/resources'
Stage 'openapi'  (Join-Path $res 'openapi/harbor-api.yaml')    'backend.yaml'
Stage 'asyncapi' (Join-Path $res 'openapi/harbor-events.yaml') 'backend.yaml'
if (Test-Path (Join-Path $res 'api')) { Get-ChildItem (Join-Path $res 'api') -File -Filter '*.yaml' | ForEach-Object { Stage 'openapi' $_.FullName ('external/' + $_.Name) } }

# ---------- 4. validate the candidate ----------
$problems = @()
if (-not ($staged | Where-Object Set -eq 'be')) { $problems += 'backend maps: nothing collected' }
if (-not ($staged | Where-Object Set -eq 'fe')) { $problems += 'frontend maps: nothing collected' }
if (-not ($staged | Where-Object { $_.Rel -eq 'generated/openapi/backend.yaml' })) { $problems += 'contract generated/openapi/backend.yaml missing' }
foreach ($f in $staged) {
    $t = Read-Text $f.Path
    if (-not $t.Trim()) { $problems += "$($f.Rel): empty"; continue }
    if ($f.Rel -like '*.md' -and $t -notmatch '^---\r?\n(?s).*?\r?\n---') { $problems += "$($f.Rel): no frontmatter (generated maps carry OKF frontmatter)" }
    if ($f.Rel -like 'generated/openapi/backend.yaml' -and $t -notmatch '(?m)^openapi:\s*3') { $problems += "$($f.Rel): not an OpenAPI 3 document" }
    if ($f.Rel -like 'generated/asyncapi/*.yaml' -and $t -notmatch '(?m)^asyncapi:\s*\d') { $problems += "$($f.Rel): not an AsyncAPI document" }
    if ($f.Rel -like 'generated/openapi/external/*.yaml' -and $t -notmatch '(?m)^(openapi|swagger):') { $problems += "$($f.Rel): not an OpenAPI document" }
    if ($f.Rel -like '*.yaml' -and $t -match '(?m)^\s*\$ref:\s*["'']?(?!#)[^"''\s]+') { $problems += "$($f.Rel): external `$ref '$($Matches[0].Trim())' would not resolve inside generated/" }
}
if ($problems.Count) {
    Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "collect-evidence: candidate snapshot rejected, nothing published:" -ForegroundColor Red
    $problems | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

# ---------- 5. compare with the current snapshot ----------
$current = @{}
foreach ($set in $sets.Keys) {
    $d = Join-Path $repo $sets[$set].Dir
    if (Test-Path $d) { Get-ChildItem $d -Recurse -File | Where-Object { $_.Name -ne 'index.md' } | ForEach-Object { $current[(Rel $_.FullName)] = $_.FullName } }
}
$added = @(); $changed = @(); $removed = @()
foreach ($f in $staged) {
    if (-not $current.ContainsKey($f.Rel)) { $added += $f.Rel }
    elseif ((Norm (Read-Text $current[$f.Rel])) -ne (Norm (Read-Text $f.Path))) { $changed += $f.Rel }
}
$stagedRel = @($staged | ForEach-Object { $_.Rel })
foreach ($k in $current.Keys) { if ($stagedRel -notcontains $k) { $removed += $k } }
Write-Host ("candidate: {0} file(s); added {1}, changed {2}, removed {3}" -f $staged.Count, $added.Count, $changed.Count, $removed.Count)
foreach ($r in $added)   { Write-Host "  + $r" -ForegroundColor Green }
foreach ($r in $changed) { Write-Host "  ~ $r" }
foreach ($r in $removed) { Write-Host "  - $r" -ForegroundColor Yellow }

$manifestPath = Join-Path $gen 'manifest.yml'
$sameSources = $false
if (Test-Path $manifestPath) {
    $old = Read-Text $manifestPath
    $sameSources = ($sources | ForEach-Object { $old -match "commit:\s*$($_.commit)" }) -notcontains $false
}
if (-not $Force -and -not $added.Count -and -not $changed.Count -and -not $removed.Count -and $sameSources) {
    Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "collect-evidence: no change against the current snapshot (sources unchanged) - nothing written" -ForegroundColor Green
    exit 0
}
if ($DryRun) { Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "dry run - nothing written"; exit 0 }

# ---------- 6. publish: replace the collector-owned sets, write the manifest ----------
foreach ($set in $sets.Keys) {
    $d = Join-Path $repo $sets[$set].Dir
    if (Test-Path $d) { Get-ChildItem $d -Recurse -File | Where-Object { $_.Name -ne 'index.md' } | ForEach-Object { Remove-Item $_.FullName -Force } }
}
foreach ($f in $staged) { $dst = Join-Path $repo $f.Rel; $d = Split-Path $dst -Parent; if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }; Copy-Item $f.Path $dst -Force }
Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
# generated/be and generated/fe index.md are reserved OKF files owned by build-index.ps1
Remove-Item (Join-Path $gen 'be/index.md'), (Join-Path $gen 'fe/index.md') -ErrorAction SilentlyContinue

$sb = [Text.StringBuilder]::new()
[void]$sb.AppendLine('# Evidence snapshot manifest - written by scripts/collect-evidence.ps1; do not edit.')
[void]$sb.AppendLine('# Records which source commits the collector-owned files under generated/ describe (be, fe, openapi, asyncapi).')
[void]$sb.AppendLine("collector: { version: '$CollectorVersion', at: $now }")
[void]$sb.AppendLine('sources:')
foreach ($s in $sources) { [void]$sb.AppendLine("  $($s.name): { remote: '$($s.remote)', branch: '$($s.branch)', commit: $($s.commit), dirty: $($s.dirty.ToString().ToLower()) }") }
[void]$sb.AppendLine('artifacts:')
foreach ($f in ($staged | Sort-Object Rel)) { [void]$sb.AppendLine("  - { path: $($f.Rel), source: $($sets[$f.Set].Source), sha256: $(Sha (Join-Path $repo $f.Rel)) }") }
Write-Text $manifestPath $sb.ToString()
Write-Host "manifest -> generated/manifest.yml ($($staged.Count) artifact(s), sources $(($sources | ForEach-Object { $_.commit.Substring(0,7) }) -join ' / '))"
if ($sources | Where-Object dirty) { Write-Host "note: a source working copy is dirty; the manifest commit does not describe the collected files exactly (fine locally, never in CI)" -ForegroundColor Yellow }

# ---------- 7. derived artifacts ----------
if ($Graph) {
    & pwsh -NoProfile -File (Join-Path $PSScriptRoot 'gen-graph.ps1');   if ($LASTEXITCODE) { throw 'gen-graph failed' }
    & pwsh -NoProfile -File (Join-Path $PSScriptRoot 'build-index.ps1'); if ($LASTEXITCODE) { throw 'build-index failed' }
} else {
    Write-Host "done - now run gen-graph.ps1 and build-index.ps1 (or pass -Graph)" -ForegroundColor Green
}
