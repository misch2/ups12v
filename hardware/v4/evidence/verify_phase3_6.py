"""Independent true-XML preservation, F5/F0 population and calculation evidence.

Reads exports only. Does not edit CAD. Engineering allocations are calculations,
not guaranteed device limits or hardware measurements.
"""
from pathlib import Path
import csv, hashlib, itertools, json, math
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
def read(name):
    root = ET.parse(HERE / name).getroot()
    assert root.tag == 'export' and root.findtext('./design/tool').startswith('Eeschema 10.0.7')
    comps = {c.get('ref'): c for c in root.findall('./components/comp')}
    pins = {(p.get('ref'), p.get('pin')): n.get('name') for n in root.findall('./nets/net') for p in n.findall('node')}
    return root, comps, pins

_, old, oldpins = read('phase3-6-entry.net.xml')
_, accepted, accepted_pins = read('phase3-5-final.net.xml')
assert oldpins == accepted_pins, 'Entry differs electrically from accepted Phase 3.5'
root, new, pins = read('phase3-6-final.net.xml')
assert all(pins[p] == net for p, net in oldpins.items()), 'Unexpected retained pin-net change'
allowed = {'R32', 'R33', 'C33', 'C45'}
for ref, c in old.items():
    n = new[ref]
    if ref not in allowed:
        for field in ['value', 'footprint', 'datasheet', 'fields', 'libsource']:
            a, b = c.find(field), n.find(field)
            assert (ET.tostring(a) if a is not None else None) == (ET.tostring(b) if b is not None else None), (ref, field)
    else:
        assert c.find('libsource').attrib == n.find('libsource').attrib
assert new['R32'].findtext('value').startswith('31k6')
assert new['R33'].findtext('value').startswith('10k')
for ref in ['C33', 'C45']:
    assert new[ref].findtext('footprint') == 'Capacitor_SMD:C_1206_3216Metric'

f5 = {'U7', 'U8', 'Q10', 'L3', 'J8'} | {f'R{i}' for i in range(60,64)} | {f'C{i}' for i in range(60,70)}
tps = {f'TP{i}' for i in range(5,18)}
assert set(new) - set(old) == f5 | tps
expected = {
    'SYS': [('U7','3'),('C60','1'),('C61','1'),('C69','1'),('R62','1')],
    'PGND': [('U7','4'),('U8','2'),('R61','2'),('R63','2'),('J8','2')] + [(f'C{i}','2') for i in [60,61,63,64,65,66,68,69]],
    'F5_EN': [('U7','2'),('R62','2'),('R63','1')],
    'F5_SS': [('U7','7'),('C63','1')],
    'F5_BST': [('U7','6'),('C62','1')],
    'F5_SW': [('U7','5'),('L3','1'),('C62','2')],
    'F5_FB': [('U7','8'),('R60','2'),('R61','1')],
    'F5_RAW': [('L3','2'),('R60','1'),('C64','1'),('C65','1'),('C66','1'),('U8','3'),('U8','6'),('C67','2')] + [('Q10',str(i)) for i in [1,2,3]],
    'F5_VCAP': [('U8','1'),('C67','1')],
    'F5_GATE': [('U8','5'),('Q10','4')],
    'F5_5V_OUT': [('U8','4'),('J8','1'),('C68','1'),('TP17','1')] + [('Q10',str(i)) for i in range(5,10)],
}
for net, entries in expected.items():
    for p in entries:
        assert pins[p].lstrip('/') == net, (p, net, pins[p])
for i, net in enumerate(['UART_TX','UART_RX','PGND','MCU3V3','MCU_EN','MCU_BOOT','MCU_SDA','MCU_SCL','MAIN_3V3','CE_N','VIN1','BATTERY','F5_5V_OUT'],5):
    assert pins[f'TP{i}','1'].lstrip('/') == net
    assert new[f'TP{i}'].findtext('footprint') == 'TestPoint:TestPoint_Pad_D1.5mm'
base_nets = {n for (r,p),n in pins.items() if r in old}
f5_nets = {n for (r,p),n in pins.items() if r in f5}
assert base_nets & f5_nets == {'SYS', 'PGND'}, 'F5 must attach to existing design only through SYS/PGND'
assert {r for r,p in pins if pins[r,p].lstrip('/') == 'F5_5V_OUT'} <= f5 | {'TP17'}
assert not {n for (r,p),n in pins.items() if r not in f5 | {'TP17'}} & {n for n in f5_nets if n.lstrip('/').startswith('F5_')}

erc = json.loads((HERE / 'phase3-6-final-erc.json').read_text())
assert erc['errors'] == 0 and erc['warnings'] == 4
assert all(v['rule'] == 'isolated_pin_label' for v in erc['violations'])

def fb(top, bottom=10000, tcr=25e-6):
    t = .001 + 125*tcr  # independently opposing drift from 25 C to 150 C
    return [v*(1+top*a/(bottom*b))+i*top*a for v,a,b,i in itertools.product([.784,.816],[1-t,1+t],[1-t,1+t],[-.15e-6,.15e-6])]
