#!/usr/bin/env python3
"""Exported TypeScript types/interfaces index (names + fields, no implementation) - the cheapest FE context for agents."""
import argparse
import os
import re

from _common import read_text, write_text, source_files, resolve_out, rel_path, header, sort_key, utf8_stdout

DECL_RX = re.compile(r'(?ms)^export\s+(?:interface|type|enum)\s+\w+[^{;=]*(?:\{[^{}\r\n]*\}|\{.*?^\}|=[^;]*;)')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/types-index.md')
    ap.add_argument('--pattern', default='*.types.ts')
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    sb = [header('Types index (FE)', a.pattern)]
    sb.append('Exported `interface`/`type` declarations verbatim (types only, ~1 line per field). Mirrors BE DTOs - compare with `api-index.md`.\n\n')
    count = 0
    for f in sorted(source_files(root, [a.pattern]), key=sort_key):
        t = read_text(f)
        rel = rel_path(root, f)
        decls = list(DECL_RX.finditer(t))
        if not decls:
            continue
        sb.append(f'## `{rel}`\n```ts\n')
        for d in decls:
            v = re.sub(r'(?m)^\s*$\r?\n', '', re.sub(r'(?m)^\s*//.*$', '', d.group(0)))
            sb.append(v.rstrip() + '\n')
            count += 1
        sb.append('```\n\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'types-index: {count} declaration(s) -> {a.out}')


if __name__ == '__main__':
    main()
