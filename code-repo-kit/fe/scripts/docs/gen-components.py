#!/usr/bin/env python3
"""Component map for a React/TS repo, two tables. Library: one row per exported component under <shared_dir>/** (the
in-house UI library: tables, modals, charts, form controls, layouts) with its props (names from the `<Name>Props`
interface), the first JSDoc line, the pages that render it and file:line. Page components: one row per exported
component under <pages_dir>/<Page>/<components_dir>/** of every page folder (shared ones included) with its page, props,
first JSDoc line, where it is rendered (file:line of the JSX tag) and which of the repository's own hooks it calls.
Lets an analyst or a coding agent name the component a story should use and see which surface opens which, and lets
the graph link pages to the shared components they depend on.
Layout keys (shared_dir, pages_dir, components_dir, app_dirs, ...) come from docs-gen.json.
Example: python3 scripts/docs/gen-components.py --root . --out docs/_generated/components.md"""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files_cfg, resolve_out, rel_path, line_number, header, escape_cell,
                     first_doc_line, sort_key, load_config, utf8_stdout, blank_comments, ticks, under)

DEFAULTS = {
    'pages_dir': 'src/pages', 'components_dir': 'components', 'shared_dir': 'src/components',
    'app_dirs': ['src/routing', 'src/App.tsx'], 'exclude_paths': [], 'test_pattern': r'\.(test|spec|stories)\.',
}
# exported components: `export function Name(` / `export const Name = (` / `export const Name: React.FC` with a capitalised name
COMP_RX = re.compile(r'(?m)^export\s+(?:default\s+)?(?:function\s+([A-Z]\w*)\s*(?:<[^>]*>)?\s*\(|const\s+([A-Z]\w*)\s*(?::\s*[^=]+)?=\s*(?:React\.)?(?:memo\()?(?:forwardRef\()?\s*(?:\([^)]*\)|\w+)\s*=>|const\s+([A-Z]\w*)\s*:\s*(?:React\.)?FC\b)')
# the repository's own hooks: `export function useX(` / `export const useX`
HOOK_DEF_RX = re.compile(r'(?m)^export\s+(?:default\s+)?(?:async\s+)?(?:function\s+(use[A-Z]\w*)|const\s+(use[A-Z]\w*)\b)')
MAX_RENDERED_BY = 8


