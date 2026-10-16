#!/usr/bin/env python3
"""Lists every page folder with the `@docs` tag of its page component, its types file(s) and its data hooks and, where
missing, the tag it should get. Deterministic input for the `docs-tagger` agent (prompt /tag-docs); nothing is written
to the sources.

For each <pages_dir>/<Page>/: context = the contexts.yml entry whose `fe` list contains the page folder name (wildcards
allowed: `*Product1Page`); the page's ID is the page component's existing `@docs` tag, else `<spec prefix>-<next free NNN>`
(NNN from docs-tags.md, 001 when none). Files checked: the page entry (`<Page>.tsx`), `*.types.ts` / `types.ts` in the
page folder, hooks `use*.ts` under the hook folders. Folders listed in `not_pages` (shared pieces) are listed too: their
untagged files get status SHARED (pick the ID of the spec that owns the rule, no proposal).
Status per file: tagged | PROPOSE | SHARED | BLOCKED (page not in contexts.yml).
Example: python3 scripts/docs/tag-candidates.py --root . --contexts ../harbor-docs/contexts.yml"""
import argparse
import os
import re
import sys

from _common import (read_text, write_text, resolve_out, rel_path, header, posix, like, sort_key, unique, source_files_cfg,
                     load_config, utf8_stdout)

DEFAULTS = {
    'pages_dir': 'src/pages', 'not_pages': ['shared'], 'page_entry': ['<Page>.tsx', 'index.tsx', 'index.ts'],
    'hook_dirs': ['hook', 'hooks', 'api'], 'exclude_paths': [], 'test_pattern': r'\.(test|spec|stories)\.',
}


