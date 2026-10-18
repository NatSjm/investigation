#!/usr/bin/env python3
"""REST API index: method | path | operationId | tag | handler | params | file:line. No app start, no build.

Contract first: the operations are read from the OpenAPI document (`rest.open_api` in docs-gen.json, auto-detected
when empty) and joined to their handler in a controller class (`rest.controller_annotation`) either
  - by operationId (`rest.handler_match: operationId`): the method named like the operation, found with
    `rest.handler_pattern` (default `override fun <operationId>(` - controllers implementing generated interfaces), or
  - by route (`rest.handler_match: mapping`): the `@GetMapping("/x")` method whose verb and path (class
    `@RequestMapping` prefix included, constants resolved) equal the contract operation - hand-written controllers.
Operations without a handler are listed as `_not implemented_`. Request mappings found in the controllers that are
not in the contract are appended with tag `(no contract)` (technical endpoints, legacy routes). Without any
contract every mapping is listed from the annotations alone.
Example: python3 scripts/docs/gen-api-index.py --root . --out docs/_generated/api-index.md"""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header,
                     escape_cell, posix, sort_key, utf8_stdout, load_config, module_dirs, main_sources,
                     const_strings, resolve_string_expr, blank_comments)

DEFAULTS = {
    'modules': [], 'source_root': 'src/main/kotlin', 'test_pattern': '', 'exclude_paths': [],
    'rest': {'open_api': '', 'handler_match': 'operationId', 'handler_pattern': r'override\s+fun\s+(\w+)\s*\(',
             'controller_annotation': 'RestController', 'session_header': 'X-Harbor-Session', 'session_marker': 'SessionHeader'},
}
VERBS = ('Get', 'Post', 'Put', 'Patch', 'Delete')
MAPPING_RX = re.compile(r'@(?P<verb>' + '|'.join(VERBS) + r'|Request)Mapping\s*(?:\((?P<args>[^)]*)\))?\s*'
                        r'(?:@\w+(?:\([^)]*\))?\s*)*(?:override\s+|suspend\s+|open\s+)*fun\s+(?P<fn>\w+)\s*\((?P<params>[^)]*)\)')


def mapping_path(args, consts):
    """Path argument of a *Mapping annotation: positional or `value =` / `path =`, literal or constant expression."""
    args = args or ''
    m = re.search(r'(?:\b(?:value|path)\s*=\s*)?(\[?\s*(?:"(?:[^"\\]|\\.)*"|[\w.]+)(?:\s*\+\s*(?:"(?:[^"\\]|\\.)*"|[\w.]+))*\s*\]?)', args)
    if not m:
        return ''
    expr = m.group(1).strip().strip('[]').split(',')[0]
    if re.match(r'^(method|produces|consumes|params|headers)\s*=', expr):
        return ''
    v = resolve_string_expr(expr, consts)
    return v if v is not None else '<' + expr.strip() + '>'


def find_open_api(root, configured):
    if configured:
        return configured if os.path.isfile(os.path.join(root, configured)) else ''
    if os.path.isfile(os.path.join(root, 'api/openapi.yaml')):
        return 'api/openapi.yaml'
    cand = []
    for f in source_files(root, ['*.yaml', '*.yml']):
        if not re.search(r'/src/main/resources/', posix(f), re.I):
            continue
        x = read_text(f)
        if re.search(r'(?m)^openapi:', x, re.I) and re.search(r'(?m)^paths:', x, re.I):
            cand.append(f)
    return rel_path(root, sorted(cand, key=sort_key)[0]) if cand else ''


