#!/usr/bin/env python3
"""Kafka topic catalogue: consumers (listener annotation) and producers (`producer_pattern`, default `.send(topic, ...)`)
with topic names resolved from `const val` constants (any module, e.g. a shared kafka-client library), string
literals and `${property}` placeholders looked up in `kafka.property_files` (application.yml). A producer wrapper
whose `.send(topic, ...)` takes the topic as a parameter is reported as "dynamic", not as a topic.
Layout keys read from docs-gen.json: kafka.listener_annotation, kafka.producer_pattern, kafka.property_files,
modules, source_root, test_pattern, exclude_paths."""
import argparse
import os
import re

from _common import (read_text, write_text, resolve_out, rel_path, line_number, header, blank_comments, sort_key,
                     utf8_stdout, load_config, module_dirs, main_sources, const_strings, load_properties,
                     resolve_string_expr)

DEFAULTS = {
    'modules': [], 'source_root': 'src/main/kotlin', 'test_pattern': '', 'exclude_paths': [],
    'kafka': {'listener_annotation': 'KafkaListener', 'producer_pattern': r'\.send\(\s*([^,)]+)', 'property_files': []},
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
    consts = const_strings(files)
    props = load_properties(root, kafka['property_files'])
    listener_rx = re.compile(r'@' + re.escape(kafka['listener_annotation']) + r'\(([^)]*)\)\s*(?:@\w+(?:\([^)]*\))?\s*)*fun\s+(\w+)')
    producer_rx = re.compile(kafka['producer_pattern'])

    def resolve_topic(expr):
        e = expr.strip()
        if re.match(r'^[a-z]\w*$', e):
            return None   # a parameter or local variable: the topic is decided by the caller
        v = resolve_string_expr(e, consts, props)
        return v if v else f'<{e}>'

    topics = {}
    dynamic = []

    def add_usage(topic, kind, who):
        topics.setdefault(topic, {'consumers': [], 'producers': []})[kind].append(who)

    for f in files:
        t = read_text(f)
        if not (listener_rx.search(t) or producer_rx.search(t)):
            continue
        # comments blanked (newlines kept, so file:line stays right): KDoc examples like `.send(Topics.X, ...)` are not producers
        t = blank_comments(t)
        rel = rel_path(root, f)
        for m in listener_rx.finditer(t):
            args = m.group(1)
            tm = re.search(r'topics\s*=\s*(\[[^\]]*\]|"[^"]*"|[\w.]+)', args)
            if not tm:
                continue
            lst = tm.group(1).strip('[]').split(',')
            gm = re.search(r'groupId\s*=\s*"([^"]*)"', args)
            grp = gm.group(1) if gm else ''
            for x in lst:
                topic = resolve_topic(x)
                if topic:
                    add_usage(topic, 'consumers', f"`{m.group(2)}` ({rel}:{line_number(t, m.start())}{', group ' + grp if grp else ''})")
        for m in producer_rx.finditer(t):
            cm = re.search(r'(?s).*class\s+(\w+)', t[:m.start()])
            cls = cm.group(1) if cm else ''
            topic = resolve_topic(m.group(1) if m.groups() else '')
            if topic:
                add_usage(topic, 'producers', f'`{cls}` ({rel}:{line_number(t, m.start())})')
            else:
                dynamic.append(f'`{cls}` ({rel}:{line_number(t, m.start())})')

    sb = [header('Kafka events (BE)', f"@{kafka['listener_annotation']} / producer-call scan (kafka.producer_pattern in docs-gen.json)")]
    sb.append(f'{len(topics)} topic(s). Payload schema: open the event class named in the handler signature.\n\n')
    sb.append('| Topic | Producers (this repo) | Consumers (this repo) |\n|---|---|---|\n')
    for k in sorted(topics, key=sort_key):
        p = '<br>'.join(topics[k]['producers']) if topics[k]['producers'] else '_external_'
        c = '<br>'.join(topics[k]['consumers']) if topics[k]['consumers'] else '_external_'
        sb.append(f'| `{k}` | {p} | {c} |\n')
    if dynamic:
        sb.append('\nProducer wrappers whose topic is a parameter (the callers above name the topic): ' + ', '.join(sorted(set(dynamic), key=sort_key)) + '\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'events: {len(topics)} topic(s) -> {a.out}')


if __name__ == '__main__':
    main()
