#!/usr/bin/env python3
"""Validates frontmatter of feature specs and calculation docs.
Examples:
  python3 scripts/validate-frontmatter.py                                # all specs
  python3 scripts/validate-frontmatter.py features/product1/P1-001.md"""
import argparse
import os
import re
import sys

from _common import repo_root, read_text, rel, walk_files, utf8_stdout

REQUIRED_FEATURE = ['id', 'title', 'context', 'status', 'owners', 'last_verified', 'code_refs', 'api', 'events', 'tables',
                    'calculations', 'flows', 'jira', 'tests']
REQUIRED_CALC = ['name', 'title', 'used_by', 'code_refs', 'last_verified']
SPEC_NAME = re.compile(r'^[A-Z][A-Z0-9]+-\d{3}\.md$', re.I)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*')
    a = ap.parse_args()
    repo = repo_root(__file__)
    paths = a.paths
    if not paths:
        paths = [rel(repo, f) for d in ('features', 'domain/calculations') for f in walk_files(os.path.join(repo, d), '*.md')
                 if not re.match(r'^(_template|README|INDEX)\.md$', os.path.basename(f), re.I)]
    errors = []

    for p in paths:
        full = p if os.path.isabs(p) else os.path.join(repo, p)
        text = read_text(full)
        m = re.match(r'(?s)^﻿?---\r?\n(.*?)\r?\n---', text)
        if not m:
            errors.append(f'{p} : missing frontmatter')
            continue
        fm = m.group(1)
        keys = [k.lower() for k in re.findall(r'(?m)^([A-Za-z_]+):', fm)]

        # Only the two repo-specific OKF types carry the extended schema; other concepts (Document,
        # Architecture View, ...) and reserved files (index.md/log.md) are covered by okf-validate.py.
        tm = re.search(r'(?m)^type:\s*"?([^"\r\n#]+?)"?\s*(#.*)?$', fm, re.I)
        typ = tm.group(1).strip() if tm else ''
        if typ.lower() not in ('feature spec', 'attested computation'):
            continue

        is_calc = typ.lower() == 'attested computation'
        required = REQUIRED_CALC if is_calc else REQUIRED_FEATURE
        for k in required:
            if k not in keys:
                errors.append(f"{p} : missing key '{k}'")

        if not is_calc:
            im = re.search(r'id:\s*([A-Z][A-Z0-9]*-\d{3}[a-z]?)', fm, re.I)
            if im:
                fid = im.group(1)
                if os.path.basename(full).lower() != f'{fid}.md'.lower():
                    errors.append(f'{p} : filename must be {fid}.md')
                if not re.search(re.escape(f'BR-{fid}-1'), text, re.I):
                    errors.append(f'{p} : no business rule BR-{fid}-1 found')
            else:
                errors.append(f'{p} : id must match ^[A-Z][A-Z0-9]*-\\d{{3}}$')
            sm = re.search(r'(?m)^status:\s*(\w+)', fm, re.I)
            if sm and sm.group(1).lower() not in ('draft', 'stable', 'deprecated'):
                errors.append(f'{p} : bad status (OKF §5.4: draft|stable|deprecated)')

        # referenced calculation and flow files must exist
        for ref in re.findall(r'domain/calculations/[\w\-]+\.md', fm) + re.findall(r'flows/[\w\-]+\.md', fm):
            if not os.path.isfile(os.path.join(repo, ref)):
                errors.append(f'{p} : missing {ref}')

    # flows: every spec a flow names in `specs:` must exist (the other direction of the spec's `flows:` key)
    spec_ids = [os.path.splitext(os.path.basename(f))[0] for f in walk_files(os.path.join(repo, 'features'), '*.md')
                if SPEC_NAME.match(os.path.basename(f))]
    spec_ids_ci = set(s.lower() for s in spec_ids)
    flow_dir = os.path.join(repo, 'flows')
    if os.path.isdir(flow_dir):
        for ff in sorted(os.listdir(flow_dir), key=str.lower):
            if not ff.lower().endswith('.md') or re.match(r'^(_template|index)\.md$', ff, re.I):
                continue
            ft = read_text(os.path.join(flow_dir, ff))
            sm = re.search(r'(?m)^specs:\s*\[(.*?)\]', ft, re.I)
            if sm:
                for sid in (s.strip().strip('"') for s in sm.group(1).split(',')):
                    if sid and sid.lower() not in spec_ids_ci:
                        errors.append(f'flows/{ff} : specs[] names {sid}, no features/*/{sid}.md')
            else:
                errors.append(f'flows/{ff} : no specs[] list (a flow must name the specs it composes)')

    # parameter_set keys: a calculation's `## Parameters` section and a feature spec's `## Parameters` section may name only
    # keys that exist in the generated catalogue, and every catalogue key must be named by a calculation or a feature spec
    # outside the admin context (the admin spec maps keys to owners; it is not itself the owner of a meaning)
    catalogue = os.path.join(repo, 'generated/be/parameters.md')
    if os.path.isfile(catalogue):
        ct = read_text(catalogue)
        known = re.findall(r'(?m)^\| `(?P<k>[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+)` \|', ct)
        key_rx = re.compile(r'`(?P<k>[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+)`')
        explained = set()
        calc_dir = os.path.normpath(os.path.join(repo, 'domain/calculations'))
        docs = [f for f in walk_files(calc_dir, '*.md')
                if os.path.normpath(os.path.dirname(f)) == calc_dir and not re.match(r'^(_template|index)\.md$', os.path.basename(f), re.I)]
        docs += [f for f in walk_files(os.path.join(repo, 'features'), '*.md') if SPEC_NAME.match(os.path.basename(f))]
        for d in docs:
            dt = read_text(d)
            r = rel(repo, d)
            is_admin = re.search(r'(?m)^context:\s*admin\s*$', dt, re.I) is not None
            sm = re.search(r'(?ms)^## Parameters\s*\r?\n(.*?)(?=^## |\Z)', dt, re.I)
            section = sm.group(1) if sm else ''
            # only the first cell of the Parameters table is checked for unknown keys (prose and other cells also use `table.column` tokens)
            for line in re.split(r'\r?\n', section):
                if not line.startswith('|') or re.match(r'^\|\s*(Key\b|-)', line, re.I):
                    continue
                first_cell = line.lstrip('|').split('|')[0]
                for m in key_rx.finditer(first_cell):
                    k = m.group('k')
                    if k not in known:
                        errors.append(f'{r} : parameter `{k}` is not in generated/be/parameters.md (unknown key or stale catalogue)')
            if not is_admin:
                for m in key_rx.finditer(dt):
                    explained.add(m.group('k'))
        for k in known:
            if k not in explained:
                errors.append(f'generated/be/parameters.md : `{k}` is named by no calculation or feature spec - document its meaning (calculation `## Parameters` or a business rule)')
    else:
        print('note: generated/be/parameters.md not found - parameter cross-check skipped (run the collector)')

    if errors:
        for e in errors:
            print(f'ERROR {e}')
        sys.exit(1)
    print(f'OK: {len(paths)} file(s) valid')


if __name__ == '__main__':
    main()
