#!/usr/bin/env python3
import argparse, json, difflib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.aegis_skillset.package import render_release_manifest, build_source_bundles

ROOT = Path(__file__).resolve().parents[1]; VERSION = "0.1.0-task6.1"
TARGET = ROOT / "skillset/releases/aegis-0.1.0-task6.1.json"

def main():
    p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true'); p.add_argument('--write-manifest',action='store_true'); p.add_argument('--package-dir'); a=p.parse_args()
    m=render_release_manifest(ROOT, VERSION); text=json.dumps(m,sort_keys=True,indent=2)+"\n"
    if a.write_manifest:
        TARGET.parent.mkdir(parents=True,exist_ok=True); TARGET.write_text(text,encoding='utf-8')
    if a.check:
        old=TARGET.read_text(encoding='utf-8') if TARGET.exists() else ''
        if old != text:
            print(''.join(difflib.unified_diff(old.splitlines(True), text.splitlines(True)))); return 1
        print('AEGIS_DISTRIBUTION_STATE_OK')
    if a.package_dir: build_source_bundles(ROOT, VERSION, Path(a.package_dir))
    return 0
if __name__=='__main__': raise SystemExit(main())
