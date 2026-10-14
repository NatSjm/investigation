#!/usr/bin/env python3
"""Feature map for a React/TS repo organised as src/features/<name>: purpose (from @module JSDoc in index.ts),
public exports, hooks/components counts, API calls and browser channels (BroadcastChannel: defines / pub / sub).
One line per feature, plus one `fe-app` row for the app shell (src/app) so its channel usage and API calls are visible.

Channels: a file containing `new BroadcastChannel(` is a channel module; its channel name comes from a
`*CHANNEL*` string constant in that file (else the literal passed to the constructor, else the file name) and gets
the suffix `.{*}` when the constructor argument is not a literal (one channel per session etc.). A feature
`pub`lishes when it imports a symbol matching /publish/i from that module, `sub`scribes for /subscri/i; the feature
that holds the module `defines` it. Keep every BroadcastChannel inside one module per channel for this to work."""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, header, escape_cell, first_doc_line,
                     unique, sort_key, utf8_stdout)

NOT_TEST = re.compile(r'\.(test|spec|stories)\.', re.I)
API_RX = re.compile(r'(?:fetch|axios\.\w+|api\.\w+)\(\s*`([^`]*)`|(?:fetch|axios\.\w+|api\.\w+)\(\s*[\'"]([^\'"]*)[\'"]')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--features-dir', default='src/features')
    ap.add_argument('--out', default='docs/_generated/codebase-map.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    features_dir = a.features_dir
    feat_root = os.path.join(root, features_dir)
    if not os.path.isdir(feat_root):
        raise SystemExit(f'No {features_dir} under {root}')

    def src(d):
        return [f for f in source_files(d, ['*.ts', '*.tsx']) if not NOT_TEST.search(os.path.basename(f))]

    # ---- browser channels (BroadcastChannel) ----
    channel_modules = {}   # module key (repo-relative path without extension, forward slashes) -> channel name
    for f in src(os.path.join(root, 'src')):
        t = read_text(f)
        if not re.search(r'new\s+BroadcastChannel\(', t, re.I):
            continue
        m1 = re.search(r'(?m)^\s*(?:export\s+)?const\s+\w*CHANNEL\w*\s*=\s*[\'"]([\w.-]+)[\'"]', t, re.I)
        m2 = re.search(r'new\s+BroadcastChannel\(\s*[\'"]([\w.-]+)[\'"]', t, re.I)
        name = m1.group(1) if m1 else m2.group(1) if m2 else os.path.splitext(os.path.basename(f))[0]
        if not re.search(r'new\s+BroadcastChannel\(\s*[\'"]', t, re.I):
            name += '.{*}'
        key = re.sub(r'\.(ts|tsx)$', '', rel_path(root, f), flags=re.I)
        channel_modules[key] = name

    def resolve_import(from_file, spec):
        # returns the repo-relative module key for a relative or '@/' import, '' otherwise
        if spec.startswith('@/'):
            return re.sub(r'/index$', '', 'src/' + spec[2:], flags=re.I)
        if not spec.startswith('.'):
            return ''
        d = os.path.dirname(os.path.join(root, from_file))
        full = os.path.normpath(os.path.join(d, spec))
        return re.sub(r'/index$', '', re.sub(r'\.(ts|tsx)$', '', rel_path(root, full), flags=re.I), flags=re.I)

    def channel_usage(dir_full):
        uses = []
        if not channel_modules:
            return uses
        for f in src(dir_full):
            rel = rel_path(root, f)
            key = re.sub(r'\.(ts|tsx)$', '', rel, flags=re.I)
            if key in channel_modules:
                uses.append(f'defines {channel_modules[key]}')
                continue
            t = read_text(f)
            for m in re.finditer(r'(?m)^import\s+(?:type\s+)?\{([^}]*)\}\s+from\s+[\'"]([^\'"]+)[\'"]', t):
                target = resolve_import(rel, m.group(2))
                tk = next((k for k in channel_modules if k == target or k == f'{target}/index' or re.sub(r'/[^/]+$', '', k) == target), None)   # direct import or the feature barrel re-exporting the hooks
                if not tk:
                    continue
                syms = [re.sub(r'\s+as\s+.*', '', s, flags=re.I).strip() for s in m.group(1).split(',')]
                if any(re.search('publish', s, re.I) for s in syms):
                    uses.append(f'pub {channel_modules[tk]}')
                if any(re.search('subscri', s, re.I) for s in syms):
                    uses.append(f'sub {channel_modules[tk]}')
        return unique(uses)

    def api_calls(files):
        apis = set()
        for f in files:
            for m in API_RX.finditer(read_text(f)):
                u = m.group(1) if m.group(1) is not None else m.group(2)
                apis.add(re.sub(r'\$\{[^}]+\}', '{*}', re.sub(r'\$\{BASE\}', '<BASE>', u, flags=re.I)))
        return sorted(apis, key=sort_key)

    rows = []
    for d in sorted((x for x in os.listdir(feat_root) if os.path.isdir(os.path.join(feat_root, x))), key=sort_key):
        d_full = os.path.join(feat_root, d)
        files = src(d_full)
        idx = next((x for x in sorted(os.listdir(d_full), key=str.lower) if os.path.isfile(os.path.join(d_full, x)) and re.match(r'^index\.ts', x, re.I)), None)
        desc = ''
        exports = []
        if idx:
            t = read_text(os.path.join(d_full, idx))
            doc = re.search(r'(?s)/\*\*(.*?)\*/', t)
            if doc:
                desc = first_doc_line(doc.group(1))
            for em in re.finditer(r'(?m)^export\s+(?:type\s+)?\{([^}]*)\}', t):
                exports.extend(x for x in (re.sub(r'\s+as\s+.*', '', s, flags=re.I).strip() for s in em.group(1).split(',')) if x)
        hooks = sum(1 for f in files if re.match(r'^use[A-Z]', os.path.basename(f), re.I))
        components = sum(1 for f in files if f.lower().endswith('.tsx') and not re.match(r'^(index|routes?)\.', os.path.basename(f), re.I))
        rows.append({'Feature': d, 'Desc': desc, 'Files': len(files), 'Components': components, 'Hooks': hooks,
                     'Exports': ', '.join(exports), 'Apis': '<br>'.join(api_calls(files)),
                     'Channels': '<br>'.join(channel_usage(d_full)),
                     'Entry': f"{features_dir}/{d}/{idx if idx else '-'}"})
    # app shell row (routes, layouts): only API calls and channel usage matter here
    app_dir = os.path.join(root, 'src/app')
    if os.path.isdir(app_dir):
        app_files = src(app_dir)
        rows.append({'Feature': 'fe-app', 'Desc': 'app shell: router, layouts, providers', 'Files': len(app_files),
                     'Components': sum(1 for f in app_files if f.lower().endswith('.tsx')), 'Hooks': 0, 'Exports': '',
                     'Apis': '<br>'.join(api_calls(app_files)), 'Channels': '<br>'.join(channel_usage(app_dir)),
                     'Entry': 'src/app/App.tsx'})

    sb = [header('Codebase map (FE)', f'{features_dir}/* + index.ts barrels')]
    sb.append('Read the feature `index.ts` (public surface) and `*.types.ts` first; open components only for UI-level questions.\n')
    sb.append('Channels = browser `BroadcastChannel`s (`defines` / `pub` / `sub`), the FE counterpart of Kafka topics; the shared component library is in `components.md`.\n\n')
    sb.append('| Feature | Purpose | Entry | Files | Components | Hooks | Public exports | API calls | Channels |\n|---|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        sb.append(f"| `{r['Feature']}` | {escape_cell(r['Desc'])} | `{r['Entry']}` | {r['Files']} | {r['Components']} | {r['Hooks']} | {escape_cell(r['Exports'])} | {r['Apis']} | {r['Channels']} |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'codebase-map: {len(rows)} feature(s) -> {a.out}')


if __name__ == '__main__':
    main()
