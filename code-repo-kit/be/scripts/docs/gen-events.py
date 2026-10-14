#!/usr/bin/env python3
"""Kafka topic catalogue: consumers (@KafkaListener) and producers (KafkaTemplate.send) with constant resolution."""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header,
                     blank_comments, sort_key, utf8_stdout)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/events.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    files = source_files(root, ['*.kt'])
    consts = {}
    for f in files:
        for m in re.finditer(r'const\s+val\s+(\w+)\s*=\s*"([^"]+)"', read_text(f)):
            consts[m.group(1)] = m.group(2)

    def resolve_topic(expr):
        e = expr.strip()
        m = re.match(r'^"([^"]+)"$', e)
        if m:
            return m.group(1)
        name = e.split('.')[-1]
        return consts.get(name, f'<{e}>')

    topics = {}

    def add_usage(topic, kind, who):
        topics.setdefault(topic, {'consumers': [], 'producers': []})[kind].append(who)

    for f in files:
        t = read_text(f)
        if not re.search(r'KafkaListener|KafkaTemplate', t, re.I):
            continue
        # blank out comments (keeping newlines so file:line stays right) - KDoc examples like `.send(Topics.X, ...)` are not producers
        t = blank_comments(t)
        rel = rel_path(root, f)
        for m in re.finditer(r'@KafkaListener\(([^)]*)\)\s*(?:@\w+\s*)*fun\s+(\w+)', t):
            args = m.group(1)
            tm = re.search(r'topics\s*=\s*(\[[^\]]*\]|"[^"]*"|[\w.]+)', args)
            if not tm:
                continue
            lst = tm.group(1).strip('[]').split(',')
            gm = re.search(r'groupId\s*=\s*"([^"]*)"', args)
            grp = gm.group(1) if gm else ''
            for x in lst:
                add_usage(resolve_topic(x), 'consumers',
                          f"`{m.group(2)}` ({rel}:{line_number(t, m.start())}{', group ' + grp if grp else ''})")
        for m in re.finditer(r'\.send\(\s*([^,)]+)', t):
            cm = re.search(r'(?s).*class\s+(\w+)', t[:m.start()])
            cls = cm.group(1) if cm else ''
            add_usage(resolve_topic(m.group(1)), 'producers', f'`{cls}` ({rel}:{line_number(t, m.start())})')

    sb = [header('Kafka events (BE)', '@KafkaListener / KafkaTemplate.send scan')]
    sb.append(f'{len(topics)} topic(s). Payload schema: open the event class named in the handler signature.\n\n')
    sb.append('| Topic | Producers (this repo) | Consumers (this repo) |\n|---|---|---|\n')
    for k in sorted(topics, key=sort_key):
        p = '<br>'.join(topics[k]['producers']) if topics[k]['producers'] else '_external_'
        c = '<br>'.join(topics[k]['consumers']) if topics[k]['consumers'] else '_external_'
        sb.append(f'| `{k}` | {p} | {c} |\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'events: {len(topics)} topic(s) -> {a.out}')


if __name__ == '__main__':
    main()
