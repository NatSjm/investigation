"""Shared helpers for the docs-repo scripts (standard library only; Python 3.11+)."""
import os
import re
import sys
from datetime import datetime, timedelta, timezone


def utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def repo_root(script_file):
    """The docs repository root: the parent of scripts/."""
    return os.path.dirname(os.path.dirname(os.path.abspath(script_file)))


def read_text(path):
    """UTF-8 (BOM tolerated), line endings kept as they are on disk."""
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        return f.read()


def read_text_or_empty(path):
    return read_text(path) if os.path.isfile(path) else ''


def write_text(path, content):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)


def posix(path):
    return path.replace('\\', '/')


def rel(root, path):
    return posix(os.path.relpath(path, root))


def like(s, pattern):
    """Case-insensitive wildcard match (* and ?) over the whole string."""
    rx = '^' + ''.join('.*' if c == '*' else '.' if c == '?' else re.escape(c) for c in pattern) + '$'
    return re.match(rx, s, re.I | re.S) is not None


def sort_key(s):
    """Sort order of every generated list: case-insensitive alphabetical, exact string as tie-break.
    No locale or ICU involved, so the output is identical on every machine."""
    return (s.casefold(), s)


def split_lines(s):
    return re.split(r'\r?\n', s)


def get_fm(text):
    m = re.match(r'(?s)\A﻿?---\r?\n(.*?)\r?\n---', text)
    return m.group(1) if m else ''


def get_val(fm, key, strip_comment=True):
    """Scalar value of a top-level frontmatter key ('' when missing); quotes and an inline comment removed."""
    m = re.search(r'(?m)^' + re.escape(key) + r':\s*(.+?)\s*$', fm, re.I)
    if not m:
        return ''
    v = m.group(1)
    if strip_comment:
        v = re.sub(r'\s+#.*$', '', v)
    return v.strip().strip('"').strip("'")


def get_list(fm, key):
    """Inline [a, b] or block list under a top-level key; trimmed strings."""
    m = re.search(r'(?m)^' + re.escape(key) + r':\s*\[([^\]]*)\]', fm, re.I)
    if m:
        return [x for x in (s.strip().strip('"').strip("'") for s in m.group(1).split(',')) if x]
    # Items are the consecutive indented `- ` lines right after the key; the next top-level key ends the list.
    # No DOTALL here: with it `.*` ran across lines and the list swallowed every indented item of the keys below.
    m = re.search(r'(?m)^' + re.escape(key) + r':[ \t]*\r?\n((?:[ \t]+-[ \t]+[^\r\n]*\r?\n?)+)', fm, re.I)
    if m:
        return [x.group(1).strip().strip('"').strip("'") for x in re.finditer(r'(?m)^[ \t]+-[ \t]+(.+?)[ \t]*$', m.group(1))]
    return []


ISO_RX = re.compile(r'^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?(?:\.\d+)?\s*(Z|[+-]\d{2}:?\d{2})?)?$', re.I)


def parse_iso_utc(s):
    """ISO 8601 date or datetime -> aware UTC datetime; a value without zone is taken as UTC. ValueError otherwise."""
    m = ISO_RX.match(s.strip())
    if not m:
        raise ValueError(f'not an ISO 8601 date: {s}')
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    hh, mi, ss = int(m.group(4) or 0), int(m.group(5) or 0), int(m.group(6) or 0)
    dt = datetime(y, mo, d, hh, mi, ss, tzinfo=timezone.utc)
    z = m.group(7)
    if z and z.upper() != 'Z':
        sign = 1 if z[0] == '+' else -1
        hz, mz = int(z[1:3]), int(z[-2:])
        dt = dt - sign * timedelta(hours=hz, minutes=mz)
    return dt


def now_utc():
    return datetime.now(timezone.utc)


def badge(fm, now=None, strict_dates=False):
    """Trust badge of a concept: status (unless stable) · human-reviewed|machine-confirmed|unverified · STALE."""
    now = now or now_utc()
    b = []
    status = get_val(fm, 'status')
    if status and status.lower() != 'stable':
        b.append(status)
    if re.search(r'(?m)^verified:', fm, re.I):
        b.append('human-reviewed' if re.search(r'verified:[\s\S]*?by:\s*human:', fm, re.I) else 'machine-confirmed')
    else:
        b.append('unverified')
    sa = get_val(fm, 'stale_after')
    if sa:
        try:
            if parse_iso_utc(sa) <= now:
                b.append('STALE')
        except ValueError:
            if strict_dates:
                raise
    return ' · '.join(b)


def walk_files(root, pattern='*', exclude_rel=()):
    """Files under root matching the wildcard (case-insensitive), in a deterministic order: per directory its
    files (name order), then its subdirectories. exclude_rel: repo-relative directory or file names to skip."""
    root = os.path.abspath(root)
    out = []
    excluded = [posix(e).strip('/') for e in exclude_rel]

    def is_excluded(r):
        return any(r == e or r.startswith(e + '/') for e in excluded)

    def visit(d):
        try:
            entries = sorted(os.listdir(d), key=str.lower)
        except OSError:
            return
        files = [e for e in entries if os.path.isfile(os.path.join(d, e))]
        dirs = [e for e in entries if os.path.isdir(os.path.join(d, e))]
        for e in files:
            full = os.path.join(d, e)
            if like(e, pattern) and not is_excluded(rel(root, full)):
                out.append(full)
        for e in dirs:
            full = os.path.join(d, e)
            if not is_excluded(rel(root, full)):
                visit(full)

    visit(root)
    return out


def code(s):
    return '`' + s + '`'
