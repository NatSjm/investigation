<#
.SYNOPSIS
  Queries generated/graph/graph.json without any library. CLI twin of the VS Code `#impact` tool,
  for IntelliJ users (paste the output into Copilot chat) and for CI analytics (PR -> impacted specs).

.EXAMPLE
  .\graph-query.ps1 -Node topic:market.rates.updated                 # neighbourhood, depth 2
  .\graph-query.ps1 -Node spec:P1-001 -Depth 3                    # spec -> code -> tables/topics/routes
  .\graph-query.ps1 -Files core/src/main/kotlin/harbor/api/Product1Controller.kt,src/features/product1/index.ts
                                                                     # git diff --name-only | impacted nodes + specs
  .\graph-query.ps1 -Find proposal                                   # fuzzy node search
  .\graph-query.ps1 -Node feature:product1 -Json                       # machine output
#>
param(
    [string]$Graph = (Join-Path (Split-Path $PSScriptRoot -Parent) 'generated/graph/graph.json'),
    [string]$Node,
    [string[]]$Files,
    [string]$Find,
    [int]$Depth = 2,
    [int]$MaxLines = 60,
    [switch]$Json
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not (Test-Path $Graph)) { Write-Error "graph not found: $Graph (run scripts/gen-graph.ps1)" }
$g = [IO.File]::ReadAllText((Resolve-Path $Graph), [Text.UTF8Encoding]::new($false)) | ConvertFrom-Json
$byId = @{}; foreach ($n in $g.nodes) { $byId[$n.id] = $n }
$out = @{}; $in = @{}
foreach ($e in $g.edges) {
    if (-not $out.ContainsKey($e.from)) { $out[$e.from] = @() }; $out[$e.from] += $e
    if (-not $in.ContainsKey($e.to)) { $in[$e.to] = @() }; $in[$e.to] += $e
}
function Fmt($n) { $loc = if ($n.location) { " - $($n.location)" } else { '' }; $note = if ($n.note) { " - $($n.note)" } else { '' }; "$($n.id) [$($n.community)]$loc$note" }

function Resolve-Start([string]$q) {
    if ($byId.ContainsKey($q)) { return @($q) }
    $hits = @($g.nodes | Where-Object { $_.id -like "*$q*" -or $_.label -like "*$q*" } | ForEach-Object { $_.id })
    if ($hits.Count -eq 1) { return $hits }
    if ($hits.Count -gt 1) { Write-Host "ambiguous '$q': $($hits -join ', ')" -ForegroundColor Yellow; return @() }
    Write-Host "no node matches '$q'" -ForegroundColor Yellow; return @()
}
function Bfs([string[]]$Start, [int]$MaxDepth) {
    $dist = @{}; $q = New-Object System.Collections.Generic.Queue[string]
    foreach ($s in $Start) { $dist[$s] = 0; $q.Enqueue($s) }
    $touched = @()
    while ($q.Count) {
        $c = $q.Dequeue(); if ($dist[$c] -ge $MaxDepth) { continue }
        foreach ($e in @($out[$c]) + @($in[$c])) {
            if ($null -eq $e) { continue }
            $touched += $e
            $o = if ($e.from -eq $c) { $e.to } else { $e.from }
            if (-not $dist.ContainsKey($o)) { $dist[$o] = $dist[$c] + 1; $q.Enqueue($o) }
        }
    }
    return @{ dist = $dist; edges = @($touched | Sort-Object -Property from, rel, to -Unique) }
}
function Emit($start, $res, [string]$title) {
    if ($Json) {
        [pscustomobject]@{ start = $start; nodes = @($res.dist.Keys | Sort-Object { $res.dist[$_] }, { $_ } | ForEach-Object { $n = $byId[$_]; [pscustomobject]@{ id = $_; depth = $res.dist[$_]; kind = $n.kind; community = $n.community; location = $n.location } }); edges = $res.edges } | ConvertTo-Json -Depth 5
        return
    }
    $lines = @("# $title", '')
    foreach ($d in 0..$Depth) {
        $ids = @($res.dist.Keys | Where-Object { $res.dist[$_] -eq $d } | Sort-Object)
        if (-not $ids.Count) { continue }
        $lines += "## depth $d"
        foreach ($id in $ids) { $lines += "- $(Fmt $byId[$id])" }
    }
    $lines += ''; $lines += '## edges'
    foreach ($e in $res.edges) { $lines += "- $($e.from) -$($e.rel)-> $($e.to)" + $(if ($e.source -ne 'regex-map') { " ($($e.source))" } else { '' }) }
    $specs = @($res.dist.Keys | Where-Object { $_ -like 'spec:*' } | Sort-Object)
    $lines += ''; $lines += "## specs in blast radius: $(if ($specs.Count) { $specs -join ', ' } else { 'none' })"
    if ($lines.Count -gt $MaxLines) { $lines = $lines[0..($MaxLines - 1)] + "... ($($lines.Count - $MaxLines) more lines; raise -MaxLines or lower -Depth)" }
    $lines | ForEach-Object { Write-Output $_ }
}

if ($Find) {
    $g.nodes | Where-Object { $_.id -like "*$Find*" -or $_.label -like "*$Find*" -or $_.note -like "*$Find*" } | Sort-Object id | ForEach-Object { Write-Output "- $(Fmt $_)" }
    exit 0
}
if ($Files) {
    $norm = @($Files | ForEach-Object { ($_ -replace '\\', '/') -replace '^\./', '' })
    $start = @($g.nodes | Where-Object { $n = $_; $n.location -and ($norm | Where-Object { $loc = ($n.location -split ':')[0]; $_ -eq $loc -or $_.EndsWith('/' + $loc) -or $loc.EndsWith('/' + $_) }) } | ForEach-Object { $_.id })
    if (-not $start.Count) { Write-Host 'no graph nodes located in the given files (not architectural, or maps stale)'; exit 0 }
    $res = Bfs $start $Depth
    Emit $start $res "Impact of $($Files.Count) changed file(s)"
    exit 0
}
if ($Node) {
    $start = @(Resolve-Start $Node)
    if (-not $start.Count) { exit 2 }
    $res = Bfs $start $Depth
    Emit $start $res "Neighbourhood of $($start -join ', ') (depth $Depth)"
    exit 0
}
Write-Host 'usage: graph-query.ps1 -Node <id|substring> | -Files <paths> | -Find <text>  [-Depth n] [-Json]'
