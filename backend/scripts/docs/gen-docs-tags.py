#!/usr/bin/env python3
"""Traceability index: every KDoc/JSDoc `@docs <ID>` tag -> declaration signature + first summary line + file:line.
Lets agents jump from a spec ID (P1-001, monthly_projection) straight to the code without searching.
Files scanned: `docs_tags_include` patterns (docs-gen.json, default *.kt *.java) under the whole repository minus
`exclude_paths`; `--include` overrides the patterns."""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header,
                     escape_cell, first_doc_line, split_list, sort_key, utf8_stdout, load_config, under)

# KDoc/JSDoc block followed by the declaration line (annotations skipped)
RX = re.compile(r'/\*\*(?P<doc>.*?)\*/\s*(?:@\w+(?:\([^)]*\))?\s*)*'
                r'(?P<decl>[^\r\n{=]*?(?:fun|class|object|interface|function|const|export)\s[^\r\n{=]*)', re.S)
DEFAULTS = {'docs_tags_include': ['*.kt', '*.java'], 'exclude_paths': []}


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/docs-tags.md')
    ap.add_argument('--config', default='')
    ap.add_argument('--include', nargs='+', default=[])
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    include = split_list(a.include) or cfg['docs_tags_include']
    excl = [os.path.join(root, p) for p in cfg['exclude_paths']]

    rows = []
    for f in source_files(root, include):
        if under(f, excl):
            continue
        t = read_text(f)
        if not re.search(r'@docs\s', t, re.I):
            continue
        rel = rel_path(root, f)
        for m in RX.finditer(t):
            doc = m.group('doc')
            ids = re.findall(r'@docs\s+([\w.-]+)', doc)
            if not ids:
                continue
            summary = first_doc_line(doc, drop=r'@docs\s+[\w.-]+')
            decl = re.sub(r'\s+', ' ', m.group('decl')).strip()
            if re.match(r'^export(\s+type)?$', decl, re.I):
                decl = f'(module) {os.path.basename(f)}'
            for i in ids:
                rows.append((i, decl, summary, f"{rel}:{line_number(t, m.start('decl'))}"))

    sb = [header('Spec-to-code traceability (@docs tags)', '@docs <ID> tags in KDoc/JSDoc')]
    sb.append(f'{len(rows)} tag(s). Resolve a spec/calculation ID here, then open only the listed location.\n\n')
    sb.append('| Spec ID | Declaration | Summary | Location |\n|---|---|---|---|\n')
    for i, decl, summary, loc in sorted(rows, key=lambda r: (sort_key(r[0]), sort_key(r[3]))):
        sb.append(f'| `{i}` | `{escape_cell(decl)}` | {escape_cell(summary)} | `{loc}` |\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'docs-tags: {len(rows)} tag(s) -> {a.out}')


if __name__ == '__main__':
    main()
