#!/usr/bin/env python3
"""Imports a Confluence HTML space export (the standard "Export space to HTML", or the same pages re-arranged one
folder per page) into the quarantine: one Markdown page per exported page under
confluence-import/<SPACE>/<section>/<slug>.md with the header block of confluence-import/README.md, the images the
page shows copied to confluence-import/<SPACE>/_attachments/<slug>/, and the inventory table of the README
regenerated between its markers. Standard library only, no pandoc.

Source layout (--src is the export root; one folder per page tree = section, or a single section folder):
  <src>/<section>/<Title>_<pageId>/<pageId>.html  + images next to it        (re-arranged export)
  <src>/<section>/<Title>_<pageId>.html            + attachments/<pageId>/..  (standard export)
Pages already migrated (a file under <SPACE>/_done/ with the same confluence_id) are skipped while the export is not
newer than the migrated copy; a newer export (last_modified of both parseable, the export's later) is written as a fresh
page in its section folder with `supersedes_done` naming the migrated copy and `supersedes_done_modified` its date, so
an agent reruns on it and scripts/import-done.py replaces the copy; nothing under _done/ is ever written or deleted.
Files the script wrote earlier for a page that disappeared from the export are deleted (only files carrying the
`imported_from` header, never _done/).

Examples:
  python3 scripts/confluence-import.py --src confluence-import/raw-html --space HARBOR --lang cs --base-url https://confluence.example.com
  python3 scripts/confluence-import.py --src confluence-import/raw-html --space HARBOR --section business --check
  python3 scripts/confluence-import.py --src confluence-import/raw-html --space HARBOR --body html   # keep the body as HTML"""
import argparse
import os
import re
import sys
import unicodedata
from datetime import datetime
from html import escape as html_escape
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit, parse_qs

sys.dont_write_bytecode = True
from _common import (repo_root, read_text_or_empty, write_text, rel, posix, get_fm, get_val, walk_files, like,
                     sort_key, split_lines, utf8_stdout)

PAGE_RX = re.compile(r'^(.*?)_(\d+)$')
IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp')
BANNER = '> Imported Confluence page. Quarantined — see `confluence-import/README.md`. Not authoritative.'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
SKIP_TAGS = {'script', 'style', 'noscript', 'head', 'title', 'meta', 'link', 'input', 'button', 'select', 'textarea'}
RAW_TAGS = {'iframe', 'object', 'embed', 'svg', 'video', 'audio', 'canvas', 'map', 'form', 'math'}
BLOCK_TAGS = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table', 'pre', 'div', 'blockquote', 'hr', 'dl',
              'section', 'article', 'header', 'footer', 'nav', 'aside', 'figure', 'details', 'center', 'body', 'html',
              'main', 'fieldset', 'address'}
PANEL_LABELS = {'information': 'Info', 'note': 'Note', 'warning': 'Warning', 'tip': 'Tip'}
ISO_DAY = re.compile(r'^\d{4}-\d{2}-\d{2}$')
MONTHS = {m: i for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], 1)}


# ---------------------------------------------------------------- HTML tree
class Node:
    __slots__ = ('tag', 'attrs', 'children', 'parent')

    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.children, self.parent = tag, dict(attrs or {}), [], parent

    def classes(self):
        return (self.attrs.get('class') or '').split()

    def has_class(self, *names):
        cs = self.classes()
        return any(n in cs for n in names)

    def text(self):
        return ''.join(c if isinstance(c, str) else c.text() for c in self.children)

    def find(self, pred):
        for c in self.children:
            if isinstance(c, Node):
                if pred(c):
                    return c
                r = c.find(pred)
                if r is not None:
                    return r
        return None

    def find_all(self, pred, out=None):
        out = [] if out is None else out
        for c in self.children:
            if isinstance(c, Node):
                if pred(c):
                    out.append(c)
                c.find_all(pred, out)
        return out


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('#root')
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        if data:
            self.cur.children.append(data)


def parse_html(text):
    b = TreeBuilder()
    b.feed(text)
    b.close()
    return b.root


def by_id(root, id_):
    return root.find(lambda n: n.attrs.get('id') == id_)


def by_class(root, cls):
    return root.find(lambda n: n.has_class(cls))


# ---------------------------------------------------------------- metadata
def slugify(title):
    s = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii').lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s or 'page'


def parse_date(s):
    """Confluence page-metadata date -> YYYY-MM-DD, or '' when the format is unknown."""
    s = s.strip().rstrip('.')
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        return m.group(0)
    m = re.match(r'^([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})', s)       # Sep 02, 2025 / September 2 2025
    if m and m.group(1).lower() in MONTHS:
        return f'{int(m.group(3)):04d}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}'
    m = re.match(r'^(\d{1,2})\.?\s+([A-Za-z]{3})[a-z]*\.?\s+(\d{4})', s)     # 02 Sep 2025 / 2. Sept 2025
    if m and m.group(2).lower() in MONTHS:
        return f'{int(m.group(3)):04d}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}'
    m = re.match(r'^(\d{1,2})\.\s?(\d{1,2})\.\s?(\d{4})', s)                   # 02.09.2025 / 2. 9. 2025
    if m:
        return f'{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}'
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})', s)                           # 09/02/2025 (US)
    if m:
        return f'{int(m.group(3)):04d}-{int(m.group(1)):02d}-{int(m.group(2)):02d}'
    return ''


