#!/usr/bin/env python3
"""Component index for a layered (package-by-layer) Kotlin backend: one row per top-level class / object /
interface with its layer (package segments after the base package, `dao/model` style for configured sub-layers),
Spring stereotype, constructor-injected dependencies, tables it touches, @docs tags and file:line. This is the map
that replaces "one module per business area": agents and the docs graph read layer + name prefix + dependencies
instead of walking folders.

Tables: `@Table(name = "x")` on entities, SQL literals (`from|into|update|join <table>`) in repositories, and for
Spring Data repositories (`: JpaRepository<Entity, Id>`) the table of the entity.
Layout keys read from docs-gen.json: modules, source_root, base_package, layers, stereotypes, repository_bases,
test_pattern, exclude_paths, migrations, kafka.listener_annotation, kafka.producer_pattern, jobs.annotation.
Example: python3 scripts/docs/gen-components.py --root . --out docs/_generated/components.md"""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header,
                     blank_comments, posix, unique, sort_key, utf8_stdout, load_config, module_dirs, main_sources,
                     module_of, package_of, base_package, layer_of)

DECL_RX = re.compile(r'(?m)^(?:@[\w.]+(?:\([^)]*\))?\s+)*(?:(?:public|internal|private|data|abstract|open|sealed|enum|annotation|value|fun)\s+)*(class|object|interface)\s+(\w+)')
ANN_RX = re.compile(r'(?:@[\w.]+(?:\([^)]*\))?\s*)*$')
DEFAULTS = {
    'modules': [], 'source_root': 'src/main/kotlin', 'base_package': '', 'layers': {}, 'test_pattern': '', 'exclude_paths': [],
    'stereotypes': ['RestControllerAdvice', 'RestController', 'Service', 'Component', 'Configuration', 'Repository', 'Entity', 'SpringBootApplication'],
    'repository_bases': ['JpaRepository', 'CrudRepository', 'PagingAndSortingRepository', 'ListCrudRepository'],
    'migrations': {'dir_pattern': '/db/migration/', 'file_patterns': ['V*.sql', 'R*.sql']},
    'kafka': {'listener_annotation': 'KafkaListener', 'producer_pattern': r'\.send\(\s*([^,)]+)'},
    'jobs': {'annotation': 'Scheduled'},
}


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/components.md')
    ap.add_argument('--config', default='')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    modules = module_dirs(root, cfg)
    layers_cfg = cfg['layers']
    stereo_rx = re.compile(r'@(' + '|'.join(re.escape(s) for s in cfg['stereotypes']) + r')\b')
    repo_rx = re.compile(r'^[^{\r\n]*?:\s*(?:' + '|'.join(re.escape(b) for b in cfg['repository_bases']) + r')<\s*(\w+)')
    listener_rx = re.compile(r'@' + re.escape(cfg['kafka']['listener_annotation']) + r'\b')
    producer_rx = re.compile(cfg['kafka']['producer_pattern'])
    scheduled_rx = re.compile(r'@' + re.escape(cfg['jobs']['annotation']) + r'\b')
    mig = cfg['migrations']

    # known tables from migrations (same source as db-schema.md)
    tables = set()
    for f in source_files(root, mig['file_patterns']):
        if not re.search(re.escape(mig['dir_pattern']), posix(f), re.I):
            continue
        for m in re.finditer(r'(?i)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', read_text(f)):
            tables.add(m.group(1).lower())

    files = main_sources(root, cfg, modules)
    texts = {f: read_text(f) for f in files}
    pkgs = {f: package_of(texts[f]) for f in files}
    # base package per module
    base_pkg = {}
    for m in modules:
        base_pkg[m] = base_package(cfg, [pkgs[f] for f in files if module_of(root, f, modules) == m])

    rows = []
    for f in files:
        t = texts[f]
        rel = rel_path(root, f)
        mod = module_of(root, f, modules)
        layer = layer_of(pkgs[f], base_pkg.get(mod, ''), layers_cfg)
        # comments blanked for the dependency / table scan (keeps offsets for line numbers)
        code = blank_comments(t)
        for d in DECL_RX.finditer(code):
            name = d.group(2)
            start = d.start()
            # annotations directly above the declaration, then the KDoc block directly above those (any length)
            prefix = t[:start]
            ann_block = ANN_RX.search(prefix).group(0)
            kdoc = ''
            before_anns = prefix[:len(prefix) - len(ann_block)].rstrip()
            if before_anns.endswith('*/'):
                kd_open = before_anns.rfind('/**')
                if kd_open >= 0:
                    kdoc = before_anns[kd_open + 3:len(before_anns) - 2]
            anns = unique(stereo_rx.findall(ann_block + d.group(0)))
            kind = list(anns)
            if listener_rx.search(code):
                kind.append('KafkaListener')
            if scheduled_rx.search(code):
                kind.append('Scheduled')
            pm = producer_rx.search(code)
            if pm and (re.search(r'KafkaTemplate', code) or re.search(r'^"|\b[A-Z][A-Z0-9_]{2,}\b', (pm.group(1) if pm.groups() else '').strip())):
                kind.append('KafkaProducer')
            if not kind:
                kind = [d.group(1)]
            # primary constructor dependencies: class Name(...) up to the matching ')'
            deps = []
            after = code[d.end():]
            if re.match(r'^\s*(?:<[^>]*>)?\s*(?:@\w+\s*)*(?:constructor\s*)?\(', after, re.I):
                op = after.find('(')
                depth = 0
                end = -1
                for i in range(op, len(after)):
                    if after[i] == '(':
                        depth += 1
                    elif after[i] == ')':
                        depth -= 1
                        if depth == 0:
                            end = i
                            break
                if end > op:
                    params = after[op + 1:end]
                    deps = unique(re.findall(r'(?:val|var)\s+\w+\s*:\s*([A-Z]\w*)', params))
            sm = repo_rx.match(after)
            sup = sm.group(1) if sm else ''
            tbl = []
            tm = re.search(r'@Table\(\s*name\s*=\s*"(\w+)"', ann_block + d.group(0))
            if tm:
                tbl.append(tm.group(1).lower())
            for sq in re.finditer(r'(?i)\b(?:from|into|update|join)\s+(\w+)', t):
                x = sq.group(1).lower()
                if x in tables and x not in tbl:
                    tbl.append(x)
            docs = re.findall(r'@docs\s+([\w.-]+)', kdoc)
            rows.append({'Name': name, 'Layer': layer, 'Module': mod, 'Kind': ', '.join(unique(kind)), 'Deps': deps,
                         'Super': sup, 'Tables': tbl, 'Docs': docs, 'Loc': f'{rel}:{line_number(t, start)}'})
    # Spring Data repositories inherit the table of their entity; dependencies limited to classes of this repo
    by_name = {r['Name']: r for r in rows}
    for r in rows:
        if r['Super'] and r['Super'] in by_name:
            for x in by_name[r['Super']]['Tables']:
                if x not in r['Tables']:
                    r['Tables'].append(x)
        r['Deps'] = [x for x in r['Deps'] if x in by_name and x != r['Name']]

    counts = {}
    for r in rows:
        counts[r['Layer']] = counts.get(r['Layer'], 0) + 1
    layers = [f'{k} {counts[k]}' for k in sorted(counts, key=sort_key)]
    sb = [header('Components (BE)', 'top-level Kotlin declarations per layer',
                 'One row per class: layer, stereotype, injected dependencies, tables, @docs tags and file:line; business context = class-name prefix.')]
    sb.append(f"{len(rows)} declaration(s). Per layer: {', '.join(layers)}. Business context of a class = its name prefix (docs repo `contexts.yml`).\n\n")
    sb.append('| Class | Layer | Module | Kind | Depends on | Tables | @docs | Location |\n|---|---|---|---|---|---|---|---|\n')
    for r in sorted(rows, key=lambda r: (sort_key(r['Layer']), sort_key(r['Name']))):
        deps = ', '.join('`' + x + '`' for x in r['Deps'])
        tb = ', '.join('`' + x + '`' for x in r['Tables'])
        docs = ', '.join('`' + x + '`' for x in r['Docs'])
        sb.append(f"| `{r['Name']}` | {r['Layer']} | {r['Module']} | {r['Kind']} | {deps} | {tb} | {docs} | `{r['Loc']}` |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'components: {len(rows)} declaration(s) -> {a.out}')


if __name__ == '__main__':
    main()
