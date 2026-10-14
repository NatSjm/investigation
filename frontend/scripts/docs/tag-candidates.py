#!/usr/bin/env python3
"""Lists every feature folder with the `@docs` tag of its barrel, types file and data hooks and, where missing, the tag
it should get. Deterministic input for the `docs-tagger` agent (prompt /tag-docs); nothing is written to the sources.

For each src/features/<name>/: context = the contexts.yml entry whose `fe` equals the folder name; the feature's ID is
the barrel's existing `@docs` tag, else `<spec prefix>-<next free NNN>` (NNN from docs-tags.md, 001 when none).
Files checked: index.ts (needs `@module <name>` + `@docs <ID>`), <name>.types.ts, api/use*.ts.
Status per file: tagged | PROPOSE | BLOCKED (folder not in contexts.yml).
Example: python3 scripts/docs/tag-candidates.py --root . --contexts ../harbor-docs/contexts.yml"""
import argparse
import os
import re
import sys

from _common import read_text, write_text, resolve_out, rel_path, header, posix, like, sort_key, unique, utf8_stdout


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--contexts', default='')
    ap.add_argument('--features-dir', default='src/features')
    ap.add_argument('--docs-tags', default='docs/_generated/docs-tags.md')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    features_dir = a.features_dir

    contexts = a.contexts
    if not contexts:
        for c in ('../harbor-docs/contexts.yml', '../docs-repo/contexts.yml'):
            if os.path.isfile(os.path.join(root, c)):
                contexts = os.path.join(root, c)
                break
        if not contexts:
            raise SystemExit('contexts.yml not found next to the repo; pass --contexts <path>')
    feat_root = os.path.join(root, features_dir)
    if not os.path.isdir(feat_root):
        raise SystemExit(f'No {features_dir} under {root}')

    # ---- contexts.yml: fe folder -> spec prefix ----
    by_folder = {}
    for m in re.finditer(r'(?m)^\s*([\w-]+):\s*\{\s*spec:\s*(\w+)\s*,\s*fe:\s*"?([\w-]*)"?\s*,', read_text(contexts)):
        if m.group(3):
            by_folder[m.group(3)] = {'Context': m.group(1), 'Spec': m.group(2)}
    used = {}
    tags_path = os.path.join(root, a.docs_tags)
    if os.path.isfile(tags_path):
        for m in re.finditer(r'(?m)^\|\s*`([A-Z][A-Z0-9]*)-(\d{3})[a-z]?`', read_text(tags_path)):
            p, n = m.group(1), int(m.group(2))
            if used.get(p, 0) < n:
                used[p] = n

    def next_id(prefix):
        n = used.get(prefix, 0) + 1
        used[prefix] = n
        return f'{prefix}-{n:03d}'

    def first_doc_tags(path):
        t = read_text(path)
        doc = re.match(r'(?s)\A\s*/\*\*(.*?)\*/', t)      # the file-level JSDoc, before any code
        if not doc:
            doc = re.search(r'(?s)/\*\*(.*?)\*/', t)   # else the first block (hooks)
        if not doc:
            return []
        return re.findall(r'@docs\s+([\w.-]+)', doc.group(1))

    rows = []
    for feature in sorted((x for x in os.listdir(feat_root) if os.path.isdir(os.path.join(feat_root, x))), key=sort_key):
        d_full = os.path.join(feat_root, feature)
        ctx = by_folder.get(feature)
        files = []
        entries = sorted((x for x in os.listdir(d_full) if os.path.isfile(os.path.join(d_full, x))), key=str.lower)
        idx = next((x for x in entries if re.match(r'^index\.ts', x, re.I)), None)
        if idx:
            files.append(os.path.join(d_full, idx))
        files += [os.path.join(d_full, x) for x in entries if x.lower() == f'{feature}.types.ts'.lower()]
        api_dir = os.path.join(d_full, 'api')
        if os.path.isdir(api_dir):
            files += [os.path.join(api_dir, x) for x in sorted(os.listdir(api_dir), key=str.lower)
                      if os.path.isfile(os.path.join(api_dir, x)) and like(x, 'use*.ts') and not re.search(r'\.(test|spec)\.', x, re.I)]
        barrel_tags = first_doc_tags(os.path.join(d_full, idx)) if idx else []
        fid = ''
        if barrel_tags:
            fid = barrel_tags[0]
        elif ctx:
            fid = next_id(ctx['Spec'])
        if not idx:
            rows.append({'File': f'{features_dir}/{feature}/index.ts', 'Feature': feature, 'Context': ctx['Context'] if ctx else '-',
                         'Current': '', 'Proposed': f'@module {feature} + @docs {fid}' if ctx else '',
                         'Status': 'PROPOSE (create the barrel)' if ctx else 'BLOCKED: folder not in contexts.yml'})
        for f in files:
            tags = first_doc_tags(f)
            rel = rel_path(root, f)
            proposed = ''
            if tags:
                status = 'tagged'
            elif not ctx:
                status = 'BLOCKED: folder not in contexts.yml'
            else:
                proposed = f'@module {feature} + @docs {fid}' if like(os.path.basename(f), 'index.*') else f'@docs {fid}'
                status = 'PROPOSE'
            rows.append({'File': rel, 'Feature': feature, 'Context': ctx['Context'] if ctx else '-',
                         'Current': ', '.join(tags), 'Proposed': proposed, 'Status': status})

    sb = [header('@docs tag candidates (FE)', f'{features_dir}/*/{{index.ts, <name>.types.ts, api/use*.ts}} + contexts.yml',
                 'Feature files with their current @docs tag and the proposed one where missing; input for the docs-tagger agent.')]
    n = len(rows)
    todo = sum(1 for r in rows if like(r['Status'], 'PROPOSE*'))
    blocked = sum(1 for r in rows if like(r['Status'], 'BLOCKED*'))
    ctx_shown = posix(os.path.abspath(contexts))
    if ctx_shown.startswith(posix(root)):
        ctx_shown = rel_path(root, ctx_shown)
    sb.append(f'{n} file(s): {n - todo - blocked} tagged, {todo} to tag, {blocked} blocked. Spec IDs come from `{ctx_shown}`; the spec file itself may not exist yet.\n\n')
    sb.append('| File | Feature | Context | Current | Proposed | Status |\n|---|---|---|---|---|---|\n')
    for r in rows:
        cur = '`' + r['Current'] + '`' if r['Current'] else ''
        pro = '`' + r['Proposed'] + '`' if r['Proposed'] else ''
        sb.append(f"| `{r['File']}` | {r['Feature']} | {r['Context']} | {cur} | {pro} | {r['Status']} |\n")
    if blocked:
        sb.append('\n## Blockers\n')
        for f in unique(r['Feature'] for r in rows if like(r['Status'], 'BLOCKED*')):
            sb.append(f'- `{f}`: add a context with `fe: {f}` to contexts.yml, then rerun.\n')
    text = ''.join(sb)
    if a.out:
        write_text(resolve_out(root, a.out), text)
        print(f'tag-candidates: {n} file(s), {todo} to tag, {blocked} blocked -> {a.out}')
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
