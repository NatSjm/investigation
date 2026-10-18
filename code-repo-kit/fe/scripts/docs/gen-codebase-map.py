#!/usr/bin/env python3
"""Page map for a React/TS repo organised as <pages_dir>/<Page>/{<Page>.tsx, hook/, components/<C>/}: one row per page
with its purpose (first JSDoc line of the page component), entry file, component and hook names, API calls and browser
channels (BroadcastChannel: defines / pub / sub). Folders listed in `not_pages` (e.g. `shared`) get one row each, and
one `fe-app` row covers the app shell (`app_dirs`: routing, layouts, channel modules) so its channel usage is visible.
Layout keys come from docs-gen.json (see _common.load_config).

Channels: a file containing `new BroadcastChannel(` is a channel module; its channel name comes from a `*CHANNEL*`
string constant in that file (else the literal passed to the constructor, else the file name) and gets the suffix
`.{*}` when the constructor argument is not a literal (one channel per session etc.). A file that imports from a
channel module is a channel hook module. A page `pub`lishes when it imports a symbol matching /publish/i from a channel
or channel hook module, `sub`scribes for /subscri/i; the row whose folder holds the channel module `defines` it."""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files_cfg, resolve_out, rel_path, header, escape_cell,
                     unique, sort_key, under, load_config, utf8_stdout)