def page_metadata(root):
    """author, editor, last_modified (ISO or ''), raw date text from the export's page-metadata block;
    raw date is None when the export has no page-metadata block at all."""
    meta = by_class(root, 'page-metadata')
    if meta is None:
        return '', '', '', None
    author = editor = ''
    a = meta.find(lambda n: n.has_class('author'))
    e = meta.find(lambda n: n.has_class('editor'))
    if a is not None:
        author = ' '.join(a.text().split())
    if e is not None:
        editor = ' '.join(e.text().split())
    text = ' '.join(meta.text().split())
    if not author:
        m = re.search(r'Created by (.+?)(?:,| on |$)', text)
        author = m.group(1).strip() if m else ''
    if not editor:
        m = re.search(r'last modified by (.+?) on ', text)
        editor = m.group(1).strip() if m else ''
    m = re.search(r'^.*\bon\s+(.+?)\s*$', text)
    raw = m.group(1).strip() if m else ''
    return author, editor, parse_date(raw), raw


def page_title(root, fallback):
    t = by_id(root, 'title-text')
    s = ' '.join(t.text().split()) if t is not None else ''
    if not s:
        t = root.find(lambda n: n.tag == 'title')
        s = ' '.join(t.text().split()) if t is not None else ''
    s = re.sub(r'^[^:]+ : ', '', s)
    return s or fallback


def breadcrumbs(root):
    ol = by_id(root, 'breadcrumbs')
    if ol is None:
        return []
    out = []
    for li in [c for c in ol.children if isinstance(c, Node) and c.tag == 'li']:
        a = li.find(lambda n: n.tag == 'a')
        out.append((' '.join(li.text().split()), a.attrs.get('href', '') if a is not None else ''))
    return [x for x in out if x[0]]


# ---------------------------------------------------------------- discovery
class Page:
    def __init__(self, section, html_path, pid, name_title):
        self.section, self.html, self.id, self.name_title = section, html_path, pid, name_title
        self.title = self.slug = self.author = self.last_modified = self.raw_date = ''
        self.crumbs = []
        self.root = None
        self.assets = []          # (published rel path under <out>, source abs path)
        self.images = 0
        self.notes = []
        self.body_text = ''
        self.done = None          # the _done/ entry this page supersedes (export newer than the migrated copy)


def export_newer(page, done):
    """True when both dates are ISO days and the export's is later; an unparsed date never counts as newer."""
    a, b = page.last_modified, done['last_modified']
    return bool(ISO_DAY.match(a or '') and ISO_DAY.match(b or '') and a > b)


def discover(src):
    """{section: [Page]} - a section is a sub-folder of src holding pages, or src itself."""
    def pages_in(folder, section):
        out = []
        for e in sorted(os.listdir(folder), key=str.lower):
            full = os.path.join(folder, e)
            if os.path.isdir(full):
                m = PAGE_RX.match(e)
                if not m:
                    continue
                htmls = [f for f in sorted(os.listdir(full), key=str.lower) if f.lower().endswith('.html')]
                pick = [f for f in htmls if os.path.splitext(f)[0] == m.group(2)] or htmls
                if pick:
                    out.append(Page(section, os.path.join(full, pick[0]), m.group(2), m.group(1)))
            elif e.lower().endswith('.html') and e.lower() != 'index.html':
                m = PAGE_RX.match(e[:-5])
                out.append(Page(section, full, m.group(2) if m else '', (m.group(1) if m else e[:-5])))
        return out

    direct = pages_in(src, os.path.basename(os.path.normpath(src)))
    if direct:
        return {direct[0].section: direct}
    sections = {}
    for e in sorted(os.listdir(src), key=str.lower):
        full = os.path.join(src, e)
        if os.path.isdir(full) and not e.startswith('.') and e not in ('attachments', 'images', 'styles'):
            ps = pages_in(full, e)
            if ps:
                sections[e] = ps
    return sections


