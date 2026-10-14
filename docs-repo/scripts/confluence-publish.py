#!/usr/bin/env python3
"""STUB - publishes Markdown docs to Confluence (one-way; repo wins).

Intended flow:
  1. Convert Markdown -> Confluence storage format (pandoc -t html, then wrap; Mermaid blocks -> rendered PNG via
     mermaid-cli in CI, or keep as code macro if the Mermaid Confluence app is installed).
  2. Lookup page id in .confluence-map.json (path -> pageId); if missing, POST /wiki/rest/api/content.
  3. PUT /wiki/rest/api/content/{id} with version+1; add banner macro
     "Managed in Git - edit at <repo url>; changes here will be overwritten".
  4. Update ancestors according to folder structure (architecture/, features/<ctx>/ ...).
  5. Language: the repo is English. --lang en publishes the English mirror (default). --lang <code> asks Copilot
     (prompt translate-for-publish, glossary-controlled) to produce a rendering in the target language into .publish/<lang>/<path>.md,
     publishes that page with the banner "Machine-translated from the English source in Git - English is
     authoritative; do not edit here", and keeps the English page as a child/link. Translations are never
     committed to the bundle - they are build artifacts.
Run from CI on merge to main, only for files changed in the merge."""
import argparse
import os


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--files', nargs='*', default=[])
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--lang', default='en')
    a = ap.parse_args()
    files = [x for v in a.files for x in v.split(',') if x.strip()]
    print(f"STUB: would publish {len(files)} file(s) in '{a.lang}' to {os.environ.get('CONFLUENCE_URL', '')} (DryRun={a.dry_run})")


if __name__ == '__main__':
    main()
