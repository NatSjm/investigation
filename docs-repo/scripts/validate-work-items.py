#!/usr/bin/env python3
"""Validates work-items/*.yml against the rules documented in work-items/_schema.yml, without a YAML library.
Feature epic (work-items/<ID>.yml): feature matches file name and spec exists. Request epic (work-items/<slug>.yml):
request matches file name (lowercase kebab-case), every specs[] entry exists, analysis: names an existing file.
Both: every story has summary / estimate (Fibonacci) / acceptance criteria; every cited BR exists in the spec its ID
names (which must be the feature, or one of specs[]); subtasks <= 8 h; jira_key present; no `depends_on` to unknown story ids.
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
    spec_files = walk_files(os.path.join(repo, 'features'), '*.md')

    def spec_file(sid):
        return next((f for f in spec_files if os.path.basename(f).lower() == f'{sid}.md'.lower()), None)

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
        spec_texts = {}   # spec ID (lower) -> text; the specs a rule may be cited from
        rm = re.search(r'(?m)^request:\s*(\S+)', y, re.I)
        if rm:
            # request epic: several specs, an analysis document beside the file
            request = rm.group(1).strip('"\'')
            if request != name:
                errors.append(f"{p} : request '{request}' must equal file name '{name}'")
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', request):
                errors.append(f"{p} : request '{request}' must be lowercase kebab-case (never a spec ID)")
            sm_ = re.search(r'(?m)^specs:\s*\[([^\]]*)\]', y, re.I)
            ids = [x.strip().strip('"\'') for x in sm_.group(1).split(',') if x.strip()] if sm_ else []
            if not ids:
                errors.append(f'{p} : request epic needs specs: [<ID>, ...] (every spec a story cites)')
            for sid in ids:
                sf = spec_file(sid)
                if sf:
                    spec_texts[sid.lower()] = read_text(sf)
                else:
                    errors.append(f'{p} : spec features/**/{sid}.md not found (specs[] entry)')
            am = re.search(r'(?m)^analysis:\s*(\S+)', y, re.I)
            if not am:
                errors.append(f'{p} : request epic needs analysis: work-items/{name}.md (template work-items/_analysis-template.md)')
            elif not os.path.isfile(os.path.join(repo, am.group(1).strip('"\''))):
                errors.append(f"{p} : analysis file {am.group(1)} not found")
            mode = 'request'
        else:
            fm = re.search(r'(?m)^feature:\s*(\S+)', y, re.I)
            feature = fm.group(1) if fm else ''
            if feature.lower() != name.lower():
                errors.append(f"{p} : feature '{feature}' must equal file name '{name}'")
            spec = spec_file(feature)
            if spec:
                spec_texts[feature.lower()] = read_text(spec)
            else:
                errors.append(f'{p} : spec features/**/{feature}.md not found')
            mode = 'feature'
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
                owner = re.match(r'BR-([A-Z0-9]+-\d{3})-\d+', r).group(1).lower()
                text = spec_texts.get(owner)
                if mode == 'request' and text is None:
                    errors.append(f'{p} : story {sid} cites {r} but {owner.upper()} is not in specs[]')
                elif spec_texts and (text is None or not re.search(re.escape(r), text, re.I)):
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
