"""Capture documentary purchasing inputs; no CAD import or external side effect."""
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'hardware/v4/sourcing'
EV = ROOT / 'hardware/v4/evidence/phase5-6-sourcing'

def main():
    EV.mkdir(exist_ok=True)
    guard = EV / 'protected-before.json'
    if guard.exists():
        raise SystemExit('Entry already captured')
    previous = json.loads((EV.parent/'phase5-5-sourcing/protected-before.json').read_text(encoding='utf-8'))
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h for p,h in previous.items())
    guard.write_text(json.dumps(previous, indent=2)+'\n', encoding='utf-8')
    entry = EV/'entry-sourcing'
    entry.mkdir()
    for p in SRC.iterdir():
        if p.is_file():
            shutil.copy2(p, entry/p.name)
    for name in ['V4_HANDOVER.md','V4_BOM_REVIEW.md']:
        shutil.copy2(ROOT/'hardware/v4'/name, EV/('entry-'+name))
    rows = list(csv.DictReader((SRC/'PHASE5_5_SHOPPING_LIST.csv').open(encoding='utf-8-sig')))
    (EV/'refresh-manifest.json').write_text(json.dumps(rows,indent=2)+'\n', encoding='utf-8')
    print(f'Captured {len(previous)} protected hashes and {len(rows)} purchase rows')

if __name__ == '__main__':
    main()
