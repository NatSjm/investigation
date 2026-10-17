#!/usr/bin/env python3
"""Joins the lib-free generated maps (BE + FE + @docs tags) into an architectural knowledge graph.
No libraries: nodes/edges from the Markdown tables, communities = BE modules / FE features,
connected components for cross-repo flows, a tiny PageRank for the budgeted REPO_MAP.

Inputs  (default: generated/be, generated/fe as pushed by the code-repo CI):
  api-index.md, events.md, db-schema.md, codebase-map.md, docs-tags.md     (BE)
  codebase-map.md, routes.md, docs-tags.md                                  (FE)
  optional generated/be/db/schema.json (database documentation) -> table comments, exact foreign keys
  optional graph-export-be.json / graph-export-fe.json  -> precise edges from
    GraphExportTest.kt (Spring context) / gen-graph-fe.ts (TS compiler API); merged, win over regex.
  features/**/<ID>.md, domain/calculations/<id>.md  -> spec nodes get path + status.

Outputs (--out, default generated/graph):
  graph.json              machine view (extension #impact tool, graph-query.py, CI analytics)
  <community>.md          one neighbourhood per module/feature (what Copilot reads, ~30 lines)
  REPO_MAP.md             ranked, budgeted overview (--budget lines) + flows + spec coverage
  index.md                written by scripts/build-index.py (OKF reserved file) - run it after this script

Examples:
  python3 scripts/gen-graph.py
  python3 scripts/gen-graph.py --be-maps ../backend/docs/_generated --fe-maps ../frontend/docs/_generated --out generated/graph
  python3 scripts/gen-graph.py --check        # exit 1 if outputs are stale (CI)"""
import argparse
import json
import os
import re
import sys
from collections import deque

from _common import (repo_root, read_text, read_text_or_empty, write_text, rel, like, sort_key, split_lines, now_utc,
                     walk_files, utf8_stdout)

GRAPH_LAYERS = ('api', 'manager', 'service', 'dao', 'event', 'job', 'client', 'utils', 'validator', 'component')
# layers (first segment or `first/second` as components.md prints them) that are data, not behaviour: no class node
GRAPH_EXCLUDE = ('dao/model', 'api/model')
KIND_ORDER = ('context', 'feature', 'endpoint', 'route', 'class', 'topic', 'channel', 'component', 'table', 'url', 'unknown')


def strip(s):
    return (s or '').strip().strip('`').strip()


def table_rows(text):
    """Every Markdown table in a file as rows (header -> cell), ignoring separator rows."""
    rows = []
    hdr = None
    for line in split_lines(text):
        if not re.match(r'^\s*\|', line):
            hdr = None
            continue
        cells = [c.strip() for c in re.split(r'(?<!\\)\|', line.strip().strip('|'))]
        if hdr is None:
            hdr = cells
            continue
        if re.match(r'^[-:\s]+$', ''.join(cells)):
            continue
        rows.append({hdr[i]: cells[i] for i in range(min(len(hdr), len(cells)))})
    return rows


def section(text, heading):
    m = re.search(r'(?ms)^## ' + re.escape(heading) + r'\s*$(.*?)(?=^## |\Z)', text)
    return m.group(1) if m else ''


def fmt_num(x):
    s = repr(float(x))
    return s[:-2] if s.endswith('.0') else s


def ticks(ids):
    return ', '.join('`' + i + '`' for i in ids)


