#!/usr/bin/env python3
"""Builds a task-scoped context pack for an agent (analyst, spec-writer, test-designer, calc-auditor): the subject
whole (spec, calculation, flow or context overview with its trust badge), the computed sections no file shows (depth-2
graph neighbourhood with file:line, contract operations, table pages, datasets, the merged slice of several subjects)
and the linked documents as POINTERS (one line each with path and badge: the calculations the spec uses, the flows it
takes part in, imported pages that mention it) to open through the indexes when the task needs them. No libraries.

The pack is the recorded slice a task starts from: what the agent read first, what it was pointed at, which files at
which generated-at dates. A `## Contents` section at the top gives the line range of every section and part so the
reader opens the part the task needs and, after a rebuild, only what came back. Every `## ` heading is a pack section
(embedded documents are demoted). Section order / ranks: .github/skills/task-context/references/pack-anatomy.md;
procedure: .github/skills/task-context/SKILL.md (six steps, the same for a question and a change request).

Subject (--task, repeatable; several subjects give ONE pack with the shared sections merged and deduplicated):
  spec ID (P1-001), calculation name (stress_test_monthly), flow (flows/<name>.md, flow:<name> or FLOW-<name>: the
  flow body, then for every spec it names the Summary and the rules the flow cites, graph impact of its code_refs),
  context (context:<name> from contexts.yml: its specs, endpoints, tables, calculations, topics, classes by layer, FE
  pages, flows, proposed contracts and the architecture lines about it - the overview for placing new work), graph
  node id (topic:..., table:..., feature:...), or free text (matched against title / description / tags / aliases of
  specs, calculations and flows with glossary aliases applied; a fallback - for a request in free text read
  generated/catalogue.md first and name the subjects yourself).
Budget: by default none - the pack holds everything its subjects need (each item is bounded on its own: a table page
60 lines, an imported page 2, a graph neighbourhood 80 per subject, a linked document one pointer line plus the flow
steps that name the subject). --budget N caps the pack for a tool with a context limit; lower-ranked sections are
truncated first and the footer names them. No agent procedure needs it any more.
Examples:
  python3 scripts/context-pack.py --task P1-001
  python3 scripts/context-pack.py --task P1-002 --task STR-001 --task flows/session-inputs-recalculation.md
  python3 scripts/context-pack.py --task context:cover --print
  python3 scripts/context-pack.py --task "transport mode toggle on the stress table" --budget 300 --print"""
import argparse
import json
import os
import re
import subprocess
import sys

from _common import (repo_root, read_text_or_empty, write_text, rel, get_fm, get_val, get_list, badge, now_utc,
                     walk_files, like, sort_key, split_lines, utf8_stdout)

# words of a free-text request that never identify a subject (the >= 4 characters filter drops the shorter ones)
STOPWORDS = set('''about able after again also another anything around because been before being between both
cannot could does done during each either else every from have having into just least like made make makes making
more most much must need needed needs never only other over same several shall should show shown shows since some
something such than that their them then there these they things this those through under until upon user users
very want wanted wants what when where whether which while will with within without would your'''.split())

PER_SUBJECT = ('Subject', 'Spec', 'Calculation', 'Flow', 'Context overview', 'Specs in the flow')
ORDER = ('Subject', 'Spec', 'Calculation', 'Flow', 'Context overview', 'Specs in the flow', 'Calculations', 'Flows',
         'Graph neighbourhood', 'Contracts', 'Data', 'Related work items and tests', 'Imported pages')


def get_section(text, heading):
    m = re.search(r'(?ms)^##\s+' + re.escape(heading) + r'[^\r\n]*\r?\n(.*?)(?=^##\s|\Z)', text)
    return m.group(1).rstrip() if m else ''


def body_of(text):
    return re.sub(r'(?s)\A﻿?---\r?\n.*?\r?\n---\r?\n', '', text).strip()


def demote(text, levels):
    """Push every heading of an embedded document down `levels`, so that `## ` in the pack always means a pack section."""
    return re.sub(r'(?m)^(#{1,})\s', lambda m: '#' * (len(m.group(1)) + levels) + ' ', text)


def one_line(text, limit=160):
    """A frontmatter description squeezed to one line for a pointer."""
    t = re.sub(r'\s+', ' ', text or '').strip().strip('"\'')
    return t if len(t) <= limit else t[:limit - 1].rstrip() + '…'


def step_items(text):
    """The numbered or bulleted items of a flow's Steps section, each with its continuation lines, fenced blocks
    (sequence diagrams) skipped - the unit a pointer quotes when it names the subject."""
    items = []
    fence = False
    for line in split_lines(text):
        if line.strip().startswith('```'):
            fence = not fence
            continue
        if fence or line.startswith('#'):
            continue
        if re.match(r'^\s*(\d+\.|[-*])\s', line):
            items.append(line.strip())
        elif line.strip() and items:
            items[-1] += ' ' + line.strip()
    return items


def select_lines(path, pattern, strip_right=True):
    out = []
    for line in split_lines(read_text_or_empty(path)):
        if re.search(pattern, line, re.I):
            out.append(line.rstrip() if strip_right else line.strip())
    return out


def load_contexts(repo):
    """contexts.yml: name -> spec prefix, FE pages, BE prefixes, the comment lines right above the entry."""
    contexts = {}
    note = []
    for line in split_lines(read_text_or_empty(os.path.join(repo, 'contexts.yml'))):
        m = re.match(r'^\s{2}([\w-]+):\s*\{(.*)\}', line)
        cm = re.match(r'^\s{2}#\s*(.*)$', line)
        if cm:
            note.append(cm.group(1).strip())
            continue
        if not m:
            note = []
            continue
        c, body = m.group(1), m.group(2)
        sp = re.search(r'spec:\s*([\w-]+)', body)
        fe = re.search(r'fe:\s*\[([^\]]*)\]', body)
        be = re.search(r'be:\s*\[([^\]]*)\]', body)
        contexts[c] = {'spec': sp.group(1) if sp else '', 'note': ' '.join(note),
                       'fe': [x.strip().strip('"\'') for x in (fe.group(1).split(',') if fe else []) if x.strip()],
                       'be': [x.strip().strip('"\'') for x in (be.group(1).split(',') if be else []) if x.strip()]}
        note = []
    return contexts


