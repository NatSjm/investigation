# Confluence import (quarantine)

Raw pages exported by `scripts/confluence-export.ps1` (Confluence REST → storage-format HTML → Markdown via
pandoc). Structure: `<space>/<page-title>.md` with frontmatter `confluence_id`, `title`, `last_modified`, `url`.

Workflow:
1. Export a space or page tree.
2. Run agent `confluence-migrator` per page (or per small batch).
3. Processed pages move to `_done/`; nothing here is authoritative.
4. After the space is fully migrated, Confluence pages are replaced by a banner + link to the published copy
   (`scripts/confluence-publish.ps1`).

Attachments are not imported automatically; screenshots containing client data must be dropped.