main, raw = fb(31600,tcr=10e-6), fb(53000)
main_mcu = [min(main)-.074-.020-.005-.005, max(main)+.020+.005]
f5_connector = [min(raw)-.050-.020-.030-.010, max(raw)+.020+.010]
assert 3.135 <= min(main_mcu) < max(main_mcu) <= 3.465
assert 4.75 <= min(f5_connector) < max(f5_connector) <= 5.25
fs = 450000*.94
Lmin = 6.8e-6*.8
ripple = max(raw)*(1-max(raw)/18)/(Lmin*fs)
irms = math.sqrt(4+ripple*ripple/12)
assert 2+ripple/2 < 4.2 and irms < 4.7
assert 5.8 < 6.0  # nominal room-temperature 30%-drop Isat, not hot guaranteed Isat
r_hot = .02945*(1+.00393*100)
vin_low = 6-.10-.02
hs_hot, ls_hot = .076*2, .032*2  # sensitivity, NOT datasheet maximums
duty_hot = (max(raw)+2*r_hot+2*ls_hot)/(vin_low-2*hs_hot+2*ls_hot)
dmax_typ = 7/(7+.14)
vmax_hot = dmax_typ*(vin_low-2*hs_hot+2*ls_hot)-2*ls_hot-2*r_hot
assert duty_hot < dmax_typ and vmax_hot > max(raw)
calc = {
 'basis':'Calculated provisional design; limits/allocations in phase3-6-review.md; no measurements',
 'U3_nominal_V':.8*(1+3.16), 'U3_static_full_temperature_V':[min(main),max(main)],
 'U3_MCU_1A_with_allocations_V':main_mcu,
 'U3_31k2_rejected_low_corner_MCU_V':min(fb(31200))-.074-.020-.005-.005,
 'F5_raw_nominal_V':.8*(1+5.3), 'F5_static_raw_V':[min(raw),max(raw)],
 'F5_connector_2A_with_allocations_V':f5_connector,
 'F5_ripple_pp_A':ripple, 'F5_peak_A':2+ripple/2, 'F5_rms_A':irms,
 'F5_output_ripple_pp_V_25uF_2mohm':ripple/(8*fs*25e-6)+ripple*.002,
 'F5_output_ripple_pp_V_15uF_2mohm_sensitivity':ripple/(8*fs*15e-6)+ripple*.002,
 'F5_L3_hot_DCR_125C_ohm':r_hot, 'F5_L3_DC_loss_W':irms**2*r_hot,
 'F5_hot_sensitivity_required_duty':duty_hot, 'F5_typ_extended_max_duty':dmax_typ,
 'F5_hot_sensitivity_max_raw_V_at_SYS6':vmax_hot,
 'F5_input_Ceff_uF_screen':2*10*.9*.52*.85*.9,
 'F5_input_ripple_V_screen':2/(4*fs*(2*10e-6*.9*.52*.85*.9)),
 'F5_SS_typ_ms':33e-9*.8/5.5e-6*1000,
 'F5_EN_at_SYS18V_typ_V':18*38.3/138.3+2.1e-6*(100000*38300/138300),
 'F5_blocker_worst_allocated_heat_W':2*.05,
 'F5_U7_thermal_screen_Tj_C_at50C_EVM60p2':50+.85*60.2,
 'F5_U7_thermal_screen_Tj_C_at50C_JEDEC112p2':50+.85*112.2,
}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = HERE.parent / 'ups_v4/ups12v_v4.kicad_sch'
artifacts = ['phase3-6-final.net.xml','phase3-6-final-erc.json','phase3-6-final.pdf','phase3-6-final.png']
assert all((HERE/n).stat().st_mtime_ns >= source.stat().st_mtime_ns for n in artifacts)
result = {'status':'PASS: exported schematic identity and bounded calculations; hardware unqualified',
 'source_sha256':sha(source), 'components':len(new), 'retained_pins_verified':len(oldpins),
 'all_retained_pin_nets_preserved':True, 'allowed_retained_metadata_changes':sorted(allowed),
 'F5_F0_isolation':'PASS: F5 joins base only at SYS/PGND; F0 omits all 19 fitted parts, including J8; TP17 is isolated copper',
 'F5_parts':sorted(f5), 'new_testpads':sorted(tps), 'erc_errors':0,'erc_warnings':4,
 'calculations':calc, 'artifact_sha256':{n:sha(HERE/n) for n in artifacts}}
(HERE/'phase3-6-verification.json').write_text(json.dumps(result,indent=2)+'\n')
with (HERE/'phase3-6-population.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['Reference','Value','Footprint','F0 fitted qty','F5 fitted qty','Notes'])
    for ref in sorted(f5|tps|{'R32','R33','C33','C45'}):
        c=new[ref]; copper=ref.startswith('TP')
        writer.writerow([ref,c.findtext('value'),c.findtext('footprint'),0 if ref in f5 or copper else 1,0 if copper else 1,'Copper only; no fitted part' if copper else 'F5 only' if ref in f5 else 'Common'])
print(json.dumps({'components':len(new),'retained_pins':len(oldpins),'ERC':[0,4],'MCU_V':main_mcu,'F5_connector_V':f5_connector,'F5_peak_A':2+ripple/2,'status':'PASS'}))
