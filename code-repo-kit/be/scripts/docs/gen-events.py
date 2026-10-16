#!/usr/bin/env python3
"""Kafka topic catalogue: consumers (listener annotation) and producers (`producer_pattern`, default `.send(topic, ...)`)
with topic names resolved from `const val` constants (the declaring file first - every listener may carry its own
`TOPIC` - then any file of any module), string literals and `${property}` placeholders looked up in
`kafka.property_files` (application.yml). `groupId` placeholders are resolved the same way. A producer wrapper whose
`.send(topic, ...)` takes the topic as a parameter is reported as "dynamic", not as a topic.
Payload column: the type of the listener method's first parameter, linked to its schema file when a file of that
name (any extension) exists under `kafka.schema_dirs` (Avro `.avsc`, JSON Schema `.json`, Kotlin event classes).
Layout keys read from docs-gen.json: kafka.listener_annotation, kafka.producer_pattern, kafka.property_files,
kafka.schema_dirs, modules, source_root, test_pattern, exclude_paths."""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header, blank_comments,
                     sort_key, utf8_stdout, load_config, module_dirs, main_sources, const_strings, load_properties,
                     resolve_string_expr)

DEFAULTS = {
    'modules': [], 'source_root': 'src/main/kotlin', 'test_pattern': '', 'exclude_paths': [],
    'kafka': {'listener_annotation': 'KafkaListener', 'producer_pattern': r'\.send\(\s*([^,)]+)', 'property_files': [], 'schema_dirs': []},
}


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
    for d in kafka.get('schema_dirs', []):
        full = os.path.join(root, d)
        if os.path.isdir(full):
            for f in source_files(full, ['*']):
                schemas.setdefault(os.path.splitext(os.path.basename(f))[0], rel_path(root, f))

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
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'events: {len(topics)} topic(s) -> {a.out}')


if __name__ == '__main__':
    main()
