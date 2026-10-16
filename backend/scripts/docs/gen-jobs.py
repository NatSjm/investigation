#!/usr/bin/env python3
"""Scheduled jobs catalogue: every method carrying the scheduling annotation (`jobs.annotation`, default `Scheduled`)
with its trigger (cron / fixedDelay / fixedRate), the first KDoc line and file:line. Lets agents answer
"what runs when" without opening the job classes."""
import argparse
import os
import re

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
    rx = re.compile(r'(?:/\*\*(?P<doc>.*?)\*/\s*)?@' + re.escape(ann) + r'\((?P<args>[^)]*)\)\s*(?:@\w+(?:\([^)]*\))?\s*)*fun\s+(?P<fn>\w+)', re.S)

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
            rows.append((f"{cls}.{m.group('fn')}", trigger, summary, f"{rel}:{line_number(t, m.start('fn'))}"))

    sb = [header('Scheduled jobs (BE)', f'@{ann} scan')]
    sb.append(f'{len(rows)} job(s). Cron expressions are Spring 6-field (seconds first).\n\n')
    sb.append('| Job | Trigger | Summary | Location |\n|---|---|---|---|\n')
    for job, trigger, summary, loc in sorted(rows, key=lambda r: sort_key(r[0])):
        sb.append(f'| `{job}` | {trigger} | {escape_cell(summary)} | `{loc}` |\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'jobs: {len(rows)} job(s) -> {a.out}')


if __name__ == '__main__':
    main()
