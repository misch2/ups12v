"""Recalculate procurement CSVs from reviewed population and explicit selections.

No KiCad imports, exports or source mutations. Run from repository root.
"""
import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'hardware/v4/evidence/phase5-2-sourcing'
POP = ROOT / 'hardware/v4/evidence/phase4-22a-manufacturing-preparation'
DATE = '2026-10-19'


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n-f0', type=int, default=0)
    parser.add_argument('--n-f5', type=int, default=5)
    a = parser.parse_args()
    if min(a.n_f0, a.n_f5) < 0 or a.n_f0 + a.n_f5 > 5:
        parser.error('N_F0 and N_F5 must be nonnegative; total <= 5')
    sel = json.loads((OUT / 'selections.json').read_text(encoding='utf-8'))
    observations = json.loads((OUT / 'supplier_observations.json').read_text(encoding='utf-8'))
    observations.update(json.loads((OUT / 'phase5_1_observations.json').read_text(encoding='utf-8')))
    observations.update(json.loads((OUT / 'phase5_2_observations.json').read_text(encoding='utf-8')))
    f0 = read_csv(POP / 'F0-population-review.csv')
    f5 = {r['reference']: r for r in read_csv(POP / 'F5-population-review.csv')}
    assert len(f0) == len(f5) == 154
    refs = []
    groups = defaultdict(list)
    for original in f0:
        ref = original['reference']
        r5 = f5[ref]
        fit0, fit5 = int(original['fitted_quantity']), int(r5['fitted_quantity'])
        s = sel.get(ref, {})
        purchasable = fit0 + fit5 > 0
        mpn = s.get('mpn', original['known_mpn']) if purchasable else 'NOT_PURCHASED'
        manufacturer = s.get('manufacturer', original['manufacturer']) if purchasable else 'N/A'
        ratings = s.get('ratings', original['component_ratings_recorded'])
        status = s.get('status', 'RETAINED_PROVISIONAL') if purchasable else 'EXCLUDED'
        row = dict(reference=ref, functionality=original['value_function'],
                   F0_state=original['state'], F5_state=r5['state'],
                   qty_per_F0=fit0, qty_per_F5=fit5,
                   fitted_qty_formula=f'{fit0}*N_F0+{fit5}*N_F5',
                   fitted_qty_scenario=fit0*a.n_f0+fit5*a.n_f5,
                   manufacturer=manufacturer, selected_mpn=mpn, selection_status=status,
                   alternative_profile_mpns='RC0805FR-078K2L (2S); RC0805FR-0713K7L (3S); RC0805FR-0727KL (4S); one mutually exclusive position' if ref=='R5' else '',
                   selection_basis=s.get('basis', 'Retained reviewed PCB fields; no new engineering approval'),
                   original_recorded_mpn=original['known_mpn'],
                   original_procurement_mpn=s.get('original_procurement_mpn', original['known_mpn']),
                   value_ratings_tolerance=ratings,
                   actual_kicad_footprint=original['footprint'],
                   package=s.get('package', original['footprint'].split(':')[-1]),
                   group_id='', uncertainties=s.get('notes', ''),
                   population_authority='Phase4.22A reviewed reference CSVs; Phase5.1 owner purchasing scenario 0F0+5F5; R5 alternatives occupy one position')
        refs.append(row)
        if purchasable:
            # A group requires the same procurement identity, package and chosen grade.
            key = (manufacturer, mpn, original['footprint'], ratings)
            groups[key].append(row)
    result = []
    for number, (key, rr) in enumerate(groups.items(), 1):
        manufacturer, mpn, footprint, ratings = key
        gid = f'P{number:03d}'
        for r in rr:
            r['group_id'] = gid
        q0, q5 = sum(r['qty_per_F0'] for r in rr), sum(r['qty_per_F5'] for r in rr)
        fitted = q0*a.n_f0 + q5*a.n_f5
        tiny = any(t in footprint for t in ('0402', '0603', '0805'))
        spares = (max(3, math.ceil(fitted*.2)) if tiny else 1) if fitted else 0
        # Expensive modules/inductors/connectors get no automatic spare.
        if rr[0]['reference'].startswith(('J', 'L', 'U1')):
            spares = 0
        if rr[0]['reference'] == 'IC1':
            spares = 0  # Owner explicitly requests exactly five selected BQ25798.
        if rr[0]['reference'] == 'R5':
            spares = max(0, 10-fitted)
        o = observations.get(mpn, {})
        moq, multiple = o.get('moq'), o.get('multiple')
        desired = fitted + spares
        purchase = 0 if not desired else math.ceil(max(desired, moq)/multiple)*multiple if moq and multiple else ''
        if rr[0]['reference'] == 'R5':
            purchase = 10  # Requested target; supplier terms remain separately unverified.
        unit_price = o.get('unit_price_usd')
        for tier in o.get('price_tiers_usd', []):
            if purchase != '' and purchase >= tier['qty']:
                unit_price = tier['price']
        # Exclude unavailable/reference-only quotations from the usable subtotal.
        usable = unit_price is not None and o.get('availability') not in ('OUT_OF_STOCK', 'NOT_AVAILABLE', 'NO_LONGER_AVAILABLE')
        ext = 0 if purchase == 0 else round(purchase*unit_price, 4) if usable and purchase != '' else ''
        row = dict(group_id=gid, references=' '.join(r['reference'] for r in rr),
                   functionality='; '.join(dict.fromkeys(r['functionality'] for r in rr)),
                   manufacturer=manufacturer, mpn=mpn, value_ratings_tolerance=ratings,
                   original_recorded_mpns='; '.join(dict.fromkeys(r['original_recorded_mpn'] for r in rr)),
                   original_procurement_mpns='; '.join(dict.fromkeys(r['original_procurement_mpn'] for r in rr)),
                   selection_basis='; '.join(dict.fromkeys(r['selection_basis'] for r in rr)),
                   package=rr[0]['package'], actual_kicad_footprint=footprint,
                   selection_status='; '.join(dict.fromkeys(r['selection_status'] for r in rr)),
                   qty_per_F0=q0, qty_per_F5=q5,
                   fitted_qty_formula=f'{q0}*N_F0+{q5}*N_F5',
                   N_F0=a.n_f0, N_F5=a.n_f5, fitted_qty_scenario=fitted,
                   suggested_spares=spares, spare_policy='20% rounded up minimum3 small chips; 1 other; 0 modules/inductors/connectors/IC1; R5 owner10 each profile',
                   desired_qty_before_MOQ=desired, supplier_MOQ=moq or '', purchase_multiple=multiple or '',
                   proposed_purchase_qty=purchase,
                   MOQ_rounding_excess=(purchase-desired) if purchase != '' and moq and multiple else '',
                   purchase_qty_formula='if fitted=0: 0; else ceil(max(fitted+spares,MOQ)/multiple)*multiple; blank if terms unknown',
                   five_board_formula=f'{5*q0}+({q5-q0})*N_F5 where N_F0=5-N_F5',
                   qty_5F0=5*q0, qty_4F0_1F5=4*q0+q5, qty_3F0_2F5=3*q0+2*q5,
                   qty_2F0_3F5=2*q0+3*q5, qty_1F0_4F5=q0+4*q5, qty_5F5=5*q5,
                   candidate_supplier=o.get('supplier', sel.get(rr[0]['reference'], {}).get('supplier', 'TME / LCSC exact-MPN quote needed')),
                   distributor_sku=o.get('sku', ''), direct_product_url=o.get('url', ''),
                   alternate_source_url=o.get('alternate_url', ''),
                   availability=o.get('availability', 'UNVERIFIED'),
                   page_observed_stock=o.get('stock', ''),
                   stock_freshness=o.get('freshness', 'UNVERIFIED; no live stock established'),
                   page_unit_price=unit_price if unit_price is not None else '',
                   currency='USD' if unit_price is not None else '',
                   price_basis=o.get('price_basis', 'UNVERIFIED'),
                   price_break_qty=o.get('price_break_qty', ''),
                   verification_date=o.get('date', ''), evidence=o.get('evidence', ''),
                   supplier_packaging=o.get('packaging', 'UNVERIFIED'),
                   phase5_2_refresh_status=o.get('refresh_status','REFRESH_ATTEMPTED_NO_USABLE_NEW_FIELDS; preceding cached observation retained'),
                   fitted_cost_F0_usd=0 if not q0 else round(q0*unit_price, 4) if usable else '',
                   fitted_cost_F5_usd=0 if not q5 else round(q5*unit_price, 4) if usable else '',
                   extended_scenario_cost_usd=ext,
                   outstanding_uncertainties='; '.join(dict.fromkeys([r['uncertainties'] for r in rr if r['uncertainties']] + [o.get('notes', 'Exact quote/stock/MOQ/multiple/price missing; do not assume one-piece order')])) )
        row['quantity_role'] = 'FITTED_POSITION_PLUS_SPARES'
        row['alternative_profile_stock_qty'] = 0
        enough_stock = isinstance(o.get('stock'), (int,float)) and purchase!='' and o['stock']>=purchase
        row['order_readiness'] = ('OWNER_ACCEPTED_EXACT_QUOTED' if row['selection_status']=='OWNER_APPROVED' and usable and purchase!='' and moq and multiple and enough_stock and o.get('availability')=='PAGE_IN_STOCK' else 'HOLD_FOR_SELECTION_OR_PROCUREMENT')
        row['approved_basket_qty'] = purchase if row['order_readiness']=='OWNER_ACCEPTED_EXACT_QUOTED' else 0
        result.append(row)
    # Additional R5 stock options never create additional fitted positions.
    r5row = next(r for r in result if r['references']=='R5')
    r5row['quantity_role'] = 'R5_4S_OPTION_ACCOUNTING_ANCHOR_NOT_CELL_PROFILE_SELECTION'
    r5row['outstanding_uncertainties'] += '; One R5 per board; 27k is accounting anchor only. 2S/3S/4S profile chosen later; 10 each requested'
    for profile, mpn, value, url in [
            ('2S','RC0805FR-078K2L','8.2k','https://www.tme.eu/en/details/rc0805fr-078k2l/smd-resistors/yageo/'),
            ('3S','RC0805FR-0713K7L','13.7k','https://www.tme.eu/en/details/rc0805fr-0713k7l/smd-resistors/yageo/')]:
        r=dict(r5row)
        r.update(group_id=f'R5-{profile}',references='R5 (alternative stock only)',mpn=mpn,
                 functionality=f'PROG {profile} 750kHz mutually exclusive R5 option',
                 value_ratings_tolerance=f'{value} +/-1%; 0805; 0.125W; 150V',
                 qty_per_F0=0,qty_per_F5=0,fitted_qty_formula='0; shares existing R5 position',fitted_qty_scenario=0,
                 suggested_spares=0,desired_qty_before_MOQ=10,proposed_purchase_qty=10,
                 supplier_MOQ='',purchase_multiple='',MOQ_rounding_excess='',
                 alternative_profile_stock_qty=10,quantity_role='MUTUALLY_EXCLUSIVE_R5_PROFILE_STOCK',
                 candidate_supplier='TME',distributor_sku=mpn,direct_product_url=url,
                 availability='UNVERIFIED',page_observed_stock='',page_unit_price='',currency='',
                 price_basis='QUOTE_MISSING',price_break_qty='',verification_date=DATE,
                 evidence='../evidence/phase5-1-sourcing/current-13.txt; owner Phase5.1',
                 fitted_cost_F0_usd=0,fitted_cost_F5_usd=0,extended_scenario_cost_usd='',
                 order_readiness='HOLD_EXACT_MPN_PROPOSAL_AND_QUOTE',approved_basket_qty=0)
        for field in ('qty_5F0','qty_4F0_1F5','qty_3F0_2F5','qty_2F0_3F5','qty_1F0_4F5','qty_5F5'):
            r[field]=0
        r['five_board_formula']='0 additional positions; alternative R5 stock'
        r['purchase_qty_formula']='Owner fixed target10; supplier MOQ/multiple must be confirmed before ordering'
        o=observations.get(mpn,{})
        for field, source in [('candidate_supplier','supplier'),('distributor_sku','sku'),('direct_product_url','url'),('availability','availability'),('page_observed_stock','stock'),('stock_freshness','freshness'),('page_unit_price','unit_price_usd'),('price_basis','price_basis'),('price_break_qty','price_break_qty'),('supplier_MOQ','moq'),('purchase_multiple','multiple'),('evidence','evidence')]:
            r[field]=o.get(source,r[field])
        if o.get('unit_price_usd') is not None:
            r.update(currency='USD',extended_scenario_cost_usd=round(10*o['unit_price_usd'],4),MOQ_rounding_excess=0)
        r['outstanding_uncertainties']=o.get('notes','Quote missing')+'; Not an additional fitted position; no cell profile selected'
        result.append(r)
    write_csv(OUT / 'REFERENCE_POPULATION.csv', refs)
    write_csv(OUT / 'MASTER_PURCHASING_BOM.csv', result)
    write_csv(OUT / 'R5_PROFILE_PURCHASES.csv', [r for r in result if r['quantity_role'].startswith(('R5_','MUTUALLY_'))])
    write_csv(OUT / 'APPROVED_PURCHASING_BASKET.csv', [r for r in result if r['approved_basket_qty']])
    harness=[]
    for raw in json.loads((OUT/'harness_inputs.json').read_text()):
        r=dict(raw)
        fitted=round(r['qty_per_F0']*a.n_f0+r['qty_per_F5']*a.n_f5+r['qty_per_batch']*bool(a.n_f0+a.n_f5),4)
        spare=r['spare_qty'] if fitted else 0
        desired=round(fitted+spare,4)
        terms=r['MOQ']!='' and r['multiple']!=''
        ordered=math.ceil(max(desired,r['MOQ'])/r['multiple'])*r['multiple'] if terms and desired else 0 if not desired else ''
        r.update(N_F0=a.n_f0,N_F5=a.n_f5,required_scenario_qty=fitted,
                 fitted_qty_formula=f"{r['qty_per_F0']}*N_F0+{r['qty_per_F5']}*N_F5+{r['qty_per_batch']}*any_boards",
                 suggested_spares=spare,desired_scenario_qty=desired,proposed_purchase_qty=ordered,
                 MOQ_rounding_excess=ordered-desired if ordered!='' else '',
                 extended_scenario_cost_usd=round(ordered*r['unit_price_usd'],4) if ordered!='' and r['unit_price_usd']!='' else '',
                 currency='USD' if r['unit_price_usd']!='' else '',
                 price_basis='Dated page observation excluding tax/shipping; cache age in evidence; no reserved stock' if r['unit_price_usd']!='' else 'UNVERIFIED',
                 qty_5F0=5*r['qty_per_F0']+r['qty_per_batch'],qty_5F5=5*r['qty_per_F5']+r['qty_per_batch'])
        harness.append(r)
    write_csv(OUT/'HARNESS_AND_ASSEMBLY_BOM.csv',harness)
    # Independent invariants include the authoritative state, not symbol DNP text.
    assert len({r['reference'] for r in refs}) == 154
    assert sum(r['qty_per_F0'] for r in refs) == 115
    assert sum(r['qty_per_F5'] for r in refs) == 134
    expected_f5 = {'U7','U8','Q10','L3','R60','R61','R62','R63','J8'} | {f'C{i}' for i in range(60,70)}
    assert {r['reference'] for r in refs if r['qty_per_F5'] and not r['qty_per_F0']} == expected_f5
    assert {r['reference'] for r in refs if r['F0_state']=='DNP' and r['F5_state']=='DNP'} == {'C20','C22','C24','C25'}
    assert sum(r['qty_per_F0'] for r in result) == 115
    assert sum(r['qty_per_F5'] for r in result) == 134
    assert sum(r['fitted_qty_scenario'] for r in result) == 115*a.n_f0+134*a.n_f5
    assert sum(r['proposed_purchase_qty'] for r in result if r['quantity_role'].startswith(('R5_','MUTUALLY_'))) == 30
    assert next(r['proposed_purchase_qty'] for r in result if r['references']=='IC1') == a.n_f0+a.n_f5
    assert all(r['selection_status']=='OWNER_APPROVED' for r in result if r['approved_basket_qty'])
    assert sum(r['F0_state'] == 'PCB_FEATURE' for r in refs) == 16
    assert all(not r['group_id'] for r in refs if r['qty_per_F0']+r['qty_per_F5']==0)
    assert {r['reference'] for r in refs if r['reference'].startswith('TP') and r['group_id']} == {'TP1','TP3','TP4'}
    assert next(r['selected_mpn'] for r in refs if r['reference']=='IC1') == 'BQ25798RQMR'
    assert all(r['selected_mpn']=='EVQP0Q02Q' for r in refs if r['reference'] in ('SW1','SW2'))
    assert next(r['selected_mpn'] for r in refs if r['reference']=='U2')=='TPD2EUSB30ADRTR'
    before=json.loads((EVIDENCE/'protected-before.json').read_text())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in before.items()), 'Protected source changed'
    unknown_qty=[r['group_id'] for r in result if r['proposed_purchase_qty']=='']
    unpriced=[r['group_id'] for r in result if r['extended_scenario_cost_usd']=='']
    summary=dict(date=DATE, scenario=dict(N_F0=a.n_f0,N_F5=a.n_f5, provisional=False, basis='Owner Phase5.1: purchase all five as F5; physical assembly split undecided'),
                 references=154,F0=115,F5=134,F5_only=19,always_DNP=4,PCB_features=16,
                 distinct_purchase_groups=len(result),
                 fitted_components_scenario=sum(r['fitted_qty_scenario'] for r in result),
                 R5_profile_purchase_pieces=30, R5_fitted_positions=a.n_f0+a.n_f5,
                 owner_accepted_quoted_lines=sum(bool(r['approved_basket_qty']) for r in result),
                 exact_mpn_unresolved=[r['reference'] for r in refs if r['group_id'] and r['selected_mpn'].startswith('OPEN')],
                 groups_unknown_order_quantities=unknown_qty, groups_without_usable_cost=unpriced,
                 priced_fitted_F0_subtotal_usd=round(sum(r['fitted_cost_F0_usd'] or 0 for r in result),4),
                 priced_fitted_F5_subtotal_usd=round(sum(r['fitted_cost_F5_usd'] or 0 for r in result),4),
                 priced_purchase_scenario_subtotal_usd=round(sum(r['extended_scenario_cost_usd'] or 0 for r in result),4),
                 harness_and_assembly_rows=len(harness),
                 priced_harness_scenario_subtotal_usd=round(sum(r['extended_scenario_cost_usd'] or 0 for r in harness),4),
                 complete_total_usd=None, protected_files_unchanged=len(before),
                 checks='PASS: population coverage, uniqueness, fit states, grouping, five-board formula, owner identities, protection hashes',
                 source_hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [POP/'F0-population-review.csv',POP/'F5-population-review.csv',OUT/'selections.json',OUT/'supplier_observations.json',OUT/'phase5_1_observations.json',OUT/'phase5_2_observations.json',OUT/'phase5_2_reviewed_overrides.json',OUT/'replacement_candidates.json',OUT/'harness_inputs.json']})
    (EVIDENCE/'consistency.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
