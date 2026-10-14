#!/usr/bin/env python3
"""Lists every manager and calculation class with its current `@docs` tag and, where it is missing, the tag it should get.
Deterministic input for the `docs-tagger` agent (prompt /tag-docs): the agent adds the comment lines, a human reviews the table.

Reads docs/_generated/components.md (run gen-all.py first) and the docs repo contexts.yml:
  - layer `manager`: context = longest class-name prefix in contexts.yml; proposed tag = `<spec prefix>-<next free NNN>`
    (NNN from the IDs already used in docs-tags.md, 001 when none). No matching prefix -> BLOCKED (add the prefix first).
  - layer `utils`: proposed tag = snake_case of the class name; the agent refines it from the KDoc (e.g. `monthly_projection`).
Status: tagged | PROPOSE | REVIEW (utils class without a context prefix: shared helper or calculation?) | BLOCKED.
A second table lists the public functions of the `utils` classes: a reusable sub-calculation is an entry point and
needs its own tag (status REVIEW when it has none and the class has several public functions).
Nothing is written to the source files.
Examples:
  python3 scripts/docs/tag-candidates.py --root . --contexts ../harbor-docs/contexts.yml
  python3 scripts/docs/tag-candidates.py --root . --out docs/_generated/tag-candidates.md"""
import argparse
import os
import re
import sys

from _common import (read_text, write_text, resolve_out, rel_path, line_number, header, posix, like, sort_key,
                     utf8_stdout)

FUN_RX = re.compile(r'(?s)(?:/\*\*(?P<doc>(?:(?!\*/).)*)\*/\s*)?(?:@\w+(?:\([^)]*\))?\s*)*'
                    r'(?P<mods>(?:(?:private|internal|protected|public|override|operator|inline|infix|suspend|tailrec|open|abstract)\s+)*)'
                    r'fun\s+(?:<[^>]*>\s*)?(?P<name>\w+)\s*\(')


