"""Independent documentary checks against reviewed populations; no KiCad imports."""
import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'hardware/v4/sourcing'
EV=Path(__file__).resolve().parent
POP=ROOT/'hardware/v4/evidence/phase4-22a-manufacturing-preparation'


def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def main():
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    assert branch=='codex/v4-phase5-component-sourcing',branch
    refs=read(OUT/'REFERENCE_POPULATION.csv')
    master=read(OUT/'MASTER_PURCHASING_BOM.csv')
    approved=read(OUT/'APPROVED_PURCHASING_BASKET.csv')
    harness=read(OUT/'HARNESS_AND_ASSEMBLY_BOM.csv')
    options=read(OUT/'R5_PROFILE_PURCHASES.csv')
    candidates=read(OUT/'UNAPPROVED_ALTERNATIVES.csv')
    checklist=read(OUT/'PROPOSED_ORDERING_CHECKLIST.csv')
    reference_map={r['reference']:r for r in refs}
    assert len(reference_map)==len(refs)==154
    for name,total in [('F0',115),('F5',134)]:
        authority={r['reference']:r for r in read(POP/f'{name}-population-review.csv')}
        assert sum(int(r[f'qty_per_{name}']) for r in refs)==total
        assert all(r[f'{name}_state']==authority[r['reference']]['state'] and
                   int(r[f'qty_per_{name}'])==int(authority[r['reference']]['fitted_quantity']) for r in refs)
    physical=[r for r in master if r['quantity_role']!='MUTUALLY_EXCLUSIVE_R5_PROFILE_STOCK']
    occurrence=Counter(ref for row in physical for ref in row['references'].split())
    fitted={r['reference'] for r in refs if r['qty_per_F5']=='1'}
    assert set(occurrence)==fitted and set(occurrence.values())=={1}
    assert sum(int(r['fitted_qty_scenario']) for r in refs)==670
    assert sum(int(r['fitted_qty_scenario']) for r in master)==670
    assert all(int(r['fitted_qty_scenario'])==5*int(r['qty_per_F5']) for r in refs)
    for n5 in range(6):
        assert sum((5-n5)*int(r['qty_per_F0'])+n5*int(r['qty_per_F5']) for r in physical)==575+19*n5
    excluded={r['reference'] for r in refs if r['qty_per_F5']=='0'}
    assert not excluded.intersection(occurrence)
    assert {'C20','C22','C24','C25'}.issubset(excluded)
    assert {r for r in occurrence if r.startswith('TP')}=={'TP1','TP3','TP4'}
    assert len(master)==67 and len(physical)==65 and len({r['group_id'] for r in master})==67
    assert len(options)==3 and sorted(int(r['proposed_purchase_qty']) for r in options)==[10,10,10]
    assert sum(int(r['fitted_qty_scenario']) for r in options)==5
    assert len([r for r in refs if r['reference']=='R5'])==1
    ic1=next(r for r in master if r['references']=='IC1')
    assert ic1['mpn']=='BQ25798RQMR' and ic1['proposed_purchase_qty']=='5' and ic1['suggested_spares']=='0'
    assert all(r['mpn']!='BQ25792RQMR' for r in master)
    assert all(r['selection_status']=='OWNER_APPROVED' for r in approved)
    assert len(checklist)==67
    for references,mpn,original,sku,qty in [
        ('U8','LM74700QDBVTQ1','LM74700QDBVRQ1','C2653623','6'),
        ('C70 C71','C1608X7R1C105K080AC','GRM188R71C105KA12D','C2167399','20')]:
        row=next(r for r in master if r['references']==references)
        assert row['mpn']==mpn and row['selection_status']=='OWNER_APPROVED'
        assert row['original_procurement_mpns']==original
        assert row['distributor_sku']==sku and row['proposed_purchase_qty']==qty
        assert row['approved_basket_qty']==qty
        assert any(r['mpn']==mpn for r in approved)
    assert not {'AO3400A','PMV16XNR','C3216X5R1V226MTJ00E'}.intersection(r['mpn'] for r in approved)
    assert next(r['mpn'] for r in master if r['references']=='Q3 Q8 Q9')=='PMV16UN,215'
    assert next(r['mpn'] for r in master if r['references']=='C33 C45 C64 C65')=='C3216X5R1V226M160AC'
    assert all(r['automatic_purchase_qty']=='0' for r in candidates)
    assert not {r['candidate_mpn'] for r in candidates}.intersection(r['mpn'] for r in approved)
    assert {r['candidate_mpn'] for r in candidates}=={'AO3400A','PMV16XNR','C3216X5R1V226MTJ00E'}
    by_id={r['group_id']:r for r in master}
    assert {r['group_id'] for r in checklist}==set(by_id)
    for r in checklist:
        original=by_id[r['group_id']]
        assert r['manufacturer_mpn']==original['mpn']
        assert r['purchase_quantity']==original['proposed_purchase_qty']
        assert r['fitted_quantity']==original['fitted_qty_scenario']
        assert r['spares']==original['suggested_spares']
        assert r['MOQ_excess']==original['MOQ_rounding_excess']
        assert r['extended_price']==original['extended_scenario_cost_usd']
    assert next(r['checklist_status'] for r in checklist if r['references']=='D3 D4')=='HOLD_INSUFFICIENT_OBSERVED_STOCK'
    assert all(r['approved_basket_qty']==by_id[r['group_id']]['proposed_purchase_qty'] for r in approved)
    for r in master:
        if r['extended_scenario_cost_usd']:
            assert abs(float(r['extended_scenario_cost_usd'])-float(r['proposed_purchase_qty'])*float(r['page_unit_price']))<0.00011
        if r['supplier_MOQ'] and r['purchase_multiple'] and r['proposed_purchase_qty']:
            quantity=int(r['proposed_purchase_qty'])
            assert quantity>=int(r['desired_qty_before_MOQ']) and quantity>=int(r['supplier_MOQ'])
            assert quantity%int(r['purchase_multiple'])==0
            assert int(r['MOQ_rounding_excess'])==quantity-int(r['desired_qty_before_MOQ'])
    h={r['item_id']:r for r in harness}
    assert h['H05']['required_scenario_qty']=='40' and h['H05']['suggested_spares']=='10'
    assert h['H05']['proposed_purchase_qty']=='50'
    assert h['H08']['required_scenario_qty']=='40' and h['H08']['proposed_purchase_qty']=='100'
    assert float(h['H08']['MOQ_rounding_excess'])==50
    assert all(float(h[r]['required_scenario_qty'])==5 for r in ('H01','H02','H03','H04','H06','H07'))
    assert all(float(h[r]['required_scenario_qty'])==0 for r in ('H13','B01','B02','B03'))
    hashes=json.loads((EV/'protected-before.json').read_text())
    mismatches=[p for p,v in hashes.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=v]
    assert not mismatches,mismatches
    before=json.loads((EV/'entry-sourcing/selections.json').read_text())
    after=json.loads((OUT/'selections.json').read_text())
    changed={r for r in after if after[r]['mpn']!=before[r]['mpn']}
    assert changed=={'U8','C70','C71'},changed
    promoted={r for r in after if after[r]['status']=='OWNER_APPROVED' and before[r]['status']!='OWNER_APPROVED'}
    assert promoted==changed
    for r in approved:
        assert int(r['page_observed_stock'])>=int(r['proposed_purchase_qty'])
    summary=json.loads((EV/'consistency.json').read_text())
    assert summary['complete_total_usd'] is None
    assert abs(sum(float(r['extended_scenario_cost_usd'] or 0) for r in master)-summary['priced_purchase_scenario_subtotal_usd'])<1e-6
    result={'result':'PASS','branch':branch,'references':154,'physical_groups':65,'planning_lines':67,
            'five_F5_fitted':670,'R5_positions':5,'R5_purchased_options':30,'IC1_purchase':5,
            'approved_exact_dated_quoted_subset':len(approved),'unapproved_candidates_excluded':len(candidates),
            'all_six_five_board_split_coefficients':'PASS','population_and_DNP_coverage':'PASS',
            'quantity_MOQ_cost_math':'PASS','harness_capacity':'PASS','protected_files_unchanged':len(hashes),
            'new_approved_identities':2,'new_approved_references':sorted(changed),
            'approved_substitutions_traceability':'PASS','conditional_candidates_still_excluded':'PASS',
            'grouped_order_checklist':'PASS','insufficient_stock_held':'PASS',
            'engineering_qualification':'INCOMPLETE; see Phase5.2 compatibility holds',
            'complete_delivered_total':None,
            'cad_operations':0,'firmware_build_required':False}
    (EV/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':
    main()
