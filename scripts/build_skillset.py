#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.aegis_skillset.build import build_all, check_distributions

def main():
    import argparse
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--check',action='store_true'); g.add_argument('--write',action='store_true')
    args=p.parse_args()
    if args.write:
        result=build_all(ROOT,write=True); print(f'SKILLSET_WRITTEN {len(result.rendered)} files'); return 0
    drift=check_distributions(ROOT)
    if drift:
        for rel in drift: print('DRIFT:',rel)
        return 1
    print('SKILLSET_STATE_OK'); return 0
if __name__=='__main__': raise SystemExit(main())
