#!/usr/bin/env python3
"""Move a processed legacy page into confluence-import/<SPACE>/_done/<section>/ and record where it went.

The last agent that takes a page (confluence-migrator, architect or calc-auditor) runs this instead of moving the
file by hand. Deterministic: the folder comes from the page's `section:` header (`_done/` itself when the page has
none, as with the REST export), the header gets `status`, `migrated` or `obsolete` with `reason`, and `superseded_by`
(every concept the page went into), and every relative link of the body is re-pointed so it still resolves from the
new place (`../_attachments/...` becomes `../../_attachments/...`; a link to a page already under `_done/` follows it
there). Links of pages already under `_done/` that pointed at this page are re-pointed too. No git command: commit the
rename with the run.

--into takes a repo path (`features/admin/ADM-001.md`, with or without the leading slash), a spec ID (`ADM-001`) or a
calculation name (`cover_ratio`); the concept file must exist. `migrated` needs at least one --into; `obsolete` needs
--reason and takes --into when part of the page was merged before it went obsolete.
Examples:
  python3 scripts/legacy-done.py confluence-import/HARBOR/business/admin-parameters-page.md --into ADM-001
  python3 scripts/legacy-done.py confluence-import/HARBOR/technical/kafka-topics.md --into architecture/integrations.md --into architecture/adr/0005-topic-naming.md
  python3 scripts/legacy-done.py confluence-import/HARBOR/business/old-export.md --status obsolete --reason "export module removed in 2024"
  python3 scripts/legacy-done.py <page> --into ADM-001 --dry-run"""
import argparse
import os
import re
import sys
from datetime import date

from _common import repo_root, read_text_or_empty, write_text, rel, posix, get_fm, get_val, walk_files, utf8_stdout

SPEC_ID = re.compile(r'^[A-Z][A-Z0-9]*-\d{3}$')
CALC_NAME = re.compile(r'^[a-z][a-z0-9_]*$')
# relative targets of markdown links / images and of HTML src / href (the `--body html` import form)
LINK = re.compile(r'(\]\(|\bsrc="|\bhref=")([^)"#\s]+)([^)"]*)([)"])')
HEADER_KEYS = ('status', 'migrated', 'obsolete', 'reason', 'superseded_by')


def resolve_concept(repo, spec):
    """--into value -> repo-relative posix path with a leading slash, or None when no such file exists."""
    s = spec.strip().lstrip('/')
    if SPEC_ID.match(s):
        hits = [f for f in walk_files(os.path.join(repo, 'features'), s + '.md')]
        return '/' + rel(repo, hits[0]) if hits else None
    if CALC_NAME.match(s) and not s.endswith('.md'):
        p = os.path.join(repo, 'domain', 'calculations', s + '.md')
        return '/' + rel(repo, p) if os.path.isfile(p) else None
    p = os.path.join(repo, s)
    return '/' + rel(repo, p) if os.path.isfile(p) else None


def is_relative(target):
    return not re.match(r'^[a-z][a-z0-9+.-]*:', target, re.I) and not target.startswith(('/', '#', '\\'))


def repoint_links(text, old_dir, new_dir, space_dir):
    """Rewrite every relative link so it resolves to the same file from new_dir; a target that is gone from its
    old place but exists at its _done/ mirror (a page moved earlier) is followed there. Returns (text, count)."""
    done_dir = os.path.join(space_dir, '_done')
    n = 0

    def fix(m):
        nonlocal n
        head, target, suffix, tail = m.groups()
        if not is_relative(target):
            return m.group(0)
        absolute = os.path.normpath(os.path.join(old_dir, target))
        if not os.path.exists(absolute):
            inside = os.path.relpath(absolute, space_dir)
            if not inside.startswith('..'):
                mirror = os.path.join(done_dir, inside)
                if os.path.exists(mirror):
                    absolute = mirror
        new_target = posix(os.path.relpath(absolute, new_dir))
        if new_target == target:
            return m.group(0)
        n += 1
        return f'{head}{new_target}{suffix}{tail}'

    return LINK.sub(fix, text), n


