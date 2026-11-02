#!/usr/bin/env python3
"""Standard-library port of the OKF v0.2 conformance checker core (okf_validate.py, MIT, scaccogatto/okf-skills).
Runs without pyyaml. ERRORs = §11 hard failures; warnings = soft guidance; stale = past stale_after (§5.5), listed
but never counted as a warning: freshness, not conformance (the reference checker does not report it either).
--path only chooses which files can fail: the whole bundle is always read, links resolve from its root (the folder
whose index.md carries okf_version) and the problems of the other files are summed up on one line. No git involved.
Examples:
  python3 scripts/okf-validate.py                          # whole repo bundle
  python3 scripts/okf-validate.py --strict                 # warnings fail too (the hook, CI, the end of a task)
  python3 scripts/okf-validate.py --path features --strict # a folder or a single file
  python3 scripts/okf-validate.py --max-warnings 5"""
import argparse
import os
import re
import sys

from _common import repo_root, rel, posix, now_utc, parse_iso_utc, walk_files, utf8_stdout

# AGENTS.md is an agent-instruction file (cross-tool convention), not a knowledge concept; .context holds throwaway packs
DEFAULT_EXCLUDE = ['.github', 'scripts', 'ci-examples', 'third-party', 'node_modules', '.git', 'confluence-import',
                   'work-items', 'test-design', 'AGENTS.md', '.context']
