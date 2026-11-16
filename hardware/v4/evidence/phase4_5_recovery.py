"""Read-only saved via inspection where installed Konnect has no via reader/editor.

Never writes CAD. Emits a precise native-selection recovery manifest.
"""
from pathlib import Path
import json, re, sys

root = Path(__file__).resolve().parent
text = (root.parent / 'ups_v4/ups12v_v4.kicad_pcb').read_text(encoding='utf-8')
vias = []
for start in re.finditer(r'\(via\s', text):
    depth, quoted, escaped, end = 0, False, False, start.start()
    for end in range(start.start(), len(text)):
        c = text[end]
        if escaped:
            escaped = False
            continue
        if c == '\\' and quoted:
            escaped = True
        elif c == '"':
            quoted = not quoted
        elif not quoted:
            depth += (c == '(') - (c == ')')
            if depth == 0:
                break
    block = text[start.start():end + 1]
    at = re.search(r'\(at\s+([\d.eE+-]+)\s+([\d.eE+-]+)', block)
    uid = re.search(r'\(uuid\s+"?([\da-f-]+)', block)
    if at and uid:
        x, y = map(float, at.groups())
        wanted = ((x == 62.7 and 64.7 <= y <= 67) or x == 57.25) if '--six' in sys.argv else (58.9 <= x <= 61.1 and 64.9 <= y <= 67.0)
        if wanted:
            vias.append({'uuid': uid[1], 'x': x, 'y': y})
assert len(vias) == (6 if '--six' in sys.argv else 16), vias
(root / 'phase4-5-native-recovery.json').write_text(json.dumps({'source': 'saved PCB read-only; Konnect lacks via reader/editor', 'remove_trial_vias': vias}, indent=2) + '\n', encoding='utf-8')
print(json.dumps(vias))
