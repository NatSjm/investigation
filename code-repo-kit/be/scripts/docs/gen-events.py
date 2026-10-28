#!/usr/bin/env python3
"""Kafka topic catalogue: consumers (listener annotation) and producers (`producer_pattern`, default `.send(topic, ...)`)
with topic names resolved from `const val` constants (the declaring file first - every listener may carry its own
`TOPIC` - then any file of any module), string literals and `${property}` placeholders looked up in
`kafka.property_files` (application.yml). `groupId` placeholders are resolved the same way. A producer wrapper whose
`.send(topic, ...)` takes the topic as a parameter is reported as "dynamic", not as a topic.
Payload column: the type of the listener method's first parameter, linked to its schema file when a file of that
name (any extension) exists under `kafka.schema_dirs` (Avro `.avsc`, JSON Schema `.json`, Kotlin event classes).
Payload schemas section: every Avro record (`.avsc`) and JSON Schema (`.json` with `properties` or `$schema`) under
`kafka.schema_dirs` with its fields (name, type, required, doc) as the file declares them - the payload classes
generated at build are never read. The docs collector copies these files to `generated/asyncapi/schemas/` and
re-points the paths of this map there.
Layout keys read from docs-gen.json: kafka.listener_annotation, kafka.producer_pattern, kafka.property_files,
kafka.schema_dirs, modules, source_root, test_pattern, exclude_paths."""
import argparse
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header, blank_comments,
                     sort_key, utf8_stdout, load_config, module_dirs, main_sources, const_strings, load_properties,
                     resolve_string_expr)

DEFAULTS = {
    'modules': [], 'source_root': 'src/main/kotlin', 'test_pattern': '', 'exclude_paths': [],
    'kafka': {'listener_annotation': 'KafkaListener', 'producer_pattern': r'\.send\(\s*([^,)]+)', 'property_files': [], 'schema_dirs': []},
}


def avro_type(t):
    """One-line rendering of an Avro field type; a union loses its `null` member (optionality is its own column)."""
    if isinstance(t, str):
        return t
    if isinstance(t, list):
        return ' | '.join(avro_type(x) for x in t if x != 'null') or 'null'
    if isinstance(t, dict):
        k = t.get('type', '')
        if k == 'array':
            return f"array<{avro_type(t.get('items', ''))}>"
        if k == 'map':
            return f"map<{avro_type(t.get('values', ''))}>"
        if k in ('record', 'enum', 'fixed'):
            name = t.get('name', k)
            return f"{k} {name}" + (f" ({', '.join(t.get('symbols', []))})" if k == 'enum' else '')
        if t.get('logicalType'):
            return f"{k} ({t['logicalType']})"
        return str(k)
    return str(t)


def json_type(p):
    """One-line rendering of a JSON Schema property: type (+ format), `enum (a, b)`, `array<items>`, a `$ref` name."""
    if not isinstance(p, dict):
        return ''
    if '$ref' in p:
        return p['$ref'].rsplit('/', 1)[-1]
    t = p.get('type', '')
    if isinstance(t, list):
        t = ' | '.join(x for x in t if x != 'null')
    if p.get('enum'):
        return f"enum ({', '.join(str(x) for x in p['enum'])})"
    if t == 'array':
        return f"array<{json_type(p.get('items', {})) or 'any'}>"
    return f"{t} ({p['format']})" if t and p.get('format') else (t or 'any')


def parse_schema(path):
    """An Avro record (`.avsc`) or a JSON Schema object (`.json` with `properties` or `$schema`) as
    {name, kind, doc, fields: [(name, type, required, doc)]}; None for any other file (a Kotlin class, a fixture)."""
    ext = os.path.splitext(path)[1].lower()
    if ext not in ('.avsc', '.json'):
        return None
    try:
        data = json.loads(read_text(path))
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    if data.get('type') == 'record' and isinstance(data.get('fields'), list):
        fields = []
        for fd in data['fields']:
            if not isinstance(fd, dict):
                continue
            t = fd.get('type')
            optional = isinstance(t, list) and 'null' in t
            fields.append((fd.get('name', ''), avro_type(t), not optional, fd.get('doc', '')))
        return {'name': data.get('name') or os.path.splitext(os.path.basename(path))[0], 'kind': 'Avro record',
                'doc': data.get('doc', ''), 'fields': fields}
    if ext == '.json' and ('properties' in data or '$schema' in data):
        required = set(data.get('required') or [])
        fields = [(name, json_type(p), name in required, p.get('description', '') if isinstance(p, dict) else '')
                  for name, p in (data.get('properties') or {}).items()]
        return {'name': data.get('title') or os.path.splitext(os.path.basename(path))[0], 'kind': 'JSON Schema',
                'doc': data.get('description', ''), 'fields': fields}
    return None


