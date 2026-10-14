#!/usr/bin/env python3
"""STUB - pushes work-items/<ID>.yml to Jira via REST v3 and writes back jira_key values.

Intended flow (no MCP needed):
  1. Parse YAML (pyyaml, or the line-based reader of validate-work-items.py).
  2. POST /rest/api/3/issue  { fields: { project, issuetype: Epic, summary, description(ADF), labels } }
  3. For each story: POST issue type Story with parent = epic key; description = spec link + AC in ADF.
  4. For each subtask: POST issue type Sub-task with parent = story key.
  5. Link depends_on via POST /rest/api/3/issueLink  { type: "Blocks" }.
  6. Write keys back into the YAML and commit (CI) or print (local).
Auth: Basic (JIRA_USER : JIRA_TOKEN) or Bearer PAT for Data Center.
Idempotency: skip creation when jira_key != null; PUT to update summary/description instead."""
import argparse
import os


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--file', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    print(f"STUB: would push {a.file} to {os.environ.get('JIRA_URL', '')} (DryRun={a.dry_run})")


if __name__ == '__main__':
    main()
