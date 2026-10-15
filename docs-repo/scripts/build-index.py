#!/usr/bin/env python3
"""Regenerates OKF index.md files (progressive disclosure, §8) from concept frontmatter.
Root index.md keeps its okf_version frontmatter and a hand-written "Start here" block between markers.
Examples:
  python3 scripts/build-index.py            # rewrite all indexes
  python3 scripts/build-index.py --check    # exit 1 if any index is out of date (CI)"""
import argparse
import os
import re
import sys

from _common import (repo_root, read_text, write_text, rel, posix, get_fm, get_val, badge, now_utc, sort_key,
                     utf8_stdout)

RESERVED = ('index.md', 'log.md', 'agents.md')
DEFAULT_EXCLUDE = ['.github', 'scripts', 'ci-examples', 'third-party', 'node_modules', '.git', 'confluence-import',
                   'work-items', 'test-design', '.context']


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--path', default=repo_root(__file__))
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--exclude', nargs='*', default=DEFAULT_EXCLUDE)
    a = ap.parse_args()
    root = os.path.abspath(a.path)
    now = now_utc()
    exclude = [posix(e).strip('/') for e in a.exclude]

    def excluded(d):
        r = rel(root, d)
        return any(r == e or r.startswith(e + '/') for e in exclude)

    def is_template(name):
        return re.match(r'^_?template', name, re.I) is not None

    def concept_files(d, recursive):
        """*.md files that are concepts (not reserved files); the exclude list is not applied here (as before)."""
        out = []
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames.sort(key=str.lower)
            for n in sorted(filenames, key=str.lower):
                if n.lower().endswith('.md') and n.lower() not in RESERVED:
                    out.append(os.path.join(dirpath, n))
            if not recursive:
                break
        return out

    def subdirs(d):
        return sorted((os.path.join(d, x) for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))), key=lambda p: sort_key(os.path.basename(p)))

    def build_dir(d):
        r = rel(root, d) if d != root else ''
        lines = ['# ' + (os.path.basename(r) if r else 'Bundle root'), '']
        subs = [s for s in subdirs(d) if not excluded(s) and concept_files(s, True)]
        concepts = [c for c in concept_files(d, False) if not is_template(os.path.basename(c))]
        concepts.sort(key=lambda p: sort_key(os.path.basename(p)))
        if subs:
            lines.append('# Sections')
            for s in subs:
                n = sum(1 for c in concept_files(s, True) if not is_template(os.path.basename(c)))
                name = os.path.basename(s)
                lines.append(f'* [{name}]({name}/) - {n} concept(s)')
            lines.append('')
        if concepts:
            lines.append('# Concepts')
            for c in concepts:
                fm = get_fm(read_text(c))
                t = get_val(fm, 'title', strip_comment=False) or os.path.splitext(os.path.basename(c))[0]
                desc = get_val(fm, 'description', strip_comment=False)
                lines.append(f'* [{t}]({os.path.basename(c)}) - {desc} · {badge(fm, now, strict_dates=True)}')
            lines.append('')
        return lines

    dirs = [root]
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = sorted((x for x in dirnames if not excluded(os.path.join(dirpath, x))), key=str.lower)
        dirs.extend(os.path.join(dirpath, x) for x in dirnames)

    changed = []
    for d in dirs:
        if not concept_files(d, True):
            continue
        body = build_dir(d)
        index_path = os.path.join(d, 'index.md')
        head = ''
        if d == root:
            existing = read_text(index_path) if os.path.isfile(index_path) else ''
            fmm = re.match(r'(?s)\A(---\r?\n.*?\r?\n---\r?\n)', existing)
            fm = fmm.group(1) if fmm else '---\nokf_version: "0.2"\n---\n'
            mm = re.search(r'(?s)(<!-- manual:start -->.*?<!-- manual:end -->)', existing)
            # bundle heading: the first `# ...` line after the manual block is kept as written (edit it once per
            # product, like the manual block); the root index frontmatter may carry nothing but okf_version (OKF §8)
            tail = existing[mm.end():] if mm else existing
            tm = re.search(r'(?m)^# (?!Sections$|Concepts$|Bundle root$)(.+?)\s*$', tail)
            bundle_title = tm.group(1) if tm else 'Documentation bundle'
            manual = mm.group(1) if mm else ('<!-- manual:start -->\n# Start here\n* [Glossary](domain/glossary.md) - canonical terms\n'
                                              '* [Codebase map](generated/codebase-map.md) - module → responsibility → entry files\n<!-- manual:end -->')
            head = fm + '\n' + manual + '\n\n'
            body = [l for l in body if l != '# Bundle root']
            body = [f'# {bundle_title}', ''] + body
        new = head + '\n'.join(body).rstrip() + '\n<!-- generated by scripts/build-index.py -->\n'
        old = read_text(index_path) if os.path.isfile(index_path) else ''
        if old.replace('\r', '') != new.replace('\r', ''):
            changed.append(rel(root, index_path))
            if not a.check:
                write_text(index_path, new)
    if a.check:
        if changed:
            for c in changed:
                print(f'OUT OF DATE {c}')
            sys.exit(1)
        print('Indexes up to date')
        return
    print(f'Indexes written: {len(changed)}')
    for c in changed:
        print(f'  {c}')


if __name__ == '__main__':
    main()
