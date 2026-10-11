<#
.SYNOPSIS
  Feature map for a React/TS repo organised as src/features/<name>: purpose (from @module JSDoc in index.ts),
  public exports, hooks/components counts, API calls and browser channels (BroadcastChannel: defines / pub / sub).
  One line per feature, plus one `fe-app` row for the app shell (src/app) so its channel usage and API calls are visible.
.NOTES
  Channels: a file containing `new BroadcastChannel(` is a channel module; its channel name comes from a
  `*CHANNEL*` string constant in that file (else the literal passed to the constructor, else the file name) and gets
  the suffix `.{*}` when the constructor argument is not a literal (one channel per session etc.). A feature
  `pub`lishes when it imports a symbol matching /publish/i from that module, `sub`scribes for /subscri/i; the feature
  that holds the module `defines` it. Keep every BroadcastChannel inside one module per channel for this to work.
#>
param(
    [string]$Root = '.',
    [string]$FeaturesDir = 'src/features',
    [string]$Out = 'docs/_generated/codebase-map.md'
)
. (Join-Path $PSScriptRoot '_common.ps1')
$Root = (Resolve-Path $Root).ProviderPath

$featRoot = Join-Path $Root $FeaturesDir
if (-not (Test-Path $featRoot)) { throw "No $FeaturesDir under $Root" }

# ---- browser channels (BroadcastChannel) ----
$channelModules = @{}   # module key (repo-relative path without extension, forward slashes) -> channel name
foreach ($f in @(Get-SourceFiles (Join-Path $Root 'src') @('*.ts', '*.tsx') | Where-Object { $_.Name -notmatch '\.(test|spec|stories)\.' })) {
    $t = Read-Text $f.FullName
    if ($t -notmatch 'new\s+BroadcastChannel\(') { continue }
    $name = ''
    if ($t -match "(?m)^\s*(?:export\s+)?const\s+\w*CHANNEL\w*\s*=\s*['""]([\w.-]+)['""]") { $name = $Matches[1] }
    elseif ($t -match "new\s+BroadcastChannel\(\s*['""]([\w.-]+)['""]") { $name = $Matches[1] }
    else { $name = [IO.Path]::GetFileNameWithoutExtension($f.Name) }
    if ($t -notmatch "new\s+BroadcastChannel\(\s*['""]") { $name += '.{*}' }
    $key = (Get-RelPath $Root $f.FullName) -replace '\.(ts|tsx)$', ''
    $channelModules[$key] = $name
}
function Resolve-Import([string]$fromFile, [string]$spec) {
    # returns the repo-relative module key for a relative or '@/' import, '' otherwise
    if ($spec.StartsWith('@/')) { return ('src/' + $spec.Substring(2)) -replace '/index$', '' }
    if (-not $spec.StartsWith('.')) { return '' }
    $dir = Split-Path (Join-Path $Root $fromFile) -Parent
    $full = [IO.Path]::GetFullPath((Join-Path $dir $spec))
    return ((Get-RelPath $Root $full) -replace '\.(ts|tsx)$', '') -replace '/index$', ''
}
function Channel-Usage([string]$dirFull) {
    $uses = New-Object System.Collections.Generic.List[string]
    if ($channelModules.Count -eq 0) { return $uses }
    foreach ($f in @(Get-SourceFiles $dirFull @('*.ts', '*.tsx') | Where-Object { $_.Name -notmatch '\.(test|spec|stories)\.' })) {
        $rel = Get-RelPath $Root $f.FullName
        $key = $rel -replace '\.(ts|tsx)$', ''
        if ($channelModules.ContainsKey($key)) { $uses.Add("defines $($channelModules[$key])"); continue }
        $t = Read-Text $f.FullName
        foreach ($m in [regex]::Matches($t, "(?m)^import\s+(?:type\s+)?\{([^}]*)\}\s+from\s+['""]([^'""]+)['""]")) {
            $target = Resolve-Import $rel $m.Groups[2].Value
            $tk = $channelModules.Keys | Where-Object { $_ -eq $target -or $_ -eq "$target/index" -or ($_ -replace '/[^/]+$', '') -eq $target } | Select-Object -First 1   # direct import or the feature barrel re-exporting the hooks
            if (-not $tk) { continue }
            $syms = @($m.Groups[1].Value -split ',' | ForEach-Object { ($_ -replace '\s+as\s+.*', '').Trim() })
            if ($syms | Where-Object { $_ -match 'publish' }) { $uses.Add("pub $($channelModules[$tk])") }
            if ($syms | Where-Object { $_ -match 'subscri' }) { $uses.Add("sub $($channelModules[$tk])") }
        }
    }
    return @($uses | Select-Object -Unique)
}