# ---------------------------------------------------------------- link and image resolution
class Resolver:
    def __init__(self, page, by_path, by_id_, out_dir, md_dir, copy_images):
        self.page, self.by_path, self.by_id, self.out, self.md_dir, self.copy_images = page, by_path, by_id_, out_dir, md_dir, copy_images
        self.used_names = set()

    def md_path_of(self, other):
        target = os.path.join(self.out, other.section, other.slug + '.md') if other.section else os.path.join(self.out, other.slug + '.md')
        return posix(os.path.relpath(target, self.md_dir))

    def local(self, href):
        """Absolute source path a relative href points at, or None."""
        if not href or re.match(r'^[a-z][a-z0-9+.-]*:', href, re.I) or href.startswith('#') or href.startswith('//'):
            return None
        path = unquote(urlsplit(href).path)
        if not path:
            return None
        return os.path.normpath(os.path.join(os.path.dirname(self.page.html), path))

    def link(self, href):
        """href of <a> -> (new href, note) ; note = 'attachment' when a non-image attachment was dropped."""
        if not href:
            return href, ''
        u = urlsplit(href)
        pid = parse_qs(u.query).get('pageId', [''])[0]
        if pid and pid in self.by_id:
            return self.md_path_of(self.by_id[pid]) + ('#' + u.fragment if u.fragment else ''), ''
        local = self.local(href)
        if local is None:
            return href, ''
        key = os.path.normcase(local)
        if key in self.by_path:
            return self.md_path_of(self.by_path[key]) + ('#' + u.fragment if u.fragment else ''), ''
        if os.path.basename(local).lower() == 'index.html':
            return '', 'index'
        if local.lower().endswith(('.html', '.htm')):
            return href, ''          # an exported page outside this import: left as exported
        if os.path.isfile(local):
            if local.lower().endswith(IMAGE_EXT):
                return self.image(href, ''), ''
            return '', 'attachment'
        return href, ''

    def image(self, src, alias):
        if re.search(r'(^|/)icons?/', posix(src or '')):
            return ''
        local = self.local(src)
        if local is None or not os.path.isfile(local):
            return src
        for pub, s in self.page.assets:
            if os.path.normcase(s) == os.path.normcase(local):
                return posix(os.path.relpath(os.path.join(self.out, pub), self.md_dir))
        if not self.copy_images:
            return posix(os.path.relpath(local, self.md_dir))
        name = os.path.basename(alias or local)
        if os.path.splitext(name)[1] == '':
            name += os.path.splitext(local)[1]
        name = re.sub(r'[^A-Za-z0-9._-]+', '-', name)
        base, ext = os.path.splitext(name)
        n = 1
        while name in self.used_names:
            n += 1
            name = f'{base}-{n}{ext}'
        self.used_names.add(name)
        pub = f'_attachments/{self.page.slug}/{name}'
        self.page.assets.append((pub, local))
        return posix(os.path.relpath(os.path.join(self.out, pub), self.md_dir))


def resolve_tree(node, r):
    """Rewrite a/img targets in place; drop icon images; count images."""
    for c in list(node.children):
        if not isinstance(c, Node):
            continue
        if c.tag == 'a' and 'href' in c.attrs:
            new, note = r.link(c.attrs['href'])
            if note == 'attachment':
                c.attrs['data-dropped'] = os.path.basename(unquote(urlsplit(c.attrs['href']).path))
                c.attrs.pop('href', None)
            elif note == 'index':
                c.attrs.pop('href', None)
            else:
                c.attrs['href'] = new
        elif c.tag == 'img':
            src = c.attrs.get('src', '')
            alt_src = r.local(c.attrs.get('data-image-src', ''))
            if (not src or not r.local(src) or not os.path.isfile(r.local(src))) and alt_src and os.path.isfile(alt_src):
                src = c.attrs['data-image-src']
            new = r.image(src, c.attrs.get('data-linked-resource-default-alias', ''))
            if new == '':
                node.children[node.children.index(c)] = c.attrs.get('alt', '')
                continue
            if new != src and not re.match(r'^[a-z]+:', new):
                r.page.images += 1
            c.attrs['src'] = new
            if not c.attrs.get('alt'):
                c.attrs['alt'] = c.attrs.get('data-linked-resource-default-alias') or os.path.basename(new)
        resolve_tree(c, r)


# ---------------------------------------------------------------- Markdown renderer
def collapse(s):
    return re.sub(r'\s+', ' ', s)


def md_text(s):
    s = s.replace('\\', '\\\\')
    s = re.sub(r'<(?=[A-Za-z/!])', r'\\<', s)
    return s


def wrap_mark(mark, inner):
    stripped = inner.strip()
    if not stripped:
        return inner
    lead = inner[:len(inner) - len(inner.lstrip())]
    trail = inner[len(inner.rstrip()):]
    return f'{lead}{mark}{stripped}{mark}{trail}'


def fence_for(code_):
    n = 3
    for m in re.finditer(r'`{3,}', code_):
        n = max(n, len(m.group(0)) + 1)
    return '`' * n


def serialize(node):
    if isinstance(node, str):
        return html_escape(node, quote=False)
    attrs = ''.join(f' {k}="{html_escape(v, quote=True)}"' for k, v in node.attrs.items() if v is not None)
    if node.tag in VOID:
        return f'<{node.tag}{attrs}/>'
    return f'<{node.tag}{attrs}>' + ''.join(serialize(c) for c in node.children) + f'</{node.tag}>'


