#!/usr/bin/env python3
"""Regenerates OKF index.md files (progressive disclosure, §8) from concept frontmatter, and the footnote block at
the end of every concept whose body cites a `[^id]` footnote: one `[^id]: [title](resource)` line per cited
`sources[]` entry, under the marker `<!-- footnotes: generated from sources[] by scripts/build-index.py -->`.
The frontmatter is the only list a person or agent edits; the block is what GitHub renders and what the context pack
carries (the pack drops the frontmatter). `generated/**` is never touched (published by the code repositories' CI).
Root index.md keeps its okf_version frontmatter and a hand-written "Start here" block between markers.
Examples:
  python3 scripts/build-index.py            # rewrite all indexes and footnote blocks
  python3 scripts/build-index.py --check    # exit 1 if any index or footnote block is out of date (CI)"""
import argparse
import os
import re
import sys

from _common import (repo_root, read_text, write_text, rel, posix, get_fm, get_val, badge, now_utc, sort_key,
                     utf8_stdout)

RESERVED = ('index.md', 'log.md', 'agents.md')
DEFAULT_EXCLUDE = ['.github', 'scripts', 'ci-examples', 'third-party', 'node_modules', '.git', 'confluence-import',
                   'work-items', 'test-design', '.context']
FOOTNOTES_MARK = '<!-- footnotes: generated from sources[] by scripts/build-index.py -->'
# the block starts with the marker at the beginning of a line; the marker quoted inside a sentence (conventions) is prose
FOOTNOTES_BLOCK_RX = re.compile(r'(?ms)(?:\r?\n)*^' + re.escape(FOOTNOTES_MARK) + r'[ \t]*\r?$.*\Z')   # \r: CRLF files


def source_entries(fm):
    """`sources[]` entries as (id, resource, title) in frontmatter order; block entries (`- id:` with indented keys)
    and inline mappings (`- { id: x, resource: y }`) both read; an entry without id or resource is skipped."""
    m = re.search(r'(?m)^sources:[ \t]*\r?\n((?:[ \t]+[^\r\n]*\r?\n?|[ \t]*\r?\n)*)', fm)
    if not m:
        return []
    out = []
    cur = None

    def kv(line):
        k = re.match(r'\s*([A-Za-z_][\w\-]*):\s*(.*?)\s*$', line)
        if not k:
            return None, None
        v = re.sub(r'\s+#.*$', '', k.group(2)).strip()
        return k.group(1), v.strip('"').strip("'")

    for line in re.split(r'\r?\n', m.group(1)):
        if not line.strip():
            continue
        im = re.match(r'\s*-\s*\{(.*)\}\s*$', line)
        if im:
            e = {}
            for p in re.finditer(r'([A-Za-z_][\w\-]*):\s*("[^"]*"|\'[^\']*\'|[^,}]+)', im.group(1)):
                e[p.group(1)] = p.group(2).strip().strip('"').strip("'")
            out.append(e)
            cur = None
            continue
        bm = re.match(r'\s*-\s+(.*)$', line)
        if bm:
            cur = {}
            out.append(cur)
            k, v = kv(bm.group(1))
            if k:
                cur[k] = v
            continue
        if cur is not None:
            k, v = kv(line)
            if k:
                cur[k] = v
    return [(e.get('id', ''), e.get('resource', ''), e.get('title', '')) for e in out if e.get('id') and e.get('resource')]


def footnote_block(text):
    """The generated block for a concept ('' when its body cites no footnote): the cited `sources[]` entries in
    frontmatter order, each `[^id]: [label](resource)` (the title, or the file name of the resource); a resource that
    is neither a URL nor a bundle path (a code-repository-relative path) is shown as code, not linked."""
    fm = get_fm(text)
    body = FOOTNOTES_BLOCK_RX.sub('', re.sub(r'(?s)\A﻿?---\r?\n.*?\r?\n---\r?\n', '', text))
    body = re.sub(r'`[^`\r\n]*`', '', re.sub(r'(?s)```.*?```', '', body))   # a `[^id]` quoted in code is not a citation
    used = set(l.lower() for l in re.findall(r'\[\^([^\]\s]+)\](?!:)', body))
    lines = []
    for sid, res, title in source_entries(fm):
        if sid.lower() not in used:
            continue
        label = title or os.path.basename(res.rstrip('/')) or res
        if re.match(r'^(https?://|/)', res):
            lines.append(f'[^{sid}]: [{label}]({res})')
        else:
            lines.append(f'[^{sid}]: {label} - `{res}`')
    return '\n'.join([FOOTNOTES_MARK] + lines) if lines else ''


def with_footnote_block(text):
    """The concept text with its footnote block regenerated (or removed when nothing is cited)."""
    nl = '\r\n' if '\r\n' in text else '\n'
    block = footnote_block(text)
    if not block and FOOTNOTES_MARK not in text:
        return text   # nothing cited, no block to remove: the file is left exactly as it is
    base = FOOTNOTES_BLOCK_RX.sub('', text).rstrip()
    if not block:
        return base + nl
    return base + nl + nl + block.replace('\n', nl) + nl


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

    # footnote blocks: every concept under the walked folders except templates and generated/** (CI-published)
    blocks = []
    for d in dirs:
        if excluded(d) or rel(root, d) == 'generated' or rel(root, d).startswith('generated/'):
            continue
        for c in concept_files(d, False):
            if is_template(os.path.basename(c)):
                continue
            old = read_text(c)
            if not get_fm(old):
                continue
            new = with_footnote_block(old)
            if old.replace('\r', '') != new.replace('\r', ''):
                blocks.append(rel(root, c))
                if not a.check:
                    write_text(c, new)
    if a.check:
        if changed or blocks:
            for c in changed:
                print(f'OUT OF DATE {c}')
            for c in blocks:
                print(f'OUT OF DATE {c} (footnote block)')
            sys.exit(1)
        print('Indexes and footnote blocks up to date')
        return
    print(f'Indexes written: {len(changed)}')
    for c in changed:
        print(f'  {c}')
    print(f'Footnote blocks written: {len(blocks)}')
    for c in blocks:
        print(f'  {c}')


if __name__ == '__main__':
    main()
