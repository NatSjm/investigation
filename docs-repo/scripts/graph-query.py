#!/usr/bin/env python3
"""Queries generated/graph/graph.json without any library. CLI twin of the VS Code `#impact` tool,
for IntelliJ users (paste the output into Copilot chat) and for CI analytics (PR -> impacted specs).
Examples:
  python3 scripts/graph-query.py --node topic:market.rates.updated              # neighbourhood, depth 2
  python3 scripts/graph-query.py --node spec:P1-001 --depth 3                   # spec -> code -> tables/topics/routes
  python3 scripts/graph-query.py --files harbor-core/src/main/kotlin/com/acme/harbor/api/Product1Controller.kt src/pages/Product1OverviewPage/Product1OverviewPage.tsx
                                                                                # git diff --name-only | impacted nodes + specs
  python3 scripts/graph-query.py --find proposal                                # fuzzy node search
  python3 scripts/graph-query.py --node feature:product1 --json                 # machine output"""
import argparse
import json
import os
import re
import sys
from collections import deque

from _common import repo_root, read_text, like, sort_key, utf8_stdout


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--graph', default=os.path.join(repo_root(__file__), 'generated/graph/graph.json'))
    ap.add_argument('--node', default='')
    ap.add_argument('--files', nargs='*', default=[])
    ap.add_argument('--find', default='')
    ap.add_argument('--depth', type=int, default=2)
    ap.add_argument('--max-lines', type=int, default=60)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    if not os.path.isfile(a.graph):
        print(f'graph not found: {a.graph} (run scripts/gen-graph.py)', file=sys.stderr)
        sys.exit(1)
    g = json.loads(read_text(a.graph))
    by_id = {n['id']: n for n in g['nodes']}
    out_e = {}
    in_e = {}
    for e in g['edges']:
        out_e.setdefault(e['from'], []).append(e)
        in_e.setdefault(e['to'], []).append(e)

    def fmt(n):
        loc = f" - {n['location']}" if n.get('location') else ''
        note = f" - {n['note']}" if n.get('note') else ''
        return f"{n['id']} [{n['community']}]{loc}{note}"

    def resolve_start(q):
        if q in by_id:
            return [q]
        hits = [n['id'] for n in g['nodes'] if like(n['id'], f'*{q}*') or like(n.get('label', ''), f'*{q}*')]
        if len(hits) == 1:
            return hits
        if len(hits) > 1:
            print(f"ambiguous '{q}': {', '.join(hits)}")
            return []
        print(f"no node matches '{q}'")
        return []

    def bfs(start, max_depth):
        dist = {}
        q = deque()
        for s in start:
            dist[s] = 0
            q.append(s)
        touched = []
        while q:
            c = q.popleft()
            if dist[c] >= max_depth:
                continue
            for e in out_e.get(c, []) + in_e.get(c, []):
                touched.append(e)
                o = e['to'] if e['from'] == c else e['from']
                if o not in dist:
                    dist[o] = dist[c] + 1
                    q.append(o)
        uniq = {}
        for e in touched:
            uniq[(e['from'], e['rel'], e['to'])] = e
        edges = [uniq[k] for k in sorted(uniq, key=lambda k: (sort_key(k[0]), sort_key(k[1]), sort_key(k[2])))]
        return dist, edges

    def emit(start, dist, edges, title):
        if a.json:
            nodes = [{'id': i, 'depth': dist[i], 'kind': by_id[i].get('kind'), 'community': by_id[i].get('community'), 'location': by_id[i].get('location')}
                     for i in sorted(dist, key=lambda i: (dist[i], sort_key(i)))]
            print(json.dumps({'start': start, 'nodes': nodes, 'edges': edges}, indent=2, ensure_ascii=False))
            return
        lines = [f'# {title}', '']
        for d in range(0, a.depth + 1):
            ids = sorted((i for i in dist if dist[i] == d), key=sort_key)
            if not ids:
                continue
            lines.append(f'## depth {d}')
            for i in ids:
                lines.append(f'- {fmt(by_id[i])}')
        lines += ['', '## edges']
        for e in edges:
            src = f" ({e['source']})" if e.get('source') != 'regex-map' else ''
            lines.append(f"- {e['from']} -{e['rel']}-> {e['to']}{src}")
        specs = sorted((i for i in dist if like(i, 'spec:*')), key=sort_key)
        lines += ['', f"## specs in blast radius: {', '.join(specs) if specs else 'none'}"]
        if len(lines) > a.max_lines:
            lines = lines[:a.max_lines] + [f'... ({len(lines) - a.max_lines} more lines; raise --max-lines or lower --depth)']
        for l in lines:
            print(l)

    if a.find:
        for n in sorted((n for n in g['nodes'] if like(n['id'], f'*{a.find}*') or like(n.get('label', ''), f'*{a.find}*') or like(n.get('note', '') or '', f'*{a.find}*')),
                        key=lambda n: sort_key(n['id'])):
            print(f'- {fmt(n)}')
        sys.exit(0)
    files = [x for v in a.files for x in v.split(',') if x.strip()]
    if files:
        norm = [re.sub(r'^\./', '', f.replace('\\', '/')) for f in files]
        start = []
        for n in g['nodes']:
            if not n.get('location'):
                continue
            loc = n['location'].split(':')[0]
            if any(f.lower() == loc.lower() or f.endswith('/' + loc) or loc.endswith('/' + f) for f in norm):
                start.append(n['id'])
        if not start:
            print('no graph nodes located in the given files (not architectural, or maps stale)')
            sys.exit(0)
        dist, edges = bfs(start, a.depth)
        emit(start, dist, edges, f'Impact of {len(files)} changed file(s)')
        sys.exit(0)
    if a.node:
        start = resolve_start(a.node)
        if not start:
            sys.exit(2)
        dist, edges = bfs(start, a.depth)
        emit(start, dist, edges, f"Neighbourhood of {', '.join(start)} (depth {a.depth})")
        sys.exit(0)
    print('usage: graph-query.py --node <id|substring> | --files <paths> | --find <text>  [--depth n] [--json]')


if __name__ == '__main__':
    main()
