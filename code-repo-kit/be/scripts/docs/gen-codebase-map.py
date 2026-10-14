#!/usr/bin/env python3
"""Codebase map for a Maven/Kotlin backend organised by technical layer (package-by-layer):
modules (root pom) -> layers (package segment after the base package) -> classes, plus resource folders.
One line per module and per layer; details per class are in components.md.
Example: python3 scripts/docs/gen-codebase-map.py --root . --out docs/_generated/codebase-map.md"""
import argparse
import os
import re
import xml.etree.ElementTree as ET

from _common import (read_text, write_text, source_files, resolve_out, rel_path, header, escape_cell, sort_key,
                     utf8_stdout)

NS = '{http://maven.apache.org/POM/4.0.0}'

# conventional meaning of layer folders (extend when the real repo has more)
ROLES = {
    'advice': 'global exception handling (@RestControllerAdvice -> ProblemDetail)',
    'api': 'REST controllers implementing the generated *Api interfaces (one per contract tag)',
    'client': 'wrappers over generated REST clients of external services (contracts in resources/api)',
    'component': 'infrastructure components (filters, parsers, template loaders)',
    'config': 'Spring configuration',
    'context': 'request / session context holders',
    'dao': 'repositories (Spring Data / JDBC) - tables per class in components.md',
    'databind': 'Jackson serializers / deserializers',
    'enums': 'enumerations',
    'event': 'Kafka listeners and publishers (topics in events.md)',
    'exception': 'exception types',
    'job': 'scheduled jobs (triggers in jobs.md)',
    'manager': 'orchestration per bounded context; transactional boundary; KDoc + @docs - READ FIRST',
    'mapper': 'entity <-> DTO mappers',
    'model': 'JPA entities and internal models',
    'service': 'business services used by managers',
    'utils': 'calculations (pure Kotlin, @docs <calculation>) and helpers',
    'validator': 'request validation',
}
LIST_ALL = ('api', 'manager', 'job', 'event', 'client', 'utils', 'validator', 'component', 'service')


def code(s):
    return s if s.startswith('(+') else '`' + s + '`'


def code_list(items):
    return ', '.join(code(str(x)) for x in items)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/codebase-map.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    root_pom = os.path.join(root, 'pom.xml')
    if not os.path.isfile(root_pom):
        raise SystemExit(f'No pom.xml in {root}')
    pom = ET.fromstring(read_text(root_pom))
    modules = [m.text.strip() for m in pom.findall(f'.//{NS}modules/{NS}module') if m.text]
    if not modules:
        modules = ['.']

    sb = [header('Codebase map (BE)', 'pom.xml modules + package-by-layer scan',
                 'Backend modules, technical layers with their classes and resource folders; read the manager of a context first.')]
    sb.append('Layered backend: the business context of a class is its **name prefix** (`Product1*`, `Stress*` ...), not its folder.\n')
    sb.append("Read order: the context's `manager/*Manager.kt` (KDoc + `@docs`) -> the service / dao / utils it depends on (components.md) -> one range.\n")
    sb.append('\n## Modules\n\n| Module | Purpose | Base package | Kotlin files | Layers |\n|---|---|---|---|---|\n')
    layer_sections = []
    other_dirs = [d for d in sorted(os.listdir(root), key=str.lower)
                  if os.path.isdir(os.path.join(root, d)) and d not in modules
                  and not re.match(r'^(\.|target|docs|scripts|node_modules)', d, re.I)]
    for m in modules:
        m_dir = os.path.join(root, m)
        desc = ''
        m_pom = os.path.join(m_dir, 'pom.xml')
        if os.path.isfile(m_pom):
            mx = ET.fromstring(read_text(m_pom))
            d = mx.find(f'{NS}description')
            if d is not None and d.text:
                desc = d.text.strip()
        src_main = os.path.join(m_dir, 'src/main')
        files = source_files(src_main, ['*.kt', '*.java']) if os.path.isdir(src_main) else []
        pkgs = {}
        for f in files:
            pm = re.search(r'(?m)^package\s+([\w.]+)', read_text(f))
            if pm:
                pkgs[f] = pm.group(1)
        base = min(pkgs.values(), key=len) if pkgs else ''
        by_layer = {}
        for f in files:
            p = pkgs.get(f)
            layer = '(root)'
            if p and base and len(p) > len(base):
                layer = p[len(base):].lstrip('.').split('.')[0]
            by_layer.setdefault(layer, []).append(os.path.splitext(os.path.basename(f))[0])
        layer_names = sorted(by_layer, key=sort_key)
        sb.append('| ' + code(m) + ' | ' + escape_cell(desc) + ' | ' + code(base) + ' | ' + str(len(files)) + ' | '
                  + ' '.join(code(x) for x in layer_names) + ' |\n')

        if len(layer_names) > 1:
            lay_rel = rel_path(root, src_main) + '/kotlin/' + base.replace('.', '/') + '/<layer>'
            layer_sections.append(f'## Layers of `{m}` (`{lay_rel}`)\n\n| Layer | Role | Files | Classes |\n|---|---|---|---|\n')
            for l in layer_names:
                names = sorted(by_layer[l], key=sort_key)
                shown = names if (l in LIST_ALL or len(names) <= 12) else names[:12] + ['(+' + str(len(names) - 12) + ')']
                role = ROLES.get(l, '')
                layer_sections.append('| ' + code(l) + ' | ' + role + ' | ' + str(len(names)) + ' | ' + code_list(shown) + ' |\n')
            layer_sections.append('\n')
        res = os.path.join(m_dir, 'src/main/resources')
        if os.path.isdir(res):
            res_rel = rel_path(root, res)
            layer_sections.append(f'## Resources of `{m}` (`{res_rel}`)\n\n| Folder | Files |\n|---|---|\n')
            for rd in sorted((d for d in os.listdir(res) if os.path.isdir(os.path.join(res, d))), key=str.lower):
                rd_full = os.path.join(res, rd)
                rf = [rel_path(rd_full, p) for p in source_files(rd_full, ['*'], exclude_dirs=())]
                shown = rf if len(rf) <= 10 else rf[:10] + ['(+' + str(len(rf) - 10) + ')']
                layer_sections.append('| ' + code(rd + '/') + ' | ' + code_list(shown) + ' |\n')
            top = sorted((f for f in os.listdir(res) if os.path.isfile(os.path.join(res, f))), key=str.lower)
            if top:
                layer_sections.append('| (root) | ' + code_list(top) + ' |\n')
            layer_sections.append('\n')
    sb.append('\n')
    if other_dirs:
        sb.append('Other top-level folders (not Maven modules): ' + code_list(d + '/' for d in other_dirs) + '\n\n')
    sb.extend(layer_sections)
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'codebase-map: {len(modules)} module(s) -> {a.out}')


if __name__ == '__main__':
    main()