def to_snake(s):
    return re.sub(r'(?<=[a-z0-9])([A-Z])|(?<=[A-Z])([A-Z][a-z])', lambda m: '_' + (m.group(1) or '') + (m.group(2) or ''), s).lower()


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--contexts', default='')
    ap.add_argument('--components', default='docs/_generated/components.md')
    ap.add_argument('--docs-tags', default='docs/_generated/docs-tags.md')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    contexts = a.contexts
    if not contexts:
        for c in ('../harbor-docs/contexts.yml', '../docs-repo/contexts.yml'):
            if os.path.isfile(os.path.join(root, c)):
                contexts = os.path.join(root, c)
                break
        if not contexts:
            raise SystemExit('contexts.yml not found next to the repo; pass --contexts <path>')
    comp_path = os.path.join(root, a.components)
    if not os.path.isfile(comp_path):
        raise SystemExit(f'{a.components} missing; run scripts/docs/gen-all.py first')

    # ---- contexts.yml: name -> { Spec; Prefixes } (one line per context, flow style) ----
    ctxs = {}
    for m in re.finditer(r'(?m)^\s*([\w-]+):\s*\{\s*spec:\s*(\w+)\s*,\s*fe:\s*[^,]*,\s*be:\s*\[([^\]]*)\]', read_text(contexts)):
        ctxs[m.group(1)] = {'Spec': m.group(2), 'Prefixes': [p.strip() for p in m.group(3).split(',') if p.strip()]}

    def resolve_context(class_name):
        best, best_len = '', 0
        for c, v in ctxs.items():
            for p in v['Prefixes']:
                if class_name.startswith(p) and len(p) > best_len:
                    best, best_len = c, len(p)
        return best

    # ---- IDs already in use per spec prefix (docs-tags.md, Spec ID column) ----
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

    # ---- components.md rows: | `Class` | Layer | Module | Kind | Depends on | Tables | @docs | `Location` | ----
    rows = []
    for line in re.split(r'\r?\n', read_text(comp_path)):
        if not re.match(r'^\|\s*`([\w.]+)`\s*\|\s*(\w+|\(root\))\s*\|', line, re.I):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 8:
            continue
        name = cells[0].strip('`')
        layer = cells[1]
        kind = cells[3]
        tag = cells[6].replace('`', '')
        loc = cells[7].strip('`')
        if layer.lower() not in ('manager', 'utils'):
            continue
        if layer.lower() == 'utils' and not re.match(r'^(object|class)$', kind, re.I):
            continue   # enums, data classes, interfaces are not calculations
        ctx = resolve_context(name)
        proposed = ''
        if layer.lower() == 'manager':
            if tag:
                status = 'tagged'
            elif not ctx:
                status = 'BLOCKED: no class-name prefix in contexts.yml'
            else:
                proposed = next_id(ctxs[ctx]['Spec'])
                status = 'PROPOSE'
        else:
            if tag:
                status = 'tagged'
            elif not ctx:
                status = 'REVIEW: shared helper? tag only if it computes a business quantity'
            else:
                proposed = to_snake(name)
                status = 'PROPOSE (confirm name from the KDoc formula)'
        rows.append({'Class': name, 'Layer': layer, 'Context': ctx or 'shared', 'Current': tag, 'Proposed': proposed,
                     'Status': status, 'Loc': loc})

    # ---- public functions of the calculation classes: a reusable sub-calculation is an entry point of its own ----
    funs = []
    for r in (x for x in rows if x['Layer'].lower() == 'utils'):
        file = r['Loc'].split(':')[0]
        src = read_text(os.path.join(root, file))
        public = [m for m in FUN_RX.finditer(src) if not re.search(r'private|internal|protected|override', m.group('mods'), re.I)]
        for m in public:
            fname = m.group('name')
            ftags = re.findall(r'@docs\s+([\w.-]+)', m.group('doc') or '')
            if ftags:
                status = 'tagged'
            elif r['Current'] and len(public) == 1:
                status = 'covered by class tag'
            elif like(r['Status'], 'REVIEW*'):
                status = 'helper (see class row)'
            else:
                status = 'REVIEW: entry point? tag if it has a business name and its own test cases'
            funs.append({'Function': f"{r['Class']}.{fname}", 'Class': r['Class'], 'Current': ', '.join(ftags),
                         'Status': status, 'Loc': f"{file}:{line_number(src, m.start('name'))}"})

    sb = [header('@docs tag candidates (BE)', f'{a.components} + contexts.yml',
                 'Managers and calculations with their current @docs tag and the proposed one where missing; input for the docs-tagger agent.')]
    n = len(rows)
    todo = sum(1 for r in rows if like(r['Status'], 'PROPOSE*'))
    blocked = sum(1 for r in rows if like(r['Status'], 'BLOCKED*'))
    review = sum(1 for r in rows if like(r['Status'], 'REVIEW*'))
    ctx_shown = posix(os.path.abspath(contexts))
    if ctx_shown.startswith(posix(root)):
        ctx_shown = rel_path(root, ctx_shown)
    sb.append(f'{n} class(es): {n - todo - blocked - review} tagged, {todo} to tag, {review} to review, {blocked} blocked. Spec IDs come from `{ctx_shown}`; the spec file itself may not exist yet.\n\n')
    sb.append('| Class | Layer | Context | Current | Proposed | Status | Location |\n|---|---|---|---|---|---|---|\n')
    for r in sorted(rows, key=lambda r: (sort_key(r['Layer']), sort_key(r['Context']), sort_key(r['Class']))):
        cur = '`' + r['Current'] + '`' if r['Current'] else ''
        pro = '`@docs ' + r['Proposed'] + '`' if r['Proposed'] else ''
        sb.append(f"| `{r['Class']}` | {r['Layer']} | {r['Context']} | {cur} | {pro} | {r['Status']} | `{r['Loc']}` |\n")
    if funs:
        f_review = sum(1 for f in funs if like(f['Status'], 'REVIEW*'))
        sb.append('\n## Public functions of the calculation classes\n')
        sb.append(f'{len(funs)} function(s), {f_review} to review. A sub-calculation reused by other calculations or cited by a spec is an entry point and carries its own `@docs`; private steps and helpers do not.\n\n')
        sb.append('| Function | Current | Status | Location |\n|---|---|---|---|\n')
        for f in sorted(funs, key=lambda f: (sort_key(f['Class']), sort_key(f['Function']))):
            cur = '`' + f['Current'] + '`' if f['Current'] else ''
            sb.append(f"| `{f['Function']}` | {cur} | {f['Status']} | `{f['Loc']}` |\n")
    if blocked:
        sb.append('\n## Blockers\n')
        for r in rows:
            if like(r['Status'], 'BLOCKED*'):
                sb.append(f"- `{r['Class']}`: add its name prefix to a context in contexts.yml, then rerun.\n")
    text = ''.join(sb)
    if a.out:
        write_text(resolve_out(root, a.out), text)
        print(f'tag-candidates: {n} class(es), {todo} to tag, {blocked} blocked -> {a.out}')
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
