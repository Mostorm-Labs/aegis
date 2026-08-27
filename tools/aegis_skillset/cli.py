from __future__ import annotations
import argparse
from pathlib import Path
from .model import load_skillset, validate_skillset

def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    v = sub.add_parser('validate'); v.add_argument('root', nargs='?', default='.')
    args = p.parse_args(argv)
    errors = validate_skillset(load_skillset(Path(args.root)))
    if errors:
        for e in errors: print('INVALID:', e)
        return 1
    print('SKILLSET_VALID')
    return 0

if __name__ == '__main__': raise SystemExit(main())
