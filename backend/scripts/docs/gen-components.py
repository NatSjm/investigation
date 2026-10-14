#!/usr/bin/env python3
"""Component index for a layered (package-by-layer) Kotlin backend: one row per top-level class / object /
interface with its layer (package segment after the base package), Spring stereotype, constructor-injected
dependencies, tables it touches, @docs tags and file:line. This is the map that replaces "one module per business
area": agents and the docs graph read layer + name prefix + dependencies instead of walking folders.

Tables: `@Table(name = "x")` on entities, SQL literals (`from|into|update|join <table>`) in DAOs, and for
Spring Data DAOs (`: JpaRepository<Entity, Id>`) the table of the entity.
Example: python3 scripts/docs/gen-components.py --root . --out docs/_generated/components.md"""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header,
                     blank_comments, posix, unique, sort_key, utf8_stdout)

DECL_RX = re.compile(r'(?m)^(?:@[\w.]+(?:\([^)]*\))?\s+)*(?:(?:public|internal|private|data|abstract|open|sealed|enum|annotation|value|fun)\s+)*(class|object|interface)\s+(\w+)')
ANN_RX = re.compile(r'(?:@[\w.]+(?:\([^)]*\))?\s*)*$')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/components.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    # known tables from migrations (same source as db-schema.md)
    tables = set()
    for f in source_files(root, ['V*.sql']):
        if not re.search(r'/(migration|db)/', posix(f), re.I):
            continue
        for m in re.finditer(r'(?i)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', read_text(f)):
            tables.add(m.group(1).lower())

    files = [f for f in source_files(root, ['*.kt']) if re.search(r'/src/main/', posix(f), re.I)]
    # base package per Maven module = shortest package found in that module
    base_pkg = {}
    for f in files:
        mod = rel_path(root, f).split('/')[0]
        pm = re.search(r'(?m)^package\s+([\w.]+)', read_text(f))
        if pm and (mod not in base_pkg or len(pm.group(1)) < len(base_pkg[mod])):
            base_pkg[mod] = pm.group(1)

    rows = []
    for f in files:
        t = read_text(f)
        rel = rel_path(root, f)
        mod = rel.split('/')[0]
        pm = re.search(r'(?m)^package\s+([\w.]+)', t)
        pkg = pm.group(1) if pm else ''
        layer = ''
        if base_pkg.get(mod) and pkg.startswith(base_pkg[mod]):
            layer = pkg[len(base_pkg[mod]):].lstrip('.').split('.')[0]
        if not layer:
            layer = '(root)'
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
            anns = unique(re.findall(r'@(RestControllerAdvice|RestController|Service|Component|Configuration|Repository|Entity|SpringBootApplication)\b', ann_block + d.group(0)))
            kind = list(anns)
            if re.search(r'@KafkaListener', code, re.I):
                kind.append('KafkaListener')
            if re.search(r'@Scheduled', code, re.I):
                kind.append('Scheduled')
            if re.search(r'kafkaTemplate\.send\(|\.send\(\s*Topics\.', code, re.I):
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
            sm = re.match(r'^[^{\r\n]*?:\s*(?:JpaRepository|CrudRepository|PagingAndSortingRepository|ListCrudRepository)<\s*(\w+)', after)
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
    # Spring Data DAOs inherit the table of their entity; dependencies limited to classes of this repo
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