class Md:
    def __init__(self):
        self.merged_tables = 0
        self.raw_blocks = 0
        self.dropped = []

    # inline ----------------------------------------------------------
    def inline(self, node, in_cell=False):
        if isinstance(node, str):
            return md_text(collapse(node))
        t = node.tag
        if t in SKIP_TAGS:
            return ''
        if t == 'br':
            return '<br>' if in_cell else '  \n'
        if t == 'img':
            src = node.attrs.get('src', '')
            if not src:
                return ''
            return f"![{collapse(node.attrs.get('alt', '')).strip()}]({src})"
        if t == 'a':
            text = self.children_inline(node, in_cell).strip()
            if 'data-dropped' in node.attrs:
                self.dropped.append(node.attrs['data-dropped'])
                return f"{text or node.attrs['data-dropped']} (attachment not imported: {node.attrs['data-dropped']})"
            href = node.attrs.get('href', '')
            if not href:
                return text
            return f'[{text or href}]({href})'
        if t in ('strong', 'b'):
            return wrap_mark('**', self.children_inline(node, in_cell))
        if t in ('em', 'i'):
            return wrap_mark('*', self.children_inline(node, in_cell))
        if t in ('s', 'del', 'strike'):
            return wrap_mark('~~', self.children_inline(node, in_cell))
        if t in ('code', 'tt', 'kbd', 'samp'):
            raw = collapse(node.text()).strip()
            if not raw:
                return ''
            tick = '``' if '`' in raw else '`'
            return f'{tick}{raw}{tick}'
        if t == 'span' and node.has_class('status-macro'):
            return wrap_mark('**', collapse(node.text()))
        if t == 'span' and node.has_class('aui-icon', 'expand-control-icon'):
            return ''
        if t in RAW_TAGS:
            self.raw_blocks += 1
            return serialize(node)
        if t in BLOCK_TAGS or t in ('li', 'dt', 'dd', 'tr', 'td', 'th', 'thead', 'tbody'):
            # a block inside an inline run (rare): flatten
            return ' '.join(self.blocks(node, in_cell)).replace('\n', '<br>' if in_cell else '  \n')
        return self.children_inline(node, in_cell)

    def children_inline(self, node, in_cell=False):
        return ''.join(self.inline(c, in_cell) for c in node.children)

    # blocks ----------------------------------------------------------
    def blocks(self, node, in_cell=False, heading_shift=0):
        """A container -> list of Markdown block strings."""
        out, run = [], []

        def flush():
            s = ''.join(run).strip()
            s = re.sub(r'\n[ \t]*', '\n', s)
            if s:
                out.append(s)
            run.clear()

        for c in node.children:
            if isinstance(c, str) or (c.tag not in BLOCK_TAGS and c.tag not in ('li', 'dt', 'dd')):
                run.append(self.inline(c, in_cell))
                continue
            flush()
            out.extend(self.block(c, in_cell, heading_shift))
        flush()
        return out

    def block(self, n, in_cell=False, hs=0):
        t = n.tag
        cs = n.classes()
        if t in SKIP_TAGS:
            return []
        if t == 'p':
            s = self.children_inline(n, in_cell).strip()
            s = re.sub(r'\n[ \t]*', '\n', s)
            if n.has_class('title'):
                s = wrap_mark('**', s)
            return [s] if s else []
        if t in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = min(6, int(t[1]) + hs)
            s = collapse(self.children_inline(n, True)).strip()
            if in_cell:
                return [wrap_mark('**', s)] if s else []
            return ['#' * level + ' ' + s] if s else []
        if t in ('ul', 'ol'):
            return [self.list(n, in_cell, hs)]
        if t == 'table':
            return self.table(n, hs)
        if t == 'pre':
            return [self.pre(n, in_cell)]
        if t == 'hr':
            return ['---']
        if t == 'blockquote':
            inner = '\n\n'.join(self.blocks(n, in_cell, hs))
            return ['\n'.join('> ' + ln if ln else '>' for ln in inner.split('\n'))] if inner else []
        if t == 'dl':
            items = []
            for c in n.children:
                if isinstance(c, Node) and c.tag == 'dt':
                    items.append('- ' + wrap_mark('**', collapse(self.children_inline(c, in_cell)).strip()))
                elif isinstance(c, Node) and c.tag == 'dd':
                    body = '\n\n'.join(self.blocks(c, in_cell, hs)).replace('\n', '\n  ')
                    if items:
                        items[-1] += ': ' + body
                    else:
                        items.append('- ' + body)
            return ['\n'.join(items)] if items else []
        if t == 'details':
            summ = n.find(lambda x: x.tag == 'summary')
            rest = Node('div')
            rest.children = [c for c in n.children if c is not summ]
            head = wrap_mark('**', collapse(summ.text()).strip()) if summ is not None else ''
            return ([head] if head else []) + self.blocks(rest, in_cell, hs)
        if t == 'div':
            if 'toc-macro' in cs or 'expand-control' in cs or 'page-metadata' in cs or 'pageSection' in cs or n.attrs.get('id') in ('breadcrumb-section', 'main-header', 'footer'):
                return []
            if 'confluence-information-macro' in cs:
                kind = next((PANEL_LABELS[k] for k in PANEL_LABELS if f'confluence-information-macro-{k}' in cs), 'Note')
                title = n.find(lambda x: x.has_class('title'))
                body = n.find(lambda x: x.has_class('confluence-information-macro-body'))
                head = collapse(self.children_inline(title, True)).strip() if title is not None else ''
                inner = self.blocks(body if body is not None else n, in_cell, hs)
                if title is not None and body is None:
                    inner = [b for b in inner if b != wrap_mark('**', head)]
                lines = [f'**{kind}{": " + head if head else ""}**'] + ([] if not inner else [''] + '\n\n'.join(inner).split('\n'))
                return ['\n'.join('> ' + ln if ln else '>' for ln in lines)]
            if 'code' in cs and 'panel' in cs:
                header = n.find(lambda x: x.has_class('codeHeader'))
                pre = n.find(lambda x: x.tag == 'pre')
                out = []
                if header is not None:
                    h = collapse(header.text()).strip()
                    if h:
                        out.append(wrap_mark('**', h))
                if pre is not None:
                    out.append(self.pre(pre, in_cell, n))
                return out
            if 'panel' in cs and 'code' not in cs:
                header = n.find(lambda x: x.has_class('panelHeader'))
                content = n.find(lambda x: x.has_class('panelContent'))
                out = []
                if header is not None:
                    h = collapse(header.text()).strip()
                    if h:
                        out.append(wrap_mark('**', h))
                out.extend(self.blocks(content if content is not None else n, in_cell, hs))
                return out
            if 'expand-container' in cs:
                ctrl = n.find(lambda x: x.has_class('expand-control-text'))
                content = n.find(lambda x: x.has_class('expand-content'))
                head = collapse(ctrl.text()).strip() if ctrl is not None else ''
                out = [f'**Expand: {head}**'] if head else []
                return out + self.blocks(content if content is not None else n, in_cell, hs)
            return self.blocks(n, in_cell, hs)
        if t in RAW_TAGS:
            self.raw_blocks += 1
            return ['<!-- raw html kept by confluence-import.py -->\n' + serialize(n)]
        if t in ('li', 'dt', 'dd', 'thead', 'tbody', 'tr', 'td', 'th'):
            return self.blocks(n, in_cell, hs)
        return self.blocks(n, in_cell, hs)

    def list(self, n, in_cell, hs):
        ordered = n.tag == 'ol'
        task = n.has_class('inline-task-list')
        lines = []
        k = 0
        for c in n.children:
            if not isinstance(c, Node) or c.tag != 'li':
                continue
            k += 1
            marker = f'{k}. ' if ordered else '- '
            if task:
                marker = '- [x] ' if c.has_class('checked') else '- [ ] '
            inner = self.blocks(c, in_cell, hs)
            if not inner:
                inner = ['']
            pad = ' ' * len(marker)
            first = inner[0].replace('\n', '\n' + pad)
            lines.append(marker + first)
            for b in inner[1:]:
                sub = b.replace('\n', '\n' + pad)
                if b.lstrip().startswith(('- ', '1. ', '* ')) or re.match(r'^\d+\. ', b.lstrip()):
                    lines.append(pad + sub)           # nested list: tight
                else:
                    lines.append('')
                    lines.append(pad + sub)
        return '\n'.join(lines)

    def pre(self, n, in_cell, panel=None):
        params = n.attrs.get('data-syntaxhighlighter-params', '') or (panel.attrs.get('data-syntaxhighlighter-params', '') if panel is not None else '')
        m = re.search(r'brush:\s*([A-Za-z0-9#+_-]+)', params)
        lang = m.group(1).lower() if m else ''
        code_node = n.find(lambda x: x.tag == 'code')
        if not lang and code_node is not None:
            m = re.search(r'(?:language|lang)-([A-Za-z0-9#+_-]+)', code_node.attrs.get('class', ''))
            lang = m.group(1).lower() if m else ''
        if lang in ('none', 'plain', 'text'):
            lang = ''
        body = n.text().strip('\n')
        body = '\n'.join(ln.rstrip() for ln in body.split('\n'))
        if in_cell:
            return '`' + collapse(body).strip() + '`'
        f = fence_for(body)
        return f'{f}{lang}\n{body}\n{f}'

    def cell(self, td, hs):
        parts = self.blocks(td, True, hs)
        s = '<br>'.join(p.replace('\n', '<br>') for p in parts)
        s = re.sub(r'(<br>)+', '<br>', s).strip()
        s = s.replace('|', '\\|')
        return s

    def table(self, n, hs):
        rows = n.find_all(lambda x: x.tag == 'tr')
        # only rows of this table (not of nested tables)
        def owner(r):
            p = r.parent
            while p is not None and p.tag != 'table':
                p = p.parent
            return p
        rows = [r for r in rows if owner(r) is n]
        if not rows:
            return []
        grid, spans, merged = [], {}, False
        is_header = []
        for r in rows:
            cells = [c for c in r.children if isinstance(c, Node) and c.tag in ('td', 'th')]
            row, col = [], 0
            all_th = bool(cells) and all(c.tag == 'th' for c in cells)
            for c in cells:
                while col in spans:
                    row.append('')
                    spans[col] -= 1
                    if spans[col] == 0:
                        del spans[col]
                    col += 1
                try:
                    cs_ = max(1, int(c.attrs.get('colspan') or 1))
                    rs_ = max(1, int(c.attrs.get('rowspan') or 1))
                except ValueError:
                    cs_, rs_ = 1, 1
                row.append(self.cell(c, hs))
                row.extend([''] * (cs_ - 1))
                if cs_ > 1 or rs_ > 1:
                    merged = True
                if rs_ > 1:
                    for k in range(col, col + cs_):
                        spans[k] = rs_ - 1
                col += cs_
            while spans and col <= max(spans):
                row.append('')
                if col in spans:
                    spans[col] -= 1
                    if spans[col] == 0:
                        del spans[col]
                col += 1
            grid.append(row)
            is_header.append(all_th)
        width = max(len(r) for r in grid)
        grid = [r + [''] * (width - len(r)) for r in grid]
        lines = []
        if is_header[0]:
            header, body = grid[0], grid[1:]
        else:
            header, body = [''] * width, grid
        lines.append('| ' + ' | '.join(header) + ' |')
        lines.append('|' + '---|' * width)
        for r in body:
            lines.append('| ' + ' | '.join(r) + ' |')
        out = ['\n'.join(lines)]
        if merged:
            self.merged_tables += 1
            out[0] = '<!-- merged cells flattened by confluence-import.py -->\n' + out[0]
        return out


