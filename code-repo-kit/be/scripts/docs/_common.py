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
    the generator's own folder. Keys unknown to the generator are kept (other generators read them).
    Nested objects (`rest`, `kafka`, ...) are merged key by key so a partial block keeps the other defaults."""
    import json
    here = os.path.dirname(os.path.abspath(sys.argv[0]))
    candidates = [explicit] if explicit else [os.path.join(root, 'scripts', 'docs', CONFIG_FILE), os.path.join(here, CONFIG_FILE)]
    cfg = {k: (dict(v) if isinstance(v, dict) else v) for k, v in defaults.items()}
    for c in candidates:
        if c and os.path.isfile(c):
            with open(c, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            for k, v in data.items():
                if k.startswith('_'):
                    continue
                if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                    cfg[k].update(v)
                else:
                    cfg[k] = v
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


# ---- JVM backend helpers (Maven modules, packages, layers, Kotlin constants, Spring properties) ----
def pom_modules(root):
    """<module> entries of the root pom.xml (Maven multi-module); [] when there is no pom or no modules."""
    import xml.etree.ElementTree as ET
    pom = os.path.join(root, 'pom.xml')
    if not os.path.isfile(pom):
        return []
    ns = '{http://maven.apache.org/POM/4.0.0}'
    x = ET.fromstring(read_text(pom))
    return [m.text.strip() for m in x.findall(f'.//{ns}modules/{ns}module') if m.text and m.text.strip()]


def module_dirs(root, cfg):
    """Build modules: `modules` of the config, else the root pom, else the repo itself ('.')."""
    return list(cfg.get('modules') or pom_modules(root) or ['.'])


def module_of(root, path, modules):
    rel = rel_path(root, path)
    for m in modules:
        if m != '.' and (rel == m or rel.startswith(m + '/')):
            return m
    return '.'


def main_sources(root, cfg, modules=None):
    """Kotlin/Java files under <module>/<source_root> of every module, minus tests and `exclude_paths`."""
    modules = modules or module_dirs(root, cfg)
    excl = [os.path.join(root, p) for p in cfg.get('exclude_paths', [])]
    out = []
    for m in modules:
        d = os.path.join(root, m, cfg.get('source_root', 'src/main/kotlin'))
        if os.path.isdir(d):
            out += source_files_cfg(d, ['*.kt', '*.java'], cfg.get('test_pattern', ''), excl)
    return out


def package_of(text):
    m = re.search(r'(?m)^package\s+([\w.]+)', text)
    return m.group(1) if m else ''


def base_package(cfg, packages):
    """The configured `base_package` when the module uses it, else the shortest package of the module."""
    pkgs = [p for p in packages if p]
    cb = cfg.get('base_package', '')
    if cb and any(p == cb or p.startswith(cb + '.') for p in pkgs):
        return cb
    return min(pkgs, key=len) if pkgs else ''


def layer_of(pkg, base, layers):
    """Layer of a package: its first segment after the base package, or `first/second` when that pair is a configured
    layer (e.g. dao/model). Classes in the base package itself are `(root)`."""
    if not base or pkg == base or not pkg.startswith(base + '.'):
        return '(root)'
    parts = pkg[len(base) + 1:].split('.')
    if len(parts) > 1 and parts[0] + '/' + parts[1] in layers:
        return parts[0] + '/' + parts[1]
    return parts[0]


def const_strings(files):
    """`const val NAME = "value"` across files -> {NAME: value}; `$OTHER` references inside values are resolved."""
    out = {}
    for f in files:
        for m in re.finditer(r'const\s+val\s+(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"', read_text(f)):
            out[m.group(1)] = m.group(2)
    for _ in range(3):
        for k, v in list(out.items()):
            out[k] = re.sub(r'\$\{(\w+)\}|\$(\w+)', lambda m: out.get(m.group(1) or m.group(2), m.group(0)), v)
    return out


def load_properties(root, files):
    """Flattened `a.b.c -> value` map of simple YAML / .properties files (scalars only, indentation based, no YAML
    library). Enough to resolve `${app.kafka.topics.x}` placeholders in annotations."""
    props = {}
    for rel in files or []:
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            continue
        text = read_text(p)
        if p.lower().endswith('.properties'):
            for line in re.split(r'\r?\n', text):
                m = re.match(r'^\s*([\w.\-\[\]]+)\s*[=:]\s*(.*?)\s*$', line)
                if m and not line.lstrip().startswith(('#', '!')):
                    props[m.group(1)] = m.group(2)
            continue
        stack = []
        for line in re.split(r'\r?\n', text):
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            if line.strip() == '---':
                stack = []
                continue
            m = re.match(r'^(\s*)([\w.\-]+)\s*:\s*(.*?)\s*$', line)
            if not m:
                continue
            indent = len(m.group(1))
            while stack and stack[-1][0] >= indent:
                stack.pop()
            key = '.'.join([k for _, k in stack] + [m.group(2)])
            val = re.sub(r'\s+#.*$', '', m.group(3)).strip()
            if val == '':
                stack.append((indent, m.group(2)))
            else:
                props[key] = val.strip('"\'')
    return props


def resolve_string_expr(expr, consts, props=None):
    """Value of a Kotlin string expression made of literals, `Object.CONST` references and `+`
    ("a" + Topics.X, HarborConstants.API_BASE_PATH + "/x"), with `${property[:default]}` placeholders looked up in
    props (application.yml) and `$CONST` templates in consts. Returns None when a reference is unknown."""
    expr = expr.strip()
    out = ''
    for lit, ref in re.findall(r'"((?:[^"\\]|\\.)*)"|([\w.]+)', expr):
        if ref:
            name = ref.split('.')[-1]
            if name not in consts:
                return None
            out += consts[name]
        else:
            out += lit.replace('\\$', '$')

    def sub(m):
        key = m.group(1) or m.group(2)
        key, _, default = key.partition(':')
        if key in consts:
            return consts[key]
        if props and key in props:
            return props[key]
        return default if default else m.group(0)
    for _ in range(3):
        out = re.sub(r'\$\{([^}]+)\}|\$(\w+)', sub, out)
    return out


def parse_contexts(text):
    """contexts.yml one-line entries: name: { spec: X, fe: [...] | "x" | x, be: [...] } -> [(name, spec, fe list, be list)]."""
    out = []
    for m in re.finditer(r'(?m)^\s{2}([\w-]+):\s*\{(.*)\}', text):
        name, body = m.group(1), m.group(2)
        sm = re.search(r'spec:\s*(\w+)', body)

        def lst(key):
            lm = re.search(key + r':\s*(\[[^\]]*\]|"[^"]*"|\'[^\']*\'|[\w*?.-]*)', body)
            if not lm:
                return []
            raw = lm.group(1).strip()
            raw = raw[1:-1] if raw[:1] in '["\'' else raw
            return [x.strip().strip('"\'') for x in raw.split(',') if x.strip().strip('"\'')]
        out.append((name, sm.group(1) if sm else '', lst('fe'), lst('be')))
    return out
