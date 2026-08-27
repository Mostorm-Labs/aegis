from __future__ import annotations
import argparse
from pathlib import Path
from .model import load_skillset, validate_skillset
from .routing import validate_routing_corpus


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('validate','routing-check'):
        sp=sub.add_parser(name); sp.add_argument('root', nargs='?', default='.')
    args=p.parse_args(argv)
    root=Path(args.root)
    errors = validate_routing_corpus(root) if args.cmd=='routing-check' else validate_skillset(load_skillset(root))
    if errors:
        for error in errors: print('INVALID:', error)
        return 1
    print('ROUTING_OK' if args.cmd=='routing-check' else 'SKILLSET_VALID')
    return 0

if __name__=='__main__': raise SystemExit(main())
