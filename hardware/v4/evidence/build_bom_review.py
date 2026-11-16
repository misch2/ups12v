"""Rebuild the exported CAD inventory portion of V4_BOM_REVIEW.md only.

Manual review decisions live above the marker and survive regeneration.
No KiCad source is modified. Run with the fresh stage XML path as the argument.
"""
from collections import defaultdict
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
target = HERE.parent / 'V4_BOM_REVIEW.md'
marker = '<!-- EXPORTED CAD INVENTORY -->'
text = target.read_text(encoding='utf-8')
assert marker in text
source = Path(sys.argv[1])
groups = defaultdict(list)
for c in ET.parse(source).findall('./components/comp'):
    fields = {f.attrib['name']: f.text or '' for f in c.findall('./fields/field')}
    key = (c.findtext('value', ''), c.findtext('footprint', ''),
           fields.get('Manufacturer', fields.get('Manufacturer_Name', 'UNVERIFIED')),
           fields.get('MPN', fields.get('Manufacturer_Part_Number', 'OPEN')),
           fields.get('Source', ''), fields.get('LCSC Part', ''),
           fields.get('PopulationGroup', ''), fields.get('DNPReason', ''),
           fields.get('Bought', ''), fields.get('Parameters', ''))
    groups[key].append(c.attrib['ref'])


def clean(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


lines = [marker, '', 'Inventory source: `' + source.name + '`.', '',
         'Quantities below count schematic instances per PCB, not fitted quantities. Apply the explicit base-profile and F0/F5 population tables above; all F5-only references are DNP in F0.', '']
for key, refs in groups.items():
    value, footprint, maker, mpn, url, lcsc, population, reason, bought, parameters = key
    lines += ['### ' + ', '.join(refs) + ' — ' + clean(value), '',
              '- Manufacturer / exact recorded MPN: ' + clean(maker) + ' / `' + clean(mpn) + '`.',
              '- Quantity: ' + str(len(refs)) + (' footprints, **0 fitted (DNP)**.' if reason else ' per assembled power stage; confirm variant below.'),
              '- Package / footprint: `' + clean(footprint or 'OPEN') + '`; package acceptance is separate from assignment.',
              '- Function / population: ' + clean(population or 'Inherited charger support; all SYS profiles unless variant review overrides') + '.',
              '- DNP: ' + clean(reason or 'No DNP reason recorded; review initial assembly BOM') + '.',
              '- Recorded source: ' + ('[existing Source](' + url + ')' if url.startswith('https://') else clean(url or 'OPEN')) + '.',
              '- Recorded LCSC field: ' + clean(lcsc or 'OPEN; see verified catalog identities above') + '.',
              '- Historical Bought / Parameters: `' + clean(bought) + '` / `' + clean(parameters) + '`.',
              '- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.',
              '- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.',
              '- Approval status: **' + ('REPLACE' if reason and mpn in ('20TQC47MYF', 'EEEFK1E470P') else 'PROPOSED') + '**; owner approval and hardware qualification are not implied.', '']
target.write_text(text.split(marker)[0] + '\n'.join(lines) + '\n', encoding='utf-8')
print(f'Updated {target} from {source}; {len(groups)} groups')