def cell(s):
    return ' '.join(str(s).split()).replace('|', '\\|')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/events.md')
    ap.add_argument('--config', default='')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    kafka = cfg['kafka']
    files = main_sources(root, cfg, module_dirs(root, cfg))
    global_consts = const_strings(files)
    props = load_properties(root, kafka['property_files'])
    listener_rx = re.compile(r'@' + re.escape(kafka['listener_annotation']) + r'\(([^)]*)\)\s*(?:@\w+(?:\([^)]*\))?\s*)*fun\s+(\w+)\s*\(([^)]*)\)')
    producer_rx = re.compile(kafka['producer_pattern'])

    # schema files by simple name (MovementsLoaded.avsc, PricesUpdated.json, SessionClosed.kt ...)
    schemas = {}
    schema_docs = []   # (repo-relative path, parsed schema) of every Avro / JSON Schema file, folder order
    for d in kafka.get('schema_dirs', []):
        full = os.path.join(root, d)
        if os.path.isdir(full):
            for f in source_files(full, ['*']):
                schemas.setdefault(os.path.splitext(os.path.basename(f))[0], rel_path(root, f))
                parsed = parse_schema(f)
                if parsed:
                    schema_docs.append((rel_path(root, f), parsed))

    def resolve_topic(expr, local):
        e = expr.strip()
        if re.match(r'^[a-z]\w*$', e):
            return None   # a parameter or local variable: the topic is decided by the caller
        v = resolve_string_expr(e, local, props)
        if v is None or v == '' or v.startswith('<'):
            v = resolve_string_expr(e, global_consts, props)
        return v if v else f'<{e}>'

    def resolve_text(s, local):
        # Kotlin sources escape the placeholder as "\${...}"; the backslash is not part of the property name
        def sub(m):
            key, _, default = m.group(1).partition(':')
            return props.get(key) or local.get(key) or default or m.group(0)
        return re.sub(r'\\?\$\{([^}]+)\}', sub, s)

    topics = {}
    dynamic = []

    def add_usage(topic, kind, who):
        topics.setdefault(topic, {'consumers': [], 'producers': [], 'payloads': []})[kind].append(who)

    for f in files:
        t = read_text(f)
        if not (listener_rx.search(t) or producer_rx.search(t)):
            continue
        # comments blanked (newlines kept, so file:line stays right): KDoc examples like `.send(TOPIC, ...)` are not producers
        t = blank_comments(t)
        rel = rel_path(root, f)
        local = dict(global_consts)
        local.update(const_strings([f]))
        for m in listener_rx.finditer(t):
            args = m.group(1)
            tm = re.search(r'topics\s*=\s*(\[[^\]]*\]|"[^"]*"|[\w.]+)', args)
            if not tm:
                continue
            lst = tm.group(1).strip('[]').split(',')
            gm = re.search(r'groupId\s*=\s*"([^"]*)"', args)
            grp = resolve_text(gm.group(1), local) if gm else ''
            pm = re.match(r'\s*\w+\s*:\s*([\w.]+)', m.group(3))
            payload = pm.group(1).split('.')[-1] if pm else ''
            for x in lst:
                topic = resolve_topic(x, local)
                if topic:
                    add_usage(topic, 'consumers', f"`{m.group(2)}` ({rel}:{line_number(t, m.start())}{', group ' + grp if grp else ''})")
                    if payload:
                        link = schemas.get(payload)
                        topics[topic]['payloads'].append(f'`{payload}`' + (f' ({link})' if link else ''))
        for m in producer_rx.finditer(t):
            cm = re.search(r'(?s).*class\s+(\w+)', t[:m.start()])
            cls = cm.group(1) if cm else ''
            topic = resolve_topic(m.group(1) if m.groups() else '', local)
            if topic:
                add_usage(topic, 'producers', f'`{cls}` ({rel}:{line_number(t, m.start())})')
            else:
                dynamic.append(f'`{cls}` ({rel}:{line_number(t, m.start())})')

    sb = [header('Kafka events (BE)', f"@{kafka['listener_annotation']} / producer-call scan (kafka.producer_pattern in docs-gen.json)")]
    sb.append(f'{len(topics)} topic(s). Payload = the listener parameter type, with its schema file when one exists under the configured schema folders.\n\n')
    sb.append('| Topic | Producers (this repo) | Consumers (this repo) | Payload |\n|---|---|---|---|\n')
    for k in sorted(topics, key=sort_key):
        p = '<br>'.join(topics[k]['producers']) if topics[k]['producers'] else '_external_'
        c = '<br>'.join(topics[k]['consumers']) if topics[k]['consumers'] else '_external_'
        seen = []
        for x in topics[k]['payloads']:
            if x not in seen:
                seen.append(x)
        sb.append(f"| `{k}` | {p} | {c} | {', '.join(seen)} |\n")
    if dynamic:
        sb.append('\nProducer wrappers whose topic is a parameter (the callers above name the topic): ' + ', '.join(sorted(set(dynamic), key=sort_key)) + '\n')
    if schema_docs:
        sb.append('\n## Payload schemas\n\n')
        sb.append(f"{len(schema_docs)} schema file(s) under the schema folders ({', '.join('`' + d + '`' for d in kafka.get('schema_dirs', []))}); "
                  'fields as the files declare them, the payload classes generated at build are not read.\n')
        for path, s in schema_docs:
            sb.append(f"\n### `{s['name']}` - {s['kind']}, {path}\n")
            if s['doc']:
                sb.append(' '.join(s['doc'].split()) + '\n')
            sb.append('\n| Field | Type | Required | Doc |\n|---|---|---|---|\n')
            for name, typ, required, doc in s['fields']:
                sb.append(f"| `{name}` | {cell(typ)} | {'yes' if required else 'no'} | {cell(doc)} |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'events: {len(topics)} topic(s), {len(schema_docs)} schema(s) -> {a.out}')


if __name__ == '__main__':
    main()
