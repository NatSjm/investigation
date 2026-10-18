#!/usr/bin/env python3
"""Single evidence collector of the docs repository: pulls the generated code maps and the contracts from the
backend and frontend checkouts into generated/, as one coherent snapshot, with a manifest of source commits and
file hashes. Replaces per-repository "publisher" CI jobs (one owner of publication; see ci-examples/collect-evidence.yml).

1. Resolves each source checkout to a commit (git rev-parse), its branch, remote and whether the working copy is dirty.
2. Optionally regenerates the maps in both repos (--generate runs scripts/docs/gen-all.py there).
3. Stages the collector-owned artifact sets in a temporary directory:
     generated/be/*.md (+ graph-export-be.json)      from <backend>/docs/_generated
     generated/fe/*.md (+ graph-export-fe.json)      from <frontend>/docs/_generated
     generated/openapi/backend.yaml, external/*.yaml  from the backend contract paths of <backend>/scripts/docs/docs-gen.json
     generated/asyncapi/backend.yaml                  (rest.open_api, external_contracts_dir, asyncapi; Harbor defaults otherwise)
     generated/be/db/**                               the backend's database documentation folder (db_docs.dir, default docs/db:
                                                      readme.md, schema.json, schema/tables/*.md, schema/erd/*.mmd), whoever wrote it
                                                      (a database tool plus its converter script, or gen-db-docs.py); scripts are not copied;
                                                      markdown pages get OKF frontmatter, the tool's index.md files are left to build-index
4. Validates the candidate snapshot (every map has frontmatter, every contract parses as an OpenAPI/AsyncAPI document,
   nothing empty). A failed validation publishes nothing; the previous snapshot stays.
5. Compares the candidate with the current generated/ ignoring volatile timestamps; when nothing changed it stops
   without touching a file (idempotent: a second run against unchanged inputs produces no diff).
6. Replaces each artifact set completely (files the sources no longer produce are deleted), never touching
   hand-written concepts, index.md files or the graph, and writes generated/manifest.yml.
7. With --graph also runs gen-graph.py and build-index.py so the snapshot is ready to commit.

Standard-library Python. In CI the source repositories are checked out into separate directories and passed as
--backend / --frontend; locally the sibling checkouts are used by default.
Examples:
  python3 scripts/collect-evidence.py                                   # sibling checkouts, maps as they are on disk
  python3 scripts/collect-evidence.py --generate --graph                # regenerate maps in both repos, collect, rebuild graph + indexes
  python3 scripts/collect-evidence.py --backend /ci/harbor-backend --frontend /ci/harbor-frontend --graph
  python3 scripts/collect-evidence.py --dry-run                         # report what would change, write nothing"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

from _common import repo_root, read_text, write_text, rel, posix, like, sort_key, utf8_stdout

COLLECTOR_VERSION = '1.0'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def norm(s):
    return re.sub(r'(?m)at:\s*[0-9T:\-Z.+]+', 'at: <t>', s).replace('\r', '')


def git(path, *args):
    r = subprocess.run(['git', '-C', path] + list(args), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, r.stdout


def git_info(path, name):
    if not os.path.isdir(path):
        raise SystemExit(f'{name} checkout not found: {path}')
    code, out = git(path, 'rev-parse', '--is-inside-work-tree')
    if code or out.strip() != 'true':
        return {'name': name, 'path': posix(path), 'remote': '', 'branch': '', 'commit': 'unknown', 'dirty': True}
    commit = git(path, 'rev-parse', 'HEAD')[1].strip()
    branch = git(path, 'rev-parse', '--abbrev-ref', 'HEAD')[1].strip()
    remote = git(path, 'config', '--get', 'remote.origin.url')[1].strip()
    dirty = any(l.strip() for l in git(path, 'status', '--porcelain')[1].splitlines())
    return {'name': name, 'path': posix(path), 'remote': remote, 'branch': branch, 'commit': commit, 'dirty': dirty}


def backend_contracts(backend):
    """Contract paths (relative to the backend root) from its scripts/docs/docs-gen.json; Harbor defaults when absent."""
    import json
    out = {'open_api': 'harbor-core/src/main/resources/openapi/openapi_harbor.yaml',
           'asyncapi': 'harbor-core/src/main/resources/openapi/harbor-events.yaml',
           'external_contracts_dir': 'harbor-core/src/main/resources/api', 'db_docs_dir': 'docs/db'}
    cfg = os.path.join(backend, 'scripts', 'docs', 'docs-gen.json')
    if os.path.isfile(cfg):
        with open(cfg, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        if data.get('rest', {}).get('open_api'):
            out['open_api'] = data['rest']['open_api']
        for k in ('asyncapi', 'external_contracts_dir'):
            if data.get(k):
                out[k] = data[k]
        if data.get('db_docs', {}).get('dir'):
            out['db_docs_dir'] = data['db_docs']['dir']
    return out


def with_frontmatter(text, rel_name):
    """OKF frontmatter for a page of the database documentation (tools write plain markdown)."""
    if re.match(r'^\ufeff?---\r?\n', text):
        return text
    body = text.lstrip('\ufeff')
    hm = re.search(r'(?m)^#\s+(.+?)\s*$', body)
    title = hm.group(1).strip() if hm else os.path.splitext(os.path.basename(rel_name))[0]
    desc = ''
    after = body[hm.end():] if hm else body
    for para in re.split(r'\r?\n\s*\r?\n', after):
        line = ' '.join(para.split())
        if line and not line.startswith(('#', '|', '-', '*', '```', '<')):
            desc = line[:300]
            break
    if not desc:
        desc = f'Database documentation page {title} (collected from the backend repository).'
    q = lambda s: s.replace('\\', '\\\\').replace('"', '\\"')
    return ('---\ntype: Document\ntitle: "' + q(title) + '"\ndescription: "' + q(desc) + '"\n'
            'generated:\n  by: process:db-docs\n  at: ' + datetime.now(timezone.utc).strftime('%Y-%m-%d') + '\nstatus: stable\n---\n' + body)


def main():
    utf8_stdout()
    repo = repo_root(__file__)
    parent = os.path.dirname(repo)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--backend', default=os.path.join(parent, 'backend'))
    ap.add_argument('--frontend', default=os.path.join(parent, 'frontend'))
    ap.add_argument('--generate', action='store_true')
    ap.add_argument('--graph', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    gen = os.path.join(repo, 'generated')
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    backend, frontend = os.path.abspath(a.backend), os.path.abspath(a.frontend)

    # ---------- 1. sources ----------
    sources = [git_info(backend, 'backend'), git_info(frontend, 'frontend')]
    for s in sources:
        print(f"source {s['name']:<8} {s['commit'][:7]} {s['branch']}{' (dirty working copy)' if s['dirty'] else ''}")

    # ---------- 2. optional regeneration ----------
    if a.generate:
        for s in sources:
            g = os.path.join(s['path'], 'scripts/docs/gen-all.py')
            if os.path.isfile(g):
                print(f"regenerate maps: {s['name']}")
                r = subprocess.run([sys.executable, g, '--root', s['path']], stdout=subprocess.DEVNULL)
                if r.returncode:
                    raise SystemExit(f"gen-all failed in {s['name']}")
            else:
                print(f"skip regenerate (no scripts/docs/gen-all.py): {s['name']}")

    # ---------- 3. stage ----------
    stage = tempfile.mkdtemp(prefix='harbor-collect-')
    # artifact set -> { Dir (relative, collector-owned), Source }
    sets = {
        'be': {'Dir': 'generated/be', 'Source': 'backend'},
        'fe': {'Dir': 'generated/fe', 'Source': 'frontend'},
        'openapi': {'Dir': 'generated/openapi', 'Source': 'backend'},
        'asyncapi': {'Dir': 'generated/asyncapi', 'Source': 'backend'},
        'db': {'Dir': 'generated/be/db', 'Source': 'backend'},
    }
    staged = []   # {Set, Rel, Path}

    def stage_file(set_, src, rel_name, transform=None):
        if not os.path.isfile(src):
            return
        dst = os.path.join(stage, sets[set_]['Dir'], rel_name)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if transform:
            write_text(dst, transform(read_text(src), rel_name))
        else:
            shutil.copyfile(src, dst)
        staged.append({'Set': set_, 'Rel': sets[set_]['Dir'] + '/' + rel_name, 'Path': dst})

    for set_, p in (('be', backend), ('fe', frontend)):
        d = os.path.join(p, 'docs/_generated')
        if not os.path.isdir(d):
            raise SystemExit(f'no generated maps in {posix(p)}/docs/_generated (run scripts/docs/gen-all.py there or pass --generate)')
        for f in sorted(os.listdir(d), key=str.lower):
            full = os.path.join(d, f)
            if os.path.isfile(full) and ((f.lower().endswith('.md') and f.lower() != 'index.md') or like(f, 'graph-export-*.json')):
                stage_file(set_, full, f)
        # the repository layout the generators read (layers, entry layer): gen-graph.py reads it as generated/<set>/docs-gen.json
        stage_file(set_, os.path.join(p, 'scripts', 'docs', 'docs-gen.json'), 'docs-gen.json')
    contracts = backend_contracts(backend)
    stage_file('openapi', os.path.join(backend, contracts['open_api']), 'backend.yaml')
    stage_file('asyncapi', os.path.join(backend, contracts['asyncapi']), 'backend.yaml')
    api_dir = os.path.join(backend, contracts['external_contracts_dir'])
    if os.path.isdir(api_dir):
        # one contract per external service: <service>.yaml in the folder, or api/<service>/<file>.(yaml|yml|json)
        for dp, dn, fn in os.walk(api_dir):
            dn.sort(key=str.lower)
            for f in sorted(fn, key=str.lower):
                if f.lower().endswith(('.yaml', '.yml', '.json')):
                    stage_file('openapi', os.path.join(dp, f), 'external/' + f)
    db_dir = os.path.join(backend, contracts['db_docs_dir'])
    if os.path.isdir(db_dir):
        # documentation files only (pages, schema.json, diagrams), relative paths kept (table pages link to the ER
        # diagram); the tool's own scripts (docs/db/scripts/*.py) and index.md files are not collected
        for dp, dn, fn in os.walk(db_dir):
            dn.sort(key=str.lower)
            for f in sorted(fn, key=str.lower):
                rel_name = posix(os.path.relpath(os.path.join(dp, f), db_dir))
                if f.lower() == 'index.md' or not f.lower().endswith(('.md', '.json', '.mmd', '.svg', '.png')):
                    continue
                if f.lower() == 'readme.md':
                    rel_name = rel_name[:-len(f)] + 'README.md'
                stage_file('db', os.path.join(dp, f), rel_name, with_frontmatter if f.lower().endswith('.md') else None)
    else:
        print(f"note: no database documentation folder at {posix(db_dir)} (db_docs.dir); generated/be/db not collected")

    # ---------- 4. validate the candidate ----------
    problems = []
    if not any(f['Set'] == 'be' for f in staged):
        problems.append('backend maps: nothing collected')
    if not any(f['Set'] == 'fe' for f in staged):
        problems.append('frontend maps: nothing collected')
    if not any(f['Rel'] == 'generated/openapi/backend.yaml' for f in staged):
        problems.append('contract generated/openapi/backend.yaml missing')
    for f in staged:
        t = read_text(f['Path'])
        if not t.strip():
            problems.append(f"{f['Rel']}: empty")
            continue
        if like(f['Rel'], '*.md') and not re.match(r'^---\r?\n.*?\r?\n---', t, re.S):
            problems.append(f"{f['Rel']}: no frontmatter (generated maps carry OKF frontmatter)")
        if like(f['Rel'], 'generated/openapi/backend.yaml') and not re.search(r'(?m)^openapi:\s*3', t, re.I):
            problems.append(f"{f['Rel']}: not an OpenAPI 3 document")
        if like(f['Rel'], 'generated/asyncapi/*.yaml') and not re.search(r'(?m)^asyncapi:\s*\d', t, re.I):
            problems.append(f"{f['Rel']}: not an AsyncAPI document")
        if like(f['Rel'], 'generated/openapi/external/*') and not re.search(r'(?m)^\s*"?(openapi|swagger)"?\s*:', t, re.I):
            problems.append(f"{f['Rel']}: not an OpenAPI document")
        if like(f['Rel'], '*.yaml'):
            m = re.search(r'(?m)^\s*\$ref:\s*["\']?(?!#)[^"\'\s]+', t, re.I)
            if m:
                problems.append(f"{f['Rel']}: external $ref '{m.group(0).strip()}' would not resolve inside generated/")
    if problems:
        shutil.rmtree(stage, ignore_errors=True)
        print('collect-evidence: candidate snapshot rejected, nothing published:')
        for p in problems:
            print(f'  - {p}')
        sys.exit(1)

    # ---------- 5. compare with the current snapshot ----------
    current = {}
    for set_ in sets.values():
        d = os.path.join(repo, set_['Dir'])
        if os.path.isdir(d):
            for dirpath, _, filenames in os.walk(d):
                for f in filenames:
                    if f.lower() != 'index.md':
                        full = os.path.join(dirpath, f)
                        current[rel(repo, full)] = full
    added, changed, removed = [], [], []
    for f in staged:
        if f['Rel'] not in current:
            added.append(f['Rel'])
        elif norm(read_text(current[f['Rel']])) != norm(read_text(f['Path'])):
            changed.append(f['Rel'])
    staged_rel = set(f['Rel'] for f in staged)
    for k in sorted(current, key=sort_key):
        if k not in staged_rel:
            removed.append(k)
    print(f'candidate: {len(staged)} file(s); added {len(added)}, changed {len(changed)}, removed {len(removed)}')
    for r in added:
        print(f'  + {r}')
    for r in changed:
        print(f'  ~ {r}')
    for r in removed:
        print(f'  - {r}')

    manifest_path = os.path.join(gen, 'manifest.yml')
    same_sources = False
    if os.path.isfile(manifest_path):
        old = read_text(manifest_path)
        same_sources = all(re.search(r'commit:\s*' + re.escape(s['commit']), old, re.I) for s in sources)
    if not a.force and not added and not changed and not removed and same_sources:
        shutil.rmtree(stage, ignore_errors=True)
        print('collect-evidence: no change against the current snapshot (sources unchanged) - nothing written')
        sys.exit(0)
    if a.dry_run:
        shutil.rmtree(stage, ignore_errors=True)
        print('dry run - nothing written')
        sys.exit(0)

    # ---------- 6. publish: replace the collector-owned sets, write the manifest ----------
    for set_ in sets.values():
        d = os.path.join(repo, set_['Dir'])
        if os.path.isdir(d):
            for dirpath, _, filenames in os.walk(d):
                for f in filenames:
                    if f.lower() != 'index.md':
                        os.remove(os.path.join(dirpath, f))
    for f in staged:
        dst = os.path.join(repo, f['Rel'])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(f['Path'], dst)
    shutil.rmtree(stage, ignore_errors=True)
    # generated/be and generated/fe index.md are reserved OKF files owned by build-index.py
    for p in (os.path.join(gen, 'be/index.md'), os.path.join(gen, 'fe/index.md')):
        if os.path.isfile(p):
            os.remove(p)

    sb = ['# Evidence snapshot manifest - written by scripts/collect-evidence.py; do not edit.\n',
          '# Records which source commits the collector-owned files under generated/ describe (be, fe, openapi, asyncapi, be/db).\n',
          f"collector: {{ version: '{COLLECTOR_VERSION}', at: {now} }}\n", 'sources:\n']
    for s in sources:
        sb.append(f"  {s['name']}: {{ remote: '{s['remote']}', branch: '{s['branch']}', commit: {s['commit']}, dirty: {'true' if s['dirty'] else 'false'} }}\n")
    sb.append('artifacts:\n')
    for f in sorted(staged, key=lambda f: sort_key(f['Rel'])):
        sb.append(f"  - {{ path: {f['Rel']}, source: {sets[f['Set']]['Source']}, sha256: {sha256(os.path.join(repo, f['Rel']))} }}\n")
    write_text(manifest_path, ''.join(sb))
    print(f"manifest -> generated/manifest.yml ({len(staged)} artifact(s), sources {' / '.join(s['commit'][:7] for s in sources)})")
    if any(s['dirty'] for s in sources):
        print('note: a source working copy is dirty; the manifest commit does not describe the collected files exactly (fine locally, never in CI)')

    # ---------- 7. derived artifacts ----------
    if a.graph:
        if subprocess.run([sys.executable, os.path.join(here, 'gen-graph.py')]).returncode:
            raise SystemExit('gen-graph failed')
        if subprocess.run([sys.executable, os.path.join(here, 'build-index.py')]).returncode:
            raise SystemExit('build-index failed')
    else:
        print('done - now run gen-graph.py and build-index.py (or pass --graph)')


if __name__ == '__main__':
    main()