def update_header(text, status, today, into, reason):
    fm = get_fm(text)
    if not fm:
        raise SystemExit('the page has no frontmatter header (`---` block); import it first')
    lines = fm.split('\n')
    kept = []
    skip_list = False
    for ln in lines:
        key = re.match(r'^([A-Za-z_]+):', ln)
        if key:
            skip_list = key.group(1).lower() in HEADER_KEYS
            if skip_list:
                continue
        elif skip_list and re.match(r'^\s+-\s', ln):
            continue   # list items of a removed key
        else:
            skip_list = False
        kept.append(ln)
    kept.append(f'status: {status}')
    if status == 'migrated':
        kept.append(f'migrated: {today}')
    else:
        kept.append(f'obsolete: {today}')
        kept.append(f'reason: {reason}')
    if len(into) == 1:
        kept.append(f'superseded_by: {into[0]}')
    elif into:
        kept.append('superseded_by:')
        kept.extend(f'  - {p}' for p in into)
    new_fm = '\n'.join(kept)
    nl = '\r\n' if '\r\n' in text[:len(fm) + 10] else '\n'
    return re.sub(r'(?s)\A(﻿?---\r?\n).*?(\r?\n---)', lambda m: m.group(1) + new_fm.replace('\n', nl) + m.group(2), text, count=1)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('page', help='confluence-import/<SPACE>/[<section>/]<slug>.md')
    ap.add_argument('--into', action='append', default=[], help='concept the page went into (path, spec ID or calculation name); repeatable')
    ap.add_argument('--status', choices=('migrated', 'obsolete'), default='migrated')
    ap.add_argument('--reason', default='', help='one line why, for --status obsolete')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    repo = repo_root(__file__)

    page = os.path.abspath(a.page if os.path.isabs(a.page) else os.path.join(repo, a.page))
    page_rel = rel(repo, page)
    if not os.path.isfile(page):
        raise SystemExit(f'no such page: {page_rel}')
    parts = page_rel.split('/')
    if len(parts) < 3 or parts[0] != 'confluence-import' or parts[1] in ('raw-html',):
        raise SystemExit('the page must sit under confluence-import/<SPACE>/')
    if '_done' in parts:
        raise SystemExit(f'{page_rel} is already under _done/')
    space_dir = os.path.join(repo, 'confluence-import', parts[1])

    text = read_text_or_empty(page)
    fm = get_fm(text)
    section = get_val(fm, 'section')
    if section and not re.match(r'^[\w-]+$', section):
        raise SystemExit(f'section header is not a folder name: {section!r}')
    new_dir = os.path.join(space_dir, '_done', section) if section else os.path.join(space_dir, '_done')
    new_page = os.path.join(new_dir, os.path.basename(page))
    new_rel = rel(repo, new_page)
    if os.path.exists(new_page):
        raise SystemExit(f'{new_rel} already exists')

    into = []
    for spec in a.into:
        p = resolve_concept(repo, spec)
        if not p:
            raise SystemExit(f'--into {spec}: no such concept file (path under the repo, a spec ID or a calculation name)')
        if p not in into:
            into.append(p)
    if a.status == 'migrated' and not into:
        raise SystemExit('status migrated needs at least one --into <concept>')
    if a.status == 'obsolete' and not a.reason.strip():
        raise SystemExit('status obsolete needs --reason "<one line why>"')

    today = date.today().isoformat()
    new_text = update_header(text, a.status, today, into, a.reason.strip())
    new_text, n_links = repoint_links(new_text, os.path.dirname(page), new_dir, space_dir)

    # pages already under _done/ that link to this page at its old place
    repointed = []
    done_dir = os.path.join(space_dir, '_done')
    for f in walk_files(done_dir, '*.md') if os.path.isdir(done_dir) else []:
        t = read_text_or_empty(f)
        d = os.path.dirname(f)
        changed = False

        def fix(m):
            nonlocal changed
            head, target, suffix, tail = m.groups()
            if is_relative(target) and os.path.normpath(os.path.join(d, target)) == os.path.normpath(page):
                changed = True
                return f'{head}{posix(os.path.relpath(new_page, d))}{suffix}{tail}'
            return m.group(0)
        t2 = LINK.sub(fix, t)
        if changed:
            repointed.append((f, t2))

    row = f"| `{new_rel}` | {get_val(fm, 'last_modified') or '-'} | {a.status} {today}" + (' into ' + ', '.join(os.path.splitext(os.path.basename(p))[0] for p in into) if into else '') + (f' - {a.reason.strip()}' if a.reason.strip() else '') + ' |'
    verb = 'would move' if a.dry_run else 'moved'
    print(f'legacy-done: {verb} {page_rel} -> {new_rel}; status {a.status}; superseded_by: {", ".join(into) or "-"}; '
          f'{n_links} link(s) re-pointed in the page, {len(repointed)} page(s) under _done/ re-pointed to it')
    print('inventory row (Known state cell is yours to extend): ' + row)
    if a.dry_run:
        return
    for f, t2 in repointed:
        write_text(f, t2)
    write_text(new_page, new_text)
    os.remove(page)
    print(f'commit the rename with the run; the importer keeps {new_rel} by its confluence_id and never rewrites it')


if __name__ == '__main__':
    sys.exit(main())
