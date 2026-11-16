"""Verify exported electrical identity after presentation-only Konnect changes."""
import hashlib
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET

here = Path(__file__).resolve().parent
source = here.parent / 'ups_v4/ups12v_v4.kicad_sch'
def read(name):
    root = ET.parse(here / name).getroot()
    assert root.tag == 'export', 'Requires true KiCad XML, not JSON/S-expression'
    components = {}
    for c in root.findall('./components/comp'):
        components[c.get('ref')] = {
            'value': c.findtext('value'), 'footprint': c.findtext('footprint'),
            'datasheet': c.findtext('datasheet'),
            'fields': {f.get('name'): f.text for f in c.findall('./fields/field')},
            'libsource': c.find('libsource').attrib,
        }
    pins = {(p.get('ref'), p.get('pin')): n.get('name')
            for n in root.findall('./nets/net') for p in n.findall('node')}
    return components, pins

before, oldpins = read('phase3-4-usb-ldo.net.xml')
after, pins = read('phase3-5-final.net.xml')
assert before == after, 'Electrical component properties changed'
assert oldpins == pins, 'Pin-to-net mapping changed'
assert pins['IC1', '2'] == pins['IC1', '3'] == pins['C7', '1'] == pins['C13', '1'] == pins['C16', '1']
assert pins['U3', '3'] == 'SYS'
assert pins['U4', '1'] == 'USB_VBUS' and pins['U4', '3'] == 'USB3V3'
assert pins['U5', '3'] == pins['U5', '5'] == 'MAIN_3V3'
assert pins['U5', '6'] == 'USB3V3' and pins['U5', '2'] == pins['U5', '7'] == 'MCU3V3'
assert pins['Q7', '1'] == 'MCU_CHG_BASE' and pins['Q7', '2'] == 'PGND'
assert pins['Q3', '3'] == pins['R9', '1'] == pins['IC1', '13'] == 'CE_N'
assert pins['R9', '2'] == pins['D3', '1'] == pins['D4', '1'] == 'CE_BIAS'
assert pins['U6', '1'] == 'MAIN_3V3' and pins['U6', '8'] == 'MCU3V3'
erc = json.loads((here/'phase3-5-final-erc.json').read_text())
assert erc['errors'] == 0 and erc['warnings'] == 6
hashfile = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
fb = [v*(1+32200*t/10000/b)+i*32200*t
      for v,t,b,i in itertools.product([.784,.816],[.999,1.001],[.999,1.001],[-.15e-6,.15e-6])]
pr = [(v+i*(8200*t*4700*b)/(8200*t+4700*b))*(8200*t+4700*b)/(4700*b)
      for v,t,b,i in itertools.product([.92,1.08],[.99,1.01],[.99,1.01],[-.1e-6,.1e-6])]
result = {
    'status': 'PASS', 'scope': 'Saved XML identity and calculations; no hardware qualification',
    'source_sha256': hashfile(source), 'components': len(after), 'exported_pins': len(pins),
    'all_component_properties_and_all_pin_nets_preserved': True,
    'charger_F01_VBUS_connectivity': 'PASS',
    'erc_errors': erc['errors'], 'erc_warnings': erc['warnings'],
    'calculations': {
        'U3_nominal_V': .8*(1+3.22), 'U3_full_temperature_static_V': [min(fb),max(fb)],
        'U3_1A_MCU_min_before_trace_ripple_V': min(fb)-.074,
        'U3_SS_typ_ms': 33e-9*.8/5.5e-6*1000,
        'U3_EN_start_typ_V':1.21*(1+100/38.3)-.7e-6*100000,
        'U3_EN_stop_typ_V':1.17*(1+100/38.3)-2.1e-6*100000,
        'U3_EN_at_SYS18V_typ_V':18*38.3/138.3+2.1e-6*(100000*38300/138300),
        'L2_ripple_18V_500kHz_nom_A':3.376/(4.7e-6*500000)*(1-3.376/18),
        'U5_PR1_nom_at_MAIN3V3_V':3.3*4.7/12.9,
        'U5_MAIN_threshold_nom_V':12.9/4.7,
        'U5_MAIN_threshold_corners_V': [min(pr),max(pr)],
        'U4_300mA_Tj_at_50C_C':50+((5.25-3.234)*.3+5.25*80e-6)*110,
        'U4_500mA_Tj_at_50C_C':50+((5.25-3.234)*.5+5.25*80e-6)*110,
    },
    'artifact_sha256': {n:hashfile(here/n) for n in ['phase3-5-final.net.xml','phase3-5-final-erc.json','phase3-5-final.pdf','phase3-5-final.png']},
}
for n in result['artifact_sha256']:
    assert (here/n).stat().st_mtime_ns >= source.stat().st_mtime_ns, n
(here/'phase3-5-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