# ---------------------------------------------------------------- contexts (guessed target, as migration-status.py)
def load_contexts(repo):
    out = []
    for line in split_lines(read_text_or_empty(os.path.join(repo, 'contexts.yml'))):
        m = re.match(r'^\s{2}([\w-]+):\s*\{(.*)\}', line)
        if not m:
            continue
        name, body = m.group(1), m.group(2)
        sm = re.search(r'spec:\s*([A-Z][A-Z0-9]*)', body)
        fm_ = re.search(r'fe:\s*\[([^\]]*)\]', body, re.I)
        fe = [x.strip().strip('"\'') for x in fm_.group(1).split(',') if x.strip()] if fm_ else []
        out.append((name, sm.group(1) if sm else '', fe))
    return out


def guess_context(contexts, title, body):
    key = re.sub(r'[^A-Za-z0-9]', '', title).lower()
    hits = []
    for name, spec, fe in contexts:
        stem = re.sub(r's$', '', name.lower())
        by_title = stem in key or any(re.sub(r'[^A-Za-z0-9]', '', p).lower() in key for p in fe if '*' not in p)
        by_id = bool(spec) and re.search(r'\b' + re.escape(spec) + r'-\d{3}\b', body, re.I) is not None
        if by_title or by_id:
            hits.append(name)
    return ', '.join(hits)