def glossary_terms(repo):
    """domain/glossary.md rows: (term, [aliases], used-in cell)."""
    terms = []
    header_seen = False
    for line in split_lines(read_text_or_empty(os.path.join(repo, 'domain', 'glossary.md'))):
        if re.match(r'^\|\s*Term\s*\|', line, re.I):
            header_seen = True
            continue
        if not header_seen or not line.startswith('|') or re.match(r'^\|\s*-', line):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 3 and cells[0]:
            aliases = [a.strip().strip('`') for a in cells[2].split(',') if a.strip()]
            terms.append((cells[0], aliases, cells[3] if len(cells) > 3 else ''))
    return terms


def openapi_summaries(repo):
    """operationId -> summary from generated/openapi/backend.yaml (line scan, no YAML library)."""
    out = {}
    op = None
    for line in split_lines(read_text_or_empty(os.path.join(repo, 'generated/openapi/backend.yaml'))):
        m = re.match(r'^\s+operationId:\s*(\S+)', line)
        if m:
            op = m.group(1).strip('"\'')
            out.setdefault(op, '')
            continue
        m = re.match(r'^\s+summary:\s*(.+)$', line)
        if m and op and not out.get(op):
            out[op] = m.group(1).strip().strip('"\'')
        if re.match(r'^  /', line) or re.match(r'^\S', line):
            op = None
    return out


