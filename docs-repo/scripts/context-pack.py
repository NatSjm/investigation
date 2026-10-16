#!/usr/bin/env python3
"""Builds a task-scoped, budgeted context pack for an agent (analyst, spec-writer, test-designer, calc-auditor):
spec + trust badge, linked calculations (formula + worked examples), the flows the spec takes part in, depth-2 graph
neighbourhood, contract operations, tables, related work items / tests and legacy pages that mention the subject. No libraries.

The pack is the only thing an agent should read for a task; everything else is reachable through the
file:line references it contains. Section order / truncation ranks: .github/skills/task-context/references/pack-anatomy.md

Task: spec ID (P1-001), calculation name (stress_test_monthly), graph node id (topic:..., context:product2,
feature:stress, table:...), or free text (matched against title/description/tags/aliases of specs and calculations).
Budget: maximum lines in the pack (default 500). Lower-ranked sections are truncated first.
Examples:
  python3 scripts/context-pack.py --task P1-001
  python3 scripts/context-pack.py --task "transport mode toggle on the stress table" --budget 300 --print"""
import argparse
import os
import re
import subprocess
import sys

from _common import (repo_root, read_text_or_empty, write_text, rel, get_fm, get_val, get_list, badge, now_utc,
                     walk_files, like, sort_key, split_lines, utf8_stdout)


def get_section(text, heading):
    m = re.search(r'(?ms)^##\s+' + re.escape(heading) + r'[^\r\n]*\r?\n(.*?)(?=^##\s|\Z)', text)
    return m.group(1).rstrip() if m else ''


def body_of(text):
    return re.sub(r'(?s)\A﻿?---\r?\n.*?\r?\n---\r?\n', '', text).strip()


