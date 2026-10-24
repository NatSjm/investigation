#!/usr/bin/env python3
"""Documentation analytics without reading code: for every feature spec, which business rules (BR-<ID>-<n>) are
cited by a story acceptance criterion (work-items/<ID>.yml, `rule:`) and by a Gherkin scenario
(test-design/features/<ID>.feature, `@BR-<ID>-<n>`), plus trust badge and staleness. Writes an OKF Document to
generated/analytics/coverage-matrix.md (and JSON next to it) so the analyst agent answers status questions from it.
Examples:
  python3 scripts/coverage-matrix.py                # all specs
  python3 scripts/coverage-matrix.py --scope P1     # one context prefix"""
import argparse
import json
import os
import re
from datetime import timedelta

from _common import (repo_root, read_text_or_empty, write_text, get_fm, get_val, badge, now_utc, walk_files, sort_key,
                     utf8_stdout)

SPEC_NAME = re.compile(r'^[A-Z][A-Z0-9]*-\d{3}[a-z]?\.md$', re.I)


def open_items(text):
    """Open question items (`- [ ]` with their indented continuation lines), one string each."""
    items, open_ = [], False
    for line in text.splitlines():
        if re.match(r'^\s*-\s*\[ \]', line):
            items.append(line)
            open_ = True
        elif open_ and line.startswith((' ', '\t')) and not re.match(r'^\s*-\s', line):
            items[-1] += ' ' + line.strip()
        else:
            open_ = False
    return items