DEFAULTS = {
    'pages_dir': 'src/pages', 'not_pages': ['shared'], 'page_entry': ['<Page>.tsx', 'index.tsx', 'index.ts'],
    'hook_dirs': ['hook', 'hooks', 'api'], 'components_dir': 'components',
    'app_dirs': ['src/routing', 'src/components/layout', 'src/App.tsx', 'src/main.tsx'],
    'exclude_paths': [], 'test_pattern': r'\.(test|spec|stories)\.',
    'api_call_pattern': r'(?:fetch|axios\.\w+|api\.\w+)\(\s*(?:`([^`]*)`|[\'"]([^\'"]*)[\'"])',
}


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--config', default='', help='docs-gen.json (default: scripts/docs/docs-gen.json of the repo)')
    ap.add_argument('--out', default='docs/_generated/codebase-map.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    pages_dir = cfg['pages_dir']
    pages_root = os.path.join(root, pages_dir)
    if not os.path.isdir(pages_root):
        raise SystemExit(f'No {pages_dir} under {root} (set pages_dir in docs-gen.json)')
    excluded = [os.path.join(root, p) for p in cfg['exclude_paths']]
    api_rx = re.compile(cfg['api_call_pattern'])

    def src(d):
        return source_files_cfg(d, ['*.ts', '*.tsx'], cfg['test_pattern'], excluded)

    def key_of(f):
        return re.sub(r'\.(ts|tsx)$', '', rel_path(root, f), flags=re.I)

    # ---- browser channels (BroadcastChannel) ----
    channel_modules = {}   # module key (repo-relative path without extension) -> channel name
    for f in src(os.path.join(root, 'src')):
        t = read_text(f)
        if not re.search(r'new\s+BroadcastChannel\(', t, re.I):
            continue
        m1 = re.search(r'(?m)^\s*(?:export\s+)?const\s+\w*CHANNEL\w*\s*=\s*[\'"]([\w.-]+)[\'"]', t, re.I)
        m2 = re.search(r'new\s+BroadcastChannel\(\s*[\'"]([\w.-]+)[\'"]', t, re.I)
        name = m1.group(1) if m1 else m2.group(1) if m2 else os.path.splitext(os.path.basename(f))[0]
        if not re.search(r'new\s+BroadcastChannel\(\s*[\'"]', t, re.I):
            name += '.{*}'
        channel_modules[key_of(f)] = name

    def resolve_import(from_file, spec):
        # repo-relative module key for a relative or '@/' import, '' otherwise
        if spec.startswith('@/'):
            return re.sub(r'/index$', '', 'src/' + spec[2:], flags=re.I)
        if not spec.startswith('.'):
            return ''
        d = os.path.dirname(os.path.join(root, from_file))
        return re.sub(r'/index$', '', re.sub(r'\.(ts|tsx)$', '', rel_path(root, os.path.normpath(os.path.join(d, spec))), flags=re.I), flags=re.I)

    def imports_of(f):
        t = read_text(f)
        for m in re.finditer(r'(?m)^import\s+(?:type\s+)?\{([^}]*)\}\s+from\s+[\'"]([^\'"]+)[\'"]', t):
            syms = [re.sub(r'\s+as\s+.*', '', s, flags=re.I).strip() for s in m.group(1).split(',')]
            yield resolve_import(rel_path(root, f), m.group(2)), syms

    def module_of(target):
        return next((k for k in channel_modules if k == target or re.sub(r'/[^/]+$', '', k) == target), None)

    # channel hook modules: files importing anything from a channel module (hooks folder, barrels)
    channel_hooks = {}
    if channel_modules:
        for f in src(os.path.join(root, 'src')):
            if key_of(f) in channel_modules:
                continue
            for target, _ in imports_of(f):
                tk = module_of(target)
                if tk:
                    channel_hooks[key_of(f)] = channel_modules[tk]
                    break

    def channel_usage(files):
        uses = []
        if not channel_modules:
            return uses
        for f in files:
            key = key_of(f)
            if key in channel_modules:
                uses.append(f'defines {channel_modules[key]} ({rel_path(root, f)})')
                continue
            for target, syms in imports_of(f):
                tk = module_of(target)
                cname = channel_modules[tk] if tk else channel_hooks.get(target) or channel_hooks.get(target + '/index')
                if not cname:
                    continue
                if any(re.search('publish', s, re.I) for s in syms):
                    uses.append(f'pub {cname}')
                if any(re.search('subscri', s, re.I) for s in syms):
                    uses.append(f'sub {cname}')
        return unique(uses)

    def api_calls(files):
        apis = set()
        for f in files:
            for m in api_rx.finditer(read_text(f)):
                u = next((g for g in m.groups() if g is not None), '')
                apis.add(re.sub(r'\$\{[^}]+\}', '{*}', re.sub(r'\$\{BASE\}', '<BASE>', u, flags=re.I)))
        return sorted(apis, key=sort_key)

    def entry_of(d_full, page):
        for pat in cfg['page_entry']:
            cand = pat.replace('<Page>', page)
            if os.path.isfile(os.path.join(d_full, cand)):
                return cand
        return ''

    def first_sentence(doc):
        # first paragraph of the JSDoc (up to a blank line or the first @tag), cut after the first sentence
        lines = []
        for line in re.split(r'\r?\n', doc):
            s = re.sub(r'^\s*\*\s?', '', line).strip()
            if not s or s.startswith('@'):
                if lines:
                    break
                continue
            lines.append(s)
        text = ' '.join(lines)
        m = re.match(r'(.*?[.!?])(?:\s|$)', text)
        return (m.group(1) if m else text).strip()

    def purpose_of(entry_full, page):
        t = read_text(entry_full)
        m = re.search(r'(?s)/\*\*((?:(?!\*/).)*)\*/\s*export\s+(?:default\s+)?(?:function|const)\s+' + re.escape(page) + r'\b', t)
        if not m:
            m = re.search(r'(?s)/\*\*(.*?)\*/', t)
        return first_sentence(m.group(1)) if m else ''

    def names(files, folder, pattern, strip_ext=True):
        out = []
        for f in files:
            rel = rel_path(os.path.join(root, pages_dir), f)
            parts = rel.split('/')
            if folder in parts[1:-1]:
                i = parts.index(folder)
                nxt = parts[i + 1]
                nm = nxt if i + 1 < len(parts) - 1 else re.sub(r'\.(ts|tsx)$', '', nxt)
                if re.match(pattern, nm):
                    out.append(nm)
        return unique(sorted(out, key=sort_key))

    rows = []
    for d in sorted((x for x in os.listdir(pages_root) if os.path.isdir(os.path.join(pages_root, x))), key=sort_key):
        d_full = os.path.join(pages_root, d)
        files = src(d_full)
        is_page = d not in cfg['not_pages']
        entry = entry_of(d_full, d) if is_page else ''
        desc = purpose_of(os.path.join(d_full, entry), d) if entry else ('' if is_page else 'pieces shared by several pages')
        comps = names(files, cfg['components_dir'], r'^[A-Z]\w*$')
        hooks = unique(sorted((re.sub(r'\.(ts|tsx)$', '', os.path.basename(f)) for f in files
                               if re.match(r'^use[A-Z]', os.path.basename(f)) and os.path.basename(os.path.dirname(f)) in cfg['hook_dirs']), key=sort_key))
        rows.append({'Page': d, 'Desc': desc, 'Files': len(files), 'Components': ', '.join(comps), 'Hooks': ', '.join(hooks),
                     'Apis': '<br>'.join(api_calls(files)), 'Channels': '<br>'.join(channel_usage(files)),
                     'Entry': f'{pages_dir}/{d}/{entry}' if entry else f'{pages_dir}/{d}' + ('/-' if is_page else '')})
    # app shell row (routing, layouts, channel modules): API calls and channel usage matter here
    app_files = []
    for p in cfg['app_dirs']:
        full = os.path.join(root, p)
        if os.path.isdir(full):
            app_files += src(full)
        elif os.path.isfile(full) and not under(full, excluded):
            app_files.append(full)
    if app_files:
        rows.append({'Page': 'fe-app', 'Desc': 'app shell: routing, layouts, providers, channel modules', 'Files': len(app_files),
                     'Components': ', '.join(unique(sorted((re.sub(r'\.tsx$', '', os.path.basename(f)) for f in app_files if f.lower().endswith('.tsx') and re.match(r'^[A-Z]', os.path.basename(f))), key=sort_key))),
                     'Hooks': ', '.join(unique(sorted((re.sub(r'\.tsx?$', '', os.path.basename(f)) for f in app_files if re.match(r'^use[A-Z]', os.path.basename(f))), key=sort_key))),
                     'Apis': '<br>'.join(api_calls(app_files)), 'Channels': '<br>'.join(channel_usage(app_files)),
                     'Entry': next((p for p in cfg['app_dirs'] if os.path.isfile(os.path.join(root, p))), cfg['app_dirs'][0])})

    sb = [header('Codebase map (FE)', f'{pages_dir}/<Page>/ + {", ".join(cfg["app_dirs"][:2])}')]
    sb.append('One row per page folder: read the page component (entry) and its hooks first; open components only for UI-level questions. '
              f'`{"`, `".join(cfg["not_pages"])}` hold pieces shared by several pages; `fe-app` is the app shell.\n')
    sb.append('Channels = browser `BroadcastChannel`s (`defines` / `pub` / `sub`), the FE counterpart of Kafka topics; the shared component library is in `components.md`.\n\n')
    sb.append('| Page | Purpose | Entry | Files | Components | Hooks | API calls | Channels |\n|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        sb.append(f"| `{r['Page']}` | {escape_cell(r['Desc'])} | `{r['Entry']}` | {r['Files']} | {escape_cell(r['Components'])} | {escape_cell(r['Hooks'])} | {r['Apis']} | {r['Channels']} |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'codebase-map: {len(rows)} row(s) -> {a.out}')


if __name__ == '__main__':
    main()
