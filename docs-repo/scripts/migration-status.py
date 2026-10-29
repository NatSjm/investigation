#!/usr/bin/env python3
"""Migration status per bounded context: which runs of the spec lifecycle are still due (skeleton, legacy merge,
calculation audit, owner decision) and the exact command for each. Deterministic input for the `migration-lead`
agent; writes migration/<scope>.md (OKF Document) or prints with --print.

Sources (all inside the docs repo, no source code): contexts.yml, features/<ctx>/*.md frontmatter,
domain/calculations/*.md (status, used_by, `## Audit` section), generated/be/docs-tags.md (every @docs tag with its
code location), generated/graph/REPO_MAP.md (spec coverage), confluence-import/<SPACE>/*.md not yet in _done/
(header status; a page is assigned to a context when its text mentions the context name, its spec prefix or a spec
ID of the context; otherwise it is listed as unassigned). A page whose title reads as architecture
(integrations, deployment, decisions) is routed to the `architect` agent instead of the migrator and listed once, outside
the contexts' runs. A `candidate spec:` line under a spec's Open questions (left by the migrator when a page describes a
capability no spec covers) is listed as a shaping decision of the context, with the next free spec number (never a
renumbering) and the run that follows: Run 1 when the line says `in code`, the analyst's request with proposed rules
(`/analyse-request`) when it says `not in code`.
Examples:
  python3 scripts/migration-status.py --scope all
  python3 scripts/migration-status.py --scope product2 --print"""
import argparse
import os
import re
import sys
from datetime import date

from _common import (repo_root, read_text_or_empty, write_text, rel, get_fm, get_val, get_list, walk_files, like,
                     sort_key, split_lines, code, utf8_stdout)

