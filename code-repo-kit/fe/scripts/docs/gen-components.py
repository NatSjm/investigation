#!/usr/bin/env python3
"""Component library map for a React/TS repo: one row per exported component under src/shared/** (the in-house UI
library: tables, modals, charts, form controls) with its props (names from the `<Name>Props` interface), the first
JSDoc line, the features that render it and file:line. Lets an analyst or a coding agent name the library component a
story should use, and lets the graph link features to the shared components they depend on.
Example: python3 scripts/docs/gen-components.py --root . --out docs/_generated/components.md"""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header, escape_cell,
                     first_doc_line, sort_key, utf8_stdout)

NOT_TEST = re.compile(r'\.(test|spec|stories)\.', re.I)
# exported components: `export function Name(` / `export const Name = (` / `export const Name: React.FC` with a capitalised name
COMP_RX = re.compile(r'(?m)^export\s+(?:default\s+)?(?:function\s+([A-Z]\w*)\s*(?:<[^>]*>)?\s*\(|const\s+([A-Z]\w*)\s*(?::\s*[^=]+)?=\s*(?:React\.)?(?:memo\()?(?:forwardRef\()?\s*(?:\([^)]*\)|\w+)\s*=>|const\s+([A-Z]\w*)\s*:\s*(?:React\.)?FC\b)')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--shared-dir', default='src/shared')
    ap.add_argument('--features-dir', default='src/features')
    ap.add_argument('--out', default='docs/_generated/components.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    shared_root = os.path.join(root, a.shared_dir)
    if not os.path.isdir(shared_root):
        raise SystemExit(f'No {a.shared_dir} under {root}')

    # usage index: component name -> features whose files reference `<Name` (JSX) or `Name(` (render helpers)
    feature_files = {}
    feat_root = os.path.join(root, a.features_dir)
    if os.path.isdir(feat_root):
        for d in sorted((x for x in os.listdir(feat_root) if os.path.isdir(os.path.join(feat_root, x))), key=str.lower):
            feature_files[d] = [read_text(f) for f in source_files(os.path.join(feat_root, d), ['*.ts', '*.tsx'])
                                if not NOT_TEST.search(os.path.basename(f))]
        # app shell counts as a pseudo-feature
        app_dir = os.path.join(root, 'src/app')
        if os.path.isdir(app_dir):
            feature_files['fe-app'] = [read_text(f) for f in source_files(app_dir, ['*.ts', '*.tsx'])]

    rows = []
    files = [f for f in source_files(shared_root, ['*.tsx', '*.ts'])
             if not NOT_TEST.search(os.path.basename(f)) and not re.match(r'^index\.', os.path.basename(f), re.I)]
    for f in files:
        t = read_text(f)
        rel = rel_path(root, f)
        group = re.sub('^' + re.escape(a.shared_dir) + '/', '', rel, flags=re.I).split('/')[0]
        for m in COMP_RX.finditer(t):
            name = next((g for g in (m.group(1), m.group(2), m.group(3)) if g), None)
            if not name:
                continue
            # props: fields of `interface <Name>Props` / `type <Name>Props = {` (names only, optional marked with ?)
            props = []
            pm = re.search(r'(?s)(?:interface|type)\s+' + re.escape(name) + r'Props(?:<[^>]*>)?\s*(?:=\s*)?\{(.*?)\n\}', t)
            if pm:
                props = re.findall(r'(?m)^\s*(\w+\??)\s*:', pm.group(1))
            else:
                dm = re.search(r'\(\s*\{([^}]*)\}', m.group(0), re.I)
                if dm:
                    props = [x for x in (re.sub(r':.*$', '', re.sub(r'=.*$', '', p)).strip() for p in dm.group(1).split(',')) if x]
            # first JSDoc line directly above the declaration
            before = t[:m.start()]
            doc = ''
            jd = re.search(r'(?s)/\*\*((?:(?!\*/).)*)\*/\s*$', before)
            if jd:
                doc = first_doc_line(jd.group(1))
            used_by = sorted((feat for feat, texts in feature_files.items()
                              if any(re.search('<' + re.escape(name) + r'\b', x, re.I) or re.search(r'\b' + re.escape(name) + r'\(', x, re.I) for x in texts)),
                             key=sort_key)
            rows.append({'Name': name, 'Group': group, 'Doc': doc, 'Props': props, 'UsedBy': used_by,
                         'Loc': f'{rel}:{line_number(t, m.start())}'})

    sb = [header('Component library (FE)', f'{a.shared_dir}/** exported components',
                 'One row per shared UI component: props, purpose, which features render it, file:line; name these in stories instead of inventing new components.')]
    sb.append(f'{len(rows)} component(s) under `{a.shared_dir}/`. Features must compose these; a new shared component is a change to this library, not to a feature.\n\n')
    sb.append('| Component | Group | Purpose | Props | Used by | Location |\n|---|---|---|---|---|---|\n')
    for r in sorted(rows, key=lambda r: (sort_key(r['Group']), sort_key(r['Name']))):
        props = ', '.join('`' + p + '`' for p in r['Props'])
        used = ', '.join('`' + u + '`' for u in r['UsedBy']) if r['UsedBy'] else '_unused_'
        sb.append(f"| `{r['Name']}` | {r['Group']} | {escape_cell(r['Doc'])} | {props} | {used} | `{r['Loc']}` |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'components: {len(rows)} component(s) -> {a.out}')


if __name__ == '__main__':
    main()
