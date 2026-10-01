<#
.SYNOPSIS
  STUB — copies test-design/features/*.feature and fixtures into the automated tests repo and opens a PR.
.NOTES
  Intended flow:
    git clone --depth 1 $env:TESTS_REPO_URL tmp; git checkout -b docs/<FEATURE-ID>-<date>
    Copy-Item test-design/features/<ID>.feature tmp/src/test/resources/features/<ctx>/
    Copy-Item test-design/fixtures/<ID>-*.json tmp/src/test/resources/fixtures/
    git commit; git push; open PR via GitHub/GitLab/Azure DevOps REST (token in $env:GIT_TOKEN)
  The tests repo CI runs a "pending steps" check: unimplemented steps fail the PR with a list for the QA engineer.
#>
param([Parameter(Mandatory)][string]$FeatureId, [switch]$DryRun)
Write-Host "STUB: would push $FeatureId test design to $env:TESTS_REPO_URL (DryRun=$DryRun)"
