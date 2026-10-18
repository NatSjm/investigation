#!/usr/bin/env python3
"""Scheduled jobs catalogue: every method carrying the scheduling annotation (`jobs.annotation`, default `Scheduled`)
with its trigger (cron / fixedDelay / fixedRate), the first KDoc line and file:line. Lets agents answer
"what runs when" without opening the job classes."""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, resolve_out, rel_path, line_number, header, escape_cell, first_doc_line,
                     sort_key, utf8_stdout, load_config, module_dirs, main_sources)

DEFAULTS = {'modules': [], 'source_root': 'src/main/kotlin', 'test_pattern': '', 'exclude_paths': [], 'jobs': {'annotation': 'Scheduled'}}


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/jobs.md')
    ap.add_argument('--config', default='')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    ann = cfg['jobs']['annotation']
    lock_ann = cfg['jobs'].get('lock_annotation', '')
    # KDoc, annotations before the scheduling one (a lock may come first), the scheduling annotation, annotations after it, the method
    rx = re.compile(r'(?:/\*\*(?P<doc>.*?)\*/\s*)?(?P<pre>(?:@(?!' + re.escape(ann) + r'\b)\w+(?:\([^)]*\))?\s*)*)@' + re.escape(ann)
                    + r'\((?P<args>[^)]*)\)\s*(?P<post>(?:@\w+(?:\([^)]*\))?\s*)*)fun\s+(?P<fn>\w+)', re.S)
    lock_rx = re.compile(r'@' + re.escape(lock_ann) + r'\(([^)]*)\)') if lock_ann else None

    def lock_of(anns):
        m = lock_rx.search(anns) if lock_rx else None
        if not m:
            return ''
        name = re.search(r'name\s*=\s*"([^"]*)"', m.group(1))
        most = re.search(r'lockAtMostFor\s*=\s*"([^"]*)"', m.group(1))
        return ('`' + name.group(1) + '`' if name else '(unnamed)') + (f' (at most {most.group(1)})' if most else '')

    rows = []
    for f in main_sources(root, cfg, module_dirs(root, cfg)):
        t = read_text(f)
        if not re.search(r'@' + re.escape(ann) + r'\b', t):
            continue
        rel = rel_path(root, f)
        cm = re.search(r'(?m)^\s*class\s+(\w+)', t)
        cls = cm.group(1) if cm else ''
        # class-level KDoc is the fallback summary when the scheduled method itself has none
        cd = re.search(r'(?s)/\*\*(.*?)\*/\s*(?:@\w+(?:\([^)]*\))?\s*)*class\s+\w+', t)
        class_doc = cd.group(1) if cd else ''
        for m in rx.finditer(t):
            args = m.group('args')
            c = re.search(r'cron\s*=\s*"([^"]+)"', args, re.I)
            d = re.search(r'(fixedDelay|fixedRate|initialDelay)\w*\s*=\s*([^,)]+)', args, re.I)
            if c:
                trigger = f'cron `{c.group(1)}`'
            elif d:
                trigger = f'{d.group(1)} {d.group(2).strip()}'
            else:
                trigger = args.strip()
            doc = m.group('doc') or ''
            summary = first_doc_line(doc) if doc else (first_doc_line(class_doc) if class_doc else '')
            lock = lock_of((m.group('pre') or '') + (m.group('post') or ''))
            rows.append((f"{cls}.{m.group('fn')}", trigger, lock, summary, f"{rel}:{line_number(t, m.start('fn'))}"))

    sb = [header('Scheduled jobs (BE)', f'@{ann} scan' + (f' + @{lock_ann} locks' if lock_ann else ''))]
    sb.append(f'{len(rows)} job(s). Cron expressions are Spring 6-field (seconds first).'
              + (f' Lock = `@{lock_ann}` name (one instance at a time) and its lockAtMostFor.' if lock_ann else '') + '\n\n')
    sb.append('| Job | Trigger | Lock | Summary | Location |\n|---|---|---|---|---|\n')
    for job, trigger, lock, summary, loc in sorted(rows, key=lambda r: sort_key(r[0])):
        sb.append(f'| `{job}` | {trigger} | {lock} | {escape_cell(summary)} | `{loc}` |\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'jobs: {len(rows)} job(s) -> {a.out}')


if __name__ == '__main__':
    main()
