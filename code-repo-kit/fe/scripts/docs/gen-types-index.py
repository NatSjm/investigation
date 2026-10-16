#!/usr/bin/env python3
"""Exported TypeScript types/interfaces index (names + fields, no implementation) - the cheapest FE context for agents.
Files come from the `types` globs of docs-gen.json (e.g. src/types/**/*.ts, src/pages/**/*.types.ts); generated clients
listed in `exclude_paths` are never read. `--pattern` overrides the globs for one run."""
import argparse
import os
import re

from _common import (read_text, write_text, source_files_cfg, resolve_out, rel_path, header, sort_key, glob_match,
                     load_config, utf8_stdout)

DEFAULTS = {'types': ['src/types/**/*.ts', 'src/**/*.types.ts'], 'exclude_paths': [], 'test_pattern': r'\.(test|spec|stories)\.'}
DECL_RX = re.compile(r'(?ms)^export\s+(?:interface|type|enum)\s+\w+[^{;=]*(?:\{[^{}\r\n]*\}|\{.*?^\}|=[^;]*;)')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--config', default='')
    ap.add_argument('--out', default='docs/_generated/types-index.md')
    ap.add_argument('--pattern', nargs='*', default=[], help='repo-relative globs; default: the `types` list of docs-gen.json')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    patterns = a.pattern or cfg['types']
    excluded = [os.path.join(root, p) for p in cfg['exclude_paths']]

    sb = [header('Types index (FE)', ', '.join(patterns))]
    sb.append('Exported `interface`/`type` declarations verbatim (types only, ~1 line per field). Mirrors BE DTOs - compare with `api-index.md`.\n\n')
    count = 0
    files = [f for f in source_files_cfg(os.path.join(root, 'src'), ['*.ts', '*.tsx'], cfg['test_pattern'], excluded)
             if any(glob_match(rel_path(root, f), p) for p in patterns) and not f.lower().endswith('.d.ts')]
    for f in sorted(files, key=lambda f: sort_key(rel_path(root, f))):
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