SPEC_NAME = re.compile(r'^[A-Z][A-Z0-9]*-\d{3}\.md$', re.I)
# matched against the page title (header `source` + H1), letters and digits only, lower case; Czech stems
# included ("Architektura", "Integrace", "Nasazení", "Rozhodnutí") because the export keeps the source titles
ARCH_TITLE = re.compile(r'architect|architekt|integration|integrac|deploy|nasazen|infrastruct|infrastrukt|hosting|kafka|decision|rozhodnut')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--scope', default='all')
    ap.add_argument('--out', default='')
    ap.add_argument('--print', dest='print_', action='store_true')
    a = ap.parse_args()
    repo = repo_root(__file__)

    # ---------- contexts ----------
    contexts = {}
    for line in split_lines(read_text_or_empty(os.path.join(repo, 'contexts.yml'))):
        m = re.match(r'^\s{2}([\w-]+):\s*\{(.*)\}', line)
        if not m:
            continue
        c, body = m.group(1), m.group(2)
        sm = re.search(r'spec:\s*([A-Z][A-Z0-9]*)', body)
        fm_ = re.search(r'fe:\s*(\[[^\]]*\]|"[^"]*"|[\w*?.-]*)', body, re.I)
        fe_raw = fm_.group(1).strip().strip('[]"') if fm_ else ''
        fe_list = [x.strip().strip('"\'') for x in fe_raw.split(',') if x.strip().strip('"\'')]
        bm = re.search(r'be:\s*\[([^\]]*)\]', body, re.I)
        be = [x for x in (p.strip().strip('"\'') for p in bm.group(1).split(',')) if x] if bm else []
        contexts[c] = {'Name': c, 'Spec': sm.group(1) if sm else '', 'Fe': fe_list, 'Be': be}
    if not contexts:
        raise SystemExit('contexts.yml has no contexts')
    # longest literal part wins; an entry with `*` is a wildcard over the whole class name (as in gen-graph.py)
    prefixes = sorted(((c['Name'], p) for c in contexts.values() for p in c['Be']), key=lambda x: -len(re.sub(r'[*?]', '', x[1])))

    def context_of(cls):
        for ctx, p in prefixes:
            if like(cls, p) if re.search(r'[*?]', p) else cls.startswith(p):
                return ctx
        return 'shared'

    def context_of_spec_id(sid):
        pfx = sid.split('-')[0]
        for c in contexts.values():
            if c['Spec'] == pfx:
                return c['Name']
        return ''

    selected = list(contexts) if a.scope == 'all' else [s.strip() for s in a.scope.split(',') if s.strip() in contexts]
    if not selected:
        raise SystemExit(f"Unknown context '{a.scope}'. Known: {', '.join(contexts)}")

    # ---------- specs ----------
    specs = {}   # ctx -> list of {Id, Status, Verified, Open, File}
    for f in walk_files(os.path.join(repo, 'features'), '*.md'):
        if not SPEC_NAME.match(os.path.basename(f)):
            continue
        t = read_text_or_empty(f)
        fm = get_fm(t)
        sid = get_val(fm, 'id') or os.path.splitext(os.path.basename(f))[0]
        ctx = get_val(fm, 'context') or context_of_spec_id(sid)
        open_q = 0
        candidates = []   # "candidate spec: <title> (...)" lines the migrator leaves when a page describes a capability no spec covers
        om = re.search(r'(?s)## Open questions\r?\n(.*?)(\r?\n## |\Z)', t, re.I)
        if om:
            open_q = len(re.findall(r'(?m)^\s*- \[ \]', om.group(1)))
            # (title, not_in_code): the parenthesis after the title may say "not in code" (behaviour still to be built)
            candidates = [(c.strip(), 'not in code' in p.lower())
                          for c, p in re.findall(r'(?im)^\s*- \[ \] candidate spec:\s*([^(\r\n]+)(\([^)\r\n]*\))?', om.group(1))]
        specs.setdefault(ctx, []).append({'Id': sid, 'Status': get_val(fm, 'status'), 'Verified': bool(get_val(fm, 'verified')),
                                          'Open': open_q, 'Candidates': candidates, 'File': rel(repo, f)})

    # ---------- calculations: tags from code vs concepts ----------
    calcs = {}   # name -> {Name, Class, Location, Ctx, Concept, Status, Audited, UsedBy}
    tags_text = read_text_or_empty(os.path.join(repo, 'generated/be/docs-tags.md'))
    for m in re.finditer(r'(?m)^\|\s*`([a-z][a-z0-9_]*)`\s*\|\s*`(?:object|class)\s+(\w+)[^`]*`\s*\|[^|]*\|\s*`([^`]+)`\s*\|', tags_text):
        name, cls = m.group(1), m.group(2)
        calcs[name] = {'Name': name, 'Class': cls, 'Location': m.group(3), 'Ctx': context_of(cls), 'Concept': '', 'Status': '',
                       'Audited': False, 'UsedBy': []}
    calc_dir = os.path.join(repo, 'domain/calculations')
    for fname in sorted(os.listdir(calc_dir), key=str.lower) if os.path.isdir(calc_dir) else []:
        if not fname.lower().endswith('.md') or fname.lower() in ('index.md', '_template.md'):
            continue
        f = os.path.join(calc_dir, fname)
        t = read_text_or_empty(f)
        fm = get_fm(t)
        name = get_val(fm, 'name') or os.path.splitext(fname)[0]
        if name not in calcs:
            calcs[name] = {'Name': name, 'Class': '', 'Location': '', 'Ctx': '', 'Concept': '', 'Status': '', 'Audited': False, 'UsedBy': []}
        c = calcs[name]
        c['Concept'] = rel(repo, f)
        c['Status'] = get_val(fm, 'status')
        c['Audited'] = re.search(r'(?m)^## Audit ', t, re.I) is not None
        c['UsedBy'] = get_list(fm, 'used_by')
        if not c['Ctx']:
            tags = [x for x in get_list(fm, 'tags') if x in contexts]
            if tags:
                c['Ctx'] = tags[0]

    # a calculation is OWNED by the context of its class-name prefix (fallback: first context tag) - its Run 3 is listed
    # there only; contexts whose specs merely use it (used_by) show it as a dependency
    def calcs_of(ctx):
        return sorted((c for c in calcs.values() if c['Ctx'] == ctx), key=lambda c: sort_key(c['Name']))

    def calcs_used_by(ctx):
        ids = [s['Id'] for s in specs.get(ctx, [])]
        c = contexts[ctx]
        return sorted((k for k in calcs.values() if k['Ctx'] != ctx and any(u in ids or like(u, f"{c['Spec']}-*") for u in k['UsedBy'])),
                      key=lambda k: sort_key(k['Name']))

    # ---------- REPO_MAP spec coverage ----------
    code_only = set(re.findall(r'(?m)^- `spec:([\w-]+)`: code only', read_text_or_empty(os.path.join(repo, 'generated/graph/REPO_MAP.md'))))

    # ---------- legacy pages not yet migrated ----------
    pages = []
    imp_dir = os.path.join(repo, 'confluence-import')
    if os.path.isdir(imp_dir):
        for f in walk_files(imp_dir, '*.md'):
            r = rel(repo, f)
            if re.search(r'(^|/)_done/', r, re.I) or os.path.basename(f).lower() == 'readme.md':
                continue
            t = read_text_or_empty(f)
            fm = get_fm(t)
            status = get_val(fm, 'status') or 'imported'
            if status.lower() in ('migrated', 'obsolete'):
                continue
            # context of a page: explicit header `target: <ctx | spec ID>`, else its title (header `source` or first H1,
            # spaces removed, so "Product 1 overview" matches product1), else spec IDs cited in the body
            hits = []
            target = get_val(fm, 'target')
            title = get_val(fm, 'source')
            hm = re.search(r'(?m)^# (.+)$', t)
            if hm:
                title += ' ' + hm.group(1)
            title_key = re.sub(r'[^A-Za-z0-9]', '', title).lower()
            for c in contexts.values():
                by_target = bool(target) and (target.lower() == c['Name'].lower() or (bool(c['Spec']) and like(target, f"{c['Spec']}-*")))
                stem = re.sub(r's$', '', c['Name'].lower())   # "meetings" also matches "Meeting flow"
                by_title = stem in title_key or any(re.sub(r'[^A-Za-z0-9]', '', p).lower() in title_key for p in c['Fe'] if '*' not in p)
                by_id = bool(c['Spec']) and re.search(r'\b' + re.escape(c['Spec']) + r'-\d{3}\b', t, re.I) is not None
                if by_target or by_title or by_id:
                    hits.append(c['Name'])
            # the title is stronger evidence than a word in the body, so an architecture title wins over a formula word
            if ARCH_TITLE.search(title_key):
                kind = 'architecture?'
            elif re.search(r'(?i)formula|threshold|calculation|rounding', t):
                kind = 'calculation?'
            else:
                kind = 'feature?'
            pages.append({'File': r, 'Modified': get_val(fm, 'last_modified'), 'Status': status, 'Kind': kind, 'Ctx': hits})

    # ---------- render ----------
    today = date.today().isoformat()
    title = 'Migration status (all contexts)' if a.scope == 'all' else f'Migration status ({a.scope})'
    sb = []
    sb.append('---\n')
    sb.append('type: Document\n')
    sb.append(f'title: {title}\n')
    sb.append('description: Which runs of the spec lifecycle (skeleton, legacy merge, calculation audit, owner decision) are still due per bounded context, with the command for each; generated by scripts/migration-status.py.\n')
    sb.append('tags: [migration, plan]\n')
    sb.append('status: stable\n')
    sb.append(f'generated: {{ by: process:migration-status, at: {today}T00:00:00Z }}\n')
    sb.append('---\n\n')
    sb.append(f'# {title}\n\n')
    sb.append('> Generated by ' + code('scripts/migration-status.py') + f' on {today} from contexts.yml, features/, domain/calculations/, generated/be/docs-tags.md, generated/graph/REPO_MAP.md and confluence-import/. Lifecycle: ' + code('.github/skills/spec-lifecycle/SKILL.md') + '. Regenerate instead of editing.\n\n')

    def route(p):
        if p['Kind'] == 'calculation?':
            return 'looks like a formula page: ' + code(f"/audit-calculation {p['File']}") + ' (agent ' + code('calc-auditor') + '); a screen page that only quotes a threshold, or has a formula section beside its screen rules, is `feature-spec`: ' + code(f"@confluence-migrator {p['File']}") + ' instead, it hands the formula part on'
        return code(f"@confluence-migrator {p['File']}")

    # architecture pages are not a spec's run: they go to `architect` after the integration map refresh and never
    # block a context, so they are listed once at the top, with the contexts they mention, not under each context
    arch_pages = [p for p in pages if p['Kind'] == 'architecture?']

    totals = {'shaping': 0, 'run1': 0, 'run2': 0, 'run3': 0, 'run4': 0, 'ready': 0}
    summary = []
    detail = []
    for ctx_name in selected:
        c = contexts[ctx_name]
        ctx_specs = sorted(specs.get(ctx_name, []), key=lambda s: sort_key(s['Id']))
        ctx_calcs = calcs_of(ctx_name)
        ctx_pages = [p for p in pages if ctx_name in p['Ctx'] and p['Kind'] != 'architecture?']
        runs = []
        first_id = f"{c['Spec']}-001"
        numbers = [int(m.group(1)) for s in ctx_specs for m in [re.search(r'-(\d{3})$', s['Id'])] if m]
        next_id = f"{c['Spec']}-{(max(numbers) + 1 if numbers else 1):03d}"
        if not ctx_specs:
            totals['run1'] += 1
            runs.append('- [ ] **Run 1 - skeleton** ' + code(first_id) + ': ' + code(f'/spec-skeleton-from-graph {ctx_name} {first_id}') + ' (agent ' + code('spec-writer') + f"; REPO_MAP: {'code only' if first_id in code_only else 'not listed'})")
        for s in ctx_specs:
            for cand, not_in_code in s['Candidates']:
                # a shaping decision, not an agent run: the lead and a developer confirm the spec, then Run 1 writes it
                # from the code (or the analyst drafts it with proposed rules when the code does not have it yet) and
                # the page is rerun; the next free number is the ID (conventions "Shaping specs" point 9: no renumbering)
                totals['shaping'] += 1
                head = '- [ ] **Shaping - candidate spec** ' + cand + f" (Open question of {code(s['Id'])}): confirm with a developer (" + code('features/conventions.md') + ', "Shaping specs" point 9), add the row to the board, then '
                if not_in_code:
                    runs.append(head + code('/analyse-request "<the legacy page as the request>" work-items') + f" (agent analyst; spec {code(next_id)}, next free number, drafted by spec-writer with proposed rules) and rerun the page it came from")
                else:
                    runs.append(head + code(f'/spec-skeleton-from-graph {ctx_name} {next_id}') + ' (next free number) and rerun the page it came from')
        for p in ctx_pages:
            totals['run2'] += 1
            who = route(p)
            runs.append('- [ ] **Run 2 - legacy merge** ' + code(p['File']) + f" (last_modified {p['Modified']}, status {p['Status']}): {who}")
        for k in ctx_calcs:
            if not k['Concept']:
                totals['run3'] += 1
                runs.append('- [ ] **Run 3 - calculation concept** ' + code(k['Name']) + f" (code only, {k['Location']}): " + code(f"/audit-calculation {k['Name']}") + ' creates ' + code(f"domain/calculations/{k['Name']}.md") + ' from ' + code('domain/calculations/_template.md') + ' with worked examples from the unit test')
            elif not k['Audited']:
                totals['run3'] += 1
                runs.append('- [ ] **Run 3 - calculation audit** ' + code(k['Name']) + f" (no audit table, status {k['Status']}): " + code(f"/audit-calculation {k['Name']}"))
            elif k['Status'].lower() != 'stable':
                # audited but not stable: the auditor found drift or the concept is new - the owner decides, not the auditor again
                totals['run4'] += 1
                runs.append('- [ ] **Run 4 - owner decision** ' + code(k['Name']) + f" (audited, status {k['Status']}): decide the open questions in " + code(k['Concept']) + ', set ' + code('status: stable') + ' and ' + code('verified: { by: human:<id>, at }'))
        for s in ctx_specs:
            if s['Status'].lower() != 'stable' or not s['Verified']:
                totals['run4'] += 1
                what = []
                if s['Open'] > 0:
                    what.append(f"{s['Open']} open question(s)")
                if s['Status'].lower() != 'stable':
                    what.append(f"status {s['Status']}")
                if not s['Verified']:
                    what.append('no verified.by')
                runs.append('- [ ] **Run 4 - owner decision** ' + code(s['Id']) + f" ({', '.join(what)}): decide the open questions in " + code(s['File']) + ', record them in the Change log, add ' + code('verified: { by: human:<id>, at }') + ' and ' + code('stale_after'))
        if not runs:
            totals['ready'] += 1
            state = 'ready'
        else:
            state = f'{len(runs)} run(s) due'
        spec_cell = ', '.join(code(s['Id']) + f" ({s['Status']}{', verified' if s['Verified'] else ''})" for s in ctx_specs) if ctx_specs else 'none'
        calc_cell = ', '.join(code(k['Name']) + (' (code only)' if not k['Concept'] else f" ({k['Status']}, unaudited)" if not k['Audited'] else f" ({k['Status']})") for k in ctx_calcs) if ctx_calcs else 'none'
        used = calcs_used_by(ctx_name)
        if used:
            calc_cell += '; uses ' + ', '.join(code(k['Name']) for k in used)
        summary.append(f"| {ctx_name} | {c['Spec']} | {spec_cell} | {calc_cell} | {len(ctx_pages)} | {state} |")

        detail.append(f'## {ctx_name}\n\n')
        detail.append(f"Spec prefix {code(c['Spec'])}; BE class prefixes {', '.join(code(x) for x in c['Be'])}; FE pages {', '.join(code(x) for x in c['Fe']) if c['Fe'] else 'none'}. Graph: " + code(f'generated/graph/{ctx_name}.md') + '.\n\n')
        if not runs:
            detail.append('Ready for the analyst agent: spec stable and verified, calculations audited, no legacy page pending.\n')
        else:
            for r in runs:
                detail.append(r + '\n')
        detail.append('\n')

    sb.append('## Summary\n\n')
    sb.append(f"Runs due: skeleton {totals['run1']}, legacy merge {totals['run2']}, calculation {totals['run3']}, owner decision {totals['run4']}; shaping decisions (candidate specs) {totals['shaping']}; architecture pages {len(arch_pages)}. Contexts ready for the analyst: {totals['ready']} of {len(selected)}.\n\n")
    sb.append('| Context | Spec prefix | Specs | Calculations | Legacy pages pending | State |\n|---|---|---|---|---|---|\n')
    for row in summary:
        sb.append(row + '\n')
    sb.append('\n')
    if arch_pages:
        sb.append('Architecture pages (not a spec\'s run and not counted above; agent ' + code('architect') + ', task "Legacy page", one page per run, after ' + code('/integrations-from-contracts') + ' has refreshed ' + code('architecture/integrations.md') + '; a page that also describes a screen goes to the migrator first, which hands the rest on; confirm the class in the triage note):\n')
        for p in arch_pages:
            mentions = (', mentions ' + ', '.join(p['Ctx'])) if p['Ctx'] else ''
            sb.append('- [ ] ' + code(p['File']) + f" (last_modified {p['Modified']}, status {p['Status']}{mentions}): " + code(f"@architect {p['File']}") + '\n')
        sb.append('\n')
    unassigned = [p for p in pages if not p['Ctx'] and p['Kind'] != 'architecture?']
    if unassigned:
        sb.append('Legacy pages that mention no context (classify by hand, then run ' + code('@confluence-migrator <page>') + '; it hands architecture and decision pages to ' + code('architect') + '):\n')
        for p in unassigned:
            sb.append('- ' + code(p['File']) + f" (last_modified {p['Modified']}, {p['Kind']})\n")
        sb.append('\n')
    sb.append('Order of work: Run 1 for every context without a spec first (code is the truth, pages are merged into a skeleton), then Run 2 page by page, Run 3 as the handoff after each spec, Run 4 by the owner. A candidate spec a page left behind is a shaping decision before its Run 1 (in code) or its request to the analyst (not in code), never a spec written from the page and never a renumbering of the context\'s specs. Architecture pages wait only for the integration map refresh, not for the specs. One run, one review, one commit.\n\n')
    sb.extend(detail)

    text = ''.join(sb)
    if a.print_:
        sys.stdout.write(text + '\n')
    out = a.out or f'migration/{a.scope}.md'
    if not a.print_ or a.out:
        out_path = out if os.path.isabs(out) else os.path.join(repo, out)
        write_text(out_path, text)
        print(f"migration-status: {len(selected)} context(s), runs due: {totals['run1'] + totals['run2'] + totals['run3'] + totals['run4']} -> {rel(repo, out_path)}")


if __name__ == '__main__':
    main()
