#!/usr/bin/env python3
"""STUB - copies test-design/features/*.feature and fixtures into the automated tests repo and opens a PR.

Intended flow:
  git clone --depth 1 $TESTS_REPO_URL tmp; git checkout -b docs/<FEATURE-ID>-<date>
  copy test-design/features/<ID>.feature -> tmp/src/test/resources/features/<ctx>/
  copy test-design/fixtures/<ID>-*.json  -> tmp/src/test/resources/fixtures/
  git commit; git push; open PR via GitHub/GitLab/Azure DevOps REST (token in $GIT_TOKEN)
The tests repo CI runs a "pending steps" check: unimplemented steps fail the PR with a list for the QA engineer."""
import argparse
import os


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--feature-id', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    print(f"STUB: would push {a.feature_id} test design to {os.environ.get('TESTS_REPO_URL', '')} (DryRun={a.dry_run})")


if __name__ == '__main__':
    main()
