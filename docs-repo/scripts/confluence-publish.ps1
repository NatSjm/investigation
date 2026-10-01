<#
.SYNOPSIS
  STUB — publishes Markdown docs to Confluence (one-way; repo wins).
.NOTES
  Intended flow:
    1. Convert Markdown → Confluence storage format (pandoc -t html, then wrap; Mermaid blocks → rendered PNG via
       mermaid-cli in CI, or keep as code macro if the Mermaid Confluence app is installed).
    2. Lookup page id in .confluence-map.json (path → pageId); if missing, POST /wiki/rest/api/content.
    3. PUT /wiki/rest/api/content/{id} with version+1; add banner macro
       "Managed in Git — edit at <repo url>; changes here will be overwritten".
    4. Update ancestors according to folder structure (architecture/, features/<ctx>/ ...).
    5. Language: the repo is English. -Lang en publishes the English mirror (default). -Lang cs asks Copilot
       (prompt translate-for-publish, glossary-controlled) to produce a Czech rendering into .publish/cs/<path>.md,
       publishes that page with the banner "Machine-translated from the English source in Git - English is
       authoritative; do not edit here", and keeps the English page as a child/link. Translations are never
       committed to the bundle - they are build artifacts.
  Run from CI on merge to main, only for files changed in the merge.
#>
param([string[]]$Files, [switch]$DryRun, [ValidateSet('en','cs')][string]$Lang = 'en')
Write-Host "STUB: would publish $($Files.Count) file(s) in '$Lang' to $env:CONFLUENCE_URL (DryRun=$DryRun)"
