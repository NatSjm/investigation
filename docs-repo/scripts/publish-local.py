#!/usr/bin/env python3
"""Deprecated name. The local publish step is now the single evidence collector: scripts/collect-evidence.py
(same inputs, plus validation, deletion handling and generated/manifest.yml). This wrapper forwards to it.
Examples:
  python3 scripts/publish-local.py                                  # == python3 scripts/collect-evidence.py
  python3 scripts/publish-local.py --backend /src/harbor-backend --frontend /src/harbor-frontend"""
import argparse
import os
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--backend', default='')
    ap.add_argument('--frontend', default='')
    a = ap.parse_args()
    print('publish-local.py is deprecated: use scripts/collect-evidence.py (forwarding)')
    args = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'collect-evidence.py')]
    if a.backend:
        args += ['--backend', a.backend]
    if a.frontend:
        args += ['--frontend', a.frontend]
    sys.exit(subprocess.run(args).returncode)


if __name__ == '__main__':
    main()
