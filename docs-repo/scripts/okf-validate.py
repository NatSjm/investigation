#!/usr/bin/env python3
"""Standard-library port of the OKF v0.2 conformance checker core (okf_validate.py, MIT, scaccogatto/okf-skills).
Runs without pyyaml. ERRORs = §11 hard failures; warnings = soft guidance; stale = past stale_after (§5.5), listed
but never counted as a warning: freshness, not conformance (the reference checker does not report it either).
--path and --changed only choose which files can fail: the whole bundle is always read, links resolve from its root
(the folder whose index.md carries okf_version) and the problems of the other files are summed up on one line.
Examples:
  python3 scripts/okf-validate.py                          # whole repo bundle
  python3 scripts/okf-validate.py --changed --strict       # the concept files changed since HEAD, untracked included
  python3 scripts/okf-validate.py --changed origin/main    # ... since a base (a branch that already has commits)
  python3 scripts/okf-validate.py --path features --strict # a folder or a single file
  python3 scripts/okf-validate.py --max-warnings 5"""
import argparse
import os
import re
import subprocess
import sys

from _common import repo_root, rel, posix, now_utc, parse_iso_utc, walk_files, utf8_stdout

# AGENTS.md is an agent-instruction file (cross-tool convention), not a knowledge concept; .context holds throwaway packs
DEFAULT_EXCLUDE = ['.github', 'scripts', 'ci-examples', 'third-party', 'node_modules', '.git', 'confluence-import',
                   'work-items', 'test-design', 'AGENTS.md', '.context']
ACTOR_RX = re.compile(r'^(human:[^\s/]+|process:[^\s/]+|[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)$', re.I)
ISO_RX = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(Z|[+\-]\d{2}:\d{2}))?$', re.I)
LEVELS = ('ERROR', 'warn', 'stale')


def frontmatter(text):
    m = re.match(r'(?s)\A﻿?---\r?\n(.*?)\r?\n---(\r?\n|\Z)', text)
    return m.group(1) if m else None


def top_keys(fm):
    return re.findall(r'(?m)^([A-Za-z_][\w\-]*):', fm)


def scalar(fm, key):
    m = re.search(r'(?m)^' + re.escape(key) + r':\s*(.+?)\s*$', fm, re.I)
    if not m:
        return None
    v = re.sub(r'\s+#.*$', '', m.group(1))   # drop inline YAML comment
    return v.strip().strip('"').strip("'")


def is_template(r):
    return re.search(r'(^|/)_?template\.md$', r, re.I) is not None


def bundle_root(path):
    """The nearest folder at or above path whose index.md carries okf_version (the bundle's root index), so a folder
    or a file inside the bundle is checked against the whole bundle; path's own folder when there is none."""
    start = path if os.path.isdir(path) else os.path.dirname(path)
    d = start
    while True:
        index = os.path.join(d, 'index.md')
        if os.path.isfile(index):
            with open(index, 'r', encoding='utf-8-sig', errors='replace') as fh:
                fm = frontmatter(fh.read())
            if fm and scalar(fm, 'okf_version'):
                return d
        parent = os.path.dirname(d)
        if parent == d:
            return start
        d = parent


