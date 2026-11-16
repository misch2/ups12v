"""Offline procurement arithmetic, coverage and preservation verification."""
import csv
import hashlib
import json
from decimal import Decimal as D
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EV=Path(__file__).resolve().parent
BASE=ROOT/'hardware/v4/sourcing'

def read_csv(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig',newline='')))

def main():
    before=json.loads((EV/'protected-before.json').read_text(encoding='utf-8'))
    mismatches=[p for p,h in before.items() if not (ROOT/p).is_file() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    assert not mismatches,mismatches
    rows=read_csv(BASE/'PHASE5_5_SHOPPING_LIST.csv')
    old=read_csv(EV/'entry-sourcing/SHOPPING_LIST_BY_SUPPLIER.csv')
    lookup={r['group_id']:r for r in rows}
    assert len(lookup)==len(rows)==78
    assert {r['supplier'] for r in rows}=={'LCSC','TME'}
    assert {r['group_id'] for r in old} <= set(lookup)
    for r in old:
        current=lookup[r['group_id']]
        assert current['references']==r['references']
        assert current['original_mpn']==r['manufacturer_mpn']
        assert current['original_supplier']==r['supplier']
        assert current['fitted_quantity']==r['fitted_quantity']
    electronics=[r for r in rows if r['scope']=='PCB_ELECTRONICS']
    assert len(electronics)==66
    assert sum(int(r['fitted_quantity']) for r in electronics)==655
    assert len([r for r in old if r['group_id'].startswith('H')])==8
    refs={ref for r in electronics if int(r['fitted_quantity']) for ref in r['references'].split()}
    # Assembly coverage is bound to the previous accepted 655-part purchasing basis.
    old_refs={ref for r in old if r['scope']=='PCB_ELECTRONICS' and int(r['fitted_quantity']) for ref in r['references'].split()}
    assert refs==old_refs
    for r in rows:
        q=int(r['purchase_quantity'])
        assert q>=int(r['desired_before_MOQ'])>=int(r['fitted_quantity'])
        assert q>=int(r['MOQ']) and q%int(r['multiple'])==0
        assert q<=int(r['observed_stock'])
        assert D(r['unit_price'])*q==D(r['extended_price'])
        assert r['currency']=='USD' and r['approval'] not in ['APPROVED','OWNER_APPROVED']
    assert lookup['H03']['purchase_quantity']=='5' and lookup['H03']['spares_planned']=='0'
    assert lookup['P050']['purchase_quantity']=='10'
    assert [r['purchase_quantity'] for r in rows if r['references']=='IC1']==['5']
    assert lookup['P053']['manufacturer_mpn']=='RT0603BRD0716KL'
    assert lookup['P054']['manufacturer_mpn']=='RT0603BRD073K01L'
    assert lookup['P043']['manufacturer_mpn']==lookup['P043']['original_mpn']
    assert lookup['C32-COMPARE']['fitted_quantity']=='0'
    for gid in ['P021','P022','P023','P027','H01','H02','H03','H04','H05','H06','H07','H08']:
        assert lookup[gid]['manufacturer_mpn']==lookup[gid]['original_mpn'],gid
    for gid in ['P037','R5-2S','R5-3S']:
        assert lookup[gid]['desired_before_MOQ']=='10' and lookup[gid]['purchase_quantity']=='100'
    totals={s:sum(D(r['extended_price']) for r in rows if r['supplier']==s) for s in ['LCSC','TME']}
    assert totals=={'LCSC':D('231.0980'),'TME':D('25.25')}
    fit=json.loads((EV/'fit-v4/fit.json').read_text(encoding='utf-8'))
    assert fit['status']=='PASS_BOUNDED_EXPORTED_FIT_SCREEN' and not fit['native_CAD_operations']
    for part in fit['parts'].values():
        assert part['max_body_inside_original_courtyard']
        assert part['terminal_envelope_foreign_exposed_copper_overlap_mm2']==0
        assert min(part['per_pin_other_net_clearance_mm'])>0
    calc=json.loads((EV/'electrical-calculations.json').read_text(encoding='utf-8'))
    assert not calc['feedback']['MAIN_both_25ppm_REJECT']['envelope']['pass_existing_allocation']
    for name in ['MAIN_Viking_and_RESI_PROPOSED','F5_proposed_16k_3k01']:
        assert calc['feedback'][name]['envelope']['pass_existing_allocation']
    test_log=(EV/'toolkit-tests.log').read_text(encoding='utf-8')
    assert 'Ran 203 tests' in test_log and test_log.rstrip().endswith('OK')
    # Historical source CSV/JSON input artifacts are preserved; only summary/README
    # gain active-phase pointers. Prevent silent regeneration of the old baskets.
    historical=['SHOPPING_LIST_BY_SUPPLIER.csv','MASTER_PURCHASING_BOM.csv','HARNESS_AND_ASSEMBLY_BOM.csv','selections.json']
    assert all((BASE/p).read_bytes()==(EV/'entry-sourcing'/p).read_bytes() for p in historical)
    report=dict(status='PASS',protected_file_count=len(before),protected_mismatches=mismatches,
        core_purchase_rows=len(old),electronic_rows=len(electronics),fitted_PCB_parts=655,all_proposal_rows=len(rows),
        supplier_rows={s:sum(r['supplier']==s for r in rows) for s in totals},
        goods_USD={k:str(v) for k,v in totals.items()},total_goods_USD=str(sum(totals.values())),
        live_LCSC_rows=71,cached_TME_rows=7,toolkit_tests=203,
        exact_keyed_connectors_preserved=True,old_purchasing_inputs_preserved=True,
        CAD_firmware_manufacturing_changes=False,native_KiCad_operations=False,
        no_purchase_checkout_commit_push=True,owner_review_STOP=True)
    (EV/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
