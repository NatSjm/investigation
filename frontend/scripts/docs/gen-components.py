#!/usr/bin/env python3
"""Component library map for a React/TS repo: one row per exported component under <shared_dir>/** (the in-house UI
library: tables, modals, charts, form controls, layouts) with its props (names from the `<Name>Props` interface), the
first JSDoc line, the pages that render it and file:line. Lets an analyst or a coding agent name the library component
a story should use, and lets the graph link pages to the shared components they depend on.
Layout keys (shared_dir, pages_dir, app_dirs, ...) come from docs-gen.json.
Example: python3 scripts/docs/gen-components.py --root . --out docs/_generated/components.md"""
import argparse
import os
import re

from _common import (read_text, write_text, source_files_cfg, resolve_out, rel_path, line_number, header, escape_cell,
                     first_doc_line, sort_key, load_config, utf8_stdout)

DEFAULTS = {
    'pages_dir': 'src/pages', 'shared_dir': 'src/components', 'app_dirs': ['src/routing', 'src/App.tsx'],
    'exclude_paths': [], 'test_pattern': r'\.(test|spec|stories)\.',
}
# exported components: `export function Name(` / `export const Name = (` / `export const Name: React.FC` with a capitalised name
COMP_RX = re.compile(r'(?m)^export\s+(?:default\s+)?(?:function\s+([A-Z]\w*)\s*(?:<[^>]*>)?\s*\(|const\s+([A-Z]\w*)\s*(?::\s*[^=]+)?=\s*(?:React\.)?(?:memo\()?(?:forwardRef\()?\s*(?:\([^)]*\)|\w+)\s*=>|const\s+([A-Z]\w*)\s*:\s*(?:React\.)?FC\b)')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--config', default='')
    ap.add_argument('--out', default='docs/_generated/components.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    shared_dir = cfg['shared_dir']
    shared_root = os.path.join(root, shared_dir)
    if not os.path.isdir(shared_root):
        raise SystemExit(f'No {shared_dir} under {root} (set shared_dir in docs-gen.json)')
    excluded = [os.path.join(root, p) for p in cfg['exclude_paths']]

    def src(d):
        return source_files_cfg(d, ['*.ts', '*.tsx'], cfg['test_pattern'], excluded)

    # usage index: component name -> pages whose files reference `<Name` (JSX) or `Name(` (render helpers)
    page_texts = {}
    pages_root = os.path.join(root, cfg['pages_dir'])
    if os.path.isdir(pages_root):
        for d in sorted((x for x in os.listdir(pages_root) if os.path.isdir(os.path.join(pages_root, x))), key=str.lower):
            page_texts[d] = [read_text(f) for f in src(os.path.join(pages_root, d))]
    app_texts = []
    for p in cfg['app_dirs']:
        full = os.path.join(root, p)
        if os.path.isdir(full) and not full.lower().startswith(os.path.abspath(shared_root).lower()):
            app_texts += [read_text(f) for f in src(full)]
        elif os.path.isfile(full):
            app_texts.append(read_text(full))
    if app_texts:
        page_texts['fe-app'] = app_texts

    rows = []
    files = [f for f in src(shared_root) if not re.match(r'^index\.', os.path.basename(f), re.I)]
    for f in files:
        t = read_text(f)
        rel = rel_path(root, f)
        inner = re.sub('^' + re.escape(shared_dir) + '/', '', rel, flags=re.I).split('/')
        group = inner[0] if len(inner) > 1 else ''
        for m in COMP_RX.finditer(t):
            name = next((g for g in (m.group(1), m.group(2), m.group(3)) if g), None)
            if not name:
                continue
            props = []
            pm = re.search(r'(?s)(?:interface|type)\s+' + re.escape(name) + r'Props(?:<[^>]*>)?\s*(?:=\s*)?\{(.*?)\n\}', t)
            if pm:
                props = re.findall(r'(?m)^\s*(\w+\??)\s*:', pm.group(1))
            else:
                dm = re.search(r'\(\s*\{([^}]*)\}', m.group(0), re.I)
                if dm:
                    props = [x for x in (re.sub(r':.*$', '', re.sub(r'=.*$', '', p)).strip() for p in dm.group(1).split(',')) if x]
            before = t[:m.start()]
            doc = ''
            jd = re.search(r'(?s)/\*\*((?:(?!\*/).)*)\*/\s*$', before)
            if jd:
                doc = first_doc_line(jd.group(1), drop=r'@docs\s+[\w.-]+')
            used_by = sorted((pg for pg, texts in page_texts.items()
                              if any(re.search('<' + re.escape(name) + r'\b', x) or re.search(r'\b' + re.escape(name) + r'\(', x) for x in texts)),
                             key=sort_key)
            rows.append({'Name': name, 'Group': group if group != name else '-', 'Doc': doc, 'Props': props, 'UsedBy': used_by,
                         'Loc': f'{rel}:{line_number(t, m.start())}'})

    sb = [header('Component library (FE)', f'{shared_dir}/** exported components',
                 'One row per shared UI component: props, purpose, which pages render it, file:line; name these in stories instead of inventing new components.')]
    sb.append(f'{len(rows)} component(s) under `{shared_dir}/`. Pages must compose these; a new shared component is a change to this library, not to a page.\n\n')
    sb.append('| Component | Group | Purpose | Props | Used by | Location |\n|---|---|---|---|---|---|\n')
    for r in sorted(rows, key=lambda r: (sort_key(r['Group']), sort_key(r['Name']))):
        props = ', '.join('`' + p + '`' for p in r['Props'])
        used = ', '.join('`' + u + '`' for u in r['UsedBy']) if r['UsedBy'] else '_unused_'
        sb.append(f"| `{r['Name']}` | {r['Group']} | {escape_cell(r['Doc'])} | {props} | {used} | `{r['Loc']}` |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'components: {len(rows)} component(s) -> {a.out}')


if __name__ == '__main__':
    main()
