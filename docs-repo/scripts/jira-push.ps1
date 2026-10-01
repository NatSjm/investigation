<#
.SYNOPSIS
  STUB — pushes work-items/<ID>.yml to Jira via REST v3 and writes back jira_key values.
.NOTES
  Intended flow (no MCP needed):
    1. Parse YAML (powershell-yaml module or ConvertFrom-Yaml in pwsh 7.4+).
    2. POST /rest/api/3/issue  { fields: { project, issuetype: Epic, summary, description(ADF), labels } }
    3. For each story: POST issue type Story with parent = epic key; description = spec link + AC in ADF.
    4. For each subtask: POST issue type Sub-task with parent = story key.
    5. Link depends_on via POST /rest/api/3/issueLink  { type: "Blocks" }.
    6. Write keys back into the YAML and commit (CI) or print (local).
  Auth: Basic ($env:JIRA_USER : $env:JIRA_TOKEN) or Bearer PAT for Data Center.
  Idempotency: skip creation when jira_key != null; PUT to update summary/description instead.
#>
param([Parameter(Mandatory)][string]$File, [switch]$DryRun)
Write-Host "STUB: would push $File to $env:JIRA_URL (DryRun=$DryRun)"
