#!/usr/bin/env python3
"""Writes generated/catalogue.md: one line per thing the bundle knows about, so that an agent given a free-text
request ("when imports change, should the stress numbers refresh?", "dashboard with cover ratio trend and a new
churn score") can resolve it to subjects for scripts/context-pack.py without anybody naming contexts or IDs.

Sections (each entry on one line, sorted, grep-able): contexts (from contexts.yml, incl. those with no spec yet),
flows, feature specs, calculations, API endpoints, Kafka topics, tables, external services, glossary terms with
aliases. Sources: contexts.yml, features/, domain/, flows/, generated/graph/graph.json, generated/openapi/,
generated/be/events.md, work-items/, test-design/. No libraries.
Examples:
  python3 scripts/gen-catalogue.py            # rewrite generated/catalogue.md
  python3 scripts/gen-catalogue.py --check    # exit 1 when the catalogue is out of date (CI)"""
import argparse
import json
import os
import re
import sys

from _common import (repo_root, read_text, read_text_or_empty, write_text, rel, get_fm, get_val, get_list, badge,
                     now_utc, walk_files, sort_key, split_lines, utf8_stdout)


def one_line(s, limit=0):
    """One table cell: whitespace folded, `|` escaped so that a summary never breaks the row."""
    s = re.sub(r'\s+', ' ', s or '').strip().replace('|', '\\|')
    return (s[:limit - 1].rstrip() + '…') if limit and len(s) > limit else s


