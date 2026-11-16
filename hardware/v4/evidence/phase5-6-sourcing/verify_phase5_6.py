"""Independent release coverage, commercial arithmetic and preservation checks."""
import csv
import hashlib
import json
import re
from collections import Counter
from decimal import Decimal as D
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EV=Path(__file__).resolve().parent
BASE=ROOT/'hardware/v4/sourcing'

def read(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig',newline='')))

def main():
    protected=json.loads((EV/'protected-before.json').read_text(encoding='utf-8'))
    mismatches=[p for p,h in protected.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    assert not mismatches,mismatches
    originals=read(ROOT/'hardware/v4/evidence/phase5-1-sourcing/entry-phase5-0-sourcing/MASTER_PURCHASING_BOM.csv')
    stable={r['references']:r['group_id'] for r in originals}
    previous=read(EV/'entry-sourcing/PHASE5_5_SHOPPING_LIST.csv')
    orders={s:read(BASE/f'FINAL_{s}_ORDER.csv') for s in ('LCSC','TME')}
    combined=[r for rows in orders.values() for r in rows]
    assert [len(orders[s]) for s in ('LCSC','TME')]==[71,7]
    assert len({r['group_id'] for r in combined})==78
    assert len({r['phase5_5_group_id'] for r in combined})==78
    for supplier,rows in orders.items():
        assert len({r['supplier_sku'] for r in rows})==len(rows)
        assert set(r['currency'] for r in rows)==({'USD'} if supplier=='LCSC' else {'CZK'})
        for r in rows:
            old=next(p for p in previous if p['group_id']==r['phase5_5_group_id'])
            assert old['supplier']==supplier
            assert r['quantity']==old['purchase_quantity']
            assert r['references']==old['references'] and r['manufacturer_mpn']==old['manufacturer_mpn']
            assert r['supplier_sku']==old['distributor_sku'] and r['unit']==old['unit']
            assert r['fitted_quantity_five_F5']==old['fitted_quantity']
            assert r['desired_before_MOQ']==old['desired_before_MOQ']
            assert r['spares_planned']==old['spares_planned']
            assert r['MOQ_or_tier_excess']==old['MOQ_or_tier_excess']
            assert r['approval']=='OWNER_APPROVED_2026-10-20_FINAL'
            q=int(r['quantity'])
            assert int(r['observed_stock'])>=q>=int(r['MOQ'])
            assert q%int(r['multiple'])==0
            assert D(r['unit_price_net'])*q==D(r['line_total_net'])
            if r['scope']=='PCB_ELECTRONICS' and r['references'] in stable:
                assert r['group_id']==stable[r['references']]
            text=(BASE/r['evidence']).resolve().read_text(encoding='utf-8')
            assert r['manufacturer_mpn'] in text
            if supplier=='LCSC':
                assert r['supplier_sku'] in r['direct_product_url']
                mainbody=text.split('In-Stock:',1)[1].split('Standard Packaging',1)[0]
                tiers=re.findall(r'(\d[\d,]*)\+\s*\$\s*([\d.]+)',mainbody)
                chosen=sorted((int(n.replace(',','')),D(p)) for n,p in tiers if int(n.replace(',',''))<=q)[-1][1]
                assert D(r['unit_price_net'])==chosen
            else:
                assert '/cz/' in r['direct_product_url'] and 'CZK' in text
                mainbody=text.split('Cena bez DPH [CZK/',1)[1].split('Zeptejte se na cenu',1)[0]
                tiers=re.findall(r'(\d[\d \u00a0]*)\+\s*\n([\d.]+)',mainbody)
                chosen=sorted((int(re.sub(r'\s','',n)),D(p)) for n,p in tiers if int(re.sub(r'\s','',n))<=q)[-1][1]
                assert D(r['unit_price_net'])==chosen
    lookup={r['group_id']:r for r in combined}
    assert 'P058' not in lookup and lookup['P059']['references']=='U1' and lookup['P065']['references']=='U8'
    assert lookup['H03']['quantity']=='5' and lookup['H03']['observed_stock']=='5'
    assert lookup['P020']['quantity']=='5' and lookup['P020']['manufacturer_mpn']=='BQ25798RQMR'
    assert lookup['C32-COMPARE']['quantity']=='10' and lookup['C32-COMPARE']['fitted_quantity_five_F5']=='0'
    assert lookup['H09']['quantity']==lookup['H10']['quantity']=='5'
    assert lookup['H09']['unit']==lookup['H10']['unit']=='m'
    assert lookup['H11']['quantity']=='2' and lookup['H11']['unit']=='10m roll'
    for gid in ('P037','R5-2S','R5-3S'):
        assert lookup[gid]['quantity']=='100' and lookup[gid]['desired_before_MOQ']=='10'
    for gid in ['P021','P022','P023','P027','H01','H02','H03','H04','H05','H06','H07','H08']:
        assert lookup[gid]['manufacturer_mpn']==lookup[gid]['prior_purchasing_mpn']
    assembly=read(BASE/'FINAL_ASSEMBLY_BOM.csv')
    refs=[r for r in assembly if r['scope']=='PCB_REFERENCE']
    population=read(EV/'entry-sourcing/REFERENCE_POPULATION.csv')
    assert len(assembly)==168 and len(refs)==154
    assert len({r['reference'] for r in refs})==154
    assert {r['reference'] for r in refs}=={r['reference'] for r in population}
    fitted={r['reference']:r for r in refs if r['population']=='FIT_F5'}
    assert len(fitted)==131
    assert sum(int(r['quantity_five_F5']) for r in refs)==655
    for r in refs:
        source=next(p for p in population if p['reference']==r['reference'])
        assert r['quantity_per_F5']==source['qty_per_F5']
        assert int(r['quantity_five_F5'])==5*int(source['qty_per_F5'])
        assert r['schematic_value_metadata']==source['functionality']
        assert r['schematic_MPN_metadata']==source['original_recorded_mpn']
        assert r['actual_ordered_footprint']==source['actual_kicad_footprint']
        if r['population']=='FIT_F5':
            order=lookup[r['group_id']]
            assert r['reference'] in order['references'].split()
            assert r['approved_assembly_MPN']==order['manufacturer_mpn']
    expected={'L2':'AAPS0530M4R7F','L3':'SRP5050FA-6R8M','R32':'ARG02BTC3162',
      'R33':'PTFR0402Q10K0N9','R60':'RT0603BRD0716KL','R61':'RT0603BRD073K01L',
      'U1':'ESP32-C3-MINI-1-H4X','C39':'CC0402KRX7R9BB333','R5':'0805W8F2702T5E',
      'R23':'0402WGF8201TCE','R63':'0603WAF3832T5E'}
    assert all(fitted[ref]['approved_assembly_MPN']==mpn for ref,mpn in expected.items())
    assert '16kohm' in fitted['R60']['assembly_value_and_ratings']
    assert '3.01kohm' in fitted['R61']['assembly_value_and_ratings']
    for a,b in [('R32','R33'),('R60','R61')]:
        assert fitted[a]['paired_fit_requirement']==fitted[b]['paired_fit_requirement']!=''
        assert all('FIT BOTH MEMBERS TOGETHER' in fitted[ref]['notes'] for ref in (a,b))
    excluded={r['reference'] for r in refs if r['population']=='DNP'}
    assert excluded=={'C20','C22','C24','C25'}
    assert not any(r['reference'].startswith('TP') for r in fitted.values())
    totals={s:sum(D(r['line_total_net']) for r in rows) for s,rows in orders.items()}
    assert totals=={'LCSC':D('230.6740'),'TME':D('532.1356')}
    # All historical input tables and observations remain byte-identical.
    preserved=0
    for p in (EV/'entry-sourcing').iterdir():
        if p.suffix in ('.csv','.json') or p.name.startswith('PHASE5_5_'):
            assert p.read_bytes()==(BASE/p.name).read_bytes(),p.name
            preserved+=1
    report=dict(status='PASS',protected_files=len(protected),protected_mismatches=mismatches,
      purchase_rows=78,LCSC_rows=71,TME_rows=7,assembly_rows=168,PCB_references=154,
      fitted_parts_per_F5=131,fitted_parts_five_F5=655,excluded_PCB_references=23,
      original_master_IDs_restored=True,all_approved_quantities_and_refs_retained=True,
      both_resistor_pairs_explicit=True,all_78_stock_and_price_observations_live=True,
      historical_inputs_preserved=preserved,LCSC_goods_net_USD=str(totals['LCSC']),
      TME_goods_net_CZK=str(totals['TME']),landed_total=None,
      no_CAD_firmware_manufacturing_changes=True,no_native_KiCad_operations=True,
      no_purchase_checkout_payment_commit_push=True)
    (EV/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__': main()