ACTOR_RX = re.compile(r'^(human:[^\s/]+|process:[^\s/]+|[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)$', re.I)
ISO_RX = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(Z|[+\-]\d{2}:\d{2}))?$', re.I)
LEVELS = ('ERROR', 'warn', 'stale')
FOOTNOTES_MARK = '<!-- footnotes: generated from sources[] by scripts/build-index.py -->'   # written by build-index.py


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


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--path', default=repo_root(__file__), help='folder or file to check (default: the whole bundle)')
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--max-warnings', type=int, default=-1)
    ap.add_argument('--exclude', nargs='*', default=DEFAULT_EXCLUDE)
    a = ap.parse_args()
    target = os.path.abspath(a.path)
    root = bundle_root(target)
    findings = []   # (level, file, message)
    now = now_utc()

    files = walk_files(root, '*.md', exclude_rel=a.exclude)
    concept_ids = set(rel(root, f) for f in files)

    for f in files:
        r = rel(root, f)
        try:
            with open(f, 'r', encoding='utf-8-sig', errors='strict', newline='') as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            findings.append(('ERROR', r, 'not readable as UTF-8'))
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
                        findings.append(('warn', r, f"root index carries unexpected keys: {', '.join(extra)} (§8/§12)"))
                    v = scalar(fm, 'okf_version')
                    if v and v != '0.2':
                        findings.append(('warn', r, f"okf_version '{v}' differs from 0.2 (§12)"))
                else:
                    findings.append(('warn', r, 'reserved file must not carry frontmatter (§8/§9)'))
            if name == 'log.md':
                for m in re.finditer(r'(?m)^## (.+)$', text):
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', m.group(1).strip()):
                        findings.append(('warn', r, f"log heading '{m.group(1)}' is not ISO YYYY-MM-DD (§9)"))
            continue

        if not fm:
            findings.append(('ERROR', r, 'no YAML frontmatter (§11)'))
            continue
        typ = scalar(fm, 'type')
        if not typ:
            findings.append(('ERROR', r, "missing or empty 'type' (§11)"))
            continue

        # Templates hold placeholders (<ISO>, [^id]); §11 checks apply, value-level warnings do not.
        if is_template(r):
            continue

        for k in ('title', 'description'):
            if not scalar(fm, k):
                findings.append(('warn', r, f"missing recommended '{k}'"))

        status = scalar(fm, 'status')
        if status and status.lower() not in ('draft', 'stable', 'deprecated'):
            findings.append(('warn', r, f"status '{status}' not in draft|stable|deprecated (§5.4)"))

        stale = scalar(fm, 'stale_after')
        if stale:
            if not ISO_RX.match(stale):
                findings.append(('warn', r, f"stale_after '{stale}' is not ISO 8601 (§5.5)"))
            elif parse_iso_utc(stale) <= now and (status or '').lower() != 'deprecated':
                findings.append(('stale', r, f'STALE since {stale} (§5.5)'))

        if re.search(r'(?m)^timestamp:', fm, re.I):
            findings.append(('warn', r, "v0.1 'timestamp' → use generated.at (§13.1)"))
        if re.search(r'(?m)^# Citations', text, re.I):
            findings.append(('warn', r, "v0.1 '# Citations' → use sources[] (§13.1)"))

        # actors in generated.by / verified[].by / sources[].author
        for m in re.finditer(r'(?m)\b(?:by|author):\s*([^\s,}\]]+)', fm):
            actor = m.group(1).strip('"\'')
            if not ACTOR_RX.match(actor):
                hint = ' — trust tier needs exact lowercase "human:<id>"' if re.match(r'^human[:/]', actor, re.I) else ''
                findings.append(('warn', r, f"actor '{actor}' does not match §7 shapes{hint}"))
        for m in re.finditer(r'(?m)\bat:\s*([^\s,}\]]+)', fm):
            d = m.group(1).strip('"\'')
            if not ISO_RX.match(d):
                findings.append(('warn', r, f"datetime '{d}' is not ISO 8601"))

        if typ.lower() == 'attested computation' and not scalar(fm, 'runtime'):
            findings.append(('warn', r, "Attested Computation without 'runtime' (§10.2)"))

        # footnote labels must match a sources[].id (a `[^id]` quoted in a code span or a fenced block is prose)
        source_ids = [m.group(1).strip('"\'').lower() for m in re.finditer(r'(?m)^\s*-\s*(?:\{\s*)?id:\s*([^\s,}]+)', fm)]
        prose = re.sub(r'`[^`\r\n]*`', '', re.sub(r'(?s)```.*?```', '', text))
        seen = []
        for m in re.finditer(r'\[\^([^\]]+)\]', prose):
            label = m.group(1)
            if label in seen:
                continue
            seen.append(label)
            if label.lower() not in source_ids:
                findings.append(('warn', r, f'footnote [^{label}] names no sources[].id (§5.1)'))

        # repo rule (features/conventions.md, "Business rules"): the footnote block at the end of a concept is written
        # by build-index.py from sources[]; a definition line outside that block is a hand-kept copy that drifts
        bm = re.search(r'(?m)^' + re.escape(FOOTNOTES_MARK) + r'[ \t]*\r?$', text)   # at line start: quoted in prose it is not the block
        block_at = bm.start() if bm else -1
        for m in re.finditer(r'(?m)^\[\^([^\]\s]+)\]:', text):   # same string as block_at (offsets must agree)
            if block_at < 0 or m.start() < block_at:
                findings.append(('warn', r, f'footnote definition [^{m.group(1)}]: written by hand - build-index.py '
                                            'generates the block from sources[]'))

        # repo rule (same section): in a Feature Spec or an Attested Computation, sources[] holds what the body cites;
        # a file nobody cites belongs in code_refs
        if typ.lower() in ('feature spec', 'attested computation'):
            cited = set(l.lower() for l in re.findall(r'\[\^([^\]\s]+)\](?!:)', prose))
            cited |= set(m.group(1).split('#')[0].lower()
                         for m in re.finditer(r'\(source: (?:code|imported) ([^\s)]+)\)', prose))
            for sid in source_ids:
                if sid not in cited:
                    findings.append(('warn', r, f"sources[].id '{sid}' is cited by no footnote or source marker "
                                                '(repo rule: sources[] holds what the body cites; an uncited file goes to code_refs)'))

        # repo rule "Provenance per rule" (features/conventions.md): in a draft Feature Spec no person has verified,
        # every business rule that is neither proposed nor withdrawn ends with a source marker
        # (source: code <sources-id>#<symbol> | imported <sources-id> | contract <operationId> | person human:<id> | spec BR-..)
        if typ.lower() == 'feature spec' and (status or '').lower() == 'draft' and not re.search(r'(?m)^verified:', fm):
            for m in re.finditer(r'(?ms)^- \*\*(BR-[A-Z0-9]+-\d+-\d+)\*\*(.*?)(?=^- |^[ \t]*$|^#|\Z)', text):
                rid, body = m.group(1), m.group(2)
                if re.search(r'\*\*proposed\*\*|withdrawn', body, re.I):
                    continue
                sm = re.search(r'\(source: (code|imported|contract|person|spec) ([^\s)]+)\)', body)
                if not sm:
                    findings.append(('warn', r, f'{rid} has no (source: ...) marker (repo rule: provenance per rule)'))
                    continue
                kind, ref = sm.group(1), sm.group(2)
                if kind in ('code', 'imported') and ref.split('#')[0].lower() not in source_ids:
                    findings.append(('warn', r, f'{rid} source marker names no sources[].id: {ref}'))
                if kind == 'code' and '#' not in ref:
                    findings.append(('warn', r, f'{rid} code marker names no symbol (<sources-id>#<symbol>): {ref}'))

        # repo rule "Provenance per step" (.github/instructions/calculations.instructions.md): in a draft Attested
        # Computation no person has verified and that is not tagged `proposed`, every numbered step of the Formula step
        # list and the Conventions paragraph end with a source marker (same forms as the spec rule)
        if typ.lower() == 'attested computation' and (status or '').lower() == 'draft' \
                and not re.search(r'(?m)^verified:', fm) and not re.search(r'(?m)^tags:.*\bproposed\b', fm):
            def check_marker(where, body):
                sm = re.search(r'\(source: (code|imported|contract|person|spec) ([^\s)]+)\)', body)
                if not sm:
                    findings.append(('warn', r, f'{where} has no (source: ...) marker (repo rule: provenance per step)'))
                    return
                kind, ref = sm.group(1), sm.group(2)
                if kind in ('code', 'imported') and ref.split('#')[0].lower() not in source_ids:
                    findings.append(('warn', r, f'{where} source marker names no sources[].id: {ref}'))
                if kind == 'code' and '#' not in ref:
                    findings.append(('warn', r, f'{where} code marker names no symbol (<sources-id>#<symbol>): {ref}'))
            fsec = re.search(r'(?ms)^## Formula[^\r\n]*\r?\n(.*?)(?=^#|\Z)', text)
            if fsec:
                steps = re.split(r'(?m)^(?=\d+\.\s)', fsec.group(1))
                for st in steps:
                    sm_ = re.match(r'(\d+)\.\s', st)
                    if sm_:
                        check_marker(f'Formula step {sm_.group(1)}', st.split('\n\n')[0].split('\r\n\r\n')[0])
            csec = re.search(r'(?ms)^## Conventions[^\r\n]*\r?\n(.*?)(?=^#|\Z)', text)
            if csec and csec.group(1).strip():
                check_marker('Conventions', csec.group(1))

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
                findings.append(('warn', r, f'broken link {link} (§6.1, tolerated)'))

    # which files can fail: everything, or only the files under --path
    scope = rel(root, target) if target != root else ''
    selected = set(c for c in concept_ids if not scope or c == scope or c.startswith(scope + '/'))
    gated = [x for x in findings if x[1] in selected]
    others = [x for x in findings if x[1] not in selected]

    def counts(xs):
        return [sum(1 for x in xs if x[0] == level) for level in LEVELS]

    for level in LEVELS:
        for x in gated:
            if x[0] == level:
                print(f'{level:<5} {x[1]} : {x[2]}')
    e, w, s = counts(gated)
    oe, ow, os_ = counts(others)
    if scope:
        print(f'{len(selected)} of {len(files)} concept file(s) checked ({scope}): '
              f'{e} error(s), {w} warning(s), {s} stale')
        if oe or ow or os_:
            print(f'other files: {oe} error(s), {ow} warning(s), {os_} stale - not checked here, '
                  'run without --path to list them')
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