def yaml_scalar(lines, i):
    """Value of `key: ...` at lines[i]; a `>-` / `|` block is joined from the indented lines that follow."""
    m = re.match(r'^(\s*)[\w-]+:\s*(.*)$', lines[i])
    if not m:
        return ''
    indent, val = len(m.group(1)), m.group(2).strip()
    if val in ('>-', '>', '|', '|-'):
        parts = []
        for l in lines[i + 1:]:
            if l.strip() == '' or len(l) - len(l.lstrip()) > indent:
                parts.append(l.strip())
            else:
                break
        return one_line(' '.join(parts))
    return val.strip('"\'')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default='')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    repo = repo_root(__file__)
    out_path = a.out or os.path.join(repo, 'generated', 'catalogue.md')
    now = now_utc()

    # ---------- contexts.yml: context -> spec prefix, fe pages, be prefixes, comment lines above the entry ----------
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

    # ---------- specs, calculations, flows ----------
    def concept_files(folder, exclude_rx):
        return [f for f in walk_files(os.path.join(repo, folder), '*.md')
                if not re.match(exclude_rx, os.path.basename(f), re.I)]

    specs = []
    for f in concept_files('features', r'^(_?template|index|conventions)\.md$'):
        fm = get_fm(read_text(f))
        sid = get_val(fm, 'id') or os.path.splitext(os.path.basename(f))[0]
        specs.append({'id': sid, 'file': rel(repo, f), 'fm': fm, 'context': get_val(fm, 'context'),
                      'title': get_val(fm, 'title', strip_comment=False), 'description': get_val(fm, 'description', strip_comment=False),
                      'aliases': get_list(fm, 'aliases'), 'calculations': [re.sub(r'^/', '', x) for x in get_list(fm, 'calculations')],
                      'flows': [re.sub(r'^/', '', x) for x in get_list(fm, 'flows')], 'api': get_list(fm, 'api'),
                      'tables': get_list(fm, 'tables'), 'events': get_list(fm, 'events'),
                      'stories': os.path.isfile(os.path.join(repo, 'work-items', sid + '.yml')),
                      'tests': os.path.isfile(os.path.join(repo, 'test-design', 'features', sid + '.feature'))})
    specs.sort(key=lambda s: sort_key(s['id']))
    specs_by_ctx = {}
    for s in specs:
        specs_by_ctx.setdefault(s['context'], []).append(s['id'])

    calcs = []
    for f in concept_files('domain/calculations', r'^(_?template|index)\.md$'):
        text = read_text(f)
        fm = get_fm(text)
        name = os.path.splitext(os.path.basename(f))[0]
        params = re.findall(r'(?m)^\s*-\s*\{\s*name:\s*([\w.]+)', fm)
        used_by = [s['id'] for s in specs if rel(repo, f) in s['calculations']]
        calcs.append({'name': name, 'file': rel(repo, f), 'fm': fm, 'title': get_val(fm, 'title', strip_comment=False),
                      'description': get_val(fm, 'description', strip_comment=False), 'params': params, 'used_by': used_by,
                      'audited': re.search(r'(?m)^##\s+Audit', text) is not None})
    calcs.sort(key=lambda c: sort_key(c['name']))

    flows = []
    for f in concept_files('flows', r'^(_?template|index)\.md$'):
        fm = get_fm(read_text(f))
        flows.append({'id': get_val(fm, 'id') or os.path.splitext(os.path.basename(f))[0], 'file': rel(repo, f), 'fm': fm,
                      'title': get_val(fm, 'title', strip_comment=False), 'description': get_val(fm, 'description', strip_comment=False),
                      'contexts': get_list(fm, 'contexts'), 'specs': get_list(fm, 'specs'), 'channels': get_list(fm, 'channels')})
    flows.sort(key=lambda x: sort_key(x['file']))

    # ---------- graph: contexts' entry points and sizes, endpoints, tables, topics ----------
    graph_path = os.path.join(repo, 'generated', 'graph', 'graph.json')
    graph = json.loads(read_text(graph_path)) if os.path.isfile(graph_path) else None
    nodes = {n['id']: n for n in graph['nodes']} if graph else {}
    community_size = {c['id']: c.get('nodes', 0) for c in graph.get('communities', [])} if graph else {}
    edges = graph['edges'] if graph else []

    # ---------- OpenAPI: tag descriptions, operation summaries ----------
    oa_text = read_text_or_empty(os.path.join(repo, 'generated', 'openapi', 'backend.yaml'))
    tag_desc = {}
    for m in re.finditer(r'(?m)^\s*-\s*\{\s*name:\s*([\w-]+),\s*description:\s*(.+?)\s*\}\s*$', oa_text):
        tag_desc[m.group(1)] = m.group(2).strip().strip('"\'')
    ops = {}   # (METHOD, path) -> {operationId, summary, tags}
    path, method, cur = '', '', None
    for line in split_lines(oa_text):
        pm = re.match(r'^  (/\S*):\s*$', line)
        if pm:
            path = pm.group(1)
            continue
        mm = re.match(r'^    (get|post|put|patch|delete):\s*$', line, re.I)
        if mm and path:
            method = mm.group(1).upper()
            cur = ops[(method, path)] = {'operationId': '', 'summary': '', 'tags': []}
            continue
        if cur is None:
            continue
        if re.match(r'^\S', line) or re.match(r'^  /', line):
            cur = None
            continue
        om = re.match(r'^      operationId:\s*(.+)$', line)
        sm = re.match(r'^      summary:\s*(.+)$', line)
        tm = re.match(r'^      tags:\s*\[([^\]]*)\]', line)
        if om:
            cur['operationId'] = om.group(1).strip().strip('"\'')
        elif sm:
            cur['summary'] = sm.group(1).strip().strip('"\'')
        elif tm:
            cur['tags'] = [t.strip().strip('"\'') for t in tm.group(1).split(',') if t.strip()]

    # ---------- external services ----------
    externals = []
    ext_dir = os.path.join(repo, 'generated', 'openapi', 'external')
    if os.path.isdir(ext_dir):
        for f in sorted(os.listdir(ext_dir), key=str.lower):
            if not re.search(r'\.(ya?ml|json)$', f, re.I):
                continue
            lines = split_lines(read_text(os.path.join(ext_dir, f)))
            title = desc = ''
            for i, l in enumerate(lines):
                if re.match(r'^  title:', l) and not title:
                    title = yaml_scalar(lines, i)
                elif re.match(r'^  description:', l) and not desc:
                    desc = yaml_scalar(lines, i)
            externals.append((title or os.path.splitext(f)[0], desc, f'generated/openapi/external/{f}'))

    # ---------- Kafka topics: generated/be/events.md rows (producers / consumers), graph for the context ----------
    topics = []
    in_topics = False   # only the rows of the `| Topic | ...` table; the "Payload schemas" field tables are not topics
    for line in split_lines(read_text_or_empty(os.path.join(repo, 'generated', 'be', 'events.md'))):
        if re.match(r'^\|\s*Topic\s*\|', line, re.I):
            in_topics = True
            continue
        if not line.startswith('|'):
            in_topics = False
        m = re.match(r'^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', line) if in_topics else None
        if not m:
            continue
        def names(cell):
            # the class of each producer / listener from the file path in the cell (two listeners may share a
            # method name), else the backticked names, else the plain cell (`_external_`)
            found = re.findall(r'([A-Za-z0-9_]+)\.(?:kt|java)\b', cell) or re.findall(r'`([^`]+)`', cell)
            return ', '.join(sorted(set(found), key=sort_key)) if found else re.sub(r'[_*]', '', cell).strip()
        topics.append((m.group(1), names(m.group(2)), names(m.group(3))))
    topics.sort(key=lambda t: sort_key(t[0]))

    # ---------- glossary: term, the `Term (<lang>)` columns, aliases, used in (columns found by header) ----------
    terms = []
    cols, lang_cols = None, []
    for line in split_lines(read_text_or_empty(os.path.join(repo, 'domain', 'glossary.md'))):
        if cols is None:
            if re.match(r'^\|\s*Term\s*\|', line, re.I):
                cols = [c.strip() for c in line.strip().strip('|').split('|')]
                lang_cols = [c for c in cols if re.match(r'^Term \(\w+\)$', c)]
            continue
        if not line.startswith('|') or re.match(r'^\|\s*-', line):
            continue
        row = dict(zip(cols, [c.strip() for c in line.strip().strip('|').split('|')]))
        if row.get('Term'):
            terms.append((row['Term'], [row.get(c, '') for c in lang_cols], row.get('Aliases', ''), row.get('Used in', '')))
    terms.sort(key=lambda t: sort_key(t[0]))

    # ---------- render ----------
    out = []
    out.append('---')
    out.append('type: Document')
    out.append('title: "Catalogue"')
    out.append('description: "One line per context, flow, spec, calculation, endpoint, topic, table, external service and glossary term; the first thing an agent reads to resolve a free-text request to pack subjects"')
    out.append('tags: [catalogue, generated]')
    out.append('generated:')
    out.append('  by: process:gen-catalogue')
    out.append(f"  at: {now.strftime('%Y-%m-%d')}")
    out.append('status: stable')
    out.append('---')
    out.append('# Catalogue')
    out.append('')
    out.append(f"> Generated by `scripts/gen-catalogue.py` on {now.strftime('%Y-%m-%d')}. Do not edit by hand.")
    out.append('')
    out.append('How to use: a request in free text names none of these IDs. Read this page once, decide which lines the request is')
    out.append('about (several contexts and several kinds are normal), then build ONE pack with a `--task` per subject:')
    out.append('`python3 scripts/context-pack.py --task <spec ID> --task <calculation> --task flows/<name>.md --task context:<name>`.')
    out.append('A part of the request that matches no line is **new** work: add `--task context:<name>` for the context it belongs to;')
    out.append('that pack section lists what the context already has (endpoints, tables, calculations, classes) to place it next to.')
    out.append('Terms people use differently are mapped in the glossary section at the end. Definitions, formulas and rules are')
    out.append('not here: they are in the files each line points to.')
    out.append('')

    # Contexts
    out.append('## Contexts (`contexts.yml`)')
    out.append('')
    out.append('| Context | Spec prefix | Specs | API tag | Graph | FE pages | Note |')
    out.append('|---|---|---|---|---|---|---|')
    for c in sorted(contexts, key=sort_key):
        v = contexts[c]
        ids = specs_by_ctx.get(c, [])
        spec_cell = ', '.join(ids) if ids else '_no spec yet (code only)_'
        cn = nodes.get(f'context:{c}')
        if graph is None:
            gcell = '_(graph missing)_'
        elif cn:
            gcell = f"{community_size.get(c, '?')} nodes; {cn.get('note', '')}"
        elif c in community_size:
            gcell = f'{community_size[c]} nodes (FE only)'
        else:
            gcell = '_not in graph_'
        out.append(f"| {c} | {v['spec']} | {spec_cell} | {tag_desc.get(c, '')} | {gcell} | {', '.join(v['fe']) or '-'} | {v['note']} |")
    out.append('')

    # Flows
    out.append('## Flows (`flows/`, cross-context behaviour)')
    out.append('')
    if flows:
        out.append('| Flow | Contexts | Specs | Badge | Description |')
        out.append('|---|---|---|---|---|')
        for f in flows:
            out.append(f"| `{f['file']}` {f['title']} | {', '.join(f['contexts'])} | {', '.join(f['specs'])} | {badge(f['fm'], now)} | {one_line(f['description'])} |")
    else:
        out.append('_(none)_')
    out.append('')

    # Specs
    out.append('## Feature specs (`features/<context>/<ID>.md`)')
    out.append('')
    out.append('| ID | Context | Badge | Title | Aliases | Has | Description |')
    out.append('|---|---|---|---|---|---|---|')
    for s in specs:
        has = []
        if s['api']:
            has.append(f"{len(s['api'])} api")
        if s['events']:
            has.append(f"{len(s['events'])} events")
        if s['tables']:
            has.append(f"{len(s['tables'])} tables")
        if s['calculations']:
            has.append(f"{len(s['calculations'])} calcs")
        if s['flows']:
            has.append(f"{len(s['flows'])} flows")
        if s['stories']:
            has.append('stories')
        if s['tests']:
            has.append('tests')
        out.append(f"| {s['id']} | {s['context']} | {badge(s['fm'], now)} | {s['title']} | {', '.join(s['aliases'])} | {', '.join(has)} | {one_line(s['description'])} |")
    out.append('')

    # Calculations
    out.append('## Calculations (`domain/calculations/<name>.md`)')
    out.append('')
    out.append('| Name | Badge | Used by | Parameters | Title | Description |')
    out.append('|---|---|---|---|---|---|')
    for c in calcs:
        out.append(f"| `{c['name']}` | {badge(c['fm'], now)}{' · audited' if c['audited'] else ''} | {', '.join(c['used_by']) or '-'} | {', '.join(c['params'])} | {c['title']} | {one_line(c['description'])} |")
    out.append('')

    # Endpoints
    out.append('## API endpoints (`generated/openapi/backend.yaml`, graph `endpoint:` nodes)')
    out.append('')
    if ops:
        out.append('| Endpoint | Context | operationId | Summary | Specs |')
        out.append('|---|---|---|---|---|')
        api_specs = {}
        for s in specs:
            for ref in s['api']:
                parts = re.split(r'\s+', ref.strip())
                p = re.sub(r'\?.*$', '', parts[-1])
                p = re.sub(r'^/api/v\d+', '', p, flags=re.I)
                api_specs.setdefault((parts[0].upper() if len(parts) > 1 else '', p), []).append(s['id'])
        for (method, p), o in sorted(ops.items(), key=lambda kv: (sort_key(kv[0][1]), sort_key(kv[0][0]))):
            n = next((nd for nid, nd in nodes.items() if nid.startswith('endpoint:') and re.match(r'^' + re.escape(method) + r'\s+(/api/v\d+)?' + re.escape(p) + r'$', nd.get('label', ''), re.I)), None)
            ctx = n['community'] if n else (o['tags'][0] if o['tags'] else '')
            linked = sorted(set(api_specs.get((method, p), []) + api_specs.get(('', p), [])), key=sort_key)
            out.append(f"| `{method} {p}` | {ctx} | {o['operationId']} | {one_line(o['summary'])} | {', '.join(linked) or '-'} |")
        # endpoints the code exposes but the contract does not describe (technical endpoints, drift): listed, marked
        for nid, nd in sorted(nodes.items(), key=lambda kv: sort_key(kv[1].get('label', ''))):
            if not nid.startswith('endpoint:'):
                continue
            method, _, p = nd['label'].partition(' ')
            p = re.sub(r'^/api/v\d+', '', p, flags=re.I)
            if (method.upper(), p) in ops:
                continue
            op = re.search(r'operationId (\S+)', nd.get('note', ''))
            out.append(f"| `{method.upper()} {p}` | {nd.get('community', '')} | {op.group(1).rstrip(';') if op else ''} | _not in the OpenAPI contract (code only: `{nd.get('location', '')}`)_ | - |")
    else:
        out.append('_(generated/openapi/backend.yaml missing)_')
    out.append('')

    # Topics
    out.append('## Kafka topics (`generated/be/events.md`)')
    out.append('')
    if topics:
        out.append('| Topic | Producers | Consumers | Context | Specs / flows |')
        out.append('|---|---|---|---|---|')
        for t, prod, cons in topics:
            n = nodes.get(f'topic:{t}')
            linked = [s['id'] for s in specs if t in s['events']] + [f['id'] for f in flows if t in f['channels']]
            out.append(f"| `{t}` | {prod} | {cons} | {n['community'] if n else ''} | {', '.join(linked) or '-'} |")
    else:
        out.append('_(generated/be/events.md missing)_')
    out.append('')

    # Tables
    out.append('## Tables (graph `table:` nodes, owner = the context whose classes persist to it)')
    out.append('')
    tables = [n for n in nodes.values() if n.get('kind') == 'table']
    if tables:
        out.append('| Table | Context | Specs | Comment |')
        out.append('|---|---|---|---|')
        owner = {}
        for e in edges:
            if e.get('rel') == 'owns' and e['from'].startswith('context:'):
                owner.setdefault(e['to'], []).append(e['from'].split(':', 1)[1])
        for n in sorted(tables, key=lambda n: sort_key(n['label'])):
            linked = [s['id'] for s in specs if n['label'] in s['tables']]
            out.append(f"| `{n['label']}` | {', '.join(sorted(owner.get(n['id'], [n.get('community', '')]), key=sort_key))} | {', '.join(linked) or '-'} | {one_line(n.get('note', ''))} |")
    else:
        out.append('_(graph missing - run scripts/gen-graph.py)_')
    out.append('')

    # External services
    out.append('## External services (`generated/openapi/external/`)')
    out.append('')
    if externals:
        out.append('| Service | Description | Contract |')
        out.append('|---|---|---|')
        for title, desc, f in sorted(externals, key=lambda x: sort_key(x[0])):
            out.append(f'| {title} | {one_line(desc)} | `{f}` |')
    else:
        out.append('_(none)_')
    out.append('')

    # Glossary
    out.append('## Glossary terms and their aliases (`domain/glossary.md`)')
    out.append('')
    if terms:
        out.append('| Term | ' + ''.join(f'{c} | ' for c in lang_cols) + 'Aliases (what people also say) | Used in |')
        out.append('|---|' + '---|' * len(lang_cols) + '---|---|')
        for term, lang_terms, aliases, used in terms:
            out.append(f'| {term} | ' + ''.join(f'{t} | ' for t in lang_terms) + f'{aliases} | {used} |')
    else:
        out.append('_(domain/glossary.md missing)_')
    out.append('')
    out.append('<!-- generated by scripts/gen-catalogue.py -->')
    content = '\n'.join(out) + '\n'

    def norm(s):
        return re.sub(r'(?m)^\s*at: .*$', '', re.sub(r'(?m)^> Generated by .* on \d{4}-\d{2}-\d{2}\.', '', s)).replace('\r', '')

    if a.check:
        old = read_text_or_empty(out_path)
        if norm(old) != norm(content):
            print(f'STALE: {rel(repo, out_path)}  (run scripts/gen-catalogue.py)')
            sys.exit(1)
        print(f'catalogue up to date ({len(contexts)} contexts, {len(specs)} specs, {len(calcs)} calculations, {len(flows)} flows, {len(ops)} endpoints)')
        return
    write_text(out_path, content)
    print(f'catalogue: {len(contexts)} contexts, {len(specs)} specs, {len(calcs)} calculations, {len(flows)} flows, '
          f'{len(ops)} endpoints, {len(topics)} topics, {len(tables)} tables, {len(terms)} terms -> {rel(repo, out_path)} ({len(out)} lines)')


if __name__ == '__main__':
    main()