def components_of(t):
    """Exported components of one file as (name, props, first JSDoc line, start, end); end is where the next one starts."""
    ms = [m for m in COMP_RX.finditer(t) if any(m.groups())]
    out = []
    for i, m in enumerate(ms):
        name = next(g for g in m.groups() if g)
        props = []
        pm = re.search(r'(?s)(?:interface|type)\s+' + re.escape(name) + r'Props(?:<[^>]*>)?\s*(?:=\s*)?\{(.*?)\n\}', t)
        if pm:
            props = re.findall(r'(?m)^\s*(\w+\??)\s*:', pm.group(1))
        else:
            dm = re.search(r'\(\s*\{([^}]*)\}', m.group(0), re.I)
            if dm:
                props = [x for x in (re.sub(r':.*$', '', re.sub(r'=.*$', '', p)).strip() for p in dm.group(1).split(',')) if x]
        doc = ''
        jd = re.search(r'(?s)/\*\*((?:(?!\*/).)*)\*/\s*$', t[:m.start()])
        if jd:
            doc = first_doc_line(jd.group(1), drop=r'@docs\s+[\w.-]+')
        out.append((name, props, doc, m.start(), ms[i + 1].start() if i + 1 < len(ms) else len(t)))
    return out


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
    texts = {}

    def src(d):
        return source_files_cfg(d, ['*.ts', '*.tsx'], cfg['test_pattern'], excluded)

    def text_of(f):
        if f not in texts:
            texts[f] = read_text(f)
        return texts[f]

    # usage index: component name -> pages whose files reference `<Name` (JSX) or `Name(` (render helpers)
    page_files = {}
    pages_root = os.path.join(root, cfg['pages_dir'])
    if os.path.isdir(pages_root):
        for d in sorted((x for x in os.listdir(pages_root) if os.path.isdir(os.path.join(pages_root, x))), key=str.lower):
            page_files[d] = src(os.path.join(pages_root, d))
    app_files = []
    for p in cfg['app_dirs']:
        full = os.path.join(root, p)
        if os.path.isdir(full) and not full.lower().startswith(os.path.abspath(shared_root).lower()):
            app_files += src(full)
        elif os.path.isfile(full):
            app_files.append(full)
    page_texts = {pg: [text_of(f) for f in fs] for pg, fs in page_files.items()}
    if app_files:
        page_texts['fe-app'] = [text_of(f) for f in app_files]

    rows = []
    library = src(shared_root)
    files = [f for f in library if not re.match(r'^index\.', os.path.basename(f), re.I)]
    for f in files:
        t = text_of(f)
        rel = rel_path(root, f)
        inner = re.sub('^' + re.escape(shared_dir) + '/', '', rel, flags=re.I).split('/')
        group = inner[0] if len(inner) > 1 else ''
        for name, props, doc, start, _ in components_of(t):
            used_by = sorted((pg for pg, texts_ in page_texts.items()
                              if any(re.search('<' + re.escape(name) + r'\b', x) or re.search(r'\b' + re.escape(name) + r'\(', x) for x in texts_)),
                             key=sort_key)
            rows.append({'Name': name, 'Group': group if group != name else '-', 'Doc': doc, 'Props': props, 'UsedBy': used_by,
                         'Loc': f'{rel}:{line_number(t, start)}'})

    # page components: where each is rendered (the JSX tag, comments blanked, not inside its own definition) and the
    # repository's own hooks it calls - the surfaces of a page and which one opens which, without a TypeScript build
    scan = sorted({f for fs in page_files.values() for f in fs} | set(app_files) | set(library), key=lambda f: sort_key(rel_path(root, f)))
    code = {f: blank_comments(text_of(f)) for f in scan}
    own_hooks = {m.group(1) or m.group(2) for f in scan for m in HOOK_DEF_RX.finditer(code[f])}
    page_rows = []
    for page, fs in page_files.items():
        comp_root = os.path.join(pages_root, page, cfg['components_dir'])
        for f in fs:
            if re.match(r'^index\.', os.path.basename(f), re.I) or not under(f, [comp_root]):
                continue
            t = text_of(f)
            for name, props, doc, start, end in components_of(t):
                tag = re.compile(r'(?<![\w$.])<' + re.escape(name) + r'(?=[\s/>])')   # JSX, not a type argument
                rendered = []
                for g in scan:
                    for m in tag.finditer(code[g]):
                        if g == f and start <= m.start() < end:
                            continue
                        rendered.append(f'{rel_path(root, g)}:{line_number(code[g], m.start())}')
                        break
                hooks = sorted({h for h in re.findall(r'\b(use[A-Z]\w*)\s*\(', code[f][start:end]) if h in own_hooks}, key=sort_key)
                page_rows.append({'Name': name, 'Page': page, 'Doc': doc, 'Props': props, 'RenderedBy': rendered, 'Hooks': hooks,
                                  'Loc': f'{rel_path(root, f)}:{line_number(t, start)}'})

    pages_dir, components_dir = cfg['pages_dir'], cfg['components_dir']
    sb = [header('Components (FE)', f'{shared_dir}/** and {pages_dir}/*/{components_dir}/** exported components',
                 'One row per shared UI component (props, purpose, which pages render it, file:line), then one row per page component (where it is rendered, which hooks it calls); name these in stories instead of inventing new components.')]
    sb.append('\n## Library\n\n')
    sb.append(f'{len(rows)} component(s) under `{shared_dir}/`. Pages must compose these; a new shared component is a change to this library, not to a page.\n\n')
    sb.append('| Component | Group | Purpose | Props | Used by | Location |\n|---|---|---|---|---|---|\n')
    for r in sorted(rows, key=lambda r: (sort_key(r['Group']), sort_key(r['Name']))):
        props = ', '.join('`' + p + '`' for p in r['Props'])
        used = ', '.join('`' + u + '`' for u in r['UsedBy']) if r['UsedBy'] else '_unused_'
        sb.append(f"| `{r['Name']}` | {r['Group']} | {escape_cell(r['Doc'])} | {props} | {used} | `{r['Loc']}` |\n")
    # first column `Page component`, not `Component`: the docs repo's gen-graph.py reads every `Component` row as a
    # library component; page components reach the graph through the TypeScript exporter (graph-export-fe.json)
    sb.append('\n## Page components\n\n')
    sb.append(f'{len(page_rows)} component(s) in page folders (`{pages_dir}/<Page>/{components_dir}/`, shared folders included). '
              'Each belongs to its page. Rendered by: the file:line of the JSX tag that renders it, first per file, its own '
              'definition excluded; Hooks: the hooks of this repository it calls.\n\n')
    sb.append('| Page component | Page | Purpose | Props | Rendered by | Hooks | Location |\n|---|---|---|---|---|---|---|\n')
    for r in sorted(page_rows, key=lambda r: (sort_key(r['Page']), sort_key(r['Name']))):
        locs = ['`' + x + '`' for x in r['RenderedBy'][:MAX_RENDERED_BY]]
        if len(r['RenderedBy']) > MAX_RENDERED_BY:
            locs.append(f"(+{len(r['RenderedBy']) - MAX_RENDERED_BY} more)")
        rendered = '<br>'.join(locs) if locs else '_not rendered_'
        sb.append(f"| `{r['Name']}` | `{r['Page']}` | {escape_cell(r['Doc'])} | {ticks(r['Props'])} | {rendered} | {ticks(r['Hooks'])} | `{r['Loc']}` |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'components: {len(rows)} library + {len(page_rows)} page component(s) -> {a.out}')


if __name__ == '__main__':
    main()
