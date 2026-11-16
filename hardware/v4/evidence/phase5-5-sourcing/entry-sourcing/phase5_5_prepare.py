"""Read-only entry capture for Phase 5.5. Never imports CAD APIs."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / 'hardware/v4/evidence/phase5-5-sourcing'

def main():
    EV.mkdir(exist_ok=True)
    target = EV / 'protected-before.json'
    if target.exists():
        raise SystemExit('Entry already captured; do not overwrite')
    previous = json.loads((EV.parent / 'phase5-4-sourcing/protected-before.json').read_text(encoding='utf-8-sig'))
    protected = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in previous}
    protected['.codex/config.toml'] = hashlib.sha256((ROOT / '.codex/config.toml').read_bytes()).hexdigest()
    target.write_text(json.dumps(protected, indent=2) + '\n')
    dest = EV / 'entry-sourcing'
    shutil.copytree(ROOT / 'hardware/v4/sourcing', dest)
    for name in ('V4_BOM_REVIEW.md', 'V4_HANDOVER.md'):
        shutil.copy2(ROOT / 'hardware/v4' / name, EV / ('entry-' + name))
    print(f'Captured {len(protected)} protected hashes and sourcing entry')

if __name__ == '__main__':
    main()