def select_lines(path, pattern, strip_right=True):
    out = []
    for line in split_lines(read_text_or_empty(path)):
        if re.search(pattern, line, re.I):
            out.append(line.rstrip() if strip_right else line.strip())
    return out


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('task_positional', nargs='?', default='')
    ap.add_argument('--task', default='')
    ap.add_argument('--budget', type=int, default=500)
    ap.add_argument('--out-dir', default='.context')
    ap.add_argument('--depth', type=int, default=2)
    ap.add_argument('--print', dest='print_', action='store_true')
    a = ap.parse_args()
    task = a.task or a.task_positional
    if not task:
        ap.error('--task is required')
    repo = repo_root(__file__)
    here = os.path.dirname(os.path.abspath(__file__))
    now = now_utc()
    budget = a.budget

    # ---------- 1. resolve the subject ----------
    specs = [f for f in walk_files(os.path.join(repo, 'features'), '*.md') if not re.match(r'^(_?template|index|conventions)\.md$', os.path.basename(f), re.I)]
    calc_dir = os.path.join(repo, 'domain/calculations')
    calcs = [os.path.join(calc_dir, x) for x in sorted(os.listdir(calc_dir), key=str.lower)
             if x.lower().endswith('.md') and not re.match(r'^(_?template|index)\.md$', x, re.I)] if os.path.isdir(calc_dir) else []
    kind = ''
    file = None
    node = ''
    candidates = []
    if re.match(r'^[A-Z][A-Z0-9]*-\d{3}[a-z]?$', task):
        kind = 'spec'
        file = next((f for f in specs if os.path.splitext(os.path.basename(f))[0] == task), None)
        node = f'spec:{task}'
        if not file:
            print(f'no spec file for {task} - packing graph neighbourhood only')
    elif re.match(r'^[a-z][a-z0-9_]+$', task, re.I) and os.path.isfile(os.path.join(repo, f'domain/calculations/{task}.md')):
        kind = 'calculation'
        file = os.path.join(repo, f'domain/calculations/{task}.md')
        node = f'spec:{task}'
    elif re.match(r'^(context|feature|endpoint|route|class|hook|component|topic|table|spec):', task, re.I):
        kind = 'node'
        node = task
    else:
        # free text: score concepts by token hits in title / description / tags / aliases / id
        tokens = [t for t in re.split(r'[^a-z0-9_\-]+', task.lower()) if len(t) >= 4]
        scored = []
        for f in specs + calcs:
            fm = get_fm(read_text_or_empty(f))
            hay = ' '.join([get_val(fm, 'title'), get_val(fm, 'description'), get_val(fm, 'tags'), get_val(fm, 'aliases'),
                            os.path.splitext(os.path.basename(f))[0]]).lower()
            scored.append((f, sum(1 for t in tokens if t in hay)))
        best = sorted((x for x in scored if x[1] > 0), key=lambda x: -x[1])
        if not best:
            print(f"nothing matches '{task}' - give a spec ID, calculation name or graph node id", file=sys.stderr)
            sys.exit(1)
        file = best[0][0]
        kind = 'calculation' if re.search(r'calculations$', os.path.dirname(file), re.I) else 'spec'
        node = f'spec:{os.path.splitext(os.path.basename(file))[0]}'
        candidates = [f'{rel(repo, f)} (score {s})' for f, s in best[1:3]]

    # ---------- 2. assemble sections (rank = truncation priority, 1 never) ----------
    sections = []

    def add_section(title, content, rank, see_also=''):
        if not content:
            content = '_(none)_'
        sections.append({'Title': title, 'Content': content.rstrip(), 'Rank': rank, 'See': see_also})

    sources = []
    fm = ''
    text = ''
    if file:
        text = read_text_or_empty(file)
        fm = get_fm(text)
        sources.append(rel(repo, file))

    # Subject
    subj = [f'- task: `{task}`', f"- resolved: **{kind}** {'`' + rel(repo, file) + '`' if file else '`' + node + '`'}"]
    if file:
        subj.append(f"- title: {get_val(fm, 'title')}")
        subj.append(f"- badge: **{badge(fm, now)}** · status: {get_val(fm, 'status')} · last_verified: {get_val(fm, 'last_verified')} · stale_after: {get_val(fm, 'stale_after')} · generated: {get_val(fm, 'generated')}")
        own = get_val(fm, 'owners')
        if own:
            subj.append(f'- owners: {own}')
    if candidates:
        subj.append(f"- candidates: {'; '.join(candidates)}  <- free text matched several concepts; confirm the subject")
    add_section('Subject', '\n'.join(subj), 1)

    # Spec / calculation body
    if file:
        body = body_of(text)
        lines = split_lines(body)
        if kind == 'spec' and (len(lines) > 200 or len(lines) > budget * 0.6):
            keep = []
            for h in ('Summary', 'Actors', 'Business rules', 'API', 'Data', 'Calculations', 'Edge cases', 'Open questions'):
                m = re.search(r'(?ms)^(##\s+' + re.escape(h) + r'[^\r\n]*)\r?\n(.*?)(?=^##\s|\Z)', body)
                if m:
                    keep.append(m.group(1) + '\n' + m.group(2).rstrip())
            add_section('Spec', '\n\n'.join(keep) + f'\n\n... (reduced to key sections: see `{rel(repo, file)}`)', 1, rel(repo, file))
        elif kind == 'calculation':
            keep = []
            for h in ('Purpose', 'Inputs', 'Outputs', 'Formula', 'Conventions', 'Worked examples', 'Audit', 'Open questions'):
                m = re.search(r'(?ms)^(##\s+' + re.escape(h) + r'[^\r\n]*)\r?\n(.*?)(?=^#{1,2}\s|\Z)', body)
                if m:
                    keep.append(m.group(1) + '\n' + m.group(2).rstrip())
            add_section('Calculation', '\n\n'.join(keep) + f'\n\n(sanctioned code shape: `# Computation` block in `{rel(repo, file)}`)', 1, rel(repo, file))
        else:
            add_section('Spec', body, 1, rel(repo, file))

    # Calculations linked from the spec
    if kind == 'spec' and file:
        parts = []
        for c in (re.sub(r'^/', '', x) for x in get_list(fm, 'calculations')):
            cp = os.path.join(repo, c)
            if not os.path.isfile(cp):
                parts.append(f'### {c}\n_(missing file)_')
                continue
            ct = read_text_or_empty(cp)
            cfm = get_fm(ct)
            sources.append(c)
            pieces = [f'**{h}**\n{s}' for h in ('Purpose', 'Formula', 'Conventions', 'Worked examples', 'Audit') if (s := get_section(ct, h))]
            parts.append(f"### {get_val(cfm, 'title')} (`{c}`) - badge: {badge(cfm, now)}\n" + '\n\n'.join(pieces))
        add_section('Calculations', '\n\n'.join(parts), 2, 'domain/calculations/')

    # Flows this spec takes part in: listed in the spec (`flows:`) or naming the spec in their own `specs:` (both directions)
    if kind == 'spec' and file:
        spec_id = os.path.splitext(os.path.basename(file))[0]
        flow_refs = [re.sub(r'^/', '', x) for x in get_list(fm, 'flows')]
        flow_dir = os.path.join(repo, 'flows')
        if os.path.isdir(flow_dir):
            for ff in sorted(os.listdir(flow_dir), key=str.lower):
                if not ff.lower().endswith('.md') or re.match(r'^(_template|index)\.md$', ff, re.I):
                    continue
                if spec_id in get_list(get_fm(read_text_or_empty(os.path.join(flow_dir, ff))), 'specs'):
                    flow_refs.append(rel(repo, os.path.join(flow_dir, ff)))
        flow_refs = list(dict.fromkeys(flow_refs))
        if flow_refs:
            parts = []
            for f in flow_refs:
                fp = os.path.join(repo, f)
                if not os.path.isfile(fp):
                    parts.append(f'### {f}\n_(missing file)_')
                    continue
                ft = read_text_or_empty(fp)
                ffm = get_fm(ft)
                sources.append(f)
                pieces = [f'**{h}**\n{s}' for h in ('Purpose', 'Trigger', 'Participants', 'Steps', 'Invariants and assumptions') if (s := get_section(ft, h))]
                parts.append(f"### {get_val(ffm, 'title')} (`{f}`) - badge: {badge(ffm, now)} - specs: {', '.join(get_list(ffm, 'specs'))}\n" + '\n\n'.join(pieces))
            add_section('Flows', '\n\n'.join(parts), 3, 'flows/')

    # Graph neighbourhood
    graph_json = os.path.join(repo, 'generated/graph/graph.json')
    if os.path.isfile(graph_json):
        q = os.path.join(here, 'graph-query.py')

        def query(n):
            r = subprocess.run([sys.executable, q, '--graph', graph_json, '--node', n, '--depth', str(a.depth), '--max-lines', '80'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
            return r.stdout + r.stderr
        start_node = node
        gout = query(start_node)
        if re.search('no node matches', gout, re.I) and file:
            # a spec without @docs tags: fall back to its context community
            ctx = get_val(fm, 'context')
            if ctx:
                # BE contexts have a `context:` node (located at the manager); FE-only contexts (e.g. presentation) only a `feature:` node
                ctx_node = f'context:{ctx}'
                gtext = read_text_or_empty(graph_json)
                if not re.search(r'"id"\s*:\s*"' + re.escape(ctx_node) + '"', gtext, re.I):
                    # FE-only: the first page (feature node) whose community is the context
                    fm_ = re.search(r'"id"\s*:\s*"(feature:[^"]+)",\s*"kind"\s*:\s*"feature",\s*"label"\s*:\s*"[^"]*",\s*"community"\s*:\s*"' + re.escape(ctx) + '"', gtext, re.I)
                    ctx_node = fm_.group(1) if fm_ else f'feature:{ctx}'
                gout = f'(`{node}` not in graph - no `@docs` tag in code; neighbourhood of `{ctx_node}` instead)\n' + query(ctx_node)
        sources.append('generated/graph/graph.json')
        gout = re.sub(r'(?m)^#', '###', gout)   # demote the query's headings under this section
        add_section('Graph neighbourhood', f'`scripts/graph-query.py --node {start_node} --depth {a.depth}`:\n\n' + gout.rstrip()
                    + '\n\nMore: `generated/graph/REPO_MAP.md`, `generated/graph/<community>.md`', 2, 'generated/graph/REPO_MAP.md')
    else:
        add_section('Graph neighbourhood', '_(generated/graph/graph.json missing - run scripts/gen-graph.py)_', 2)

    # Contracts
    if file:
        api_refs = get_list(fm, 'api')
        event_refs = get_list(fm, 'events')
        oa = os.path.join(repo, 'generated/openapi/backend.yaml')
        parts = []
        if api_refs and os.path.isfile(oa):
            oa_text = read_text_or_empty(oa)
            sources.append('generated/openapi/backend.yaml')
            for ref in api_refs:
                p = re.sub(r'^/api/v\d+', '', re.split(r'\s+', ref)[-1], flags=re.I)
                m = re.search(r'(?ms)^  ' + re.escape(p) + r':\s*\r?\n(.*?)(?=^  /|^\S)', oa_text)
                if m:
                    block = [l.rstrip() for l in split_lines(m.group(1))
                             if re.search(r'^\s{4}(get|post|put|patch|delete):|operationId|summary:|\$ref: .#/components/(schemas|parameters)|in: (query|path)|- name:', l, re.I)]
                    parts.append(f'### `{ref}`\n```yaml\n' + '\n'.join(block) + '\n```')
                else:
                    parts.append(f'### `{ref}` - _not found in the contract (verify the path)_')
        if event_refs:
            parts.append('**Kafka**: ' + ', '.join(f'`{e}`' for e in event_refs) + ' - channels in `generated/asyncapi/backend.yaml`; producers/consumers in `generated/be/events.md`')
        add_section('Contracts', '\n\n'.join(parts), 4, 'generated/openapi/backend.yaml')

    # Data
    if file:
        tables = get_list(fm, 'tables')
        schema = os.path.join(repo, 'generated/be/db-schema.md')
        parts = []
        if tables and os.path.isfile(schema):
            st = read_text_or_empty(schema)
            sources.append('generated/be/db-schema.md')
            for t in tables:
                m = re.search(r'(?ms)^## `' + re.escape(t) + r'`\s*\r?\n(.*?)(?=^## |\Z)', st)
                parts.append(f'### `{t}`\n' + m.group(1).strip() if m else f'### `{t}` - _not in db-schema.md_')
        # named datasets (seeds, test fixtures) that touch these tables - cite them by name instead of describing rows
        ds_file = os.path.join(repo, 'generated/be/datasets.md')
        if tables and os.path.isfile(ds_file):
            ds_rows = []
            tables_ci = set(t.lower() for t in tables)
            for line in split_lines(read_text_or_empty(ds_file)):
                if not re.match(r'^\| `[a-z0-9\-]+` \| (seed|fixture) \|', line, re.I):
                    continue
                cells = line.lstrip('|').split('|')
                touched = re.findall(r'`([a-z_]+)`', cells[3])
                if any(x.lower() in tables_ci for x in touched):
                    ds_rows.append(f'- {cells[0].strip()} ({cells[1].strip()}): {cells[2].strip()} - tables {cells[3].strip()}')
            ds_rows = ds_rows[:8]
            if ds_rows:
                sources.append('generated/be/datasets.md')
                parts.append('### Datasets touching these tables\n(cite by name: `Given dataset "<name>" is loaded`; full list and sample rows in `generated/be/datasets.md`)\n' + '\n'.join(ds_rows))
        add_section('Data', '\n\n'.join(parts), 4, 'generated/be/db-schema.md')

    # Related work items and tests
    if file and kind == 'spec':
        sid = os.path.splitext(os.path.basename(file))[0]
        parts = []
        wi = os.path.join(repo, f'work-items/{sid}.yml')
        if os.path.isfile(wi):
            sources.append(f'work-items/{sid}.yml')
            parts.append(f'**work-items/{sid}.yml**\n' + '\n'.join(select_lines(wi, r'^\s*(- id:|\s+summary:|^questions:|^\s+- ")')))
        ft = os.path.join(repo, f'test-design/features/{sid}.feature')
        if os.path.isfile(ft):
            sources.append(f'test-design/features/{sid}.feature')
            parts.append(f'**test-design/features/{sid}.feature**\n' + '\n'.join(select_lines(ft, r'^\s*(@|Scenario)', strip_right=False)))
        add_section('Related work items and tests', '\n\n'.join(parts), 3)

    # Legacy pages
    legacy_dir = os.path.join(repo, 'confluence-import')
    if os.path.isdir(legacy_dir):
        needle = []
        if file:
            needle.append(os.path.splitext(os.path.basename(file))[0])
            needle += [w for w in re.split(r'[^a-z0-9]+', get_val(fm, 'title').lower()) if len(w) >= 5]
        else:
            needle.append(re.sub(r'^\w+:', '', task))
        parts = []
        for p in walk_files(legacy_dir, '*.md'):
            if os.path.basename(p).lower() == 'readme.md' or re.search(r'(^|/)_done/', rel(repo, p), re.I):
                continue
            pt = read_text_or_empty(p)
            low = pt.lower()
            hits = [n for n in needle if n and n.lower() in low]
            if len(hits) >= min(2, len(needle)):
                head = [l for l in split_lines(pt) if l.strip()][:5]
                parts.append(f"### `{rel(repo, p)}` (matches: {', '.join(hits)}) - legacy, UNVERIFIED\n" + '\n'.join(f'> {l}' for l in head))
        add_section('Legacy pages', '\n\n'.join(parts), 5, 'confluence-import/')

    # ---------- 3. budget ----------
    header = f"# Context pack: {task} - {rel(repo, file) if file else node} - {badge(fm, now) if fm else 'n/a'} - built {now.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
    fixed = 12  # header + footer allowance
    truncated = []
    budget_left = budget - fixed
    for s in sorted(sections, key=lambda s: s['Rank']):
        n = len(split_lines(s['Content'])) + 2
        if n <= budget_left:
            budget_left -= n
            continue
        allow = max(0, budget_left - 2)
        s['Content'] = '\n'.join(split_lines(s['Content'])[:allow]) + f"\n... (truncated: see `{s['See'] if s['See'] else 'the files listed under Sources'}`)"
        truncated.append(s['Title'])
        budget_left = 0
    order = ('Subject', 'Spec', 'Calculation', 'Calculations', 'Flows', 'Graph neighbourhood', 'Contracts', 'Data', 'Related work items and tests', 'Legacy pages')
    out = [header + '\n']
    for t in order:
        s = next((x for x in sections if x['Title'] == t), None)
        if s:
            out.append(f'## {t}\n' + s['Content'] + '\n\n')
    out.append('## Sources and limits\n')
    out.append('- files: ' + ', '.join(f'`{s}`' for s in dict.fromkeys(sources)) + '\n')
    out.append(f"- truncated sections: {', '.join(truncated) if truncated else 'none'} (budget {budget} lines)\n")
    out.append('- rule: open nothing else unless a question above is unanswered; then open only the `file:line` named above in `../backend` or `../frontend`. Record new facts as Open questions / Change log, never as silent assumptions.\n')
    result = ''.join(out)

    slug = re.sub(r'[^a-z0-9]+', '-', task.lower()).strip('-')[:60]
    out_path = os.path.join(repo, a.out_dir, f'{slug}.md')
    write_text(out_path, result)
    line_count = len(split_lines(result))
    if a.print_:
        sys.stdout.write(result + '\n')
    print(f"context pack: {rel(repo, out_path)} ({line_count} lines, budget {budget}{', truncated: ' + ', '.join(truncated) if truncated else ''})")


if __name__ == '__main__':
    main()
