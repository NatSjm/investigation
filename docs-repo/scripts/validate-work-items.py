#!/usr/bin/env python3
"""Validates work-items/<ID>.yml against the rules documented in work-items/_schema.yml, without a YAML library:
feature matches file name and spec exists; every story has summary / estimate (Fibonacci) / acceptance criteria;
every cited BR exists in the spec; subtasks <= 8 h; jira_key present; no `depends_on` to unknown story ids.
Examples:
  python3 scripts/validate-work-items.py                       # all files
  python3 scripts/validate-work-items.py work-items/P1-001.yml"""
import argparse
import os
import re
import sys

from _common import repo_root, read_text, rel, walk_files, utf8_stdout


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*')
    a = ap.parse_args()
    repo = repo_root(__file__)
    paths = a.paths
    if not paths:
        wi = os.path.join(repo, 'work-items')
        paths = [rel(repo, os.path.join(wi, f)) for f in sorted(os.listdir(wi), key=str.lower)
                 if f.lower().endswith('.yml') and not f.startswith('_')]
    errors = []
    count = 0
    for p in paths:
        full = p if os.path.isabs(p) else os.path.join(repo, p)
        if not os.path.isfile(full):
            errors.append(f'{p} : not found')
            continue
        count += 1
        y = read_text(full)
        name = os.path.splitext(os.path.basename(full))[0]
        fm = re.search(r'(?m)^feature:\s*(\S+)', y, re.I)
        feature = fm.group(1) if fm else ''
        if feature.lower() != name.lower():
            errors.append(f"{p} : feature '{feature}' must equal file name '{name}'")
        spec = next((f for f in walk_files(os.path.join(repo, 'features'), '*.md') if os.path.basename(f).lower() == f'{feature}.md'.lower()), None)
        if spec:
            spec_text = read_text(spec)
        else:
            errors.append(f'{p} : spec features/**/{feature}.md not found')
            spec_text = ''
        if not re.search(r'(?m)^epic:', y, re.I):
            errors.append(f'{p} : missing epic')
        if not re.search(r'(?m)^\s+jira_key:', y, re.I):
            errors.append(f'{p} : missing jira_key (leave null)')
        # split stories by '  - id:' blocks
        story_blocks = re.split(r'(?m)^\s{2}-\s+id:', re.split(r'(?m)^stories:', y, flags=re.I)[-1])[1:]
        ids = [re.split(r'\r?\n', b)[0].strip() for b in story_blocks]
        if not ids:
            errors.append(f'{p} : no stories')
        for b in story_blocks:
            sid = re.split(r'\r?\n', b)[0].strip()
            block = re.split(r'(?m)^questions:', b, flags=re.I)[0]
            sm = re.search(r'(?m)^\s+summary:\s*"?(.+?)"?\s*$', block, re.I)
            if not sm:
                errors.append(f'{p} : story {sid} missing summary')
            elif len(sm.group(1)) > 80:
                errors.append(f'{p} : story {sid} summary > 80 chars')
            em = re.search(r'(?m)^\s{4}estimate:\s*(\d+)', block, re.I)
            if em:
                if int(em.group(1)) not in (1, 2, 3, 5, 8):
                    errors.append(f'{p} : story {sid} estimate must be 1,2,3,5,8')
            else:
                errors.append(f'{p} : story {sid} missing estimate')
            rules = re.findall(r'rule:\s*(BR-[A-Z0-9]+-\d{3}-\d+)', block)
            if not rules:
                errors.append(f'{p} : story {sid} has no acceptance criterion citing a BR')
            for r in rules:
                if spec_text and not re.search(re.escape(r), spec_text, re.I):
                    errors.append(f'{p} : story {sid} cites {r} which is not in the spec')
            for m in re.finditer(r'estimate_hours:\s*(\d+)', block):
                if int(m.group(1)) > 8:
                    errors.append(f'{p} : story {sid} subtask > 8 h')
            for m in re.finditer(r'depends_on:\s*\[([^\]]*)\]', block):
                for d in (x.strip() for x in m.group(1).split(',')):
                    if d and d.lower() not in (i.lower() for i in ids):
                        errors.append(f'{p} : story {sid} depends_on unknown {d}')
    if errors:
        for e in errors:
            print(f'ERROR {e}')
        sys.exit(1)
    print(f'OK: {count} work-item file(s) valid')


if __name__ == '__main__':
    main()
