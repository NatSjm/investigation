<#
.SYNOPSIS
  STUB — exports a Confluence space/page tree to confluence-import/<space>/*.md.
.NOTES
  Intended flow:
    GET /wiki/rest/api/content?spaceKey=X&type=page&expand=body.storage,version,ancestors&limit=50 (paginate)
    → save body.storage HTML → pandoc -f html -t gfm → prepend frontmatter (confluence_id, title, last_modified, url)
    → strip images that are attachments (list them in frontmatter `attachments:` for manual review).
#>
param([Parameter(Mandatory)][string]$SpaceKey, [string]$RootPageId)
Write-Host "STUB: would export space $SpaceKey (root $RootPageId) from $env:CONFLUENCE_URL"
