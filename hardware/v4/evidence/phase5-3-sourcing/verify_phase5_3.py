"""Independent documentary checks; no KiCad imports or native CAD operations."""
import csv
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EV = Path(__file__).resolve().parent
OUT = ROOT/'hardware/v4/sourcing'
POP = ROOT/'hardware/v4/evidence/phase4-22a-manufacturing-preparation'


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    refs = read(OUT/'REFERENCE_POPULATION.csv')
    master = read(OUT/'MASTER_PURCHASING_BOM.csv')
    checklist = read(OUT/'PROPOSED_ORDERING_CHECKLIST.csv')
    accepted = read(OUT/'APPROVED_PURCHASING_BASKET.csv')
    harness = read(OUT/'HARNESS_AND_ASSEMBLY_BOM.csv')
    options = read(OUT/'R5_PROFILE_PURCHASES.csv')
    probes = {'TP1','TP3','TP4'}
    assert len(refs) == len({r['reference'] for r in refs}) == 154
    for variant, actual, historical in [('F0',112,115),('F5',131,134)]:
        authority = {r['reference']:r for r in read(POP/f'{variant}-population-review.csv')}
        assert sum(int(r[f'qty_per_{variant}']) for r in refs) == actual
        assert sum(int(r[f'authoritative_qty_per_{variant}']) for r in refs) == historical
        for r in refs:
            source = authority[r['reference']]
            assert r[f'authoritative_{variant}_state'] == source['state']
            assert r[f'authoritative_qty_per_{variant}'] == source['fitted_quantity']
            expected = 0 if r['reference'] in probes else int(source['fitted_quantity'])
            assert int(r[f'qty_per_{variant}']) == expected
            if r['reference'] not in probes:
                assert r[f'{variant}_state'] == source['state']
            else:
                assert r[f'{variant}_state'] == 'PCB_PROBE_PAD_NO_HARDWARE'
                assert not r['group_id'] and r['selected_mpn'] == 'NOT_PURCHASED'
    physical = [r for r in master if r['quantity_role'] != 'MUTUALLY_EXCLUSIVE_R5_PROFILE_STOCK']
    occurrence = Counter(ref for r in physical for ref in r['references'].split())
    assert len(master) == len(checklist) == 66 and len(physical) == 64
    assert set(occurrence) == {r['reference'] for r in refs if r['qty_per_F5'] == '1'}
    assert set(occurrence.values()) == {1} and not probes.intersection(occurrence)
    assert sum(int(r['fitted_qty_scenario']) for r in master) == 655
    assert sum(int(r['fitted_qty_scenario']) for r in refs) == 655
    for n5 in range(6):
        assert sum((5-n5)*int(r['qty_per_F0'])+n5*int(r['qty_per_F5']) for r in physical) == 560+19*n5
    assert {r['reference'] for r in refs if r['F0_state'] == r['F5_state'] == 'DNP'} == {'C20','C22','C24','C25'}
    assert sum(r['F5_state'] == 'PCB_FEATURE' for r in refs) == 16
    assert len(options) == 3 and sorted(int(r['proposed_purchase_qty']) for r in options) == [10]*3
    assert sum(int(r['fitted_qty_scenario']) for r in options) == 5
    by_ref = {r['references']:r for r in master}
    assert by_ref['IC1']['mpn'] == 'BQ25798RQMR' and by_ref['IC1']['proposed_purchase_qty'] == '5'
    assert by_ref['IC1']['suggested_spares'] == '0'
    q = by_ref['Q3 Q8 Q9']
    assert (q['mpn'],q['distributor_sku'],q['proposed_purchase_qty'],q['selection_status']) == ('AO3400A','C20917','20','OWNER_APPROVED')
    assert q['original_procurement_mpns'] == 'PMV16UN,215'
    m = by_ref['C35 C36']
    assert m['mpn'] == 'GRM21BR61E226ME44L' and m['selection_status'] == 'OWNER_APPROVED_PROTOTYPE'
    assert m['proposed_purchase_qty'] == '15'
    bank = by_ref['C33 C45 C64 C65']
    assert bank['mpn'] == 'C3216X5R1V226MTJ00E' and bank['original_procurement_mpns'] == 'C3216X5R1V226M160AC'
    assert bank['proposed_purchase_qty'] == '30' and bank['approved_basket_qty'] == '0'
    assert by_ref['C32']['approved_basket_qty'] == by_ref['C63']['approved_basket_qty'] == '0'
    assert by_ref['D3 D4']['mpn'] == 'BAS116H,115' and by_ref['D3 D4']['distributor_sku'] == 'C74210'
    assert by_ref['D3 D4']['proposed_purchase_qty'] == '20'
    assert {r['references'] for r in master if not r['extended_scenario_cost_usd']} == {'L3','R32'}
    assert all(r['proposed_purchase_qty'] and r['supplier_MOQ'] and r['purchase_multiple'] for r in master)
    for r in master:
        quantity = int(r['proposed_purchase_qty'])
        desired = int(r['desired_qty_before_MOQ'])
        moq, multiple = int(r['supplier_MOQ']), int(r['purchase_multiple'])
        assert quantity == math.ceil(max(desired,moq)/multiple)*multiple
        assert int(r['MOQ_rounding_excess']) == quantity-desired
        if r['extended_scenario_cost_usd']:
            assert r['availability'] == 'PAGE_IN_STOCK'
            assert abs(float(r['extended_scenario_cost_usd'])-quantity*float(r['page_unit_price'])) < .00011
            assert int(r['page_observed_stock']) >= quantity
    expected_accepted = [r for r in master if r['approved_basket_qty'] != '0']
    assert {r['group_id'] for r in accepted} == {r['group_id'] for r in expected_accepted}
    assert len(accepted) == 15
    assert all(r['selection_status'] in ('OWNER_APPROVED','OWNER_APPROVED_PROTOTYPE') for r in accepted)
    assert not {'PMV16UN,215','PMV16XNR','C3216X5R1V226MTJ00E'}.intersection(r['mpn'] for r in accepted)
    by_id = {r['group_id']:r for r in master}
    for r in checklist:
        original = by_id[r['group_id']]
        for target, source in [('manufacturer_mpn','mpn'),('fitted_quantity','fitted_qty_scenario'),('purchase_quantity','proposed_purchase_qty'),('MOQ_excess','MOQ_rounding_excess'),('extended_price','extended_scenario_cost_usd')]:
            assert r[target] == original[source]
    entry_harness = read(EV/'entry-sourcing/HARNESS_AND_ASSEMBLY_BOM.csv')
    assert harness == entry_harness
    before = json.loads((EV/'entry-sourcing/selections.json').read_text())
    after = json.loads((OUT/'selections.json').read_text())
    promoted = {k for k,v in after.items() if v['status'].startswith('OWNER_APPROVED') and not before[k]['status'].startswith('OWNER_APPROVED')}
    assert promoted == {'Q3','Q8','Q9','C35','C36'}
    changed_identity = {k for k,v in after.items() if v['mpn'] != before[k]['mpn']}
    assert changed_identity == probes | {'Q3','Q8','Q9','C33','C45','C64','C65','C63'}
    hashes = json.loads((EV/'protected-before.json').read_text())
    assert len(hashes) == 196
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h for p,h in hashes.items())
    assert hashlib.sha256((ROOT/'.codex/config.toml').read_bytes()).hexdigest() == (EV/'config-before.sha256').read_text()
    tracked_changes = subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    assert set(tracked_changes) <= {'.codex/config.toml','hardware/v4/V4_BOM_REVIEW.md','hardware/v4/V4_HANDOVER.md'}
    branch = subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    assert branch == 'codex/v4-phase5-component-sourcing'
    summary = json.loads((EV/'consistency.json').read_text())
    total = round(sum(float(r['extended_scenario_cost_usd'] or 0) for r in master),4)
    accepted_total = round(sum(float(r['extended_scenario_cost_usd']) for r in accepted),4)
    assert total == summary['priced_purchase_scenario_subtotal_usd'] == 244.1846
    assert accepted_total == 98.6589 and summary['complete_total_usd'] is None
    result = dict(result='PASS', branch=branch, references=154, physical_groups=64,
        planning_lines=66, actual_F0=112, actual_F5=131, actual_five_F5=655,
        authoritative_CAD_F0=115, authoritative_CAD_F5=134, omitted_optional_loops=15,
        all_six_five_board_splits='PASS', always_DNP_and_probe_coverage='PASS',
        R5_purchase=30, R5_fitted_positions=5, IC1_purchase=5,
        accepted_dated_price_lines=15, accepted_partial_usd=accepted_total,
        partial_electronics_usd=total, unpriced_lines=['L3','R32'],
        no_unknown_MOQ_derived_quantities=True, quantity_MOQ_cost_math='PASS',
        harness_unchanged=True, protected_files_unchanged=196, unrelated_config_preserved=True,
        new_approved_references=sorted(promoted), engineering_hardware_qualification='NOT_PERFORMED',
        commercial_completion='INCOMPLETE; no full delivered quote', purchasing_release=False)
    (EV/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:154refs;655physical;66lines;15accepted;196protected;2unpriced;no purchasing release')


if __name__ == '__main__':
    main()