# ---------------------------------------------------------------- page -> markdown
def build_page(page, by_path, by_id_, out_dir, args, md):
    root = page.root
    main = by_id(root, 'main-content') or by_class(root, 'wiki-content') or root.find(lambda n: n.tag == 'body') or root
    md_dir = os.path.join(out_dir, page.section) if page.section else out_dir
    r = Resolver(page, by_path, by_id_, out_dir, md_dir, not args.no_images)
    resolve_tree(main, r)
    # headings: a body that uses h1 is shifted one level down (the page title is the only h1)
    shift = 1 if main.find(lambda n: n.tag == 'h1') is not None else 0
    if args.body == 'html':
        body = serialize(main)
    else:
        body = '\n\n'.join(md.blocks(main, False, shift))
        body = re.sub(r'\n{3,}', '\n\n', body).strip()
    crumbs = page.crumbs
    parent = ''
    if crumbs:
        last_title, last_href = crumbs[-1]
        target, _ = r.link(last_href) if last_href else ('', '')
        parent = target if target and target.endswith('.md') else last_title
    fm = [f'source: Confluence {args.space}/{page.title}', f'title: {page.title}']
    if page.section:
        fm.append(f'section: {page.section}')
    if page.id:
        fm.append(f'confluence_id: {page.id}')
        if args.base_url:
            fm.append(f'url: {args.base_url.rstrip("/")}/pages/viewpage.action?pageId={page.id}')
    fm.append(f'author: {page.author or "unknown"}')
    if page.last_modified:
        fm.append(f'last_modified: {page.last_modified}')
    elif page.raw_date:
        fm.append(f'last_modified: {page.raw_date}   # unparsed export date')
    elif page.raw_date is None:
        fm.append('last_modified: unknown   # no page-metadata block in the export')
    else:
        fm.append('last_modified: unknown   # the export names no modification date')
    if crumbs:
        fm.append('path: ' + ' > '.join(c[0] for c in crumbs) + ' > ' + page.title)
    if parent:
        fm.append(f'parent: {parent}')
    if args.lang:
        fm.append(f'source_lang: {args.lang}')
    fm.append('status: imported')
    if page.done:
        fm.append(f"supersedes_done: {page.done['path']}")
        fm.append(f"supersedes_done_modified: {page.done['last_modified']}   # last_modified of the migrated copy; this export: {page.last_modified}")
    if page.assets:
        fm.append('attachments:')
        fm.extend(f'  - {pub}' for pub, _ in page.assets)
    if md.dropped:
        fm.append('attachments_not_imported: [' + ', '.join(sorted(set(md.dropped), key=sort_key)) + ']')
    fm.append(f'imported_from: {rel(args.repo, page.html)}')
    text = '---\n' + '\n'.join(fm) + '\n---\n\n# ' + page.title + '\n\n' + BANNER + '\n\n' + body + '\n'
    return text


