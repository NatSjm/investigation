#!/usr/bin/env python3
"""Runs all FE generators and writes docs/_generated/index.md. --check: exit 1 if any output is stale (CI gate).
The generators read the repository layout from scripts/docs/docs-gen.json (pages dir, shared components, routing, ...)."""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import read_text, write_text, utf8_stdout

GENERATORS = [
    ('gen-codebase-map.py', 'codebase-map.md', []),
    ('gen-components.py', 'components.md', []),
    ('gen-routes.py', 'routes.md', []),
    ('gen-types-index.py', 'types-index.md', []),
    ('gen-docs-tags.py', 'docs-tags.md', ['--include', '*.ts', '*.tsx']),
]

INDEX = """# Generated code maps

Read these before opening source. Each file is a few hundred tokens.

- [codebase-map.md](codebase-map.md): pages, purpose, components and hooks, API calls, browser channels
- [components.md](components.md): shared component library: props, purpose, used by which pages
- [routes.md](routes.md): URL -> page component (nested routes joined, route constants resolved)
- [types-index.md](types-index.md): exported types/interfaces (DTO mirrors)
- [docs-tags.md](docs-tags.md): spec ID (`@docs`) to code location

The folder layout the generators assume is in `scripts/docs/docs-gen.json`.
"""


def norm(s):
    return re.sub(r'(?m)^  at: .*$', '', s).replace('\r', '')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out-dir', default='docs/_generated')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(root, a.out_dir)
    # --check: the generators write a throwaway copy into a folder this run creates in the system temp directory
    # (tempfile.mkdtemp); the finally block removes that folder, and nothing else, on every exit path (a failed
    # generator, stale output); nothing under the repository is written or deleted by --check
    tmp_dirs = []
    try:
        work = tempfile.mkdtemp(prefix='gen-docs-') if a.check else target
        if a.check:
            tmp_dirs.append(work)
        os.makedirs(work, exist_ok=True)
        rel = work if a.check else a.out_dir
        for script, out, extra in GENERATORS:
            # -B: the child interpreter writes no __pycache__ next to the scripts either
            r = subprocess.run([sys.executable, '-B', os.path.join(here, script),
                                '--root', root, '--out', rel + '/' + out] + extra)
            if r.returncode:
                sys.exit(r.returncode)
        write_text(os.path.join(work, 'index.md'), INDEX)
        if a.check:
            diff = 0
            for name in sorted(os.listdir(work), key=str.lower):
                cur = os.path.join(target, name)
                a_text = norm(read_text(cur)) if os.path.isfile(cur) else ''
                b_text = norm(read_text(os.path.join(work, name)))
                if a_text != b_text:
                    print(f'STALE: {a.out_dir}/{name}')
                    diff += 1
            if diff:
                print(f'{diff} generated file(s) out of date. Run scripts/docs/gen-all.py', file=sys.stderr)
                sys.exit(1)
            print('generated docs up to date')
    finally:
        for d in tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    main()
