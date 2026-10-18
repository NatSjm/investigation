#!/usr/bin/env python3
"""Codebase map for a Maven/Kotlin backend organised by technical layer (package-by-layer):
modules (root pom or `modules` of docs-gen.json) -> layers (package segments after the base package) -> classes,
plus resource folders. One line per module and per layer; details per class are in components.md.
Layout keys read from docs-gen.json: modules, source_root, resources_root, base_package, layers (name -> role;
a key with a slash such as `dao/model` makes that sub-package a layer of its own), list_all_layers, entry_layer.
Example: python3 scripts/docs/gen-codebase-map.py --root . --out docs/_generated/codebase-map.md"""
import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files, resolve_out, rel_path, header, escape_cell, sort_key,
                     utf8_stdout, load_config, module_dirs, main_sources, package_of, base_package, layer_of)

NS = '{http://maven.apache.org/POM/4.0.0}'
DEFAULTS = {
    'modules': [], 'source_root': 'src/main/kotlin', 'resources_root': 'src/main/resources', 'base_package': '',
    'layers': {}, 'list_all_layers': ['api', 'manager', 'job', 'event', 'client', 'utils', 'validator', 'component', 'service'],
    'entry_layer': 'manager', 'test_pattern': '', 'exclude_paths': [],
}


def code(s):
    return s if s.startswith('(+') else '`' + s + '`'


def code_list(items):
    return ', '.join(code(str(x)) for x in items)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/codebase-map.md')
    ap.add_argument('--config', default='', help='docs-gen.json (default: scripts/docs/docs-gen.json of the repo)')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    modules = module_dirs(root, cfg)
    layers_cfg = cfg['layers']
    entry = cfg['entry_layer']

    sb = [header('Codebase map (BE)', 'pom.xml modules + package-by-layer scan',
                 f'Backend modules, technical layers with their classes and resource folders; read the {entry} of a context first.')]
    sb.append('Layered backend: the business context of a class is its **name prefix** (`Product1*`, `Stress*` ...), not its folder.\n')
    sb.append(f"Read order: the context's `{entry}/*` class (KDoc + `@docs`) -> the classes it depends on (components.md) -> one range.\n")
    sb.append('\n## Modules\n\n| Module | Purpose | Base package | Kotlin files | Layers |\n|---|---|---|---|---|\n')
    layer_sections = []
    other_dirs = [d for d in sorted(os.listdir(root), key=str.lower)
                  if os.path.isdir(os.path.join(root, d)) and d not in modules
                  and not re.match(r'^(\.|target|build|docs|scripts|node_modules)', d, re.I)
                  and not set(os.listdir(os.path.join(root, d))) <= {'target', 'build'}]   # leftover build output only
    for m in modules:
        m_dir = os.path.join(root, m)
        desc = ''
        m_pom = os.path.join(m_dir, 'pom.xml')
        if os.path.isfile(m_pom):
            mx = ET.fromstring(read_text(m_pom))
            d = mx.find(f'{NS}description')
            if d is not None and d.text:
                desc = ' '.join(d.text.split())
        files = main_sources(root, cfg, [m])
        pkgs = {f: package_of(read_text(f)) for f in files}
        base = base_package(cfg, pkgs.values())
        by_layer = {}
        for f in files:
            layer = layer_of(pkgs.get(f, ''), base, layers_cfg)
            by_layer.setdefault(layer, []).append(os.path.splitext(os.path.basename(f))[0])
        layer_names = sorted(by_layer, key=sort_key)
        sb.append('| ' + code(m) + ' | ' + escape_cell(desc) + ' | ' + code(base) + ' | ' + str(len(files)) + ' | '
                  + ' '.join(code(x) for x in layer_names) + ' |\n')

        if len(layer_names) > 1:
            src_rel = (m + '/' if m != '.' else '') + cfg['source_root'] + '/' + base.replace('.', '/') + '/<layer>'
            layer_sections.append(f'## Layers of `{m}` (`{src_rel}`)\n\n| Layer | Role | Files | Classes |\n|---|---|---|---|\n')
            for l in layer_names:
                names = sorted(by_layer[l], key=sort_key)
                shown = names if (l in cfg['list_all_layers'] or len(names) <= 12) else names[:12] + ['(+' + str(len(names) - 12) + ')']
                role = layers_cfg.get(l, '')
                layer_sections.append('| ' + code(l) + ' | ' + role + ' | ' + str(len(names)) + ' | ' + code_list(shown) + ' |\n')
            layer_sections.append('\n')
        res = os.path.join(m_dir, cfg['resources_root'])
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
        sb.append('Other top-level folders (not build modules): ' + code_list(d + '/' for d in other_dirs) + '\n\n')
    sb.extend(layer_sections)
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'codebase-map: {len(modules)} module(s) -> {a.out}')


if __name__ == '__main__':
    main()
