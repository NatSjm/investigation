"""Tables from the Flyway SQL migrations, shared by gen-db-docs.py and gen-db-schema.py. Regex over the DDL, no database.
Read, in version order: CREATE TABLE (plain, schema-qualified or quoted names, column constraints, table constraints,
the PostgreSQL multi-word types), ALTER TABLE with several actions per statement (ADD [COLUMN], ADD [CONSTRAINT]
FOREIGN KEY | PRIMARY KEY | UNIQUE | CHECK, DROP [COLUMN], DROP CONSTRAINT, RENAME [COLUMN], ALTER COLUMN ... TYPE |
SET|DROP NOT NULL | SET|DROP DEFAULT), DROP TABLE, COMMENT ON TABLE|COLUMN. Comments (-- and /* */), string literals and
dollar quotes are honoured when statements and column lists are split. A schema prefix is dropped (public.x -> x); names
are lower-cased. Types and constraints are indicative."""
import os
import re

from _common import read_text, source_files, posix, rel_path

IDENT = r'(?:"[^"]+"|[\w$]+)(?:\s*\.\s*(?:"[^"]+"|[\w$]+))*'          # name | schema.name | "Schema"."Name"
TYPE = (r'(?:(?:timestamp|time)(?:\s*\(\s*\d+\s*\))?\s+(?:with|without)\s+time\s+zone|'
        r'(?:double\s+precision|character\s+varying|bit\s+varying|[\w$]+)(?:\s*\([^)]*\))?)'
        r'(?:\s*\[\s*\d*\s*\])*')                                        # text, varchar(64), numeric(18, 2), text[], double precision
SIZE_RX = re.compile(r'^(.*?)\s*\(\s*(\d+)(?:\s*,\s*(\d+))?\s*\)((?:\s*\[\s*\d*\s*\])*)$', re.S)
CONSTRAINT_RX = re.compile(r'^(?:CONSTRAINT\s+(' + IDENT + r')\s+)?(PRIMARY\s+KEY|UNIQUE|FOREIGN\s+KEY|CHECK|EXCLUDE)\b\s*(.*)$', re.I | re.S)
COLUMN_RX = re.compile(r'^(' + IDENT + r')\s+(' + TYPE + r')(.*)$', re.I | re.S)
FK_RX = re.compile(r'^\(([^)]*)\)\s*REFERENCES\s+(' + IDENT + r')\s*(?:\(([^)]*)\))?', re.I | re.S)
REF_RX = re.compile(r'\bREFERENCES\s+(' + IDENT + r')\s*(?:\(([^)]*)\))?', re.I)
DEFAULT_RX = re.compile(r"\bDEFAULT\s+((?:'(?:[^']|'')*'|[\w$:.\-]+(?:\s*\([^)]*\))?))", re.I)


def version_key(path):
    """Flyway order: V<version>__ files by their numeric version parts, everything else (R__) after them, by name."""
    name = os.path.basename(path)
    m = re.match(r'^V(\d+(?:[._]\d+)*)__', name)
    if m:
        parts = [int(x) for x in re.split(r'[._]', m.group(1))]
        if len(parts) == 1:
            parts.append(0)
        return (tuple(parts), name)
    return ((9999, 0), name)


def _dollar_tag(text, i):
    m = re.match(r'\$(\w*)\$', text[i:])
    return m.group(0) if m else ''


def strip_comments(sql):
    """-- and /* */ comments (nested) removed; string literals and dollar-quoted bodies kept as they are."""
    out, i, n = [], 0, len(sql)
    while i < n:
        ch = sql[i]
        if ch == '-' and sql.startswith('--', i):
            j = sql.find('\n', i)
            i = n if j < 0 else j
        elif ch == '/' and sql.startswith('/*', i):
            depth, i = 1, i + 2
            while i < n and depth:
                if sql.startswith('/*', i):
                    depth, i = depth + 1, i + 2
                elif sql.startswith('*/', i):
                    depth, i = depth - 1, i + 2
                else:
                    i += 1
            out.append(' ')
        elif ch == "'":
            j = i + 1
            while j < n:
                if sql[j] == "'":
                    if sql.startswith("''", j):
                        j += 2
                        continue
                    break
                j += 1
            out.append(sql[i:j + 1])
            i = j + 1
        elif ch == '$' and _dollar_tag(sql, i):
            tag = _dollar_tag(sql, i)
            j = sql.find(tag, i + len(tag))
            j = n if j < 0 else j + len(tag)
            out.append(sql[i:j])
            i = j
        else:
            out.append(ch)
            i += 1
    return ''.join(out)


