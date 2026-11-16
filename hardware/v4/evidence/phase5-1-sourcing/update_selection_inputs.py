"""One-time Phase5.1 documentary updates; no CAD operations."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[4]
out=root/'hardware/v4/sourcing'
path=out/'selections.json'
s=json.loads(path.read_text(encoding='utf-8'))
s['IC1'].update(status='OWNER_APPROVED',basis='Explicit owner Phase5.1:5xTI BQ25798RQMR; current accepted RQM footprint retained',notes='Purchase exactly5; owned BQ25792 retained as separate inventory; no substitution or architecture change')
s['R5'].update(status='SPEC_OWNER_APPROVED_MPN_PROPOSED',basis='Owner Phase5.1:10 each8.2k/13.7k/27k0805 1% at750kHz; one mutually exclusive position per PCB',notes='27k accounting anchor only; battery cell profile not selected by purchasing. Yageo exact ordering code remains procurement proposal')
for ref in ('Q3','Q8','Q9'):
    s[ref]['notes']='PMV16UN manufacturer EOL. Exact small-order supply unverified. PMV16XN and AO3400A reviewed separately; neither owner accepted or substituted'
for ref in ('TP1','TP3','TP4'):
    s[ref]['notes']='Actual exported circular drill1.00mm; copper pad2mm; beaded loop courtyard3.6mm. Vero20-313137 and Keystone5000 specify1.02mm hole; no guaranteed fit. No drilling/CAD change authorized'
for ref in ('C33','C45','C64','C65'):
    s[ref]['notes']='Manufacturer old code in production and maps to item-description family C3216X5R1V226MT****. LCSC C342620 suffixTJ00E stocked, but full manufacturer suffix equivalence and combined bias bound remain unproven; separate held candidate'
s['C32']['notes']='Manufacturer Yageo9March2023 curve captured:about0.5-0.6uF typical at18V; illustrative0.38uF after tolerance/temp/assumed aging. Input-network Ceff/ripple justification incomplete; HOLD selection. See PHASE5_1_COMPATIBILITY_REVIEW.md'
for ref in ('C35','C36'):
    s[ref]['notes']='Murata12/2020 manufacturer curve captured:roughly12-14uF typical at3.3V; explicit illustrative bias/tol/temp/aging/AC screen4.7124uF. C35 existing2.2uF floor supported for prototype under assumptions, not guaranteed combined bound; C36 remains nominal22uF bulk. Exact proposal awaits owner acceptance'
path.write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
path=out/'harness_inputs.json'
h=json.loads(path.read_text(encoding='utf-8'))
for r in h:
    if r['item_id']=='B01':
        r['mpn']='2S/3S/4S matched cells and matching BMS; final pack configuration not selected'
        r['notes']='Match series cell count, chemistry/CV, balancing, continuous/peak load and charge current, temperature and wiring. No cells/BMS ordered; accepted exceptional disconnection may reset SYS; no added protection proposal'
    if r['item_id']=='B03':
        r['notes']='Match R5 option and programmed cell count/chemistry/CV/current/temp to approved cells/BMS/pack. 3S firmware profile deferred; no firmware edits. F0/F5 is output population, not battery profile'
    if r['item_id']=='H04':
        r['notes']='Natural/keyB3pos;1=PGND2=empty3=5V. Purchase for all5F5 even if initial physical assembly uses F0'
    if r['item_id']=='H05':
        r['spare_qty']=10
        r['notes']='Tin female20-22AWG;40 minimum contacts for20 two-wire power harnesses;10 trial/rework spares; never populate centre3pos cavity'
    if r['item_id']=='H08':
        r['spare_qty']=10
        r['notes']='Tin female28-22AWG;40 minimum for5x(6J4+2J6);10 rework spares; supplier MOQ100 excess50 separated'
path.write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8')
print('Updated selected identities/status and five-board harness allowances; no CAD')