def db_relations(tbl):
    """Foreign keys of one table of schema.json, tolerant to the common tool shapes:
    table-level `parents` / `foreignKeys` / `relations` entries ({table|parent_table|parentTable|name, columns|column}),
    or column-level `references` / `parents` ({table|parent_table, columns}). Yields {'parent', 'column', 'implied'};
    `implied: true` (SchemaSpy: relation guessed from column names, no constraint in the database) is kept and labelled."""
    out = []
    def parent_name(d):
        for k in ('parent_table', 'parentTable', 'parent', 'referencedTable', 'refTable', 'ref_table', 'foreignTable', 'table', 'tableName', 'name'):
            if isinstance(d.get(k), str) and d[k]:
                return d[k].lower()
        return ''
    def cols(d):
        for k in ('columns', 'column', 'childColumns', 'child_columns', 'foreignKeyColumns', 'fkColumn'):
            v = d.get(k)
            if isinstance(v, str):
                return [v.lower()]
            if isinstance(v, list) and v:
                return [str(x).lower() for x in v]
        return ['']
    for key in ('parents', 'foreignKeys', 'foreign_keys', 'relations'):
        for d in tbl.get(key) or []:
            p = parent_name(d) if isinstance(d, dict) else ''
            if p and p != (tbl.get('name') or '').lower():
                out.append({'parent': p, 'column': cols(d)[0], 'implied': bool(d.get('implied'))})
    for c in tbl.get('columns') or []:
        for key in ('references', 'parents', 'foreignKey'):
            v = c.get(key)
            for d in (v if isinstance(v, list) else [v] if isinstance(v, dict) else []):
                p = parent_name(d)
                if p:
                    out.append({'parent': p, 'column': (c.get('name') or '').lower(), 'implied': bool(d.get('implied'))})
    seen, uniq = set(), []
    for r in out:
        k = (r['parent'], r['column'])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default=repo_root(__file__))
    ap.add_argument('--be-maps', default='generated/be')
    ap.add_argument('--fe-maps', default='generated/fe')
    ap.add_argument('--out', default='generated/graph')
    ap.add_argument('--budget', type=int, default=120)
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    def absp(p):
        return p if os.path.isabs(p) else os.path.join(root, p)
    be_maps, fe_maps, out_dir = absp(a.be_maps), absp(a.fe_maps), absp(a.out)
    date = now_utc().strftime('%Y-%m-%d')

    nodes = {}   # id -> node (insertion order)
    edges = {}   # key -> edge

    def add_node(nid, kind, label, community, repo, location='', note=''):
        if nid not in nodes:
            nodes[nid] = {'id': nid, 'kind': kind, 'label': label, 'community': community, 'repo': repo, 'location': location, 'note': note}
        else:
            n = nodes[nid]
            if not n['location'] and location:
                n['location'] = location
            if not n['note'] and note:
                n['note'] = note
            if n['community'] == 'external' and community != 'external':
                n['community'] = community
                n['repo'] = repo
        return nodes[nid]

    def add_edge(frm, to, rel_, source='regex-map'):
        k = f'{frm}|{rel_}|{to}'
        if k not in edges:
            edges[k] = {'from': frm, 'to': to, 'rel': rel_, 'source': source}
        elif source != 'regex-map':
            edges[k]['source'] = source

    page_dirs = []   # (entry folder, page) from the FE codebase map, longest folder first

    def feature_of(location):
        loc = file_of(location).lower()
        for d, p in page_dirs:
            if loc == d or loc.startswith(d + '/'):
                return p
        return 'fe-app'

    def file_of(location):
        return location.split(':')[0]

    def class_of(location):
        return os.path.splitext(os.path.basename(file_of(location)))[0]

    def path_tokens(p):
        p = re.sub(r'^<BASE>', '', p, flags=re.I)
        p = re.sub(r'^/api/v\d+', '', p, flags=re.I)
        p = re.sub(r'\{[^}]*\}', '{*}', p)
        p = re.sub(r':[A-Za-z_]+', '{*}', p)
        return [x for x in p.strip('/').split('/') if x]

    # FE call "/clients/{*}/overview" matches BE "/api/v1/clients/{clientId}/overview" when FE tokens are a suffix of BE tokens.
    def url_matches(fe_url, be_path):
        f, b = path_tokens(fe_url), path_tokens(be_path)
        if not f or len(f) > len(b):
            return False
        for i in range(1, len(f) + 1):
            # wildcards only match wildcards; a literal must match literally (prevents {*}/x matching every /{id})
            if f[-i].lower() != b[-i].lower():
                return False
        return True

    # ---------- bounded contexts (contexts.yml) ----------
    # Layered backend: the business context of a class is its NAME PREFIX (longest match wins), not its folder. An entry
    # with `*` is a wildcard over the whole class name (`*StressTest` for `Product1StressTestUtils`); its literal part counts.
    ctx_prefixes = []
    ctx_of_feature = {}
    for line in split_lines(read_text_or_empty(os.path.join(root, 'contexts.yml'))):
        m = re.match(r'^\s{2}([\w-]+):\s*\{(.*)\}', line)
        if not m:
            continue
        c, body = m.group(1), m.group(2)
        bm = re.search(r'be:\s*\[([^\]]*)\]', body, re.I)
        if bm:
            for p in bm.group(1).split(','):
                p = p.strip().strip('"\'')
                if p:
                    ctx_prefixes.append((c, p))
        fm_ = re.search(r'fe:\s*(\[[^\]]*\]|"[^"]*"|\'[^\']*\'|[\w*?.-]*)', body, re.I)
        if fm_:
            raw = fm_.group(1).strip()
            raw = raw[1:-1] if raw[:1] in '["\'' else raw
            for p in (x.strip().strip('"\'') for x in raw.split(',')):
                if p:
                    ctx_of_feature[p] = c
    ctx_prefixes.sort(key=lambda x: -len(re.sub(r'[*?]', '', x[1])))

    def context_of(cls):
        for c, p in ctx_prefixes:
            if like(cls, p) if re.search(r'[*?]', p) else cls.startswith(p):
                return c
        return 'shared'

    def context_of_page(page):
        # the bounded context a page folder belongs to (contexts.yml fe list, wildcards), else the page itself
        for p, c in ctx_of_feature.items():
            if like(page, p):
                return c
        # a page folder outside contexts.yml is its own community; `shared` (pieces used by several pages) must not
        # collide with the BE `shared` community (classes matching no prefix)
        return 'fe-shared' if page.lower() == 'shared' else page

    # ---------- BE (components.md: one row per class with layer, deps, tables) ----------
    class_info = {}
    for r in table_rows(read_text_or_empty(os.path.join(be_maps, 'components.md'))):
        cls = strip(r.get('Class'))
        if not cls:
            continue
        class_info[cls] = {'Layer': strip(r.get('Layer')), 'Loc': strip(r.get('Location')), 'Kind': strip(r.get('Kind')),
                           'Deps': re.findall(r'`(\w+)`', r.get('Depends on', '')), 'Tables': re.findall(r'`(\w+)`', r.get('Tables', ''))}
    for cls, ci in class_info.items():
        if ci['Layer'].lower() in GRAPH_EXCLUDE or ci['Layer'].lower().split('/')[0] not in GRAPH_LAYERS:
            continue
        ctx = context_of(cls)
        add_node(f'class:{cls}', 'class', cls, ctx, 'be', ci['Loc'], ci['Layer'] + ('; ' + ci['Kind'] if ci['Kind'] else ''))
        if ctx != 'shared':
            add_node(f'context:{ctx}', 'context', ctx, ctx, 'be')
            add_edge(f'context:{ctx}', f'class:{cls}', 'contains')
            if ci['Layer'].lower() == 'manager':
                nodes[f'context:{ctx}']['location'] = file_of(ci['Loc'])
                nodes[f'context:{ctx}']['note'] = f'entry point {cls} (manager)'
    # constructor injection and static calls to Kotlin objects between architectural classes (controller -> manager ->
    # service -> dao / utils / client, calculator -> helper object)
    for cls, ci in class_info.items():
        if f'class:{cls}' not in nodes:
            continue
        for d in ci['Deps']:
            if f'class:{d}' in nodes:
                add_edge(f'class:{cls}', f'class:{d}', 'depends-on')
    for r in table_rows(read_text_or_empty(os.path.join(be_maps, 'api-index.md'))):
        path = strip(r.get('Path'))
        if not path:
            continue
        loc = strip(r.get('Location'))
        handler = strip(r.get('Handler'))
        if re.match(r'^_', handler):
            cls = ''
            ctx = strip(r.get('Tag')) if r.get('Tag') else 'shared'
        else:
            cls = handler.split('.')[0]
            ctx = context_of(cls)
        method = r.get('Method', '')
        nid = f'endpoint:{method} {path}'
        add_node(nid, 'endpoint', f'{method} {path}', ctx, 'be', loc, f"operationId {strip(r.get('operationId'))}; handler {handler}; params {r.get('Params', '')}")
        if cls:
            add_node(f'class:{cls}', 'class', cls, ctx, 'be', file_of(loc), 'api')
            add_edge(nid, f'class:{cls}', 'handled-by')
        if ctx != 'shared':
            add_node(f'context:{ctx}', 'context', ctx, ctx, 'be')
            add_edge(f'context:{ctx}', nid, 'exposes')
    for r in table_rows(read_text_or_empty(os.path.join(be_maps, 'events.md'))):
        t = strip(r.get('Topic'))
        if not t:
            continue
        tid = f'topic:{t}'
        add_node(tid, 'topic', t, 'external', 'kafka')
        producers = r.get('Producers (this repo)', '')
        consumers = r.get('Consumers (this repo)', '')
        for m in re.finditer(r'`?(\w+)`?\s*\(([^,)]+)', producers):
            loc = m.group(2).strip()
            cls = class_of(loc)
            ctx = context_of(cls)
            add_node(f'class:{cls}', 'class', cls, ctx, 'be', file_of(loc), 'event; producer')
            add_edge(f'class:{cls}', tid, 'produces')
            nodes[tid]['community'] = ctx
            nodes[tid]['repo'] = 'be'
        for m in re.finditer(r'`?(\w+)`?\s*\(([^,)]+)', consumers):
            loc = m.group(2).strip()
            cls = class_of(loc)
            ctx = context_of(cls)
            add_node(f'class:{cls}', 'class', cls, ctx, 'be', file_of(loc), 'event; listener')
            add_edge(tid, f'class:{cls}', 'consumed-by')
            if nodes[tid]['community'] == 'external':
                nodes[tid]['community'] = ctx
                nodes[tid]['repo'] = 'be'
        if re.search('_external_', producers, re.I):
            nodes[tid]['note'] = 'produced outside this repo'
        if re.search('_external_', consumers, re.I):
            nodes[tid]['note'] = '; '.join(x for x in (nodes[tid]['note'], 'consumed outside this repo') if x)
    schema = read_text_or_empty(os.path.join(be_maps, 'db-schema.md'))
    for m in re.finditer(r'(?m)^## `(\w+)`\s*\r?\nCreated in `([^`]+)`', schema):
        t, loc = m.group(1), m.group(2)
        sec = section(schema, f'`{t}`')
        cols = [strip(r.get('Column')) for r in table_rows(sec)]
        # classes touching the table: components.md (exact: @Table, SQL, Spring Data entity) first, db-schema "Used in" second
        touch = [c for c, ci in class_info.items() if t.lower() in (x.lower() for x in ci['Tables'])]
        if not touch:
            um = re.search(r'(?m)^Used in:\s*(.+)$', sec)
            touch = re.findall(r'`(\w+)`', um.group(1) if um else '')
        daos = [c for c in touch if c in class_info and class_info[c]['Layer'].lower().split('/')[0] == 'dao']
        owner = next((c for c in daos + touch if context_of(c) != 'shared'), None)
        ctx = context_of(owner) if owner else 'shared'
        add_node(f'table:{t}', 'table', t, ctx, 'be', loc, f"{len(cols)} columns: {', '.join(cols)}")
        if ctx != 'shared':
            add_node(f'context:{ctx}', 'context', ctx, ctx, 'be')
            add_edge(f'context:{ctx}', f'table:{t}', 'owns')
        for c in touch:
            if f'class:{c}' in nodes:
                add_edge(f'class:{c}', f'table:{t}', 'persists-to')
    db_json = os.path.join(be_maps, 'db', 'schema.json')
    db_tables = []
    if os.path.isfile(db_json):
        try:
            db_tables = json.loads(read_text(db_json)).get('tables', [])
        except ValueError as e:
            print(f'warning: {db_json}: not valid JSON ({e}); ignored')
    if db_tables:
        # database documentation (schema.json of the backend's docs/db): comments and exact foreign keys
        for tbl in db_tables:
            tn = (tbl.get('name') or '').lower()
            if not tn:
                continue
            cols = [c.get('name', '') for c in tbl.get('columns', [])]
            comment = ' '.join((tbl.get('comment') or '').split())
            note = (comment[:160] + ('...' if len(comment) > 160 else '')) if comment else ''
            nid = f'table:{tn}'
            page = f'generated/be/db/schema/tables/{tn}.md'
            if nid in nodes:
                if note:
                    nodes[nid]['note'] = note + f' ({len(cols)} columns)'
                if not nodes[nid]['location']:
                    nodes[nid]['location'] = page
            else:
                add_node(nid, 'table', tn, 'shared', 'be', page, (note + ' ' if note else '') + f"({len(cols)} columns: {', '.join(cols)})")
            for rel_ in db_relations(tbl):
                label = f"fk {rel_['column']}" + (' (implied, no constraint)' if rel_['implied'] else '')
                add_edge(f"table:{rel_['parent']}", nid, label, 'db-docs')
    for m in re.finditer(r'(?m)^\s*(\w+)\s*\|[|o}{\-]+\s*(\w+)\s*:\s*(\w+)', schema):
        if not db_tables:
            add_edge(f'table:{m.group(2)}', f'table:{m.group(1)}', f'fk {m.group(3)}')

    # ---------- FE ----------
    fe_exports = {}
    fe_rows = table_rows(read_text_or_empty(os.path.join(fe_maps, 'codebase-map.md')))
    for r in fe_rows:
        f = strip(r.get('Page')) or strip(r.get('Feature'))
        entry = strip(r.get('Entry'))
        if f and f != 'fe-app' and entry:
            d = re.sub(r'/[^/]*$', '', entry) if re.search(r'\.\w+$', entry) or entry.endswith('/-') else entry
            page_dirs.append((d.rstrip('/').lower(), f))
    page_dirs.sort(key=lambda x: -len(x[0]))
    for r in fe_rows:
        f = strip(r.get('Page')) or strip(r.get('Feature'))
        if not f:
            continue
        add_node(f'feature:{f}', 'feature', f, context_of_page(f), 'fe', strip(r.get('Entry')), strip(r.get('Purpose')))
        fe_exports[f] = [f] + [x.strip() for x in re.split(r',\s*', (r.get('Public exports') or '') + ',' + (r.get('Components') or '')) if x.strip()]
        for url in (x.strip() for x in r.get('API calls', '').split('<br>') if x.strip()):
            hits = [n for n in list(nodes.values()) if n['kind'] == 'endpoint' and url_matches(url, re.sub(r'^\w+\s+', '', n['label']))]
            if not hits:
                add_node(f'url:{url}', 'url', url, f, 'fe', '', 'no BE endpoint matched (external service or stale map?)')
                add_edge(f'feature:{f}', f'url:{url}', 'calls')
            for h in hits:
                add_edge(f'feature:{f}', h['id'], 'calls')
        # browser channels (BroadcastChannel) - the FE counterpart of topics: `defines` / `pub` / `sub` <name>
        if 'Channels' in r:
            for c in (x.strip() for x in r['Channels'].split('<br>') if x.strip()):
                cm = re.match(r'^(defines|pub|sub)\s+(\S+)(?:\s+\((\S+)\))?$', c, re.I)
                if not cm:
                    continue
                verb, cname = cm.group(1).lower(), cm.group(2)
                cid_ = f'channel:{cname}'
                add_node(cid_, 'channel', cname, nodes[f'feature:{f}']['community'], 'fe', '', 'BroadcastChannel')
                if verb == 'defines':
                    nodes[cid_]['community'] = nodes[f'feature:{f}']['community']
                    nodes[cid_]['location'] = cm.group(3) or re.sub(r'/index\.tsx?$', '/channel.ts', strip(r.get('Entry')), flags=re.I)
                    add_edge(f'feature:{f}', cid_, 'defines')
                elif verb == 'pub':
                    add_edge(f'feature:{f}', cid_, 'produces')
                else:
                    add_edge(cid_, f'feature:{f}', 'consumed-by')
    # shared component library (components.md, optional): component nodes in community `shared-ui`, rendered by features
    fe_components = os.path.join(fe_maps, 'components.md')
    if os.path.isfile(fe_components):
        for r in table_rows(read_text(fe_components)):
            c = strip(r.get('Component'))
            if not c:
                continue
            add_node(f'component:{c}', 'component', c, 'shared-ui', 'fe', strip(r.get('Location')), f"library/{strip(r.get('Group'))}; {strip(r.get('Purpose'))}")
            for u in re.findall(r'`([\w-]+)`', r.get('Used by', '')):
                add_edge(f'feature:{u}', f'component:{c}', 'renders')
    for r in table_rows(read_text_or_empty(os.path.join(fe_maps, 'routes.md'))):
        p = strip(r.get('Path'))
        if not p:
            continue
        comp = strip(r.get('Component'))
        loc = strip(r.get('Location'))
        feat = next((k for k, v in fe_exports.items() if comp.lower() in (x.lower() for x in v)), None) or feature_of(loc)
        add_node(f'route:{p}', 'route', p, nodes.get(f'feature:{feat}', {}).get('community', feat), 'fe', loc, f'renders {comp}')
        add_edge(f'route:{p}', f'feature:{feat}', 'renders')

    # ---------- @docs tags (both repos) + spec files ----------
    def add_tags(file, repo):
        for r in table_rows(read_text_or_empty(file)):
            sid = strip(r.get('Spec ID'))
            if not sid:
                continue
            loc = strip(r.get('Location'))
            comm = context_of(class_of(loc)) if repo == 'be' else feature_of(loc)
            kind = 'calculation' if re.match(r'^[a-z][a-z0-9_]+$', sid, re.I) else 'spec'
            add_node(f'spec:{sid}', kind, sid, 'docs', 'docs')
            target = f'class:{class_of(loc)}' if repo == 'be' else f'feature:{comm}'
            if repo == 'be':
                add_node(target, 'class', class_of(loc), comm, 'be', file_of(loc))
            else:
                add_node(target, 'feature', comm, context_of_page(comm), 'fe', '' if comm == 'fe-app' else file_of(loc))
            add_edge(f'spec:{sid}', target, 'implemented-by')
            nodes[f'spec:{sid}']['note'] = '; '.join(x for x in (nodes[f'spec:{sid}']['note'], f'{repo} {loc}') if x)
    add_tags(os.path.join(be_maps, 'docs-tags.md'), 'be')
    add_tags(os.path.join(fe_maps, 'docs-tags.md'), 'fe')
    for d in ('features', 'domain'):
        for f in walk_files(os.path.join(root, d), '*.md'):
            if os.path.basename(f).lower() in ('index.md', 'log.md'):
                continue
            sid = os.path.splitext(os.path.basename(f))[0]
            if sid.startswith('_') or sid.lower() == 'conventions' or 'template' in sid.lower():
                continue
            fm = read_text(f)
            sm = re.search(r'(?m)^status:\s*(\S+)', fm, re.I)
            status = sm.group(1) if sm else ''
            r = rel(root, f)
            kind = 'calculation' if like(r, 'domain/calculations/*') else 'spec' if like(r, 'features/*') else 'doc'
            if kind == 'doc':
                continue
            n = add_node(f'spec:{sid}', kind, sid, 'docs', 'docs', r)
            n['location'] = r
            if status:
                n['note'] = '; '.join(x for x in (f'status {status}', n['note']) if x)

    # ---------- docs-map.yml: explicit code path -> spec mappings (makes @docs tags optional) ----------
    # A row `paths: [be/..., fe/...] -> specs: [features/x/ID.md]` adds the same `implemented-by` edges an `@docs ID`
    # tag would, so a repository can start documenting before anyone touches application source. Spec globs
    # (`domain/calculations/**`) are skipped: they map paths to a folder, not to one concept.
    docs_map = os.path.join(root, 'docs-map.yml')
    if os.path.isfile(docs_map):
        def test_map_glob(glob_, path):
            rx = '^' + re.escape(glob_).replace(r'\*\*/', '(.*/)?').replace(r'\*\*', '.*').replace(r'\*', '[^/]*') + '$'
            return re.match(rx, path, re.I) is not None
        map_rows = []
        cur = None
        sect = ''
        for l in split_lines(read_text(docs_map)):
            if re.match(r'^\s*#', l) or not l.strip():
                continue
            if re.match(r'^mappings:', l, re.I):
                sect = 'map'
                continue
            if re.match(r'^ignore:', l, re.I):
                sect = 'ignore'
                continue
            if sect == 'map':
                pm = re.match(r'^\s*-\s*paths:\s*\[(.*)\]', l, re.I)
                if pm:
                    cur = {'Paths': [x for x in (p.strip().strip('"') for p in pm.group(1).split(',')) if x], 'Specs': []}
                    map_rows.append(cur)
                    continue
                sm = re.match(r'^\s*specs:\s*\[(.*?)\]', l, re.I)
                if sm and cur is not None:
                    cur['Specs'] = [x for x in (p.strip().strip('"') for p in sm.group(1).split(',')) if x]
        be_classes = [n for n in nodes.values() if n['kind'] == 'class' and n['repo'] == 'be' and n['location']]
        fe_features = [n for n in nodes.values() if n['kind'] == 'feature' and n['location']]
        map_edges = 0
        for row in map_rows:
            ids = [os.path.splitext(os.path.basename(s))[0] for s in row['Specs']
                   if '*' not in s and re.match(r'^(features/[^/]+/|domain/calculations/)[^/]+\.md$', s, re.I)]
            if not ids:
                continue
            for g in row['Paths']:
                targets = []
                if like(g, 'be/*'):
                    targets = [n['id'] for n in be_classes if test_map_glob(g, 'be/' + file_of(n['location']))]
                elif like(g, 'fe/*'):
                    targets = [n['id'] for n in fe_features if test_map_glob(g, 'fe/' + file_of(n['location']))]
                for sid in ids:
                    if f'spec:{sid}' not in nodes:
                        continue
                    for t in targets:
                        if f'spec:{sid}|implemented-by|{t}' not in edges:
                            add_edge(f'spec:{sid}', t, 'implemented-by', 'docs-map')
                            map_edges += 1
        print(f'docs-map: {map_edges} implemented-by edge(s) added from docs-map.yml')

    # ---------- precise exports (optional) ----------
    for fname, d in (('graph-export-be.json', be_maps), ('graph-export-fe.json', fe_maps)):
        p = os.path.join(d, fname)
        if not os.path.isfile(p):
            continue
        j = json.loads(read_text(p))
        for n in j.get('nodes') or []:
            # the BE export leaves the community empty: the bounded context comes from the class-name prefix (contexts.yml)
            comm = str(n.get('community') or '')
            if not comm:
                comm = context_of(n.get('label', '')) if n.get('kind') == 'class' else 'external' if n.get('kind') == 'topic' else 'shared'
            elif (n.get('repo') or '') == 'fe' and comm != 'fe-app':
                # the FE export names the page folder: fold it into its bounded context (contexts.yml fe list)
                comm = context_of_page(comm)
            add_node(n['id'], n.get('kind', ''), n.get('label', ''), comm, n.get('repo') or '', str(n.get('location') or ''), str(n.get('note') or ''))
        for e in j.get('edges') or []:
            add_edge(e['from'], e['to'], e['rel'], 'export')
    # Fold exported FE "url:METHOD path" nodes onto the matching BE endpoint (method + suffix match); unmatched ones stay as url nodes.
    for u in [n for n in list(nodes.values()) if n['kind'] == 'url' and re.match(r'^(GET|POST|PUT|PATCH|DELETE) (.+)$', n['label'], re.I)]:
        m = re.match(r'^(\w+) (.+)$', u['label'])
        method, url = m.group(1), m.group(2)
        hit = next((n for n in list(nodes.values()) if n['kind'] == 'endpoint' and like(n['label'], f'{method} *')
                    and url_matches(url, re.sub(r'^\w+\s+', '', n['label']))), None)
        if not hit:
            continue
        for k in list(edges):
            e = edges[k]
            if e['to'] == u['id']:
                del edges[k]
                add_edge(e['from'], hit['id'], 'calls', 'export')
        del nodes[u['id']]

    # ---------- analytics: components, PageRank ----------
    adj = {nid: [] for nid in nodes}
    for e in list(edges.values()):
        if e['from'] not in nodes:
            add_node(e['from'], 'unknown', e['from'], 'external', '?')
            adj[e['from']] = []
        if e['to'] not in nodes:
            add_node(e['to'], 'unknown', e['to'], 'external', '?')
            adj[e['to']] = []
        adj[e['from']].append(e['to'])
        adj[e['to']].append(e['from'])
    component = {}
    cid = 0
    for nid in sorted(nodes, key=sort_key):   # sorted so component ids are deterministic across processes
        if nid in component:
            continue
        cid += 1
        q = deque([nid])
        component[nid] = cid
        while q:
            c = q.popleft()
            for n in adj[c]:
                if n not in component:
                    component[n] = cid
                    q.append(n)
    total = len(nodes)
    pr = {nid: 1.0 / total for nid in nodes}
    for _ in range(25):
        nxt = {}
        for nid in nodes:
            s = 0.0
            for nb in adj[nid]:
                if adj[nb]:
                    s += pr[nb] / len(adj[nb])
            nxt[nid] = 0.15 / total + 0.85 * s
        pr = nxt
    for nid, n in nodes.items():
        n['component'] = component[nid]
        n['rank'] = round(pr[nid] * 1000, 2)
        n['degree'] = len(adj[nid])

    # ---------- render ----------
    node_objs = sorted(nodes.values(), key=lambda n: sort_key(n['id']))
    edge_objs = list(edges.values())
    groups = {}
    for n in node_objs:
        if n['community'].lower() in ('docs', 'external'):
            continue
        groups.setdefault(n['community'], []).append(n)
    communities = [(k, groups[k]) for k in sorted(groups, key=sort_key)]

    def header(title, desc):
        t = title.replace('"', '\\"')
        d = desc.replace('"', '\\"')
        return (f'---\ntype: Document\ntitle: "{t}"\ndescription: "{d}"\ngenerated:\n  by: process:gen-graph\n  at: {date}\nstatus: stable\n---\n'
                f'# {title}\n\n> Generated by `scripts/gen-graph.py` from `generated/be`, `generated/fe` and `@docs` tags. Do not edit by hand.\n')

    def fmt(n):
        loc = f" - `{n['location']}`" if n['location'] else ''
        note = f" - {n['note']}" if n['note'] else ''
        return f"`{n['id']}`{loc}{note}"

    def cross(e, comm):
        o = nodes[e['to']] if nodes[e['from']]['community'] == comm else nodes[e['from']]
        return f" (-> {o['community']})" if o['community'] != comm else ''

    def repos_of(group):
        return '+'.join(sorted(set(n['repo'] for n in group), key=sort_key))

    files = {}
    for comm, group in communities:
        members = sorted(group, key=lambda n: (-n['rank'], sort_key(n['id'])))
        ids = [n['id'] for n in members]
        ids_set = set(ids)
        head = next((n for n in members if n['kind'] in ('context', 'feature')), None)
        desc = head['note'] if head and head['note'] else f'Neighbourhood of {comm}'
        sb = [header(f'Graph: {comm} ({repos_of(group)})', desc)]
        sb.append(f'{len(members)} nodes. Read this file instead of walking the module; open only the `file:line` you need.\n\n')
        kinds = {}
        for n in members:
            kinds.setdefault(n['kind'], []).append(n)
        for kind in sorted(kinds, key=lambda k: KIND_ORDER.index(k) if k in KIND_ORDER else -1):
            plural = 'classes' if kind == 'class' else f'{kind}s'
            sb.append(f'## {plural}\n')
            for n in kinds[kind]:
                sb.append(f'- {fmt(n)}\n')
            sb.append('\n')
        sb.append('## Edges\n')
        own = sorted((e for e in edge_objs if e['from'] in ids_set or e['to'] in ids_set),
                     key=lambda e: (sort_key(e['rel']), sort_key(e['from']), sort_key(e['to'])))
        for e in own:
            flag = ' (heuristic)' if e['source'] == 'name-heuristic' else ' (exact)' if e['source'] == 'export' else ''
            sb.append(f"- `{e['from']}` -{e['rel']}-> `{e['to']}`{cross(e, comm)}{flag}\n")
        sb.append('\n')
        specs = sorted(set(e['from'] for e in own if like(e['from'], 'spec:*')), key=sort_key)
        sb.append('## Specs touching this community\n')
        if specs:
            for s in specs:
                sb.append(f'- {fmt(nodes[s])}\n')
        else:
            sb.append('- none (add `@docs <ID>` tags)\n')
        files[f'{comm}.md'] = ''.join(sb)

    # REPO_MAP: ranked within budget
    sb = [header('REPO_MAP', 'Ranked architectural map of BE + FE + docs; read first, then one graph/<community>.md')]
    sb.append(f'{len(nodes)} nodes, {len(edges)} edges, {len(communities)} communities, {cid} connected component(s). Budget {a.budget} lines; lower-ranked nodes live only in `<community>.md` / `graph.json`.\n\n')
    sb.append('## Communities\n')
    for comm, group in communities:
        h = next((n for n in group if n['kind'] in ('context', 'feature')), None)
        d = f" - {h['note']}" if h and h['note'] else ''
        sb.append(f'- [{comm}]({comm}.md) ({repos_of(group)}, {len(group)} nodes){d}\n')
    sb.append('\n## Top nodes (PageRank)\n')
    used = ''.join(sb).count('\n') + 1
    ranked = sorted((n for n in node_objs if n['kind'] != 'unknown'), key=lambda n: (-n['rank'], sort_key(n['id'])))
    left = max(10, a.budget - used - 30)
    for n in ranked[:left]:
        sb.append(f"- {fmt_num(n['rank'])} `{n['id']}` [{n['community']}] deg {n['degree']}" + (f" - `{n['location']}`" if n['location'] else '') + '\n')
    sb.append('\n## Cross-repo flows (route -> feature -> endpoint -> class -> topic/table)\n')
    for e in sorted((e for e in edge_objs if e['rel'] == 'calls' and like(e['to'], 'endpoint:*')), key=lambda e: (sort_key(e['from']), sort_key(e['to']))):
        ep = nodes[e['to']]
        cls = sorted((x['to'] for x in edges.values() if x['from'] == ep['id'] and x['rel'] == 'handled-by'), key=sort_key)
        down = sorted((x['to'] for x in edges.values() if x['from'] in cls and x['rel'] in ('produces', 'persists-to')), key=sort_key)
        routes = sorted((x['from'] for x in edges.values() if x['to'] == e['from'] and x['rel'] == 'renders'), key=sort_key)
        line = '- ' + ticks(routes + [e['from']]) + ' -> ' + ticks([ep['id']]) + ' -> ' + ticks(cls)
        if down:
            line += ' -> ' + ticks(down)
        sb.append(line + '\n')
    sb.append('\n## Spec coverage\n')
    impl = set(e['from'] for e in edges.values() if e['rel'] == 'implemented-by')
    for s in sorted((n for n in node_objs if n['kind'] in ('spec', 'calculation')), key=lambda n: sort_key(n['id'])):
        has_file, has_code = bool(s['location']), s['id'] in impl
        state = 'spec + code' if has_file and has_code else 'spec only - no @docs tag and no docs-map.yml path in code' if has_file else 'code only - no spec file in docs repo'
        sb.append(f"- `{s['id']}`: {state}" + (f" ({s['note']})" if s['note'] else '') + '\n')
    files['REPO_MAP.md'] = ''.join(sb)

    # graph.json
    gj = {
        'generated': {'by': 'process:gen-graph', 'at': date},
        'communities': [{'id': comm, 'repo': repos_of(group), 'nodes': len(group)} for comm, group in communities],
        'nodes': node_objs,
        'edges': sorted(edge_objs, key=lambda e: (sort_key(e['from']), sort_key(e['rel']), sort_key(e['to']))),
    }
    files['graph.json'] = json.dumps(gj, indent=2, ensure_ascii=False) + '\n'

    # index.md is an OKF reserved file: scripts/build-index.py owns it (run after this script / in CI).

    # ---------- write / check ----------
    def norm(s):
        return re.sub(r'(?m)^\s*"at":\s*".*"\s*,?$', '', re.sub(r'(?m)^\s*at: .*$', '', s)).replace('\r', '')
    if a.check:
        stale = []
        for k, content in files.items():
            p = os.path.join(out_dir, k)
            if not os.path.isfile(p) or norm(read_text(p)) != norm(content):
                stale.append(k)
        # community files of contexts that no longer exist are stale too
        if os.path.isdir(out_dir):
            stale += [f'{f} (orphan)' for f in sorted(os.listdir(out_dir), key=str.lower)
                      if f.lower().endswith('.md') and f.lower() != 'index.md' and f not in files]
        if stale:
            print(f"STALE: {', '.join(stale)}  (run scripts/gen-graph.py)")
            sys.exit(1)
        print(f'graph up to date ({len(nodes)} nodes, {len(edges)} edges)')
        sys.exit(0)
    for k, content in files.items():
        write_text(os.path.join(out_dir, k), content)
    # prune community files of contexts that disappeared (renamed/merged contexts, restructured repos)
    if os.path.isdir(out_dir):
        for f in sorted(os.listdir(out_dir), key=str.lower):
            if f.lower().endswith('.md') and f.lower() != 'index.md' and f not in files:
                os.remove(os.path.join(out_dir, f))
                print(f'  removed orphan {f}')
    print(f'graph: {len(nodes)} nodes, {len(edges)} edges, {len(communities)} communities -> {out_dir}')


if __name__ == '__main__':
    main()