def build_subject(task, repo, here, now, budget, depth, contexts, glossary):
    """One subject -> its sections (title, content, rank, see-also, parts for merging), sources and header bits."""
    sections = []
    sources = []
    pointed = []   # documents the pack points at (one line each) instead of copying: the agent opens them through the indexes

    def add_section(title, content, rank, see_also='', parts=None):
        if not content:
            content = '_(none)_'
        sections.append({'Title': title, 'Content': content.rstrip(), 'Rank': rank, 'See': see_also,
                         'Parts': parts if parts else []})

    # ---------- 1. resolve the subject ----------
    specs = [f for f in walk_files(os.path.join(repo, 'features'), '*.md') if not re.match(r'^(_?template|index|conventions)\.md$', os.path.basename(f), re.I)]
    calc_dir = os.path.join(repo, 'domain/calculations')
    calcs = [os.path.join(calc_dir, x) for x in sorted(os.listdir(calc_dir), key=str.lower)
             if x.lower().endswith('.md') and not re.match(r'^(_?template|index)\.md$', x, re.I)] if os.path.isdir(calc_dir) else []
    flow_dir = os.path.join(repo, 'flows')
    flows = [os.path.join(flow_dir, x) for x in sorted(os.listdir(flow_dir), key=str.lower)
             if x.lower().endswith('.md') and not re.match(r'^(_?template|index)\.md$', x, re.I)] if os.path.isdir(flow_dir) else []
    kind = ''
    file = None
    node = ''
    candidates = []
    glossary_notes = []
    ctx_name = ''
    fm_ = re.match(r'^(?:flows/(.+?)\.md|flow:(.+)|FLOW-(.+))$', task, re.I)
    cm_ = re.match(r'^context:([\w-]+)$', task, re.I)
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
    elif fm_ and os.path.isfile(os.path.join(repo, 'flows', (fm_.group(1) or fm_.group(2) or fm_.group(3)) + '.md')):
        kind = 'flow'
        file = os.path.join(repo, 'flows', (fm_.group(1) or fm_.group(2) or fm_.group(3)) + '.md')
    elif cm_ and cm_.group(1) in contexts:
        kind = 'context'
        ctx_name = cm_.group(1)
        node = f'context:{ctx_name}'
    elif re.match(r'^(context|feature|endpoint|route|class|hook|component|topic|table|spec):', task, re.I):
        kind = 'node'
        node = task
    else:
        # free text: score concepts by token hits (title / aliases / id count double, description / tags / contexts
        # once); a glossary alias in the text (customer -> Client, lane -> Corridor) adds the term's words and gives
        # the concepts the glossary lists the term under a bonus - only for an alias, a term typed as such is a token already
        low = task.lower()
        tokens = [t for t in re.split(r'[^a-z0-9_\-]+', low) if len(t) >= 4 and t not in STOPWORDS]
        bonus = {}
        for term, aliases, used in glossary:
            hit = next((a for a in [term] + aliases if len(a) >= 4 and re.search(r'(?<![a-z0-9])' + re.escape(a.lower()) + r'(?![a-z0-9])', low)), None)
            if not hit or hit.lower() == term.lower():
                continue
            glossary_notes.append(f'{hit} -> {term}')
            tokens += [t for t in re.split(r'[^a-z0-9_\-]+', term.lower()) if len(t) >= 4 and t not in tokens]
            for u in re.findall(r'([A-Z][A-Z0-9]*-\d{3})|`([a-z][a-z0-9_]+)`', used):
                bonus[(u[0] or u[1]).lower()] = bonus.get((u[0] or u[1]).lower(), 0) + 1
        tokens = list(dict.fromkeys(tokens))
        scored = []
        for f in specs + calcs + flows:
            fm = get_fm(read_text_or_empty(f))
            name = os.path.splitext(os.path.basename(f))[0]
            strong = ' '.join([get_val(fm, 'title'), get_val(fm, 'aliases'), name]).lower()
            weak = ' '.join([get_val(fm, 'description'), get_val(fm, 'tags'), get_val(fm, 'contexts')]).lower()
            scored.append((f, sum(2 if t in strong else 1 if t in weak else 0 for t in tokens) + bonus.get(name.lower(), 0)))
        best = sorted((x for x in scored if x[1] > 0), key=lambda x: (-x[1], sort_key(rel(repo, x[0]))))
        if not best:
            print(f"nothing matches '{task}' - read generated/catalogue.md and give a spec ID, calculation name, flow, context:<name> or graph node id", file=sys.stderr)
            sys.exit(1)
        file = best[0][0]
        folder = os.path.dirname(file)
        kind = 'calculation' if re.search(r'calculations$', folder, re.I) else 'flow' if re.search(r'(^|[\\/])flows$', folder, re.I) else 'spec'
        node = '' if kind == 'flow' else f'spec:{os.path.splitext(os.path.basename(file))[0]}'
        candidates = [f'{rel(repo, f)} (score {s})' for f, s in best[1:4]]

    # ---------- 2. assemble sections (rank = truncation priority, 1 never) ----------
    fm = ''
    text = ''
    if file:
        text = read_text_or_empty(file)
        fm = get_fm(text)
        sources.append(rel(repo, file))

    # Subject
    subj = [f'- task: `{task}`', f"- resolved: **{kind}** {'`' + rel(repo, file) + '`' if file else '`' + node + '`'}"]
    if kind == 'context':
        cv = contexts[ctx_name]
        subj[-1] = f"- resolved: **context** `{ctx_name}` (`contexts.yml`): spec prefix {cv['spec'] or '-'}; BE class-name prefixes {', '.join(cv['be']) or '-'}; FE pages {', '.join(cv['fe']) or '-'}"
        if cv['note']:
            subj.append(f"- note: {cv['note']}")
    if file:
        subj.append(f"- title: {get_val(fm, 'title')}")
        subj.append(f"- badge: **{badge(fm, now)}** · status: {get_val(fm, 'status')} · last_verified: {get_val(fm, 'last_verified')} · stale_after: {get_val(fm, 'stale_after')} · generated: {get_val(fm, 'generated')}")
        own = get_val(fm, 'owners')
        if own:
            subj.append(f'- owners: {own}')
    if kind == 'flow':
        subj.append(f"- contexts: {', '.join(get_list(fm, 'contexts'))} · specs: {', '.join(get_list(fm, 'specs'))}"
                    + (f" · channels: {', '.join(get_list(fm, 'channels'))}" if get_list(fm, 'channels') else ''))
    if glossary_notes:
        subj.append(f"- glossary: {'; '.join(glossary_notes)}")
    if candidates:
        subj.append(f"- candidates: {'; '.join(candidates)}  <- free text matched several concepts; confirm the subject (generated/catalogue.md lists them all)")
    add_section('Subject', '\n'.join(subj), 1)

    # Spec / calculation / flow body
    if file:
        body = re.sub(r'(?m)\A# [^\n]*\n', '', body_of(text), count=1).strip()   # the title line: the Subject already carries it
        lines = split_lines(body)
        # The document's own headings sit one level under the pack section (`### Business rules` under `## Spec`);
        # merge() pushes them one more level under the `### <task>` block of a multi-subject pack.
        if kind == 'spec' and (len(lines) > 200 or (budget and len(lines) > budget * 0.6)):
            keep = []
            # UI flow stays in: it is the section a "what does the screen show or allow" question reads
            for h in ('Summary', 'Actors', 'Business rules', 'UI flow', 'API', 'Data', 'Calculations', 'Edge cases', 'Open questions'):
                m = re.search(r'(?ms)^(##\s+' + re.escape(h) + r'[^\r\n]*)\r?\n(.*?)(?=^##\s|\Z)', body)
                if m:
                    keep.append(m.group(1) + '\n' + m.group(2).rstrip())
            add_section('Spec', demote('\n\n'.join(keep), 1) + f'\n\n... (reduced to key sections: see `{rel(repo, file)}`)', 1, rel(repo, file))
        elif kind == 'calculation':
            # The `# Computation` block (sanctioned code shape, a level-1 heading in the concept) is kept at the same level
            keep = []
            for h in ('Purpose', 'Inputs', 'Outputs', 'Formula', 'Computation', 'Conventions', 'Worked examples', 'Audit', 'Open questions'):
                m = re.search(r'(?ms)^#{1,2}\s+(' + re.escape(h) + r'[^\r\n]*)\r?\n(.*?)(?=^#{1,2}\s|\Z)', body)
                if m:
                    keep.append('### ' + m.group(1) + '\n' + demote(m.group(2).rstrip(), 1))
            add_section('Calculation', '\n\n'.join(keep), 1, rel(repo, file))
        elif kind == 'flow':
            if len(lines) > 200 or (budget and len(lines) > budget * 0.6):
                keep = []
                for h in ('Purpose', 'Questions this document answers', 'Trigger', 'Participants', 'Steps', 'Data and state changes',
                          'Failure behaviour', 'Invariants and assumptions', 'Open questions'):
                    m = re.search(r'(?ms)^(##\s+' + re.escape(h) + r'[^\r\n]*)\r?\n(.*?)(?=^##\s|\Z)', body)
                    if m:
                        keep.append(m.group(1) + '\n' + m.group(2).rstrip())
                add_section('Flow', demote('\n\n'.join(keep), 1) + f'\n\n... (reduced to key sections: see `{rel(repo, file)}`)', 1, rel(repo, file))
            else:
                add_section('Flow', demote(body, 1), 1, rel(repo, file))
        else:
            add_section('Spec', demote(body, 1), 1, rel(repo, file))

    # Flow: the specs it composes - Summary and the rules the flow cites ("P1-001 BR-8", "BR-STR-001-3")
    if kind == 'flow':
        cited = {}
        for m in re.finditer(r'\b([A-Z][A-Z0-9]*-\d{3})\s+(BR-\d+(?:\s*,\s*BR-\d+)*(?:\s*(?:,\s*)?and\s+BR-\d+)?)', text):
            for n in re.findall(r'BR-(\d+)', m.group(2)):
                cited.setdefault(m.group(1), set()).add(int(n))
        for m in re.finditer(r'\bBR-([A-Z][A-Z0-9]*-\d{3})-(\d+)\b', text):
            cited.setdefault(m.group(1), set()).add(int(m.group(2)))
        parts = []
        for sid in get_list(fm, 'specs'):
            sf = next((f for f in specs if os.path.splitext(os.path.basename(f))[0] == sid), None)
            if not sf:
                parts.append({'Key': sid, 'Text': f'### {sid}\n_(no spec file)_'})
                continue
            st = read_text_or_empty(sf)
            sfm = get_fm(st)
            sources.append(rel(repo, sf))
            block = [f"### {sid} — {get_val(sfm, 'title')} (`{rel(repo, sf)}`) - badge: {badge(sfm, now)}"]
            summary = get_section(st, 'Summary')
            if summary:
                block.append('**Summary**\n' + summary)
            rules = get_section(st, 'Business rules')
            wanted = cited.get(sid, set())
            picked = []
            if rules and wanted:
                cur = None
                for line in split_lines(rules):
                    bm = re.match(r'^\s*[-*]\s+\*\*BR-' + re.escape(sid) + r'-(\d+)\*\*', line)
                    if bm:
                        cur = int(bm.group(1)) in wanted
                    elif re.match(r'^\s*[-*]\s', line) or re.match(r'^#', line):
                        cur = False
                    if cur:
                        picked.append(line.rstrip())
            if picked:
                block.append(f"**Rules the flow cites** (BR-{sid}-{', '.join(str(n) for n in sorted(wanted))})\n" + '\n'.join(picked))
            elif wanted:
                block.append(f"**Rules the flow cites**: BR-{sid}-{', '.join(str(n) for n in sorted(wanted))} - _not found under `## Business rules` of the spec (renumbered?)_")
            else:
                block.append('_(the flow cites no rule of this spec; its pack has them all)_')
            parts.append({'Key': sid, 'Text': '\n\n'.join(block)})
        add_section('Specs in the flow', '\n\n'.join(p['Text'] for p in parts), 2, 'features/', parts)

    # Calculations linked from the spec: pointers. The concept (formula, worked examples, audit) is one hop away
    # through domain/calculations/index.md; a calculation that is a subject itself is whole under `## Calculation`.
    if kind == 'spec' and file and get_list(fm, 'calculations'):
        parts = [{'Key': 'intro:Calculations',
                  'Text': '_Pointers: open the concept for Formula, Conventions, Worked examples and Audit (task-context step 4); '
                          'a calculation named as `--task` is whole under `## Calculation`._'}]
        for c in (re.sub(r'^/', '', x) for x in get_list(fm, 'calculations')):
            cp = os.path.join(repo, c)
            if not os.path.isfile(cp):
                parts.append({'Key': c, 'Text': f'- `{c}` - _(missing file)_'})
                continue
            cfm = get_fm(read_text_or_empty(cp))
            pointed.append(c)
            name = os.path.splitext(os.path.basename(c))[0]
            desc = one_line(get_val(cfm, 'description'))
            parts.append({'Key': c, 'Text': f"- `{name}` — {get_val(cfm, 'title')} (`{c}`) - badge: {badge(cfm, now)}" + (f' - {desc}' if desc else '')})
        add_section('Calculations', '\n'.join(p['Text'] for p in parts), 2, 'domain/calculations/index.md', parts)

    # Flows this spec takes part in: listed in the spec (`flows:`) or naming the spec in their own `specs:` (both directions)
    if kind == 'spec' and file:
        spec_id = os.path.splitext(os.path.basename(file))[0]
        flow_refs = [re.sub(r'^/', '', x) for x in get_list(fm, 'flows')]
        if os.path.isdir(flow_dir):
            for ff in sorted(os.listdir(flow_dir), key=str.lower):
                if not ff.lower().endswith('.md') or re.match(r'^(_template|index)\.md$', ff, re.I):
                    continue
                if spec_id in get_list(get_fm(read_text_or_empty(os.path.join(flow_dir, ff))), 'specs'):
                    flow_refs.append(rel(repo, os.path.join(flow_dir, ff)))
        flow_refs = list(dict.fromkeys(flow_refs))
        if flow_refs:
            # pointers, each with the steps of the flow that name this spec (the cross-context behaviour the spec does
            # not show); the whole flow - trigger, participants, invariants - is one hop away through flows/index.md
            parts = [{'Key': 'intro:Flows',
                      'Text': '_Pointers with the steps that name the subject: open the flow for Trigger, Participants, Data and state '
                              'changes, Failure behaviour and Invariants (task-context step 4); a flow named as `--task` is whole under `## Flow`._'}]
            for f in flow_refs:
                fp = os.path.join(repo, f)
                if not os.path.isfile(fp):
                    parts.append({'Key': f, 'Text': f'- `{f}` - _(missing file)_'})
                    continue
                ft = read_text_or_empty(fp)
                ffm = get_fm(ft)
                pointed.append(f)
                steps = [s for s in step_items(get_section(ft, 'Steps')) if re.search(r'(?<![\w-])' + re.escape(spec_id) + r'(?![\w-])', s)][:6]
                line = f"- {get_val(ffm, 'title')} (`{f}`) - badge: {badge(ffm, now)} - specs: {', '.join(get_list(ffm, 'specs'))}"
                if steps:
                    line += '\n' + '\n'.join('  ' + one_line(s, 220) for s in steps)
                parts.append({'Key': f, 'Text': line})
            add_section('Flows', '\n'.join(p['Text'] for p in parts), 3, 'flows/index.md', parts)

    # Context overview: what the context already has, for placing new work in it
    graph_json = os.path.join(repo, 'generated/graph/graph.json')
    if kind == 'context':
        cv = contexts[ctx_name]
        parts = []
        ctx_specs = [f for f in specs if get_val(get_fm(read_text_or_empty(f)), 'context') == ctx_name]
        if ctx_specs:
            rows = []
            for f in sorted(ctx_specs, key=lambda p: sort_key(os.path.basename(p))):
                sfm = get_fm(read_text_or_empty(f))
                rows.append(f"- {os.path.splitext(os.path.basename(f))[0]} — {get_val(sfm, 'title')} (`{rel(repo, f)}`, {badge(sfm, now)}; aliases: {get_val(sfm, 'aliases')})")
            parts.append('**Specs** (build a pack per ID for rules and contracts)\n' + '\n'.join(rows))
        else:
            parts.append(f"**Specs**: _none yet (code only)_ - the first spec of a context is its main screen, `{cv['spec'] or '<PREFIX>'}-001` "
                         f"(`features/conventions.md`, prompt `spec-skeleton-from-graph`); until then the graph below and `generated/graph/{ctx_name}.md` are the description")
        ctx_flows = [f for f in flows if ctx_name in get_list(get_fm(read_text_or_empty(f)), 'contexts')]
        if ctx_flows:
            parts.append('**Flows this context takes part in**\n' + '\n'.join(
                f"- `{rel(repo, f)}` {get_val(get_fm(read_text_or_empty(f)), 'title')}" for f in ctx_flows))
        if os.path.isfile(graph_json):
            g = json.loads(read_text_or_empty(graph_json))
            by_id = {n['id']: n for n in g['nodes']}
            edges = g['edges']
            summaries = openapi_summaries(repo)
            ctx_classes = {e['to'] for e in edges if e['from'] == node and e['rel'] == 'contains'}
            ctx_classes |= {n['id'] for n in g['nodes'] if n.get('kind') == 'class' and n.get('community') == ctx_name}
            eps = sorted((by_id[e['to']] for e in edges if e['from'] == node and e['rel'] == 'exposes' and e['to'] in by_id), key=lambda n: sort_key(n['label']))
            if eps:
                rows = []
                for n in eps:
                    op = re.search(r'operationId (\S+?);?(\s|$)', n.get('note', ''))
                    opid = op.group(1) if op else ''
                    rows.append(f"- `{n['label']}` {opid}{' - ' + summaries[opid] if opid and summaries.get(opid) else ''} (`{n.get('location', '')}`)")
                parts.append('**Endpoints** (a new operation of this context goes next to these; `generated/openapi/backend.yaml`)\n' + '\n'.join(rows))
            else:
                parts.append('**Endpoints**: _none in the graph_')
            tabs = sorted((by_id[e['to']] for e in edges if e['from'] == node and e['rel'] == 'owns' and e['to'] in by_id), key=lambda n: sort_key(n['label']))
            if tabs:
                parts.append('**Tables owned** (`generated/be/db/schema/tables/<table>.md`)\n' + '\n'.join(
                    f"- `{n['label']}` - {n.get('note', '')}" for n in tabs))
            calc_rows = []
            for e in edges:
                if e['rel'] == 'implemented-by' and e['to'] in ctx_classes and by_id.get(e['from'], {}).get('kind') == 'calculation':
                    cname = e['from'].split(':', 1)[1]
                    cp = os.path.join(repo, f'domain/calculations/{cname}.md')
                    cfm = get_fm(read_text_or_empty(cp))
                    calc_rows.append(f"- `{cname}` — {get_val(cfm, 'title')} ({badge(cfm, now) if cfm else 'no concept'}; implemented by `{e['to']}`)")
            if calc_rows:
                parts.append('**Calculations implemented here** (`domain/calculations/`; a new metric starts from their inputs and outputs)\n' + '\n'.join(sorted(set(calc_rows), key=sort_key)))
            topic_rows = []
            for e in edges:
                if e['rel'] == 'produces' and e['from'] in ctx_classes and e['to'].startswith('topic:'):
                    topic_rows.append(f"- produces `{e['to'].split(':', 1)[1]}` (`{e['from']}`)")
                if e['rel'] == 'consumed-by' and e['to'] in ctx_classes and e['from'].startswith('topic:'):
                    topic_rows.append(f"- consumes `{e['from'].split(':', 1)[1]}` (`{e['to']}`)")
            if topic_rows:
                parts.append('**Kafka topics** (`generated/be/events.md`)\n' + '\n'.join(sorted(set(topic_rows), key=sort_key)))
            by_layer = {}
            for cid in ctx_classes:
                n = by_id.get(cid)
                if not n:
                    continue
                layer = (n.get('note', '') or '').split(';')[0].strip() or 'other'
                by_layer.setdefault(layer, []).append(n['label'])
            if by_layer:
                parts.append('**Classes by layer** (the layer a new class joins; `file:line` in the graph section and `generated/be/components.md`)\n' + '\n'.join(
                    f"- {layer}: {', '.join(sorted(names, key=sort_key))}" for layer, names in sorted(by_layer.items(), key=lambda kv: sort_key(kv[0]))))
            feats = sorted((n for n in g['nodes'] if n.get('kind') == 'feature' and n.get('community') == ctx_name), key=lambda n: sort_key(n['label']))
            if feats:
                rows = []
                for n in feats:
                    routes = sorted((e['from'].split(':', 1)[1] for e in edges if e['to'] == n['id'] and e['rel'] == 'renders' and e['from'].startswith('route:')), key=sort_key)
                    hooks = sum(1 for e in edges if e['from'] == n['id'] and e['rel'] == 'contains' and e['to'].startswith('hook:'))
                    comps = sum(1 for e in edges if e['from'] == n['id'] and e['rel'] == 'contains' and e['to'].startswith('component:'))
                    rows.append(f"- `{n['label']}` routes {', '.join('`' + r + '`' for r in routes) or '-'}; {hooks} hook(s), {comps} component(s) (`{n.get('location', '')}`)")
                parts.append('**FE pages** (`generated/fe/`)\n' + '\n'.join(rows))
            elif cv['fe']:
                parts.append(f"**FE pages**: {', '.join(cv['fe'])} (not in the graph - FE maps stale?)")
            else:
                parts.append('**FE pages**: _none (no page of its own)_')
            class_names = {by_id[c]['label'] for c in ctx_classes if c in by_id}
            integ = os.path.join(repo, 'architecture/integrations.md')
            if os.path.isfile(integ):
                rows = [l.rstrip() for l in split_lines(read_text_or_empty(integ))
                        if l.startswith('|') and not re.match(r'^\|\s*-', l)
                        and (re.search(r'(?<![\w-])' + re.escape(ctx_name) + r'(?![\w-])', l, re.I) or any(('`' + c) in l or ('/' + c) in l for c in class_names))]
                if rows:
                    sources.append('architecture/integrations.md')
                    parts.append('**Integrations** (`architecture/integrations.md`)\n' + '\n'.join(rows[:10]))
            sources.append('generated/graph/graph.json')
        else:
            parts.append('_(generated/graph/graph.json missing - run scripts/gen-graph.py; endpoints, tables, classes and pages come from the graph)_')
        ov = os.path.join(repo, 'architecture/overview.md')
        if os.path.isfile(ov):
            rows = [l.rstrip() for l in split_lines(read_text_or_empty(ov)) if re.search(r'(?<![\w-])' + re.escape(ctx_name) + r'(?![\w-])', l, re.I) and not re.match(r'^\s*(```|#)', l)]
            if rows:
                sources.append('architecture/overview.md')
                parts.append('**Architecture overview lines** (`architecture/overview.md`)\n' + '\n'.join(f'> {r.strip()}' for r in rows[:12]))
        prop_dir = os.path.join(repo, 'contracts/proposed')
        if os.path.isdir(prop_dir):
            rows = []
            for f in sorted(os.listdir(prop_dir), key=str.lower):
                if not re.search(r'\.(ya?ml|json)$', f, re.I) or f.lower().startswith('_template'):
                    continue
                pt = read_text_or_empty(os.path.join(prop_dir, f))
                if re.search(r'tags:\s*\[[^\]]*(?<![\w-])' + re.escape(ctx_name) + r'(?![\w-])', pt, re.I) or (cv['spec'] and re.search(r'x-specs?:.*\b' + re.escape(cv['spec']) + r'-\d{3}', pt)):
                    t = re.search(r'(?m)^\s+title:\s*(.+)$', pt)
                    rows.append(f"- `contracts/proposed/{f}` {t.group(1).strip().strip(chr(34)) if t else ''}")
            if rows:
                parts.append('**Proposed contracts** (designed, not implemented; `contracts/conventions.md`)\n' + '\n'.join(rows))
        add_section('Context overview', '\n\n'.join(parts), 1, f'generated/graph/{ctx_name}.md')

    # Graph neighbourhood
    if os.path.isfile(graph_json):
        q = os.path.join(here, 'graph-query.py')

        def query(n):
            r = subprocess.run([sys.executable, q, '--graph', graph_json, '--node', n, '--depth', str(depth), '--max-lines', '80'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
            return r.stdout + r.stderr

        if kind == 'flow':
            refs = get_list(fm, 'code_refs')
            if refs:
                r = subprocess.run([sys.executable, q, '--graph', graph_json, '--files'] + refs + ['--depth', '1', '--max-lines', '80'],
                                   capture_output=True, text=True, encoding='utf-8', errors='replace')
                gout = re.sub(r'(?m)^#', '###', r.stdout + r.stderr)
                sources.append('generated/graph/graph.json')
                add_section('Graph neighbourhood', f'`scripts/graph-query.py --files <code_refs of the flow> --depth 1` ({len(refs)} file(s)):\n\n' + gout.rstrip()
                            + '\n\nMore: `generated/graph/REPO_MAP.md`, `generated/graph/<community>.md`', 2, 'generated/graph/REPO_MAP.md',
                            [{'Key': 'files:' + rel(repo, file), 'Text': ''}])
            else:
                add_section('Graph neighbourhood', '_(the flow lists no code_refs)_', 2)
        else:
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
                        fm2 = re.search(r'"id"\s*:\s*"(feature:[^"]+)",\s*"kind"\s*:\s*"feature",\s*"label"\s*:\s*"[^"]*",\s*"community"\s*:\s*"' + re.escape(ctx) + '"', gtext, re.I)
                        ctx_node = fm2.group(1) if fm2 else f'feature:{ctx}'
                    gout = f'(`{node}` not in graph - no `@docs` tag in code; neighbourhood of `{ctx_node}` instead)\n' + query(ctx_node)
                    start_node = ctx_node
            elif re.search('no node matches', gout, re.I) and kind == 'context':
                # FE-only context: no `context:` node, use its first page
                gtext = read_text_or_empty(graph_json)
                fm2 = re.search(r'"id"\s*:\s*"(feature:[^"]+)",\s*"kind"\s*:\s*"feature",\s*"label"\s*:\s*"[^"]*",\s*"community"\s*:\s*"' + re.escape(ctx_name) + '"', gtext, re.I)
                if fm2:
                    gout = f'(`{node}` not in graph - FE-only context; neighbourhood of `{fm2.group(1)}` instead)\n' + query(fm2.group(1))
                    start_node = fm2.group(1)
            sources.append('generated/graph/graph.json')
            gout = re.sub(r'(?m)^#', '###', gout)   # demote the query's headings under this section
            add_section('Graph neighbourhood', f'`scripts/graph-query.py --node {node} --depth {depth}`:\n\n' + gout.rstrip()
                        + '\n\nMore: `generated/graph/REPO_MAP.md`, `generated/graph/<community>.md`', 2, 'generated/graph/REPO_MAP.md',
                        [{'Key': 'node:' + start_node, 'Text': ''}])
    else:
        add_section('Graph neighbourhood', '_(generated/graph/graph.json missing - run scripts/gen-graph.py)_', 2)

    # Contracts
    if file:
        api_refs = get_list(fm, 'api')
        event_refs = get_list(fm, 'events') if kind != 'flow' else get_list(fm, 'channels')
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
                    parts.append({'Key': ref, 'Text': f'### `{ref}`\n```yaml\n' + '\n'.join(block) + '\n```'})
                else:
                    parts.append({'Key': ref, 'Text': f'### `{ref}` - _not found in the contract (verify the path)_'})
        if event_refs:
            # the AsyncAPI document is optional: a backend with Avro / JSON schemas only has events.md (topic, producer,
            # consumer, payload type and the path of its schema file) as the Kafka source
            where = ('channels in `generated/asyncapi/backend.yaml`; producers/consumers in `generated/be/events.md`'
                     if os.path.isfile(os.path.join(repo, 'generated/asyncapi/backend.yaml'))
                     else 'producers, consumers, payload types and schema file paths in `generated/be/events.md` (no AsyncAPI document)')
            # the payload of each topic: type and schema file from the events.md row, the field table from its
            # "Payload schemas" section (the collector copies the schema files to generated/asyncapi/schemas/)
            ev_text = read_text_or_empty(os.path.join(repo, 'generated/be/events.md'))
            payloads = []
            for e in event_refs:
                row = re.search(r'(?m)^\|\s*`' + re.escape(e) + r'`\s*\|[^\n]*?\|[^\n]*?\|\s*([^\n]*?)\s*\|\s*$', ev_text)
                pm = re.search(r'`(\w+)`(?:\s*\(([^)\s]+)\))?', row.group(1)) if row else None
                if not pm:
                    continue
                typ, path = pm.group(1), pm.group(2) or ''
                line = f'- `{e}`: payload `{typ}`' + (f' (`{path}`)' if path else '')
                block = re.search(r'(?ms)^### `' + re.escape(typ) + r'`[^\n]*\n(.*?)(?=^### |\Z)', ev_text)
                if block:
                    table = [l for l in split_lines(block.group(1)) if l.startswith('|')]
                    line += '\n' + '\n'.join('  ' + l for l in table) if table else ''
                if path and os.path.isfile(os.path.join(repo, path)) and path not in sources:
                    sources.append(path)
                payloads.append(line)
            if payloads and 'generated/be/events.md' not in sources:
                sources.append('generated/be/events.md')
            parts.append({'Key': 'kafka', 'Events': list(event_refs), 'Where': where,
                          'Text': '**Kafka**: ' + ', '.join(f'`{e}`' for e in event_refs) + ' - ' + where
                                  + ('\n\n' + '\n'.join(payloads) if payloads else '')})
        if kind != 'flow' or parts:
            add_section('Contracts', '\n\n'.join(p['Text'] for p in parts), 4, 'generated/openapi/backend.yaml', parts)

    # Data
    if file and kind != 'flow':
        tables = get_list(fm, 'tables')
        schema = os.path.join(repo, 'generated/be/db-schema.md')
        db_pages = os.path.join(repo, 'generated/be/db/schema/tables')
        parts = []
        if tables and os.path.isdir(db_pages):
            # database documentation pages (table comment, columns with comments, relations, constraints) beat the regex schema
            sources.append('generated/be/db/schema/tables/')
            st = read_text_or_empty(schema)
            for t in tables:
                page = os.path.join(db_pages, f'{t}.md')
                if os.path.isfile(page):
                    body = body_of(read_text_or_empty(page))
                    body = re.sub(r'(?m)^# .*\r?\n', '', body, count=1).strip()
                    body = re.sub(r'\]\(([\w-]+)\.md\)', r'](generated/be/db/schema/tables/\1.md)', body)
                    body = body.replace('(../erd/overview.mmd)', '(generated/be/db/schema/erd/overview.mmd)')
                    body = demote(body, 2)   # the page's `## Columns` / `## Relations` / `## Constraints` go under the table's `###`
                    lines = split_lines(body)
                    if len(lines) > 60:
                        body = '\n'.join(lines[:60]) + f'\n_... {len(lines) - 60} more line(s) in generated/be/db/schema/tables/{t}.md_'
                    parts.append({'Key': t, 'Text': f'### `{t}`\n' + body})
                else:
                    m = re.search(r'(?ms)^## `' + re.escape(t) + r'`\s*\r?\n(.*?)(?=^## |\Z)', st)
                    parts.append({'Key': t, 'Text': f'### `{t}`\n' + m.group(1).strip() if m else f'### `{t}` - _no table page and not in db-schema.md_'})
        elif tables and os.path.isfile(schema):
            st = read_text_or_empty(schema)
            sources.append('generated/be/db-schema.md')
            for t in tables:
                m = re.search(r'(?ms)^## `' + re.escape(t) + r'`\s*\r?\n(.*?)(?=^## |\Z)', st)
                parts.append({'Key': t, 'Text': f'### `{t}`\n' + m.group(1).strip() if m else f'### `{t}` - _not in db-schema.md_'})
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
                parts.append({'Key': 'datasets', 'Rows': ds_rows,
                              'Text': '### Datasets touching these tables\n(cite by name: `Given dataset "<name>" is loaded`; full list and sample rows in `generated/be/datasets.md`)\n' + '\n'.join(ds_rows)})
        add_section('Data', '\n\n'.join(p['Text'] for p in parts), 4, 'generated/be/db-schema.md', parts)

    # Related work items and tests
    if file and kind == 'spec':
        sid = os.path.splitext(os.path.basename(file))[0]
        parts = []
        wi = os.path.join(repo, f'work-items/{sid}.yml')
        if os.path.isfile(wi):
            sources.append(f'work-items/{sid}.yml')
            parts.append({'Key': wi, 'Text': f'**work-items/{sid}.yml**\n' + '\n'.join(select_lines(wi, r'^\s*(- id:|\s+summary:|^questions:|^\s+- ")'))})
        ft = os.path.join(repo, f'test-design/features/{sid}.feature')
        if os.path.isfile(ft):
            sources.append(f'test-design/features/{sid}.feature')
            parts.append({'Key': ft, 'Text': f'**test-design/features/{sid}.feature**\n' + '\n'.join(select_lines(ft, r'^\s*(@|Scenario)', strip_right=False))})
        add_section('Related work items and tests', '\n\n'.join(p['Text'] for p in parts), 3, '', parts)

    # Imported pages
    import_dir = os.path.join(repo, 'confluence-import')
    if os.path.isdir(import_dir):
        needle = []
        if file:
            needle.append(os.path.splitext(os.path.basename(file))[0])
            needle += [w for w in re.split(r'[^a-z0-9]+', get_val(fm, 'title').lower()) if len(w) >= 5]
        else:
            needle.append(re.sub(r'^\w+:', '', task))
        parts = []
        for p in walk_files(import_dir, '*.md'):
            if os.path.basename(p).lower() == 'readme.md' or re.search(r'(^|/)_done/', rel(repo, p), re.I):
                continue
            pt = read_text_or_empty(p)
            low = pt.lower()
            hits = [n for n in needle if n and n.lower() in low]
            if len(hits) >= min(2, len(needle)):
                # a pointer: path, what matched, the page title; the page itself is evidence to open, never a rule
                pfm = get_fm(pt)
                title = one_line(get_val(pfm, 'title')) or next((l.strip().lstrip('#').strip() for l in split_lines(body_of(pt)) if l.strip()), '')
                pointed.append(rel(repo, p))
                parts.append({'Key': rel(repo, p), 'Text': f"- `{rel(repo, p)}` (matches: {', '.join(hits)}) - imported, UNVERIFIED" + (f' - {title}' if title else '')})
        add_section('Imported pages', '\n'.join(p['Text'] for p in parts), 5, 'confluence-import/', parts)

    label = rel(repo, file) if file else node
    return {'task': task, 'kind': kind, 'file': file, 'label': label, 'badge': badge(fm, now) if fm else 'n/a',
            'sections': sections, 'sources': sources, 'pointed': pointed}


def truncate(sections, budget, fixed=12):
    """Lower-ranked sections lose lines first; returns the titles truncated. No budget (0) = nothing truncated."""
    truncated = []
    if budget <= 0:
        return truncated
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
    return truncated


def merge(subjects):
    """Several subjects -> one section list: per-subject sections become `### <task>` blocks, shared sections keep
    each part once (a calculation or flow that is itself a subject is not repeated as a linked one)."""
    own_files = {rel_file for s in subjects for rel_file in [s['label']] if s['file']}
    merged = []
    for title in ORDER:
        secs = [(s, next((x for x in s['sections'] if x['Title'] == title), None)) for s in subjects]
        secs = [(s, x) for s, x in secs if x]
        if not secs:
            continue
        rank, see = secs[0][1]['Rank'], secs[0][1]['See']
        texts = []
        seen = set(own_files) if title in ('Calculations', 'Flows') else set()
        kafka, datasets = [], []
        for s, x in secs:
            if title in PER_SUBJECT:
                # the subject's own headings (already `###` under the section) go one level under the `### <task>` block
                body = demote(x['Content'], 1) if title in ('Spec', 'Flow', 'Calculation', 'Context overview', 'Specs in the flow') else x['Content']
                texts.append(f"### {s['task']} ({s['kind']}: `{s['label']}`)\n{body}")
                continue
            parts = x['Parts'] or ([{'Key': s['task'], 'Text': x['Content']}] if x['Content'] != '_(none)_' else [])
            for p in parts:
                if p['Key'] == 'kafka':
                    kafka.append(p)
                    continue
                if p['Key'] == 'datasets':
                    datasets.append(p)
                    continue
                if p['Key'] in seen:
                    continue
                seen.add(p['Key'])
                texts.append(p['Text'] if p['Text'] else x['Content'])
        if datasets:
            rows = list(dict.fromkeys(r for p in datasets for r in p['Rows']))
            texts.append('### Datasets touching these tables\n(cite by name: `Given dataset "<name>" is loaded`; full list and sample rows in `generated/be/datasets.md`)\n' + '\n'.join(rows))
        if kafka:
            events = list(dict.fromkeys(e for p in kafka for e in p['Events']))
            texts.append('**Kafka**: ' + ', '.join(f'`{e}`' for e in events) + ' - ' + kafka[0]['Where'])
        sep = '\n' if title in ('Calculations', 'Flows', 'Imported pages') else '\n\n'   # pointer lists stay compact
        merged.append({'Title': title, 'Content': sep.join(texts) if texts else '_(none)_', 'Rank': rank, 'See': see, 'Parts': []})
    return merged


def contents(header_lines, sections, footer_title='Sources and limits'):
    """The `## Contents` section: line range of every section and the start line of every `### ` part in it, so a
    reader opens the part the task needs and, after a rebuild, only what came back. Line numbers count the finished file."""
    entries = []
    for s in sections:
        parts = []
        for i, l in enumerate(split_lines(s['Content'])):
            if not l.startswith('### '):
                continue
            label = re.sub(r'\s+', ' ', l[4:].replace('`', '').replace('**', '')).strip()
            m = re.match(r'^(\S+) \((?:spec|calculation|flow|context|node): ', label)   # a `### <task> (<kind>: <path>)` block
            label = m.group(1) if m else label
            parts.append((i, label if len(label) <= 60 else label[:59].rstrip() + '…'))
        entries.append((s['Title'], len(split_lines(s['Content'])), parts))
    entries.append((footer_title, 0, []))
    toc_len = 1 + len(entries) + 1                      # heading, one line per section, blank line
    out = ['## Contents']
    line = header_lines + toc_len + 1                   # first line of the first section heading
    for title, n, parts in entries:
        start, end = line, line + n                     # `## title` on `start`, the last content line on `end`
        row = f'- {title}: lines {start}-{end}' if n else f'- {title}: line {start}'
        if parts:
            row += ' - ' + '; '.join(f'{p} {start + 1 + i}' for i, p in parts)
        out.append(row)
        line = end + 2                                  # blank line after the section
    return '\n'.join(out), toc_len


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('task_positional', nargs='*', default=[])
    ap.add_argument('--task', action='append', default=[])
    ap.add_argument('--budget', type=int, default=0)
    ap.add_argument('--out-dir', default='.context')
    ap.add_argument('--depth', type=int, default=2)
    ap.add_argument('--print', dest='print_', action='store_true')
    a = ap.parse_args()
    tasks = list(dict.fromkeys([t for t in a.task + a.task_positional if t.strip()]))
    if not tasks:
        ap.error('--task is required')
    repo = repo_root(__file__)
    here = os.path.dirname(os.path.abspath(__file__))
    now = now_utc()
    budget = a.budget   # 0 = no cap
    contexts = load_contexts(repo)
    glossary = glossary_terms(repo)
    share = 0 if not budget else budget if len(tasks) == 1 else max(300, budget // len(tasks))
    subjects = [build_subject(t, repo, here, now, share, a.depth, contexts, glossary) for t in tasks]

    # ---------- 3. budget ----------
    if len(subjects) == 1:
        s = subjects[0]
        sections, sources, pointed = s['sections'], s['sources'], s['pointed']
        header = f"# Context pack: {s['task']} - {s['label']} - {s['badge']} - built {now.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
    else:
        sections = merge(subjects)
        sections[0]['Content'] = (f"- subjects: {len(subjects)} - one pack; shared sections merged and deduplicated, "
                                  f"per-subject blocks headed `### <task>`\n\n" + sections[0]['Content'])
        sources = [x for s in subjects for x in s['sources']]
        pointed = [x for s in subjects for x in s['pointed'] if x not in {s2['label'] for s2 in subjects}]
        header = f"# Context pack: {' + '.join(s['task'] for s in subjects)} - {len(subjects)} subjects - built {now.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
    truncated = truncate(sections, budget)
    ordered = [next(x for x in sections if x['Title'] == t) for t in ORDER if any(x['Title'] == t for x in sections)]
    toc, _ = contents(2, ordered)                       # header line + blank line precede the Contents section
    out = [header + '\n', toc + '\n\n']
    for s in ordered:
        out.append(f"## {s['Title']}\n" + s['Content'] + '\n\n')
    out.append('## Sources and limits\n')
    out.append('- files read into the pack: ' + ', '.join(f'`{s}`' for s in dict.fromkeys(sources)) + '\n')
    out.append('- pointed at (open through the indexes when the task needs them): ' + (', '.join(f'`{s}`' for s in dict.fromkeys(pointed)) or 'none') + '\n')
    out.append(f"- truncated sections: {', '.join(truncated) if truncated else 'none'} ({f'budget {budget} lines' if budget else 'no budget: every section complete'})\n")
    out.append('- rule: this pack is the recorded slice of the task - what was read first and what it points at. Procedure: `.github/skills/task-context/SKILL.md`, six steps, the same for a question and a change request: the documentation folders of this repository are open after the pack (never `raw-html/` or `_attachments/`; what you open is listed in your Sources), code last - at the `file:line` named above for most agents, through the generated maps and then freely for the analyst - and whatever code says is evidence and an Open question, never a rule.\n')
    result = ''.join(out)

    slug = re.sub(r'[^a-z0-9]+', '-', '+'.join(tasks).lower()).strip('-')[:60]
    out_path = os.path.join(repo, a.out_dir, f'{slug}.md')
    write_text(out_path, result)
    line_count = len(split_lines(result))
    if a.print_:
        sys.stdout.write(result + '\n')
    print(f"context pack: {rel(repo, out_path)} ({line_count} lines, {f'budget {budget}' if budget else 'no budget'}{f', {len(subjects)} subjects' if len(subjects) > 1 else ''}{', truncated: ' + ', '.join(truncated) if truncated else ''})")


if __name__ == '__main__':
    main()
