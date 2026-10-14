#!/usr/bin/env python3
"""Route table from react-router usage: object routes `{ path: '...', element: <X/> }` and JSX `<Route path="..." element={<X/>}>`."""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header, sort_key,
                     utf8_stdout)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/routes.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    rows = []
    for f in source_files(root, ['*.tsx', '*.ts']):
        if re.search(r'\.(test|spec)\.', os.path.basename(f), re.I):
            continue
        t = read_text(f)
        if not re.search(r'\bpath\s*[:=]', t, re.I):
            continue
        rel = rel_path(root, f)
        for m in re.finditer(r'path:\s*[\'"`]([^\'"`]+)[\'"`][^}]*?element:\s*<(\w+)', t):
            rows.append((m.group(1), m.group(2), f'{rel}:{line_number(t, m.start())}'))
        for m in re.finditer(r'<Route\s+[^>]*?path=[\'"]([^\'"]+)[\'"][^>]*?element=\{<(\w+)', t):
            rows.append((m.group(1), m.group(2), f'{rel}:{line_number(t, m.start())}'))

    sb = [header('Routes (FE)', 'react-router route objects / <Route> elements')]
    sb.append(f'{len(rows)} route(s). Component -> feature: see codebase-map.md public exports.\n\n')
    sb.append('| Path | Component | Location |\n|---|---|---|\n')
    for path, comp, loc in sorted(rows, key=lambda r: sort_key(r[0])):
        sb.append(f'| `{path}` | `{comp}` | `{loc}` |\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'routes: {len(rows)} route(s) -> {a.out}')


if __name__ == '__main__':
    main()
