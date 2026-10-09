<#
.SYNOPSIS
  Codebase map for a Maven/Kotlin backend organised by technical layer (package-by-layer):
  modules (root pom) -> layers (package segment after the base package) -> classes, plus resource folders.
  One line per module and per layer; details per class are in components.md.
.EXAMPLE
  ./gen-codebase-map.ps1 -Root . -Out docs/_generated/codebase-map.md
#>
param(
    [string]$Root = '.',
    [string]$Out = 'docs/_generated/codebase-map.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$bt = [char]96   # backtick, kept out of interpolated strings
function Code([string]$s) { if ($s.StartsWith('(+')) { $s } else { $bt + $s + $bt } }
function Code-List($items) { (@($items) | ForEach-Object { Code ([string]$_) }) -join ', ' }
$Root = (Resolve-Path $Root).ProviderPath

# conventional meaning of layer folders (extend when the real repo has more)
$roles = [ordered]@{
    'advice'    = 'global exception handling (@RestControllerAdvice -> ProblemDetail)'
    'api'       = 'REST controllers implementing the generated *Api interfaces (one per contract tag)'
    'client'    = 'wrappers over generated REST clients of external services (contracts in resources/api)'
    'component' = 'infrastructure components (filters, parsers, template loaders)'
    'config'    = 'Spring configuration'
    'context'   = 'request / session context holders'
    'dao'       = 'repositories (Spring Data / JDBC) - tables per class in components.md'
    'databind'  = 'Jackson serializers / deserializers'
    'enums'     = 'enumerations'
    'event'     = 'Kafka listeners and publishers (topics in events.md)'
    'exception' = 'exception types'
    'job'       = 'scheduled jobs (triggers in jobs.md)'
    'manager'   = 'orchestration per bounded context; transactional boundary; KDoc + @docs - READ FIRST'
    'mapper'    = 'entity <-> DTO mappers'
    'model'     = 'JPA entities and internal models'
    'service'   = 'business services used by managers'
    'utils'     = 'calculations (pure Kotlin, @docs <calculation>) and helpers'
    'validator' = 'request validation'
}
$listAll = @('api', 'manager', 'job', 'event', 'client', 'utils', 'validator', 'component', 'service')

$rootPom = Join-Path $Root 'pom.xml'
if (-not (Test-Path $rootPom)) { throw "No pom.xml in $Root" }
[xml]$pom = Read-Text $rootPom
$ns = @{ m = 'http://maven.apache.org/POM/4.0.0' }
$modules = @(Select-Xml -Xml $pom -Namespace $ns -XPath '//m:modules/m:module' | ForEach-Object { $_.Node.InnerText })
if ($modules.Count -eq 0) { $modules = @('.') }

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Codebase map (BE)' 'pom.xml modules + package-by-layer scan' 'Backend modules, technical layers with their classes and resource folders; read the manager of a context first.'))
[void]$sb.AppendLine('Layered backend: the business context of a class is its **name prefix** (`Product1*`, `Stress*` ...), not its folder.')
[void]$sb.AppendLine('Read order: the context''s `manager/*Manager.kt` (KDoc + `@docs`) -> the service / dao / utils it depends on (components.md) -> one range.')
[void]$sb.AppendLine()
[void]$sb.AppendLine('## Modules')
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Module | Purpose | Base package | Kotlin files | Layers |')
[void]$sb.AppendLine('|---|---|---|---|---|')
$layerSections = New-Object System.Text.StringBuilder
$otherDirs = @(Get-ChildItem $Root -Directory | Where-Object { $_.Name -notin $modules -and $_.Name -notmatch '^(\.|target|docs|scripts|node_modules)' } | ForEach-Object { $_.Name })
foreach ($m in $modules) {
    $mDir = Join-Path $Root $m
    $desc = ''
    $mPom = Join-Path $mDir 'pom.xml'
    if (Test-Path $mPom) {
        [xml]$mx = Read-Text $mPom
        $d = Select-Xml -Xml $mx -Namespace $ns -XPath '/m:project/m:description'
        if ($d) { $desc = $d.Node.InnerText.Trim() }
    }
    $srcMain = Join-Path $mDir 'src/main'
    $files = @(); if (Test-Path $srcMain) { $files = @(Get-SourceFiles $srcMain @('*.kt', '*.java')) }
    $pkgs = @{}
    foreach ($f in $files) { $pm = [regex]::Match((Read-Text $f.FullName), '(?m)^package\s+([\w.]+)'); if ($pm.Success) { $pkgs[$f.FullName] = $pm.Groups[1].Value } }
    $base = ($pkgs.Values | Sort-Object { $_.Length } | Select-Object -First 1)
    $byLayer = [ordered]@{}
    foreach ($f in $files) {
        $p = $pkgs[$f.FullName]; $layer = '(root)'
        if ($p -and $base -and $p.Length -gt $base.Length) { $layer = ($p.Substring($base.Length).TrimStart('.') -split '\.')[0] }
        if (-not $byLayer.Contains($layer)) { $byLayer[$layer] = New-Object System.Collections.Generic.List[string] }
        $byLayer[$layer].Add([IO.Path]::GetFileNameWithoutExtension($f.Name))
    }
    $layerNames = @($byLayer.Keys | Sort-Object)
    [void]$sb.AppendLine('| ' + (Code $m) + ' | ' + (Escape-Cell $desc) + ' | ' + (Code $base) + ' | ' + $files.Count + ' | ' + ((@($layerNames) | ForEach-Object { Code $_ }) -join ' ') + ' |')

    if ($layerNames.Count -gt 1) {
        $layRel = (Get-RelPath $Root $srcMain) + '/kotlin/' + ($base -replace '\.', '/') + '/<layer>'; [void]$layerSections.AppendLine('## Layers of ' + $bt + $m + $bt + ' (' + $bt + $layRel + $bt + ')')
        [void]$layerSections.AppendLine()
        [void]$layerSections.AppendLine('| Layer | Role | Files | Classes |')
        [void]$layerSections.AppendLine('|---|---|---|---|')
        foreach ($l in $layerNames) {
            $names = @($byLayer[$l] | Sort-Object)
            $shown = if ($l -in $listAll -or $names.Count -le 12) { $names } else { @($names | Select-Object -First 12) + ('(+' + ($names.Count - 12) + ')') }
            $role = if ($roles.Contains($l)) { $roles[$l] } else { '' }
            [void]$layerSections.AppendLine('| ' + (Code $l) + ' | ' + $role + ' | ' + $names.Count + ' | ' + (Code-List $shown) + ' |')
        }
        [void]$layerSections.AppendLine()
    }
    $res = Join-Path $mDir 'src/main/resources'
    if (Test-Path $res) {
        $resRel = Get-RelPath $Root $res; [void]$layerSections.AppendLine('## Resources of ' + $bt + $m + $bt + ' (' + $bt + $resRel + $bt + ')')
        [void]$layerSections.AppendLine()
        [void]$layerSections.AppendLine('| Folder | Files |')
        [void]$layerSections.AppendLine('|---|---|')
        foreach ($rd in Get-ChildItem $res -Directory | Sort-Object Name) {
            $rf = @(Get-ChildItem $rd.FullName -Recurse -File | ForEach-Object { $_.FullName.Substring($rd.FullName.Length + 1).Replace('\', '/') })
            $shown = if ($rf.Count -le 10) { $rf } else { @($rf | Select-Object -First 10) + ('(+' + ($rf.Count - 10) + ')') }
            [void]$layerSections.AppendLine('| ' + (Code ($rd.Name + '/')) + ' | ' + (Code-List $shown) + ' |')
        }
        $top = @(Get-ChildItem $res -File | ForEach-Object { $_.Name })
        if ($top) { [void]$layerSections.AppendLine('| (root) | ' + (Code-List $top) + ' |') }
        [void]$layerSections.AppendLine()
    }
}
[void]$sb.AppendLine()
if ($otherDirs) {
    [void]$sb.AppendLine('Other top-level folders (not Maven modules): ' + (Code-List ($otherDirs | ForEach-Object { $_ + '/' })))
    [void]$sb.AppendLine()
}
[void]$sb.Append($layerSections.ToString())
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "codebase-map: $($modules.Count) module(s) -> $Out"
