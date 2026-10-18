#!/usr/bin/env python3
"""Route table from react-router usage (v6 object routes: `useRoutes([...])`, `createBrowserRouter([...])`, exported
`RouteObject` constants, and JSX `<Route path= element=>`). Understands `{ path, element: <X /> }` and
`{ path, Component: X }`, nested `children` with relative paths, `index: true`, pathless layout routes, route constants
(`ROUTES.X`, template literals around them) resolved from the files in `route_constants`, and route objects declared in
another file and referenced by name inside a `children` array (`children: [sessionRoutes, ...adminRoutes]`).
Layout keys (route_files, route_constants) come from docs-gen.json."""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files_cfg, resolve_out, rel_path, line_number, header, sort_key,
                     blank_comments, load_config, utf8_stdout)

DEFAULTS = {'route_files': ['src'], 'route_constants': [], 'exclude_paths': [], 'test_pattern': r'\.(test|spec|stories)\.'}

TOKEN_RX = re.compile(
    r'(?P<open>\{)|(?P<close>\})'
    r'|\bpath\s*:\s*(?P<path>\'[^\']*\'|"[^"]*"|`[^`]*`|[\w.]+)'
    r'|\b(?:element|Component)\s*:\s*(?:<\s*)?(?P<comp>[\w.]+)'
    r'|\bindex\s*:\s*(?P<index>true)'
    r'|(?<=[\[,])\s*(?:\.\.\.)?(?P<ref>[A-Za-z_]\w*)\s*(?=[,\]])'
    r'|\bexport\s+const\s+(?P<decl>\w+)\s*(?::[^=]+)?=(?=\s*[\[{])'
)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--config', default='')
    ap.add_argument('--out', default='docs/_generated/routes.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    excluded = [os.path.join(root, p) for p in cfg['exclude_paths']]

    # ---- route constants: NAME.KEY -> '/path' ----
    consts = {}
    for p in cfg['route_constants']:
        full = os.path.join(root, p)
        if not os.path.isfile(full):
            continue
        t = blank_comments(read_text(full))
        for m in re.finditer(r'(?s)export\s+const\s+(\w+)\s*(?::[^=]+)?=\s*\{(.*?)\n\}', t):
            for km in re.finditer(r'(?m)^\s*(\w+)\s*:\s*[\'"`]([^\'"`]*)[\'"`]', m.group(2)):
                consts[f'{m.group(1)}.{km.group(1)}'] = km.group(2)

    def value_of(raw):
        if raw[0] in '\'"':
            return raw[1:-1]
        if raw[0] == '`':
            return re.sub(r'\$\{([\w.]+)\}', lambda mm: consts.get(mm.group(1), '{' + mm.group(1) + '}'), raw[1:-1])
        return consts.get(raw, '{' + raw + '}')

    # ---- parse every route file into trees ----
    files = []
    for p in cfg['route_files']:
        full = os.path.join(root, p)
        if os.path.isdir(full):
            files += source_files_cfg(full, ['*.tsx', '*.ts'], cfg['test_pattern'], excluded)
        elif os.path.isfile(full):
            files.append(full)
    by_var = {}      # exported const name -> root-level nodes it holds
    all_roots = []   # (file, nodes) for files with route objects
    jsx_rows = []
    for f in files:
        raw = read_text(f)
        if not re.search(r'\bpath\s*[:=]', raw):
            continue
        t = blank_comments(raw)
        rel = rel_path(root, f)
        for m in re.finditer(r'<Route\s+[^>]*?path=[\'"]([^\'"]+)[\'"][^>]*?element=\{<(\w+)', t):
            jsx_rows.append((m.group(1), m.group(2), '', f'{rel}:{line_number(t, m.start())}'))
        root_node = {'path': None, 'comp': None, 'index': False, 'children': [], 'refs': [], 'pos': 0, 'file': rel, 'var': None}
        stack = [root_node]
        decl = None
        for m in TOKEN_RX.finditer(t):
            top = stack[-1]
            if m.group('decl'):
                decl = m.group('decl')
            elif m.group('open'):
                node = {'path': None, 'comp': None, 'index': False, 'children': [], 'refs': [], 'pos': m.start(), 'file': rel, 'var': decl if top is root_node else None}
                stack.append(node)
            elif m.group('close'):
                if len(stack) > 1:
                    node = stack.pop()
                    stack[-1]['children'].append(node)
            elif m.group('path'):
                top['path'] = value_of(m.group('path'))
            elif m.group('comp'):
                top['comp'] = m.group('comp')
            elif m.group('index'):
                top['index'] = True
            elif m.group('ref'):
                top['refs'].append((m.group('ref'), m.start()))
        for n in root_node['children']:
            if n['var']:
                by_var.setdefault(n['var'], []).append(n)
        all_roots.append(root_node)

    rows = []

    def join(parent, child):
        if child is None:
            return parent
        if child.startswith('/'):
            return child
        return (parent.rstrip('/') + '/' + child) if parent else child

    def walk(node, parent_full, layout, seen):
        full = parent_full if node['index'] else join(parent_full, node['path'])
        if node['path'] is not None or node['index']:
            rows.append((full or '/', node['comp'] or '-', layout or '', f"{node['file']}:{line_number(read_text(os.path.join(root, node['file'])), node['pos'])}"))
            next_layout = node['comp'] if node['children'] or node['refs'] else layout
        else:
            next_layout = node['comp'] or layout
        for c in node['children']:
            walk(c, full, next_layout, seen)
        for name, _ in node['refs']:
            for ref in by_var.get(name, []):
                if id(ref) in seen:
                    continue
                walk(ref, full, next_layout, seen | {id(ref)})

    referenced = {id(n) for nodes in by_var.values() for n in nodes}
    for root_node in all_roots:
        for n in root_node['children']:
            if id(n) in referenced:
                continue    # rendered where it is referenced (children: [sessionRoutes])
            walk(n, '', '', set())
        for name, _ in root_node['refs']:
            for ref in by_var.get(name, []):
                walk(ref, '', '', {id(ref)})
    # exported route objects nobody references (a file-local table still counts)
    for name, nodes in by_var.items():
        for n in nodes:
            if not any(name == r for rn in all_roots for r, _ in rn['refs']) and not any(name == r for rn in all_roots for c in rn['children'] for r, _ in c['refs']):
                if not any(loc.startswith(n['file'] + ':') and p for p, _, _, loc in rows):
                    walk(n, '', '', {id(n)})
    rows += jsx_rows
    rows = sorted(set(rows), key=lambda r: (sort_key(r[0]), sort_key(r[3])))

    sb = [header('Routes (FE)', 'react-router route objects / <Route> elements')]
    sb.append(f'{len(rows)} route(s). Child paths are joined to their parent; `Layout` is the nearest enclosing pathless or parent element. Component -> page: the page folder of the same name in codebase-map.md.\n\n')
    sb.append('| Path | Component | Layout | Location |\n|---|---|---|---|\n')
    for path, comp, layout, loc in rows:
        sb.append(f'| `{path}` | `{comp}` | {("`" + layout + "`") if layout else ""} | `{loc}` |\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'routes: {len(rows)} route(s) -> {a.out}')


if __name__ == '__main__':
    main()