def parse_contract(text, session_marker):
    """Operations of an OpenAPI document (indentation based, no YAML library): verb, path, operationId, tag, query params, session header."""
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
        elif session_marker and re.search(re.escape(session_marker), line, re.I):
            op['Session'] = True
        elif (m := re.match(r'^\s+-\s+name:\s*(\S+)', line, re.I)):
            pending = m.group(1).strip('"\'')
        elif re.match(r'^\s+in:\s*query', line, re.I) and pending:
            op['Query'].append(pending)
            pending = None
        elif re.match(r'^\s+in:\s*(path|header)', line, re.I):
            pending = None
    return base, ops


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/api-index.md')
    ap.add_argument('--config', default='')
    ap.add_argument('--open-api', default='', help='contract path relative to --root (overrides rest.open_api)')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    rest = cfg['rest']
    open_api = find_open_api(root, a.open_api or rest['open_api'])
    files = main_sources(root, cfg, module_dirs(root, cfg))
    consts = const_strings(files)
    ctrl_rx = re.compile(r'@' + re.escape(rest['controller_annotation']) + r'\b')
    handler_rx = re.compile(rest['handler_pattern'])

    # ---------- controllers: handlers by operationId and request mappings by route ----------
    impls = {}
    mappings = []   # {'Verb','Path','Fn','Params','Handler','Loc'}
    for f in files:
        t = read_text(f)
        if not ctrl_rx.search(t):
            continue
        t = blank_comments(t)   # a comment between an annotation and `class` must not hide the mapping; offsets stay
        rel = rel_path(root, f)
        cm = re.search(r'(?m)^\s*(?:class|object)\s+(\w+)', t)
        cls = cm.group(1) if cm else ''
        for m in handler_rx.finditer(t):
            impls.setdefault(m.group(1), {'Handler': f'{cls}.{m.group(1)}', 'Loc': f'{rel}:{line_number(t, m.start())}'})
        prefix = ''
        pm = re.search(r'@RequestMapping\s*\(([^)]*)\)\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:open\s+)?class\b', t)
        if pm:
            prefix = mapping_path(pm.group(1), consts)
        for m in MAPPING_RX.finditer(t):
            verb = m.group('verb').upper()
            if verb == 'REQUEST':
                vm = re.search(r'RequestMethod\.(\w+)', m.group('args') or '')
                verb = vm.group(1).upper() if vm else 'GET'
            sub = mapping_path(m.group('args'), consts)
            path = (prefix.rstrip('/') + '/' + sub.lstrip('/')).rstrip('/') or '/'
            mappings.append({'Verb': verb, 'Path': path, 'Fn': m.group('fn'),
                             'Params': re.sub(r'\s+', ' ', re.sub(r'@\w+(\([^)]*\))?\s*', '', m.group('params'))).strip(),
                             'Handler': f"{cls}.{m.group('fn')}", 'Loc': f"{rel}:{line_number(t, m.start())}"})
    by_route = {}
    for mp in mappings:
        by_route.setdefault((mp['Verb'], mp['Path']), mp)

    rows = []
    used = set()
    base = ''
    if open_api:
        base, ops = parse_contract(read_text(os.path.join(root, open_api)), rest['session_marker'])
        for o in ops:
            params = re.findall(r'\{(\w+)\}', o['Path']) + [q + '?' for q in o['Query']]
            if o['Session'] and rest['session_header']:
                params.append(rest['session_header'])
            full = base + o['Path']
            if rest['handler_match'] == 'mapping':
                impl = by_route.get((o['Verb'], full)) or by_route.get((o['Verb'], o['Path']))
            else:
                impl = impls.get(o['OpId'])
            if impl and 'Fn' in impl:
                used.add(id(impl))
            rows.append({'Verb': o['Verb'], 'Path': full, 'OpId': o['OpId'], 'Tag': o['Tag'],
                         'Handler': impl['Handler'] if impl else '_not implemented_',
                         'Params': ', '.join(params), 'Loc': impl['Loc'] if impl else open_api})
        implemented = sum(1 for r in rows if r['Handler'] != '_not implemented_')
        how = ('`@*Mapping` route' if rest['handler_match'] == 'mapping' else 'handler method named like the operationId (rest.handler_pattern)') + f" in @{rest['controller_annotation']} classes"
        source = f'{open_api} (contract) + {how}'
        note = (f'{len(rows)} operation(s) from the contract; {implemented} implemented. '
                'Request/response schemas: open the contract `components/schemas`, not the DTO files.')
    else:
        source = f"@{rest['controller_annotation']} / @*Mapping scan"
        note = 'No OpenAPI contract found: endpoints listed from the request mappings. DTO field lists: open the DTO file, not the controller.'
    extra = 0
    for mp in mappings:
        # annotation paths are relative to the servlet context path; the contract's server base names that path
        full = (base + mp['Path']) if (base and not mp['Path'].startswith(base)) else mp['Path']
        if id(mp) in used or (open_api and any(r['Verb'] == mp['Verb'] and r['Path'] == full for r in rows)):
            continue
        rows.append({'Verb': mp['Verb'], 'Path': full, 'OpId': mp['Fn'], 'Tag': '(no contract)' if open_api else '',
                     'Handler': mp['Handler'], 'Params': mp['Params'], 'Loc': mp['Loc']})
        extra += 1
    if open_api and extra:
        note += f' {extra} request mapping(s) outside the contract are tagged `(no contract)`.'

    sb = [header('REST API index (BE)', source), note + '\n', '\n']
    sb.append('| Method | Path | operationId | Tag | Handler | Params | Location |\n|---|---|---|---|---|---|---|\n')
    for r in sorted(rows, key=lambda r: (sort_key(r['Path']), sort_key(r['Verb']))):
        sb.append(f"| {r['Verb']} | `{r['Path']}` | `{r['OpId']}` | {r['Tag']} | `{r['Handler']}` | {escape_cell(r['Params'])} | `{r['Loc']}` |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'api-index: {len(rows)} endpoint(s) -> {a.out}')


if __name__ == '__main__':
    main()