def split_top(text, sep):
    """Split on `sep` at parenthesis depth 0, outside quotes and dollar quotes; parts stripped, empty parts dropped."""
    parts, cur, depth, i, n = [], [], 0, 0, len(text)
    while i < n:
        ch = text[i]
        if ch in ('"', "'"):
            j = i + 1
            while j < n and text[j] != ch:
                j += 1
            cur.append(text[i:j + 1])
            i = j + 1
            continue
        if ch == '$' and _dollar_tag(text, i):
            tag = _dollar_tag(text, i)
            j = text.find(tag, i + len(tag))
            j = n if j < 0 else j + len(tag)
            cur.append(text[i:j])
            i = j
            continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == sep and depth == 0:
            parts.append(''.join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    parts.append(''.join(cur))
    return [p.strip() for p in parts if p.strip()]


def name_parts(ident):
    """`"Public"."Summary_Periods"` -> ['public', 'summary_periods']; quotes removed, lower-cased."""
    return [p.strip().strip('"').lower() for p in re.split(r'\s*\.\s*', ident.strip()) if p.strip()]


def table_name(ident):
    return name_parts(ident)[-1]


def name_list(text):
    return [table_name(x) for x in split_top(text, ',')]


def parse_type(t):
    """'numeric(18, 2)' -> ('numeric', 18, 2); 'character varying(64)' -> ('character varying', 64, 0); 'text[]' -> ('text[]', 0, 0)."""
    t = re.sub(r'\s+', ' ', t.strip().lower())
    m = SIZE_RX.match(t)
    if not m:
        return t, 0, 0
    return m.group(1).strip() + re.sub(r'\s+', '', m.group(4) or ''), int(m.group(2)), int(m.group(3) or 0)


def new_table(source):
    return {'columns': [], 'source': source, 'comment': '', 'checks': [], 'uniques': [], 'foreignKeys': []}


def column_of(t, name):
    for col in t['columns']:
        if col['name'] == name:
            return col
    return None


def add_foreign_key(t, columns, ref_ident, parent_columns, constraint):
    fk = {'table': table_name(ref_ident), 'columns': columns,
          'parentColumns': name_list(parent_columns) if parent_columns else ['id'], 'constraint': constraint.lower()}
    t['foreignKeys'].append(fk)
    for c in columns:
        col = column_of(t, c)
        if col is not None:
            col['references'] = {'table': fk['table'], 'columns': fk['parentColumns'], 'constraint': fk['constraint']}


def add_column(t, definition, added_in=''):
    """One column definition `name type [constraints]` appended to the table; inline REFERENCES / UNIQUE / CHECK recorded."""
    m = COLUMN_RX.match(definition)
    if not m:
        return None
    typ, size, digits = parse_type(m.group(2))
    rest = m.group(3)
    pk = bool(re.search(r'\bPRIMARY\s+KEY\b', rest, re.I))
    col = {'name': table_name(m.group(1)), 'type': typ, 'size': size, 'digits': digits,
           'nullable': not re.search(r'\bNOT\s+NULL\b', rest, re.I) and not pk, 'primaryKey': pk, 'default': None,
           'autoUpdated': typ in ('serial', 'bigserial', 'smallserial') or bool(re.search(r'\bGENERATED\s+(?:ALWAYS|BY\s+DEFAULT)\b', rest, re.I)),
           'comment': '', 'position': len(t['columns'])}
    if added_in:
        col['addedIn'] = added_in
    dm = DEFAULT_RX.search(rest)
    if dm:
        col['default'] = dm.group(1)
    t['columns'].append(col)
    rm = REF_RX.search(rest)
    if rm:
        add_foreign_key(t, [col['name']], rm.group(1), rm.group(2), '')
    if re.search(r'\bUNIQUE\b', rest, re.I) and not pk:
        t['uniques'].append({'name': '', 'columns': [col['name']]})
    cm = re.search(r'\bCHECK\s*(\(.*\))', rest, re.I | re.S)
    if cm:
        t['checks'].append({'name': '', 'expression': re.sub(r'\s+', ' ', cm.group(1)).strip()})
    return col


def add_constraint(t, name, kind, rest):
    """A table constraint (CREATE TABLE body or ALTER TABLE ADD): PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK; EXCLUDE ignored."""
    name = table_name(name) if name else ''
    kind = re.sub(r'\s+', ' ', kind.upper())
    if kind == 'PRIMARY KEY':
        pm = re.match(r'^\(([^)]*)\)', rest)
        for c in name_list(pm.group(1)) if pm else []:
            col = column_of(t, c)
            if col is not None:
                col['primaryKey'], col['nullable'] = True, False
    elif kind == 'FOREIGN KEY':
        fm = FK_RX.match(rest)
        if fm:
            add_foreign_key(t, name_list(fm.group(1)), fm.group(2), fm.group(3), name)
    elif kind == 'UNIQUE':
        um = re.match(r'^(?:NULLS\s+(?:NOT\s+)?DISTINCT\s+)?\(([^)]*)\)', rest, re.I)
        if um:
            t['uniques'].append({'name': name, 'columns': name_list(um.group(1))})
    elif kind == 'CHECK':
        t['checks'].append({'name': name, 'expression': re.sub(r'\s+', ' ', rest).strip()})


def add_definition(t, part):
    """One top-level part of a CREATE TABLE body or one ALTER TABLE ADD action (without the ADD): column or constraint."""
    cm = CONSTRAINT_RX.match(part)
    if cm:
        add_constraint(t, cm.group(1), cm.group(2), cm.group(3))
        return
    if not re.match(r'^LIKE\b', part, re.I):
        add_column(t, part)


def drop_column(t, name):
    t['columns'] = [c for c in t['columns'] if c['name'] != name]
    t['foreignKeys'] = [f for f in t['foreignKeys'] if name not in f['columns']]
    t['uniques'] = [u for u in t['uniques'] if name not in u['columns']]


def rename_column(t, old, new):
    col = column_of(t, old)
    if col is not None:
        col['name'] = new
    for f in t['foreignKeys']:
        f['columns'] = [new if c == old else c for c in f['columns']]
    for u in t['uniques']:
        u['columns'] = [new if c == old else c for c in u['columns']]


def drop_constraint(t, name):
    dropped = [f for f in t['foreignKeys'] if f['constraint'] == name]
    t['foreignKeys'] = [f for f in t['foreignKeys'] if f['constraint'] != name]
    for f in dropped:
        for c in f['columns']:
            col = column_of(t, c)
            if col is not None and col.get('references', {}).get('constraint') == name:
                del col['references']
    t['uniques'] = [u for u in t['uniques'] if u['name'] != name]
    t['checks'] = [c for c in t['checks'] if c['name'] != name]


def apply_alter(tables, tn, actions, rel):
    t = tables.get(tn)
    if t is None:
        return
    for act in actions:
        m = re.match(r'^ADD\s+(?:COLUMN\s+)?(?:IF\s+NOT\s+EXISTS\s+)?(.*)$', act, re.I | re.S)
        if m:
            body = m.group(1)
            if CONSTRAINT_RX.match(body):
                add_definition(t, body)
            else:
                add_column(t, body, rel)
            continue
        m = re.match(r'^DROP\s+CONSTRAINT\s+(?:IF\s+EXISTS\s+)?(' + IDENT + ')', act, re.I)
        if m:
            drop_constraint(t, table_name(m.group(1)))
            continue
        m = re.match(r'^DROP\s+(?:COLUMN\s+)?(?:IF\s+EXISTS\s+)?(' + IDENT + ')', act, re.I)
        if m:
            drop_column(t, table_name(m.group(1)))
            continue
        m = re.match(r'^RENAME\s+(?:COLUMN\s+)?(' + IDENT + r')\s+TO\s+(' + IDENT + ')', act, re.I)
        if m:
            rename_column(t, table_name(m.group(1)), table_name(m.group(2)))
            continue
        m = re.match(r'^RENAME\s+TO\s+(' + IDENT + ')', act, re.I)
        if m:
            new = table_name(m.group(1))
            tables[new] = tables.pop(tn)
            for other in tables.values():
                for f in other['foreignKeys']:
                    if f['table'] == tn:
                        f['table'] = new
                for c in other['columns']:
                    if c.get('references', {}).get('table') == tn:
                        c['references']['table'] = new
            tn, t = new, tables[new]
            continue
        m = re.match(r'^ALTER\s+(?:COLUMN\s+)?(' + IDENT + r')\s+(.*)$', act, re.I | re.S)
        if m:
            col = column_of(t, table_name(m.group(1)))
            change = m.group(2).strip()
            if col is None:
                continue
            tm = re.match(r'^(?:SET\s+DATA\s+)?TYPE\s+(' + TYPE + ')', change, re.I)
            if tm:
                col['type'], col['size'], col['digits'] = parse_type(tm.group(1))
            elif re.match(r'^SET\s+NOT\s+NULL\b', change, re.I):
                col['nullable'] = False
            elif re.match(r'^DROP\s+NOT\s+NULL\b', change, re.I):
                col['nullable'] = not col['primaryKey']
            elif re.match(r'^DROP\s+DEFAULT\b', change, re.I):
                col['default'] = None
            else:
                dm = re.match(r'^SET\s+' + DEFAULT_RX.pattern, change, re.I)
                if dm:
                    col['default'] = dm.group(1)


def parse_statement(tables, stmt, rel):
    stmt = stmt.strip()
    m = re.match(r'^CREATE\s+(?:(?:GLOBAL|LOCAL)\s+)?(?:(?:TEMP|TEMPORARY|UNLOGGED)\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(' + IDENT + r')\s*\((.*)$', stmt, re.I | re.S)
    if m:
        # the body ends at the parenthesis matching the one after the name; WITH (...) / PARTITION BY / TABLESPACE follow it
        body, depth = m.group(2), 1
        for i, ch in enumerate(body):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    body = body[:i]
                    break
        t = new_table(rel)
        for part in split_top(body, ','):
            add_definition(t, re.sub(r'\s+', ' ', part))
        tables[table_name(m.group(1))] = t
        return
    m = re.match(r'^ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:ONLY\s+)?(' + IDENT + r')\s+(.*)$', stmt, re.I | re.S)
    if m:
        apply_alter(tables, table_name(m.group(1)), [re.sub(r'\s+', ' ', a) for a in split_top(m.group(2), ',')], rel)
        return
    m = re.match(r'^DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?(.*?)(?:\s+(?:CASCADE|RESTRICT))?$', stmt, re.I | re.S)
    if m:
        for tn in name_list(m.group(1)):
            tables.pop(tn, None)
        return
    m = re.match(r"^COMMENT\s+ON\s+TABLE\s+(" + IDENT + r")\s+IS\s+(?:'((?:[^']|'')*)'|NULL)", stmt, re.I | re.S)
    if m:
        t = tables.get(table_name(m.group(1)))
        if t is not None:
            t['comment'] = (m.group(2) or '').replace("''", "'").strip()
        return
    m = re.match(r"^COMMENT\s+ON\s+COLUMN\s+(" + IDENT + r")\s+IS\s+(?:'((?:[^']|'')*)'|NULL)", stmt, re.I | re.S)
    if m:
        parts = name_parts(m.group(1))
        if len(parts) >= 2:
            col = column_of(tables.get(parts[-2], new_table('')), parts[-1])
            if col is not None:
                col['comment'] = (m.group(2) or '').replace("''", "'").strip()


def migration_files(root, mig):
    return sorted((f for f in source_files(root, mig['file_patterns']) if re.search(re.escape(mig['dir_pattern']), posix(f), re.I)),
                  key=version_key)


def parse_migrations(root, mig):
    """name -> {'columns': [col], 'source', 'comment', 'checks', 'uniques', 'foreignKeys'} in version order of the migrations.
    col: name, type, size, digits, nullable, primaryKey, default, autoUpdated, comment, position (+ references, addedIn)."""
    tables = {}
    for f in migration_files(root, mig):
        rel = rel_path(root, f)
        for stmt in split_top(strip_comments(read_text(f)), ';'):
            parse_statement(tables, stmt, rel)
    for t in tables.values():
        for i, col in enumerate(t['columns']):
            col['position'] = i
    return tables


def relations(tables):
    """parents / children per table from the foreign keys (one entry per constraint, composite keys stay together)."""
    parents = {tn: [] for tn in tables}
    children = {tn: [] for tn in tables}
    for tn, t in tables.items():
        for fk in t['foreignKeys']:
            rel = {'table': fk['table'], 'columns': list(fk['columns']), 'parentColumns': list(fk['parentColumns']), 'constraint': fk['constraint']}
            parents[tn].append(rel)
            children.setdefault(fk['table'], []).append({'table': tn, 'columns': list(fk['columns']), 'parentColumns': list(fk['parentColumns']), 'constraint': fk['constraint']})
    return parents, children


def type_text(col):
    if col['size'] and col['digits']:
        return f"{col['type']}({col['size']}, {col['digits']})"
    if col['size']:
        return f"{col['type']}({col['size']})"
    return col['type']


def erd_word(s):
    """A Mermaid erDiagram attribute type or name: letters, digits, _ - [ ] ( ) only, so `double precision` -> double_precision."""
    s = re.sub(r'[^A-Za-z0-9_\-\[\]()]+', '_', s.strip())
    return s if re.match(r'^[A-Za-z_]', s) else '_' + s


def erd_label(columns):
    """The relationship label: a bare word for one column, quoted for a composite key (Mermaid wants one word or a string)."""
    return columns[0] if len(columns) == 1 and re.match(r'^[A-Za-z0-9_\-]+$', columns[0]) else '"' + ', '.join(columns) + '"'
