#!/usr/bin/env python3
"""Copies the code-repo-kit files for one flavour into a code repository (harbor-backend or harbor-frontend).

Copied (relative to the kit):
  <flavour>/.github/**          -> <target>/.github/**           (copilot-instructions, instructions, agents, prompts, hooks, workflows)
  <flavour>/AGENTS.md           -> <target>/AGENTS.md
  <flavour>/scripts/docs/**     -> <target>/scripts/docs/**      (generators, gen-all.py, FE graph exporter)
  shared/check-file-size.py     -> <target>/scripts/check-file-size.py
  ci/docs-maps.yml              -> <target>/.github/workflows/docs-maps.yml
Existing files are overwritten (the kit is the source of truth). --what-if lists the plan without copying.
--pilot leaves out what the pilot does not need yet: .github/hooks/**, .github/workflows/** and docs-maps.yml.
--replace OLD=NEW (repeatable) rewrites the Harbor names in the copied text files (.md, .yml, .yaml, .json, .kt;
never the .py / .ts scripts, which read docs-gen.json); longest OLD first. After copying, the script lists the
copied text files that still mention harbor / acme, so the remaining Harbor wording is visible at once.
Examples:
  python3 apply-kit.py --flavour be --target ../backend --what-if
  python3 apply-kit.py --flavour fe --target ../frontend
  python3 apply-kit.py --flavour be --target ../backend --pilot --replace harbor-core=app-core --replace com/acme/harbor=com/example/app \\
      --replace com.acme.harbor=com.example.app --replace openapi_harbor.yaml=openapi_app.yaml --replace harbor-backend=app-backend \\
      --replace harbor-frontend=app-frontend --replace harbor-docs=app-docs --replace Harbor=App --replace harbor=app"""
import argparse
import os
import re
import shutil
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = re.compile(r'[\\/](node_modules|out)[\\/]')
PILOT_SKIP = re.compile(r'[\\/]\.github[\\/](hooks|workflows)[\\/]')
TEXT_EXT = ('.md', '.yml', '.yaml', '.json', '.kt')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--flavour', required=True, choices=['be', 'fe'])
    ap.add_argument('--target', required=True)
    ap.add_argument('--what-if', action='store_true')
    ap.add_argument('--pilot', action='store_true', help='skip .github/hooks, .github/workflows and docs-maps.yml')
    ap.add_argument('--replace', action='append', default=[], metavar='OLD=NEW',
                    help='rewrite OLD to NEW in the copied text files (.md .yml .yaml .json .kt); repeatable')
    a = ap.parse_args()
    replacements = []
    for r in a.replace:
        if '=' not in r:
            raise SystemExit(f'--replace expects OLD=NEW, got {r!r}')
        old, new = r.split('=', 1)
        replacements.append((old, new))
    replacements.sort(key=lambda x: -len(x[0]))   # longest first: harbor-core before harbor
    if not os.path.isdir(a.target):
        raise SystemExit(f"Target '{a.target}' does not exist (expected the root of the harbor-{'backend' if a.flavour == 'be' else 'frontend'} checkout).")
    target = os.path.abspath(a.target)

    plan = []

    def add_tree(src_dir, dst_dir):
        if not os.path.isdir(src_dir):
            return
        for dirpath, dirnames, filenames in os.walk(src_dir):
            dirnames.sort(key=str.lower)
            for name in sorted(filenames, key=str.lower):
                full = os.path.join(dirpath, name)
                if SKIP_DIRS.search(full + os.sep):
                    continue
                if a.pilot and PILOT_SKIP.search(full):
                    continue
                rel = os.path.relpath(full, src_dir)
                plan.append((full, os.path.join(dst_dir, rel)))

    def add_file(src, dst):
        if not os.path.isfile(src):
            raise SystemExit(f'Kit file missing: {src}')
        plan.append((os.path.abspath(src), dst))

    add_tree(os.path.join(KIT, a.flavour, '.github'), os.path.join(target, '.github'))
    add_file(os.path.join(KIT, a.flavour, 'AGENTS.md'), os.path.join(target, 'AGENTS.md'))
    add_tree(os.path.join(KIT, a.flavour, 'scripts', 'docs'), os.path.join(target, 'scripts', 'docs'))
    add_file(os.path.join(KIT, 'shared', 'check-file-size.py'), os.path.join(target, 'scripts', 'check-file-size.py'))
    if not a.pilot:
        add_file(os.path.join(KIT, 'ci', 'docs-maps.yml'), os.path.join(target, '.github', 'workflows', 'docs-maps.yml'))

    copied = 0
    leftovers = []   # copied text files that still mention Harbor (wording to adapt by hand)
    for src, dst in plan:
        rel_dest = os.path.relpath(dst, target).replace('\\', '/')
        if a.what_if:
            print(f'What if: copy from kit ({a.flavour}) -> {rel_dest}')
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if replacements and dst.lower().endswith(TEXT_EXT):
            with open(src, 'rb') as fh:
                text = fh.read().decode('utf-8')
            for old, new in replacements:
                text = text.replace(old, new)
            with open(dst, 'wb') as fh:
                fh.write(text.encode('utf-8'))
        else:
            shutil.copyfile(src, dst)
        shutil.copymode(src, dst)
        print(f'  copied  {rel_dest}')
        copied += 1
        if dst.lower().endswith(TEXT_EXT):
            with open(dst, 'rb') as fh:
                left = len(re.findall(r'(?i)harbor|acme', fh.read().decode('utf-8', 'replace')))
            if left:
                leftovers.append((rel_dest, left))
    if not a.what_if:
        print(f'apply-kit ({a.flavour}): {copied} file(s) -> {target}')
        if leftovers:
            print('Harbor wording left to adapt by hand (file: mentions of harbor / acme):')
            for rel_dest, n in leftovers:
                print(f'  {rel_dest}: {n}')
        print(f"Next: python3 scripts/docs/gen-all.py  |  python3 scripts/check-file-size.py --root . --max-lines {400 if a.flavour == 'be' else 300} --baseline .filesize-baseline.txt --write-baseline")
        print(f'Then set the repo variable REPO_KIND={a.flavour} (docs-maps.yml) and configure content exclusion from shared/copilot-content-exclusion.yml.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