def unique(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--scope', default='')
    ap.add_argument('--out', default='generated/analytics/coverage-matrix.md')
    a = ap.parse_args()
    repo = repo_root(__file__)
    now = now_utc()

    rows = []
    js = []
    specs = sorted((f for f in walk_files(os.path.join(repo, 'features'), '*.md') if SPEC_NAME.match(os.path.basename(f))),
                   key=lambda f: sort_key(os.path.basename(f)))
    # request epics (work-items/<slug>.yml with `request:` and `specs: [...]`) count for every spec they cite
    requests = []
    wi_dir = os.path.join(repo, 'work-items')
    if os.path.isdir(wi_dir):
        for f in sorted(os.listdir(wi_dir), key=str.lower):
            if not f.lower().endswith('.yml') or f.startswith('_'):
                continue
            t = read_text_or_empty(os.path.join(wi_dir, f))
            if re.search(r'(?m)^request:', t, re.I):
                m = re.search(r'(?m)^specs:\s*\[([^\]]*)\]', t, re.I)
                requests.append(([x.strip().strip('"\'').lower() for x in m.group(1).split(',') if x.strip()] if m else [], t))
    for f in specs:
        sid = os.path.splitext(os.path.basename(f))[0]
        if a.scope and not sid.startswith(a.scope):
            continue
        t = read_text_or_empty(f)
        fm = get_fm(t)
        brs = unique(re.findall(r'(?m)^\s*-\s+\*\*(BR-' + re.escape(sid) + r'-\d+)\*\*', t))
        if not brs:
            brs = unique(re.findall(r'\bBR-' + re.escape(sid) + r'-\d+\b', t))
        wi = read_text_or_empty(os.path.join(repo, f'work-items/{sid}.yml'))
        wi += ''.join('\n' + t for ids, t in requests if sid.lower() in ids)
        ft = read_text_or_empty(os.path.join(repo, f'test-design/features/{sid}.feature'))
        with_story = [b for b in brs if re.search(r'rule:\s*' + re.escape(b) + r'\b', wi, re.I)]
        with_scenario = [b for b in brs if re.search('@' + re.escape(b) + r'\b', ft, re.I)]
        # stories that cite a rule of this spec (a request epic's other stories belong to other specs)
        stories = sum(1 for b in re.split(r'(?m)^\s{2}-\s+id:', wi)[1:] if re.search(r'rule:\s*BR-' + re.escape(sid) + r'-\d+\b', b, re.I))
        scenarios = len(re.findall(r'(?m)^\s*Scenario', ft))
        items = open_items(t)
        open_q = len(items)
        from_code = sum(1 for x in items if 'code-read' in x)
        missing_story = [b for b in brs if b not in with_story]
        missing_scenario = [b for b in brs if b not in with_scenario]

        def fmt_missing(lst, total):
            if not lst:
                return '-'
            if len(lst) == total:
                return 'all'
            return ', '.join(re.sub('^BR-' + re.escape(sid) + '-', '', x) for x in lst)

        ctx = get_val(fm, 'context')
        bd = badge(fm, now)
        sa = get_val(fm, 'stale_after')
        rows.append(f'| {sid} | {ctx} | {len(brs)} | {len(with_story)} ({stories} stories) | {len(with_scenario)} ({scenarios} scenarios) | {open_q} | {from_code} | {bd} | {sa} | {fmt_missing(missing_story, len(brs))} | {fmt_missing(missing_scenario, len(brs))} |')
        js.append({'id': sid, 'context': ctx, 'rules': len(brs), 'rulesWithStory': len(with_story), 'rulesWithScenario': len(with_scenario),
                   'stories': stories, 'scenarios': scenarios, 'openQuestions': open_q, 'openQuestionsFromCode': from_code, 'badge': bd, 'staleAfter': sa,
                   'rulesWithoutStory': missing_story, 'rulesWithoutScenario': missing_scenario})

    calc_rows = []
    calc_dir = os.path.join(repo, 'domain/calculations')
    for name in sorted((x for x in os.listdir(calc_dir) if x.lower().endswith('.md') and not re.match(r'^(_?template|index)\.md$', x, re.I)), key=sort_key):
        t = read_text_or_empty(os.path.join(calc_dir, name))
        fm = get_fm(t)
        examples_text = re.split(r'(?m)^#', re.split('## Worked examples', t, flags=re.I)[-1])[0]
        examples = len(re.findall(r'(?m)^\|\s*\d+\s*\|', examples_text))
        audit = 'yes' if re.search(r'(?m)^## Audit', t, re.I) else 'no'
        calc_rows.append(f"| {os.path.splitext(name)[0]} | {get_val(fm, 'used_by')} | {examples} | {audit} | {badge(fm, now)} |")

    date = now.strftime('%Y-%m-%d')
    scope_note = f' (scope {a.scope})' if a.scope else ''
    md = f"""---
type: Document
title: Coverage matrix (BR -> stories -> scenarios)
description: Which business rules of each feature spec are covered by Jira stories and Gherkin scenarios, with trust badges; generated analytics for the analyst agent.
tags: [analytics, generated]
status: stable
generated: {{ by: process:coverage-matrix, at: {date} }}
stale_after: {(now + timedelta(days=14)).strftime('%Y-%m-%d')}T00:00:00Z
---
# Coverage matrix

> Generated by `scripts/coverage-matrix.py` on {date}{scope_note}. Do not edit by hand.

## Feature specs

| Spec | Context | BRs | with story | with scenario | open questions | answered from code | badge | stale_after | BR numbers without story | BR numbers without scenario |
|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

## Calculations

| Calculation | used_by | worked examples | audited | badge |
|---|---|---|---|---|
{chr(10).join(calc_rows)}

**answered from code**: open questions whose item cites `code-read` - the analyst had to settle them from source
(analyst agent steps 9 and 10), so the documentation ran out there; refresh those specs first.

Spec coverage of the code (`spec + code` / `code only` / `spec only`): see `generated/graph/REPO_MAP.md`.
"""
    out_path = a.out if os.path.isabs(a.out) else os.path.join(repo, a.out)
    write_text(out_path, md)
    write_text(re.sub(r'\.md$', '.json', out_path), json.dumps(js, indent=2, ensure_ascii=False) + '\n')
    print(f'coverage-matrix: {len(rows)} spec(s), {len(calc_rows)} calculation(s) -> {a.out}')


if __name__ == '__main__':
    main()