def parse_contexts(text):
    """contexts.yml one-line entries: name: { spec: X, fe: name | "name" | [a, b] | "", be: [...] } -> [(name, spec, [fe patterns])]."""
    out = []
    for m in re.finditer(r'(?m)^\s{2}([\w-]+):\s*\{(.*)\}', text):
        name, body = m.group(1), m.group(2)
        sm = re.search(r'spec:\s*(\w+)', body)
        fm = re.search(r'fe:\s*(\[[^\]]*\]|"[^"]*"|\'[^\']*\'|[\w*?.-]*)', body)
        fe = []
        if fm:
            raw = fm.group(1).strip()
            raw = raw[1:-1] if raw[:1] in '["\'' else raw
            fe = [x.strip().strip('"\'') for x in raw.split(',') if x.strip().strip('"\'')]
        out.append((name, sm.group(1) if sm else '', fe))
    return out


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--config', default='')
    ap.add_argument('--contexts', default='')
    ap.add_argument('--docs-tags', default='docs/_generated/docs-tags.md')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    pages_dir = cfg['pages_dir']

    contexts = a.contexts
    if not contexts:
        for c in ('../harbor-docs/contexts.yml', '../docs-repo/contexts.yml'):
            if os.path.isfile(os.path.join(root, c)):
                contexts = os.path.join(root, c)
                break
        if not contexts:
            raise SystemExit('contexts.yml not found next to the repo; pass --contexts <path>')
    pages_root = os.path.join(root, pages_dir)
    if not os.path.isdir(pages_root):
        raise SystemExit(f'No {pages_dir} under {root} (set pages_dir in docs-gen.json)')
    excluded = [os.path.join(root, p) for p in cfg['exclude_paths']]

    ctx_list = parse_contexts(read_text(contexts))

    def context_of(page):
        for name, spec, fe in ctx_list:
            if any(like(page, p) for p in fe):
                return {'Context': name, 'Spec': spec}
        return None

    used = {}
    tags_path = os.path.join(root, a.docs_tags)
    if os.path.isfile(tags_path):
        for m in re.finditer(r'(?m)^\|\s*`([A-Z][A-Z0-9]*)-(\d{3})`', read_text(tags_path)):
            p, n = m.group(1), int(m.group(2))
            if used.get(p, 0) < n:
                used[p] = n

    def next_id(prefix):
        n = used.get(prefix, 0) + 1
        used[prefix] = n
        return f'{prefix}-{n:03d}'

    def doc_tags(path):
        t = read_text(path)
        found = []
        for doc in re.finditer(r'(?s)/\*\*(.*?)\*/', t):
            found += re.findall(r'@docs\s+([\w.-]+)', doc.group(1))
        return unique(found)

    def entry_of(d_full, page):
        for pat in cfg['page_entry']:
            cand = pat.replace('<Page>', page)
            if os.path.isfile(os.path.join(d_full, cand)):
                return cand
        return ''

    rows = []
    for page in sorted((x for x in os.listdir(pages_root) if os.path.isdir(os.path.join(pages_root, x))), key=sort_key):
        d_full = os.path.join(pages_root, page)
        shared = page in cfg['not_pages']
        ctx = None if shared else context_of(page)
        entry = '' if shared else entry_of(d_full, page)
        files = []
        if entry:
            files.append(os.path.join(d_full, entry))
        files += [os.path.join(d_full, x) for x in sorted(os.listdir(d_full), key=str.lower)
                  if os.path.isfile(os.path.join(d_full, x)) and (like(x, '*.types.ts') or x.lower() == 'types.ts')]
        files += [f for f in source_files_cfg(d_full, ['use*.ts', 'use*.tsx'], cfg['test_pattern'], excluded)
                  if os.path.basename(os.path.dirname(f)) in cfg['hook_dirs']]
        page_tags = doc_tags(os.path.join(d_full, entry)) if entry else []
        fid = page_tags[0] if page_tags else (next_id(ctx['Spec']) if ctx else '')
        if not shared and not entry:
            rows.append({'File': f'{pages_dir}/{page}/{cfg["page_entry"][0].replace("<Page>", page)}', 'Page': page,
                         'Context': ctx['Context'] if ctx else '-', 'Current': '', 'Proposed': f'@docs {fid}' if ctx else '',
                         'Status': 'PROPOSE (create the page component with a JSDoc block)' if ctx else 'BLOCKED: page not in contexts.yml'})
        for f in files:
            tags = doc_tags(f)
            proposed = ''
            if tags:
                status = 'tagged'
            elif shared:
                status = 'SHARED: tag with the ID of the spec that owns the rule'
            elif not ctx:
                status = 'BLOCKED: page not in contexts.yml'
            else:
                proposed = f'@docs {fid}'
                status = 'PROPOSE'
            rows.append({'File': rel_path(root, f), 'Page': page, 'Context': ctx['Context'] if ctx else '-',
                         'Current': ', '.join(tags), 'Proposed': proposed, 'Status': status})

    sb = [header('@docs tag candidates (FE)', f'{pages_dir}/*/{{<Page>.tsx, *.types.ts, {"|".join(cfg["hook_dirs"])}/use*.ts}} + contexts.yml',
                 'Page files with their current @docs tag and the proposed one where missing; input for the docs-tagger agent.')]
    n = len(rows)
    todo = sum(1 for r in rows if like(r['Status'], 'PROPOSE*'))
    blocked = sum(1 for r in rows if like(r['Status'], 'BLOCKED*'))
    shared_n = sum(1 for r in rows if like(r['Status'], 'SHARED*'))
    ctx_shown = posix(os.path.abspath(contexts))
    if ctx_shown.startswith(posix(root)):
        ctx_shown = rel_path(root, ctx_shown)
    sb.append(f'{n} file(s): {n - todo - blocked - shared_n} tagged, {todo} to tag, {shared_n} shared (owner to decide), {blocked} blocked. '
              f'Spec IDs come from `{ctx_shown}`; the spec file itself may not exist yet.\n\n')
    sb.append('| File | Page | Context | Current | Proposed | Status |\n|---|---|---|---|---|---|\n')
    for r in rows:
        cur = '`' + r['Current'] + '`' if r['Current'] else ''
        pro = '`' + r['Proposed'] + '`' if r['Proposed'] else ''
        sb.append(f"| `{r['File']}` | {r['Page']} | {r['Context']} | {cur} | {pro} | {r['Status']} |\n")
    if blocked:
        sb.append('\n## Blockers\n')
        for f in unique(r['Page'] for r in rows if like(r['Status'], 'BLOCKED*')):
            sb.append(f'- `{f}`: add the page folder name to the `fe` list of its context in contexts.yml, then rerun.\n')
    text = ''.join(sb)
    if a.out:
        write_text(resolve_out(root, a.out), text)
        print(f'tag-candidates: {n} file(s), {todo} to tag, {shared_n} shared, {blocked} blocked -> {a.out}')
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
