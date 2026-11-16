"""Independent procurement arithmetic, approval and preservation checks. No CAD APIs."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

EV=Path(__file__).resolve().parent
ROOT=EV.parents[3]
OUT=ROOT/'hardware/v4/sourcing'


def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def main():
    rows=read(OUT/'MASTER_PURCHASING_BOM.csv')
    refs=read(OUT/'REFERENCE_POPULATION.csv')
    check=read(OUT/'PROPOSED_ORDERING_CHECKLIST.csv')
    shop=read(OUT/'SHOPPING_LIST_BY_SUPPLIER.csv')
    physical=[r for r in rows if r['quantity_role']!='MUTUALLY_EXCLUSIVE_R5_PROFILE_STOCK']
    assert len(rows)==len(check)==66 and len(physical)==64 and len(shop)==74
    assert len(refs)==len({r['reference'] for r in refs})==154
    assert sum(int(r['fitted_qty_scenario']) for r in rows)==655
    assert sum(int(r['fitted_qty_scenario']) for r in refs)==655
    counts=Counter(ref for r in physical for ref in r['references'].split())
    assert len(counts)==131 and set(counts.values())=={1}
    assert not set(counts).intersection({'TP1','TP3','TP4','C20','C22','C24','C25'})
    assert sum(int(r['authoritative_qty_per_F5']) for r in refs)==134
    byref={r['references']:r for r in rows}
    for refs_,mpn,qty,status in [
        ('C32','CC0805KKX7R9BB225','10','OWNER_APPROVED_PROTOTYPE'),
        ('C33 C45 C64 C65','C3216X5R1V226MTJ00E','30','OWNER_APPROVED_PROTOTYPE'),
        ('C63','CC0603KRX7R9BB333','8','OWNER_APPROVED'),
        ('IC1','BQ25798RQMR','5','OWNER_APPROVED'),
    ]:
        r=byref[refs_]
        assert (r['mpn'],r['proposed_purchase_qty'],r['selection_status'])==(mpn,qty,status)
    r5=[r for r in rows if r['references'].startswith('R5')]
    assert len(r5)==3 and {r['proposed_purchase_qty'] for r in r5}=={'10'}
    assert {r['mpn'] for r in r5}=={'RC0805FR-078K2L','RC0805FR-0713K7L','RC0805FR-0727KL'}
    assert sum(int(r['fitted_qty_scenario']) for r in r5)==5
    assert {r['references'] for r in rows if not r['quoted_extended_price_native']}=={'L3'}
    totals=defaultdict(Decimal)
    for r in rows:
        qty=int(r['proposed_purchase_qty']);moq=int(r['supplier_MOQ']);mult=int(r['purchase_multiple'])
        assert qty>=moq and qty%mult==0
        if r['quoted_extended_price_native']:
            expected=Decimal(r['quoted_unit_price_native'])*qty
            assert abs(expected-Decimal(r['quoted_extended_price_native']))<=Decimal('.00005')
            assert int(r['page_observed_stock'])>=qty
    for r in shop:
        if r['extended_price']:totals[r['currency']]+=Decimal(r['extended_price'])
        assert r['direct_url'].startswith('https://') and r['distributor_sku']
    assert totals=={'USD':Decimal('259.7746'),'EUR':Decimal('6.4')},totals
    assert byref['R32']['quoted_currency']=='EUR' and byref['R32']['quoted_extended_price_native']=='6.4'
    assert byref['R32']['extended_scenario_cost_usd']==''
    assert byref['C8']['proposed_purchase_qty']=='100'
    assert byref['D3 D4']['distributor_sku']=='C74210' and byref['D3 D4']['proposed_purchase_qty']=='20'
    alt=json.loads((OUT/'phase5_4_c32_alternative.json').read_text())
    assert alt['mpn']=='C2012X7R1H225K125AC' and alt['approval'].startswith('PENDING')
    assert alt['order_quantity']==10 and alt['fitted_quantity']==0
    assert Decimal(str(alt['unit_price']))*10==Decimal(str(alt['extended_price']))
    accepted=read(OUT/'APPROVED_PURCHASING_BASKET.csv')
    assert len(accepted)==18 and all(r['selection_status'].startswith('OWNER_APPROVED') for r in accepted)
    assert not any(r['mpn']==alt['mpn'] for r in accepted+rows)
    # Actual CSV data, not copied prose, is the numerical C32 evidence.
    with (EV/'TDK-C32-dc-bias.csv').open(newline='') as f:curve=list(csv.reader(f))
    points={float(r[0]):float(r[1])*1e6 for r in curve if len(r)==2 and r[0][0].isdigit()}
    at18=points[16]+(18-16)/(25-16)*(points[25]-points[16])
    assert abs(at18-1.1908504444444445)<1e-9
    (EV/'C32-interpolation.json').write_text(json.dumps(dict(source='TDK-C32-dc-bias.csv',low_V=16,low_uF=points[16],high_V=25,high_uF=points[25],evaluation_V=18,interpolated_typical_uF=at18,guaranteed_minimum=False),indent=2)+'\n')
    before=json.loads((EV/'protected-before.json').read_text(encoding='utf-8-sig'))
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in before.items())
    assert hashlib.sha256((ROOT/'.codex/config.toml').read_bytes()).hexdigest().upper()==(EV/'config-before.sha256').read_text(encoding='utf-8-sig').strip()
    source_before=read(EV/'entry-sourcing/REFERENCE_POPULATION.csv')
    old={r['reference']:r for r in source_before}
    for r in refs:
        for field in ('qty_per_F0','qty_per_F5','F0_state','F5_state','actual_kicad_footprint','authoritative_qty_per_F0','authoritative_qty_per_F5'):
            assert r[field]==old[r['reference']][field],(r['reference'],field)
    # Optional lower-total price tiers, no change to approved/default quantities.
    obs=json.loads((OUT/'phase5_4_observations.json').read_text())
    options=[]
    for r in rows:
        if r['references']=='C63' or r['references'].startswith('R5'):continue
        currency=r['quoted_currency'];current=r['quoted_extended_price_native']
        if not current:continue
        tiers=obs[r['mpn']].get('price_tiers_native' if currency=='EUR' else 'price_tiers_usd',[])
        for tier in tiers:
            q=tier['qty'];cost=Decimal(str(tier['price']))*q
            if int(r['proposed_purchase_qty'])<q<=10 and cost<Decimal(current):
                options.append(dict(references=r['references'],mpn=r['mpn'],default_qty=r['proposed_purchase_qty'],default_cost=current,optional_qty=q,optional_unit=tier['price'],optional_cost=str(cost),currency=currency,saving=str(Decimal(current)-cost),approval='OPTIONAL_ONLY; default unchanged'))
    if options:
        with (OUT/'PRICE_BREAK_OPTIONS.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(options[0]));w.writeheader();w.writerows(options)
    result=dict(status='PASS',electronics_lines=66,harness_exact_lines=8,additional_C32_line='pending; would make67electronics',fitted_components=655,approved_exact_USD_lines=18,goods_USD=str(totals['USD']),goods_EUR=str(totals['EUR']),unpriced_exact_electronics=['L3'],czech_delivery_R32='OPEN',protected_files_unchanged=len(before),unrelated_config_unchanged=True,native_CAD_operations=0,orders=0)
    (EV/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
