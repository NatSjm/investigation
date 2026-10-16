"""Shared helpers for the lib-free doc generators (standard library only). Imported by the gen-*.py scripts."""
import os
import re
import sys
from datetime import datetime, timezone

EXCLUDE_DIRS = ('target', 'build', 'node_modules', '.git', 'dist', 'coverage', 'generated')


def utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def read_text(path):
    """UTF-8 (BOM tolerated), line endings kept as they are on disk (file:line numbers depend on it)."""
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        return f.read()


def write_text(path, content):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)


def like(s, pattern):
    """Case-insensitive wildcard match (* and ?) over the whole string."""
    rx = '^' + ''.join('.*' if c == '*' else '.' if c == '?' else re.escape(c) for c in pattern) + '$'
    return re.match(rx, s, re.I | re.S) is not None


def posix(path):
    return path.replace('\\', '/')


def source_files(root, include, exclude_dirs=EXCLUDE_DIRS):
    """Files under root whose name matches one of the include wildcards, skipping the excluded directory names.
    Deterministic order: per directory its files (name order, case-insensitive), then its subdirectories."""
    root = os.path.abspath(root)
    out = []
    excluded = set(d.lower() for d in exclude_dirs)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((d for d in dirnames if d.lower() not in excluded), key=str.lower)
        for name in sorted(filenames, key=str.lower):
            if any(like(name, p) for p in include):
                out.append(os.path.join(dirpath, name))
    return out


def resolve_out(root, out):
    return out if os.path.isabs(out) else os.path.join(root, out)


def rel_path(root, full):
    return posix(os.path.relpath(full, root))


def line_number(text, index):
    return text.count('\n', 0, index) + 1


def utc_date():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')


def header(title, source, description=''):
    if not description:
        description = f'Generated map: {title}, derived from {source}; read instead of source files.'
    t = title.replace('"', '\\"')
    d = description.replace('"', '\\"')
    return (
        '---\n'
        'type: Document\n'
        f'title: "{t}"\n'
        f'description: "{d}"\n'
        'generated:\n'
        '  by: process:gen-docs\n'
        f'  at: {utc_date()}\n'
        'status: stable\n'
        '---\n'
        f'# {title}\n'
        '\n'
        f'> Generated from `{source}` by `scripts/docs` (regex scan, no build required). Do not edit by hand.\n'
    )


def sort_key(s):
    """Sort order of every generated table: case-insensitive alphabetical, exact string as tie-break.
    No locale or ICU involved, so the output is identical on every machine."""
    return (s.casefold(), s)


def escape_cell(s):
    return re.sub(r'\r?\n', ' ', re.sub(r'\|', r'\\|', s or '')).strip()


def blank_comments(text):
    """Blanks /* */ and // comments keeping line breaks, so offsets and file:line stay right."""
    return re.sub(r'(?s)/\*.*?\*/|//[^\r\n]*', lambda m: re.sub(r'[^\r\n]', ' ', m.group(0)), text)


def first_doc_line(doc, drop=None):
    """First non-empty line of a KDoc/JSDoc body that is not a @tag (leading `* ` removed)."""
    for line in re.split(r'\r?\n', doc or ''):
        s = re.sub(r'^\s*\*\s?', '', line)
        if drop:
            s = re.sub(drop, '', s, flags=re.I)
        s = s.strip()
        if s and not s.startswith('@'):
            return s
    return ''


def ticks(items):
    return ', '.join('`' + x + '`' for x in items)


def unique(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def split_list(values):
    """argparse helper: ['a,b', 'c'] -> ['a', 'b', 'c']."""
    out = []
    for v in values or []:
        out.extend(x.strip() for x in v.split(',') if x.strip())
    return out


# ---- layout configuration (docs-gen.json next to the generators) ----
CONFIG_FILE = 'docs-gen.json'


def load_config(root, defaults, explicit=''):
    """Merges docs-gen.json over the generator's defaults. Looked up in this order: --config, <root>/scripts/docs/,
    the generator's own folder. Keys unknown to the generator are kept (other generators read them)."""
    import json
    here = os.path.dirname(os.path.abspath(sys.argv[0]))
    candidates = [explicit] if explicit else [os.path.join(root, 'scripts', 'docs', CONFIG_FILE), os.path.join(here, CONFIG_FILE)]
    cfg = dict(defaults)
    for c in candidates:
        if c and os.path.isfile(c):
            with open(c, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            cfg.update({k: v for k, v in data.items() if not k.startswith('_')})
            cfg['_config_path'] = c
            break
    return cfg


def glob_match(rel, pattern):
    """Path glob on a repo-relative posix path: `**` spans folders, `*` and `?` stay inside one segment."""
    rx = ''
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith('**/', i):
            rx += '(?:.*/)?'
            i += 3
            continue
        if pattern.startswith('**', i):
            rx += '.*'
            i += 2
            continue
        rx += '[^/]*' if c == '*' else '[^/]' if c == '?' else re.escape(c)
        i += 1
    return re.match('^' + rx + '$', posix(rel), re.I) is not None


def under(path, prefixes):
    """True when the absolute path lies under one of the absolute prefixes (file or folder)."""
    p = posix(os.path.abspath(path)).lower()
    for x in prefixes:
        x = posix(os.path.abspath(x)).lower()
        if p == x or p.startswith(x + '/'):
            return True
    return False


def source_files_cfg(root, include, test_rx, exclude_paths=()):
    """source_files() minus tests (regex on the file name) and minus the configured excluded paths (absolute)."""
    rx = re.compile(test_rx, re.I) if test_rx else None
    return [f for f in source_files(root, include)
            if not (rx and rx.search(os.path.basename(f))) and not under(f, exclude_paths)]
