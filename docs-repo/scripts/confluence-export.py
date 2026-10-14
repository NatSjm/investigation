#!/usr/bin/env python3
"""STUB - exports a Confluence space/page tree to confluence-import/<space>/*.md.

Intended flow:
  GET /wiki/rest/api/content?spaceKey=X&type=page&expand=body.storage,version,ancestors&limit=50 (paginate)
  -> save body.storage HTML -> pandoc -f html -t gfm -> prepend frontmatter (confluence_id, title, last_modified, url)
  -> strip images that are attachments (list them in frontmatter `attachments:` for manual review)."""
import argparse
import os


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--space-key', required=True)
    ap.add_argument('--root-page-id', default='')
    a = ap.parse_args()
    print(f"STUB: would export space {a.space_key} (root {a.root_page_id}) from {os.environ.get('CONFLUENCE_URL', '')}")


if __name__ == '__main__':
    main()
