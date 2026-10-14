#!/usr/bin/env python3
"""REST API index: method | path | operationId | handler | params | file:line. No app start, no build.

Contract-first mode (default when api/openapi.yaml exists): operations are read from the OpenAPI document
(the contract both FE and BE are generated from) and joined to the implementing `override fun <operationId>(`
in a `@RestController` class. Endpoints without an implementation are listed as `_not implemented_`.

Annotation mode (fallback): `@RestController` + `@*Mapping` scan, for repos that are not contract-first.
Example: python3 scripts/docs/gen-api-index.py --root . --out docs/_generated/api-index.md"""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header,
                     escape_cell, posix, sort_key, utf8_stdout)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/api-index.md')
    # path of OUR OpenAPI contract relative to --root; empty = auto-detect: api/openapi.yaml, else the first
    # */src/main/resources/openapi/*.y*ml that is an OpenAPI document with paths (AsyncAPI files are skipped)
    ap.add_argument('--open-api', default='')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    rows = []
    open_api = a.open_api
    if not open_api:
        if os.path.isfile(os.path.join(root, 'api/openapi.yaml')):
            open_api = 'api/openapi.yaml'
        else:
            cand = []
            for f in source_files(root, ['*.yaml', '*.yml']):
                if not re.search(r'/src/main/resources/openapi/', posix(f), re.I):
                    continue
                x = read_text(f)
                if re.search(r'(?m)^openapi:', x, re.I) and re.search(r'(?m)^paths:', x, re.I):
                    cand.append(f)
            if cand:
                open_api = rel_path(root, sorted(cand, key=sort_key)[0])
    spec_path = os.path.join(root, open_api) if open_api else os.path.join(root, '__none__')

    if os.path.isfile(spec_path):
        # ---------- contract-first: parse the OpenAPI document (indentation-based, no YAML library) ----------
        text = read_text(spec_path)
        base = ''
        sm = re.search(r'(?ms)^servers:\s*\r?\n\s*-\s*url:\s*(\S+)', text)
        if sm:
            base = sm.group(1).strip('"\'').rstrip('/')
            hm = re.match(r'^https?://[^/]+(/.*)?$', base, re.I)
            if hm:
                base = hm.group(1) or ''
        ops = []
        in_paths = False
        cur_path = None
        op = None
        pending = None
        tags_list = False
        for line in re.split(r'\r?\n', text):
            if re.match(r'^paths:\s*$', line, re.I):
                in_paths = True
                continue
            if in_paths and re.match(r'^\S', line):
                in_paths = False
            if not in_paths:
                continue
            m = re.match(r'^  (/\S*):\s*$', line, re.I)
            if m:
                cur_path = m.group(1)
                op = None
                continue
            m = re.match(r'^    (get|post|put|patch|delete|head|options):\s*$', line, re.I)
            if m:
                op = {'Verb': m.group(1).upper(), 'Path': cur_path, 'OpId': '', 'Tag': '', 'Query': [], 'Session': False, 'Summary': ''}
                ops.append(op)
                tags_list = False
                continue
            if op is None:
                continue
            if (m := re.match(r'^      operationId:\s*(\S+)', line, re.I)):
                op['OpId'] = m.group(1).strip('"\'')
            elif (m := re.match(r'^      summary:\s*(.+)$', line, re.I)):
                op['Summary'] = m.group(1).strip().strip('"\'')
            elif (m := re.match(r'^      tags:\s*\[([^\]]*)\]', line, re.I)):
                op['Tag'] = m.group(1).split(',')[0].strip().strip('"\'')
            elif re.match(r'^      tags:\s*$', line, re.I):
                tags_list = True
            elif tags_list and (m := re.match(r'^\s+-\s*(\S+)', line, re.I)):
                op['Tag'] = m.group(1).strip('"\'')
                tags_list = False
            elif re.search(r'SessionHeader', line, re.I):
                op['Session'] = True
            elif (m := re.match(r'^\s+-\s+name:\s*(\S+)', line, re.I)):
                pending = m.group(1).strip('"\'')
            elif re.match(r'^\s+in:\s*query', line, re.I) and pending:
                op['Query'].append(pending)
                pending = None
            elif re.match(r'^\s+in:\s*(path|header)', line, re.I):
                pending = None
        # implementations: override fun <operationId>( inside @RestController classes
        impls = {}
        for f in source_files(root, ['*.kt']):
            t = read_text(f)
            if not re.search(r'@RestController', t, re.I):
                continue
            rel = rel_path(root, f)
            cm = re.search(r'(?m)^\s*class\s+(\w+)', t)
            cls = cm.group(1) if cm else ''
            for m in re.finditer(r'override\s+fun\s+(\w+)\s*\(', t):
                impls[m.group(1)] = {'Handler': f'{cls}.{m.group(1)}', 'Loc': f'{rel}:{line_number(t, m.start())}'}
        for o in ops:
            params = re.findall(r'\{(\w+)\}', o['Path']) + [q + '?' for q in o['Query']]
            if o['Session']:
                params.append('X-Harbor-Session')
            impl = impls.get(o['OpId'])
            rows.append({
                'Verb': o['Verb'], 'Path': base + o['Path'], 'OpId': o['OpId'], 'Tag': o['Tag'],
                'Handler': impl['Handler'] if impl else '_not implemented_',
                'Params': ', '.join(params), 'Loc': impl['Loc'] if impl else open_api,
            })
        source = f'{open_api} (contract) + override fun <operationId> lookup in @RestController classes'
        implemented = sum(1 for r in rows if r['Handler'] != '_not implemented_')
        note = (f'{len(rows)} operation(s) from the contract; {implemented} implemented. '
                'Request/response schemas: open the contract `components/schemas`, not the DTO files.')
    else:
        # ---------- annotation mode ----------
        verbs = ['Get', 'Post', 'Put', 'Patch', 'Delete']
        rx = re.compile(r'@(' + '|'.join(verbs) + r')Mapping\s*(?:\(\s*(?:value\s*=\s*)?\[?"([^"]*)"[^)]*\))?\s*'
                        r'(?:@\w+(?:\([^)]*\))?\s*)*(?:override\s+|suspend\s+)*fun\s+(\w+)\s*\(([^)]*)\)')
        for f in source_files(root, ['*.kt']):
            t = read_text(f)
            if not re.search(r'@RestController', t, re.I):
                continue
            rel = rel_path(root, f)
            base = ''
            cm = re.search(r'@RequestMapping\(\s*(?:value\s*=\s*)?\[?"([^"]*)"', t)
            if cm:
                base = cm.group(1)
            km = re.search(r'(?m)^\s*class\s+(\w+)', t)
            cls = km.group(1) if km else ''
            for m in rx.finditer(t):
                path = (base.rstrip('/') + '/' + (m.group(2) or '').lstrip('/')).rstrip('/')
                if not path:
                    path = '/'
                rows.append({
                    'Verb': m.group(1).upper(), 'Path': path, 'OpId': m.group(3), 'Tag': '',
                    'Handler': f'{cls}.{m.group(3)}',
                    'Params': re.sub(r'\s+', ' ', re.sub(r'@\w+(\([^)]*\))?\s*', '', m.group(4))).strip(),
                    'Loc': f'{rel}:{line_number(t, m.start())}',
                })
        source = '@RestController / @*Mapping scan'
        note = f'{len(rows)} endpoint(s). DTO field lists: open the DTO file, not the controller.'

    sb = [header('REST API index (BE)', source), note + '\n', '\n']
    sb.append('| Method | Path | operationId | Tag | Handler | Params | Location |\n|---|---|---|---|---|---|---|\n')
    for r in sorted(rows, key=lambda r: (sort_key(r['Path']), sort_key(r['Verb']))):
        sb.append(f"| {r['Verb']} | `{r['Path']}` | `{r['OpId']}` | {r['Tag']} | `{r['Handler']}` | {escape_cell(r['Params'])} | `{r['Loc']}` |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'api-index: {len(rows)} endpoint(s) -> {a.out}')


if __name__ == '__main__':
    main()