# ---------------------------------------------------------------- inventory
def inventory_block(space, pages_by_section, done_pages, existing_readme, contexts, out_rel, n_done):
    start = f'<!-- confluence-import:inventory {space} -->'
    end = f'<!-- /confluence-import:inventory {space} -->'
    known = {}
    for line in split_lines(existing_readme):
        m = re.match(r'^\|\s*`([^`]+)`\s*\|(.*)\|\s*$', line)
        if m:
            cells = [c.strip() for c in m.group(2).split('|')]
            if len(cells) >= 6:
                known[m.group(1)] = cells[-1]
    n_all = sum(len(v) for v in pages_by_section.values())
    n_re = sum(1 for v in pages_by_section.values() for p in v if p.done)
    re_note = f' ({n_re} of them re-imported over a migrated copy)' if n_re else ''
    lines = [start, f'> Generated by `scripts/confluence-import.py` from the HTML export; edit only the **Known state** column (kept on re-import). Pages: {n_all - n_done} imported{re_note}, {n_done} already in `_done/`.', '']
    for section in sorted(pages_by_section, key=sort_key):
        pages = pages_by_section[section]
        lines.append(f'### {section or space}')
        lines.append('')
        lines.append('| Page | confluence_id | last_modified | author | Images | Guessed context | Known state |')
        lines.append('|---|---|---|---|---|---|---|')
        for p in sorted(pages, key=lambda x: sort_key(x.slug)):
            path = f'{out_rel}/{section}/{p.slug}.md' if section else f'{out_rel}/{p.slug}.md'
            lm = p.last_modified or p.raw_date or 'unknown'
            d = done_pages.get(p.id)
            if d is not None and p.done:
                lm = f'**{lm}** (re-imported, migrated copy {d["last_modified"]})'
                old = known.get(path, '')
                state = old if old.lower().startswith('re-imported') else f"re-imported, migrated copy `{d['path']}` ({d['status']} {d['migrated']})".replace('  ', ' ')
            elif d is not None:
                path = d['path']
                if not (ISO_DAY.match(p.last_modified or '') and ISO_DAY.match(d['last_modified'] or '')):
                    lm = f'{lm} (not comparable with the migrated copy, {d["last_modified"] or "unknown"})'
                state = known.get(path) or f"{d['status']} {d['migrated']}".strip()
            else:
                state = known.get(path) or 'to triage'
            ctx = guess_context(contexts, p.title, p.body_text) or '-'
            lines.append(f'| `{path}` | {p.id or "-"} | {lm} | {p.author or "unknown"} | {p.images} | {ctx} | {state} |')
        lines.append('')
    lines.append(end)
    block = '\n'.join(lines)
    if start in existing_readme and end in existing_readme:
        new = re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _m: block, existing_readme, count=1, flags=re.S)
    else:
        new = existing_readme.rstrip('\n') + f'\n\n## Imported pages (space `{space}`, generated)\n\n' + block + '\n'
    return new


