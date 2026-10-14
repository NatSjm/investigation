#!/usr/bin/env python3
"""preToolUse hook: denies edit/write tool calls that target generated/** (CI-owned) or index.md files
(built by scripts/build-index.py). Reads the hook payload from stdin, answers with a permission decision
on stdout, as described in the GitHub Copilot hooks reference (.github/hooks/*.json).
Best effort: the exact payload shape may differ per surface, so the check is a tolerant regex over the raw JSON."""
import json
import re
import sys


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ''
    is_edit = re.search(r'"(toolName|tool_name|name)"\s*:\s*"(edit|write|create|str_replace_editor|multi_edit|MultiEdit|Write|Edit)', raw, re.I) is not None
    targets_generated = re.search(r'(?i)"(path|file_path|filePath|uri)"\s*:\s*"[^"]*(^|[\\/])generated[\\/]', raw) is not None
    targets_index = re.search(r'(?i)"(path|file_path|filePath|uri)"\s*:\s*"[^"]*[\\/]index\.md"', raw) is not None
    if is_edit and (targets_generated or targets_index):
        why = ('generated/** is published by the code repositories CI - fix the generator or the code, never the artifact'
               if targets_generated else 'index.md files are built by scripts/build-index.py - run it instead of editing')
        print(json.dumps({'permissionDecision': 'deny', 'permissionDecisionReason': why}, separators=(',', ':')))
        return 0
    print(json.dumps({'permissionDecision': 'allow'}, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
