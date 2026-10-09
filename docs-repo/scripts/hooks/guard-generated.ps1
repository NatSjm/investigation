<#
.SYNOPSIS
  preToolUse hook: denies edit/write tool calls that target generated/** (CI-owned) or index.md files
  (built by scripts/build-index.ps1). Reads the hook payload from stdin, answers with a permission decision
  on stdout, as described in the GitHub Copilot hooks reference (.github/hooks/*.json).
  Best effort: the exact payload shape may differ per surface, so the check is a tolerant regex over the raw JSON.
#>
$ErrorActionPreference = 'SilentlyContinue'
$raw = [Console]::In.ReadToEnd()
$isEdit = $raw -match '"(toolName|tool_name|name)"\s*:\s*"(edit|write|create|str_replace_editor|multi_edit|MultiEdit|Write|Edit)'
$targetsGenerated = $raw -match '(?i)"(path|file_path|filePath|uri)"\s*:\s*"[^"]*(^|[\\/])generated[\\/]'
$targetsIndex = $raw -match '(?i)"(path|file_path|filePath|uri)"\s*:\s*"[^"]*[\\/]index\.md"'
if ($isEdit -and ($targetsGenerated -or $targetsIndex)) {
    $why = if ($targetsGenerated) { 'generated/** is published by the code repositories CI - fix the generator or the code, never the artifact' } else { 'index.md files are built by scripts/build-index.ps1 - run it instead of editing' }
    Write-Output (@{ permissionDecision = 'deny'; permissionDecisionReason = $why } | ConvertTo-Json -Compress)
    exit 0
}
Write-Output (@{ permissionDecision = 'allow' } | ConvertTo-Json -Compress)