# ---------------------------------------------------------------- main
def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', required=True, help='export root: one folder per section (page tree), or a single section folder')
    ap.add_argument('--space', required=True, help='Confluence space key, the folder under confluence-import/')
    ap.add_argument('--section', action='append', default=[], help='import only this section (repeatable); links to other sections are still resolved')
    ap.add_argument('--out', default='', help='default confluence-import/<SPACE>')
    ap.add_argument('--base-url', default='', help='Confluence base URL for the url header')
    ap.add_argument('--lang', default='', help='language code of the pages (source_lang header)')
    ap.add_argument('--body', choices=['md', 'html'], default='md', help='convert the body to Markdown (default) or keep it as HTML under the header')
    ap.add_argument('--no-images', action='store_true', help='do not copy images; link them where they are in the export')
    ap.add_argument('--check', action='store_true', help='write nothing; exit 1 when the quarantine differs from what the export yields')
    args = ap.parse_args()
    args.repo = repo_root(__file__)
    src = os.path.abspath(args.src)
    if not os.path.isdir(src):
        raise SystemExit(f'--src not found: {src}')
    out_dir = os.path.abspath(args.out) if args.out else os.path.join(args.repo, 'confluence-import', args.space)
    out_rel = rel(args.repo, out_dir)

    sections = discover(src)
    if not sections:
        raise SystemExit(f'no pages found under {src} (expected <Title>_<pageId>/<pageId>.html folders or <Title>_<pageId>.html files)')
    unknown = [s for s in args.section if s not in sections]
    if unknown:
        raise SystemExit(f'--section not in the export: {", ".join(unknown)} (found: {", ".join(sections)})')
    all_pages = [p for ps in sections.values() for p in ps]

    # parse every page (titles and slugs are needed for the links of every other page)
    for p in all_pages:
        p.root = parse_html(read_text_or_empty(p.html))
        p.title = page_title(p.root, p.name_title.replace('-', ' ').strip() or f'page {p.id}')
        author, editor, p.last_modified, p.raw_date = page_metadata(p.root)
        p.author = editor or author
        p.crumbs = breadcrumbs(p.root)
        p.slug = slugify(p.title)
    counts = {}
    for p in all_pages:
        counts[p.slug] = counts.get(p.slug, 0) + 1
    for p in all_pages:
        if counts[p.slug] > 1 and p.id:
            p.slug = f'{p.slug}-{p.id}'
    by_path = {os.path.normcase(os.path.normpath(p.html)): p for p in all_pages}
    by_id_ = {p.id: p for p in all_pages if p.id}

    # pages already migrated: <SPACE>/_done/**/*.md with a confluence_id header
    done_pages = {}
    done_dir = os.path.join(out_dir, '_done')
    for f in walk_files(done_dir, '*.md') if os.path.isdir(done_dir) else []:
        fm = get_fm(read_text_or_empty(f))
        cid = get_val(fm, 'confluence_id')
        if cid:
            done_pages[cid] = {'path': rel(args.repo, f), 'last_modified': get_val(fm, 'last_modified'),
                               'status': get_val(fm, 'status') or 'migrated', 'migrated': get_val(fm, 'migrated')}

    wanted = {s: ps for s, ps in sections.items() if not args.section or s in args.section}
    contexts = load_contexts(args.repo)
    generated = {}      # rel path under out_dir -> text
    assets = {}         # rel path under out_dir -> source abs path
    skipped = []
    reimported = []
    for section, pages in wanted.items():
        for p in pages:
            d = done_pages.get(p.id) if p.id else None
            if d is not None and export_newer(p, d):
                p.done = d          # written as a fresh page; the migrated copy stays untouched
                reimported.append(p)
            md = Md()
            text = build_page(p, by_path, by_id_, out_dir, args, md)
            p.body_text = text
            if md.merged_tables:
                p.notes.append(f'{md.merged_tables} table(s) with merged cells flattened')
            if md.raw_blocks:
                p.notes.append(f'{md.raw_blocks} block(s) kept as raw HTML')
            if d is not None and not p.done:
                skipped.append(p)
                continue
            relp = f'{section}/{p.slug}.md' if section else f'{p.slug}.md'
            generated[relp] = text
            for pub, s in p.assets:
                assets[pub] = s

    # README inventory
    readme_path = os.path.join(args.repo, 'confluence-import', 'README.md')
    readme_old = read_text_or_empty(readme_path)
    readme_new = inventory_block(args.space, wanted, done_pages, readme_old, contexts, out_rel, len(skipped))

    # compare with the disk: new / changed / stale
    def norm(s):
        return s.replace('\r\n', '\n')

    changed, new, same = [], [], []
    for relp, text in generated.items():
        full = os.path.join(out_dir, relp)
        if not os.path.isfile(full):
            new.append(relp)
        elif norm(read_text_or_empty(full)) != norm(text):
            changed.append(relp)
        else:
            same.append(relp)
    for pub, s in assets.items():
        full = os.path.join(out_dir, pub)
        if not os.path.isfile(full):
            new.append(pub)
        else:
            with open(full, 'rb') as a, open(s, 'rb') as b:
                (same if a.read() == b.read() else changed).append(pub)
    stale = []
    for section in wanted:
        sec_dir = os.path.join(out_dir, section) if section else out_dir
        if not os.path.isdir(sec_dir):
            continue
        for f in walk_files(sec_dir, '*.md', exclude_rel=('_done', '_attachments')):
            if not section and os.path.dirname(rel(out_dir, f)) not in ('', '.'):
                continue
            relp = rel(out_dir, f)
            if relp not in generated and get_val(get_fm(read_text_or_empty(f)), 'imported_from'):
                stale.append(relp)
    slugs_this_run = {p.slug for ps in wanted.values() for p in ps if p not in skipped}
    att_dir = os.path.join(out_dir, '_attachments')
    if os.path.isdir(att_dir):
        for f in walk_files(att_dir):
            relp = rel(out_dir, f)
            slug = relp.split('/')[1] if relp.count('/') >= 2 else ''
            stale_page = any(s.endswith(f'/{slug}.md') or s == f'{slug}.md' for s in stale)
            if relp not in assets and (slug in slugs_this_run or stale_page):
                stale.append(relp)
    readme_changed = norm(readme_old) != norm(readme_new)

    n_pages = len(generated)
    summary = (f'{args.space}: {n_pages} page(s) in {len(wanted)} section(s), {len(assets)} image(s); '
               f'{len(skipped)} already in _done/'
               + (f', {len(reimported)} re-imported over a migrated copy' if reimported else '')
               + f'; {len(new)} new, {len(changed)} changed, {len(stale)} stale'
               + (', README inventory updated' if readme_changed else ''))
    for p in skipped:
        d = done_pages[p.id]
        flag = '' if ISO_DAY.match(p.last_modified or '') and ISO_DAY.match(d['last_modified'] or '') else f" - dates not comparable ({p.last_modified or p.raw_date or 'unknown'} vs {d['last_modified'] or 'unknown'})"
        print(f"  skipped {p.section + '/' if p.section else ''}{p.slug} (migrated: {d['path']}){flag}")
    for p in reimported:
        d = p.done
        print(f"  re-imported {p.section + '/' if p.section else ''}{p.slug}, migrated copy {d['path']} ({d['last_modified']} -> {p.last_modified}): "
              f"rerun the agent on the fresh page; scripts/import-done.py replaces the copy")
    for p in [p for ps in wanted.values() for p in ps if p.notes]:
        print(f"  note {p.section + '/' if p.section else ''}{p.slug}: {'; '.join(p.notes)}")

    if args.check:
        for relp in new:
            print(f'  new: {out_rel}/{relp}')
        for relp in changed:
            print(f'  changed: {out_rel}/{relp}')
        for relp in stale:
            print(f'  stale: {out_rel}/{relp}')
        if readme_changed:
            print('  changed: confluence-import/README.md (inventory)')
        print(summary)
        return 1 if (new or changed or stale or readme_changed) else 0

    for relp, text in generated.items():
        if relp in new or relp in changed:
            write_text(os.path.join(out_dir, relp), text)
    for pub, s in assets.items():
        if pub in new or pub in changed:
            full = os.path.join(out_dir, pub)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(s, 'rb') as a, open(full, 'wb') as b:
                b.write(a.read())
    for relp in stale:
        full = os.path.join(out_dir, relp)
        os.remove(full)
        d = os.path.dirname(full)
        while d != out_dir and os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
            d = os.path.dirname(d)
    if readme_changed:
        write_text(readme_path, readme_new)
    print(summary)
    return 0


if __name__ == '__main__':
    sys.exit(main())