def changed_paths(root, base):
    """(changed, removed): bundle-relative paths that differ between base and the working tree, untracked files
    included, and the paths deleted or renamed away (links to them break in files nobody touched).
    (None, None) when git cannot answer (no repository, unknown base)."""
    def git(*args):
        try:
            r = subprocess.run(['git', '-C', root] + list(args), capture_output=True, text=True, encoding='utf-8',
                               errors='replace')
        except OSError:
            return None
        return r.stdout if r.returncode == 0 else None

    diff = git('diff', '--name-status', '-z', '-M', '--relative', base, '--')
    untracked = git('ls-files', '--others', '--exclude-standard', '-z')
    if diff is None or untracked is None:
        return None, None
    changed, removed = set(), set()
    fields = diff.split('\0')
    i = 0
    while i + 1 < len(fields) and fields[i]:
        status = fields[i][0]
        if status in 'RC':                   # R<score> old new, C<score> old new
            if status == 'R':
                removed.add(posix(fields[i + 1]))
            changed.add(posix(fields[i + 2]))
            i += 3
        else:
            (removed if status == 'D' else changed).add(posix(fields[i + 1]))
            i += 2
    changed.update(posix(p) for p in untracked.split('\0') if p)
    return changed, removed


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--path', default=repo_root(__file__), help='folder or file to check (default: the whole bundle)')
    ap.add_argument('--changed', nargs='?', const='HEAD', metavar='BASE',
                    help='check only the concept files changed since BASE (default HEAD), untracked ones included')
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--max-warnings', type=int, default=-1)
    ap.add_argument('--exclude', nargs='*', default=DEFAULT_EXCLUDE)
    a = ap.parse_args()
    target = os.path.abspath(a.path)
    root = bundle_root(target)
    findings = []   # (level, file, message, target of a broken link or None)
    now = now_utc()

    files = walk_files(root, '*.md', exclude_rel=a.exclude)
    concept_ids = set(rel(root, f) for f in files)

    for f in files:
        r = rel(root, f)
        try:
            with open(f, 'r', encoding='utf-8-sig', errors='strict', newline='') as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            findings.append(('ERROR', r, 'not readable as UTF-8', None))
            continue
        fm = frontmatter(text)
        name = os.path.basename(f).lower()
        is_reserved = name in ('index.md', 'log.md')
        is_root_index = r.lower() == 'index.md'

        if is_reserved:
            if fm:
                keys = top_keys(fm)
                if is_root_index:
                    extra = [k for k in keys if k.lower() != 'okf_version']
                    if extra:
                        findings.append(('warn', r, f"root index carries unexpected keys: {', '.join(extra)} (§8/§12)", None))
                    v = scalar(fm, 'okf_version')
                    if v and v != '0.2':
                        findings.append(('warn', r, f"okf_version '{v}' differs from 0.2 (§12)", None))
                else:
                    findings.append(('warn', r, 'reserved file must not carry frontmatter (§8/§9)', None))
            if name == 'log.md':
                for m in re.finditer(r'(?m)^## (.+)$', text):
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', m.group(1).strip()):
                        findings.append(('warn', r, f"log heading '{m.group(1)}' is not ISO YYYY-MM-DD (§9)", None))
            continue

        if not fm:
            findings.append(('ERROR', r, 'no YAML frontmatter (§11)', None))
            continue
        typ = scalar(fm, 'type')
        if not typ:
            findings.append(('ERROR', r, "missing or empty 'type' (§11)", None))
            continue

        # Templates hold placeholders (<ISO>, [^id]); §11 checks apply, value-level warnings do not.
        if is_template(r):
            continue

        for k in ('title', 'description'):
            if not scalar(fm, k):
                findings.append(('warn', r, f"missing recommended '{k}'", None))

        status = scalar(fm, 'status')
        if status and status.lower() not in ('draft', 'stable', 'deprecated'):
            findings.append(('warn', r, f"status '{status}' not in draft|stable|deprecated (§5.4)", None))

        stale = scalar(fm, 'stale_after')
        if stale:
            if not ISO_RX.match(stale):
                findings.append(('warn', r, f"stale_after '{stale}' is not ISO 8601 (§5.5)", None))
            elif parse_iso_utc(stale) <= now and (status or '').lower() != 'deprecated':
                findings.append(('stale', r, f'STALE since {stale} (§5.5)', None))

        if re.search(r'(?m)^timestamp:', fm, re.I):
            findings.append(('warn', r, "v0.1 'timestamp' → use generated.at (§13.1)", None))
        if re.search(r'(?m)^# Citations', text, re.I):
            findings.append(('warn', r, "v0.1 '# Citations' → use sources[] (§13.1)", None))

        # actors in generated.by / verified[].by / sources[].author
        for m in re.finditer(r'(?m)\b(?:by|author):\s*([^\s,}\]]+)', fm):
            actor = m.group(1).strip('"\'')
            if not ACTOR_RX.match(actor):
                hint = ' — trust tier needs exact lowercase "human:<id>"' if re.match(r'^human[:/]', actor, re.I) else ''
                findings.append(('warn', r, f"actor '{actor}' does not match §7 shapes{hint}", None))
        for m in re.finditer(r'(?m)\bat:\s*([^\s,}\]]+)', fm):
            d = m.group(1).strip('"\'')
            if not ISO_RX.match(d):
                findings.append(('warn', r, f"datetime '{d}' is not ISO 8601", None))

        if typ.lower() == 'attested computation' and not scalar(fm, 'runtime'):
            findings.append(('warn', r, "Attested Computation without 'runtime' (§10.2)", None))

        # footnote labels must match a sources[].id
        source_ids = [m.group(1).strip('"\'').lower() for m in re.finditer(r'(?m)^\s*-\s*(?:\{\s*)?id:\s*([^\s,}]+)', fm)]
        seen = []
        for m in re.finditer(r'\[\^([^\]]+)\]', text):
            label = m.group(1)
            if label in seen:
                continue
            seen.append(label)
            if label.lower() not in source_ids:
                findings.append(('warn', r, f'footnote [^{label}] names no sources[].id (§5.1)', None))

        # internal links (spec-tolerated → warn), resolved from the bundle root whatever --path is
        for m in re.finditer(r'\]\((/[^)#\s]+\.md|(?:\./|\.\./)[^)#\s]+\.md)', text):
            link = m.group(1)
            if link.startswith('/'):
                target_id = link.lstrip('/')
            else:
                d = posix(os.path.dirname(r))
                combined = f'{d}/{link}' if d else link
                parts = []
                for p in combined.split('/'):   # normalise ./ and ../
                    if p in ('.', ''):
                        continue
                    if p == '..':
                        if parts:
                            parts.pop()
                    else:
                        parts.append(p)
                target_id = '/'.join(parts)
            if target_id not in concept_ids and not os.path.exists(os.path.join(root, target_id)):
                findings.append(('warn', r, f'broken link {link} (§6.1, tolerated)', target_id))

    # which files can fail: everything, or the files under --path and/or changed since --changed BASE
    scope = rel(root, target) if target != root else ''
    selected = set(c for c in concept_ids if not scope or c == scope or c.startswith(scope + '/'))
    removed = set()
    what = [scope] if scope else []
    if a.changed:
        changed, removed = changed_paths(root, a.changed)
        if changed is None:
            print(f'note  --changed: git could not compare with {a.changed}; checking every selected file')
            removed = set()
        else:
            selected &= changed
            what.append(f'changed since {a.changed}')

    # a broken link to a path deleted or renamed in this change belongs to the change, wherever the link is
    def gates(x):
        return x[1] in selected or (x[3] is not None and x[3] in removed)

    gated = [x for x in findings if gates(x)]
    others = [x for x in findings if not gates(x)]

    def counts(xs):
        return [sum(1 for x in xs if x[0] == level) for level in LEVELS]

    for level in LEVELS:
        for x in gated:
            if x[0] == level:
                print(f'{level:<5} {x[1]} : {x[2]}')
    e, w, s = counts(gated)
    oe, ow, os_ = counts(others)
    if what:
        print(f"{len(selected)} of {len(files)} concept file(s) checked ({', '.join(what)}): "
              f'{e} error(s), {w} warning(s), {s} stale')
        if oe or ow or os_:
            print(f'other files: {oe} error(s), {ow} warning(s), {os_} stale - not checked here, '
                  'run without --path / --changed to list them')
    else:
        print(f'{len(files)} concept file(s) checked: {e} error(s), {w} warning(s), {s} stale')
    if s or os_:
        print('stale = past stale_after: freshness, not conformance, never fails a run - a person re-verifies a spec, '
              'its generator refreshes a generated page; never move stale_after or write verified to clear it')

    gate = 0 if a.strict else (a.max_warnings if a.max_warnings >= 0 else sys.maxsize)
    if e or w > gate:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