function Api-Calls([object[]]$files) {
    $apis = New-Object System.Collections.Generic.HashSet[string]
    foreach ($f in $files) {
        foreach ($m in [regex]::Matches((Read-Text $f.FullName), '(?:fetch|axios\.\w+|api\.\w+)\(\s*`([^`]*)`|(?:fetch|axios\.\w+|api\.\w+)\(\s*[''"]([^''"]*)[''"]')) {
            $u = if ($m.Groups[1].Success) { $m.Groups[1].Value } else { $m.Groups[2].Value }
            [void]$apis.Add(($u -replace '\$\{BASE\}', '<BASE>' -replace '\$\{[^}]+\}', '{*}'))
        }
    }
    return @($apis | Sort-Object)
}

$rows = foreach ($d in Get-ChildItem $featRoot -Directory | Sort-Object Name) {
    $files = @(Get-SourceFiles $d.FullName @('*.ts','*.tsx') | Where-Object { $_.Name -notmatch '\.(test|spec|stories)\.' })
    $idx = Get-ChildItem $d.FullName -File -Filter 'index.ts*' | Select-Object -First 1
    $desc = ''; $exports = @()
    if ($idx) {
        $t = Read-Text $idx.FullName
        $doc = [regex]::Match($t, '(?s)/\*\*(.*?)\*/')
        if ($doc.Success) {
            $desc = (($doc.Groups[1].Value -split '\r?\n' | ForEach-Object { ($_ -replace '^\s*\*\s?', '').Trim() } | Where-Object { $_ -and $_ -notmatch '^@' }) | Select-Object -First 1)
        }
        $exports = [regex]::Matches($t, '(?m)^export\s+(?:type\s+)?\{([^}]*)\}') | ForEach-Object { ($_.Groups[1].Value -split ',') | ForEach-Object { ($_ -replace '\s+as\s+.*', '').Trim() } | Where-Object { $_ } }
    }
    $hooks = @($files | Where-Object { $_.Name -match '^use[A-Z]' }).Count
    $components = @($files | Where-Object { $_.Extension -eq '.tsx' -and $_.Name -notmatch '^(index|routes?)\.' }).Count
    [pscustomobject]@{
        Feature = $d.Name; Desc = $desc; Files = $files.Count; Components = $components; Hooks = $hooks
        Exports = ($exports -join ', '); Apis = ((Api-Calls $files) -join '<br>')
        Channels = ((Channel-Usage $d.FullName) -join '<br>')
        Entry = "$FeaturesDir/$($d.Name)/$(if ($idx) { $idx.Name } else { '-' })"
    }
}
# app shell row (routes, layouts): only API calls and channel usage matter here
$appDir = Join-Path $Root 'src/app'
if (Test-Path $appDir) {
    $appFiles = @(Get-SourceFiles $appDir @('*.ts', '*.tsx') | Where-Object { $_.Name -notmatch '\.(test|spec|stories)\.' })
    $rows = @($rows) + [pscustomobject]@{
        Feature = 'fe-app'; Desc = 'app shell: router, layouts, providers'; Files = $appFiles.Count
        Components = @($appFiles | Where-Object { $_.Extension -eq '.tsx' }).Count; Hooks = 0; Exports = ''
        Apis = ((Api-Calls $appFiles) -join '<br>'); Channels = ((Channel-Usage $appDir) -join '<br>'); Entry = 'src/app/App.tsx'
    }
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append((New-Header 'Codebase map (FE)' "$FeaturesDir/* + index.ts barrels"))
[void]$sb.AppendLine('Read the feature `index.ts` (public surface) and `*.types.ts` first; open components only for UI-level questions.')
[void]$sb.AppendLine('Channels = browser `BroadcastChannel`s (`defines` / `pub` / `sub`), the FE counterpart of Kafka topics; the shared component library is in `components.md`.')
[void]$sb.AppendLine()
[void]$sb.AppendLine('| Feature | Purpose | Entry | Files | Components | Hooks | Public exports | API calls | Channels |')
[void]$sb.AppendLine('|---|---|---|---|---|---|---|---|---|')
foreach ($r in $rows) {
    [void]$sb.AppendLine("| ``$($r.Feature)`` | $(Escape-Cell $r.Desc) | ``$($r.Entry)`` | $($r.Files) | $($r.Components) | $($r.Hooks) | $(Escape-Cell $r.Exports) | $($r.Apis) | $($r.Channels) |")
}
Write-Text (Resolve-Out $Root $Out) $sb.ToString()
Write-Host "codebase-map: $(@($rows).Count) feature(s) -> $Out"
