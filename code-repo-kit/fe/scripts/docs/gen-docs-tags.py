#!/usr/bin/env python3
"""Traceability index: every KDoc/JSDoc `@docs <ID>` tag -> declaration signature + first summary line + file:line.
Lets agents jump from a spec ID (P1-001, monthly_projection) straight to the code without searching."""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header,
                     escape_cell, first_doc_line, split_list, sort_key, under, load_config, utf8_stdout)

# KDoc/JSDoc block followed by the declaration line (annotations skipped)
RX = re.compile(r'/\*\*(?P<doc>.*?)\*/\s*(?:@\w+(?:\([^)]*\))?\s*)*'
                r'(?P<decl>[^\r\n{=]*?(?:fun|class|object|interface|function|const|export)\s[^\r\n{=]*)', re.S)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/docs-tags.md')
    ap.add_argument('--include', nargs='+', default=['*.kt', '*.java', '*.ts', '*.tsx'])
    ap.add_argument('--config', default='', help='docs-gen.json; its exclude_paths (generated clients) are skipped')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    include = split_list(a.include)
    excluded = [os.path.join(root, p) for p in load_config(root, {'exclude_paths': []}, a.config)['exclude_paths']]

    rows = []
    for f in source_files(root, include):
        if under(f, excluded):
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
