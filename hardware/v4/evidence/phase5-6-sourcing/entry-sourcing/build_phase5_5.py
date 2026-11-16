"""Rebuild proposed two-supplier baskets from saved observations only.

No network, supplier cart, CAD import or file mutation on import.
"""
import csv
import json
import math
import re
from collections import Counter
from decimal import Decimal as D
from pathlib import Path

BASE=Path(__file__).resolve().parent
EV=BASE.parent/'evidence/phase5-5-sourcing'

def csv_read(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig',newline='')))

def csv_write(path,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8-sig',newline='') as out:
        w=csv.DictWriter(out,fieldnames=fields);w.writeheader();w.writerows(rows)

def observation(records,row):
    matches=[r for r in records if re.search(r'/'+re.escape(row['distributor_sku'])+r'\.html(?:$|\?)',r['url'])
             and 'Minimum:' in r['text'] and row['manufacturer_mpn'].lower() in r['text'].lower()]
    assert matches,(row['group_id'],'No exact live product observation')
    record=matches[-1]
    text=record['text'].split('Standard Packaging')[0].split('Other Suppliers on LCSC')[0]
    stock=re.search(r'In-Stock:\s*([\d,]+)',text)
    terms=re.search(r'Minimum:\s*([\d,]+)\s*Multiple:\s*([\d,]+)',text)
    assert stock and terms,row['group_id']
    tiers=[(int(q.replace(',','')),D(p)) for q,p in re.findall(r'([\d,]+)\+\s*\$\s*([\d.]+)',text)]
    assert tiers,row['group_id']
    return record,int(stock[1].replace(',','')),int(terms[1].replace(',','')),int(terms[2].replace(',','')),tiers

def price_for(q,tiers):
    valid=[(n,p) for n,p in tiers if n<=q]
    assert valid,(q,tiers)
    return max(valid,key=lambda x:x[0])[1]

def main():
    plan=json.loads((BASE/'phase5_5_plan.json').read_text(encoding='utf-8'))
    records=json.loads((EV/'browser-live.json').read_text(encoding='utf-8'))
    master={r['group_id']:r for r in csv_read(EV/'entry-sourcing/MASTER_PURCHASING_BOM.csv')}
    harness={r['item_id']:r for r in csv_read(EV/'entry-sourcing/HARNESS_AND_ASSEMBLY_BOM.csv')}
    rows=[]
    for r in plan:
        gid=r['group_id'];m=master.get(gid,{})
        desired=int(m.get('desired_qty_before_MOQ') or harness.get(gid,{}).get('desired_scenario_qty') or r['purchase_quantity'])
        note=r['proposal_reason']
        if gid=='H03':
            desired=5;note+='; buy five required, omit one discretionary spare because live stock is five'
        if r['supplier']=='LCSC':
            rec,stock,moq,multiple,tiers=observation(records,r)
            minimum=math.ceil(max(desired,moq)/multiple)*multiple
            # A price break is worthwhile only when its total spend is LOWER.
            candidates={minimum}|{math.ceil(max(n,desired,moq)/multiple)*multiple for n,_ in tiers}
            candidates=[q for q in candidates if q<=stock]
            assert candidates,(gid,'Insufficient stock')
            qty=min(candidates,key=lambda q:(D(q)*price_for(q,tiers),q))
            unit=price_for(qty,tiers)
            freshness='LIVE_BROWSER_2026-10-20; public page, not reserved'
            evidence='../evidence/phase5-5-sourcing/browser-live.json#'+rec['id']
            if qty>minimum:note+='; higher tier lowers TOTAL goods spend versus minimum quantity'
            obs_time=rec.get('observed_utc','2026-10-20 (capture date; time not recorded)')
        else:
            stock=int(r['observed_stock']);moq=int(r['MOQ']);multiple=int(r['multiple'])
            qty=int(r['purchase_quantity']);unit=D(r['unit_price'])
            freshness=r['freshness']+'; CACHED_ONLY, live TME unavailable on 2026-10-20'
            evidence=r['evidence'];obs_time=r['observation_date']
        assert qty>=int(r['fitted_quantity']) and qty>=desired
        assert qty>=moq and qty%multiple==0 and qty<=stock
        row=dict(supplier=r['supplier'],group_id=gid,references=r['references'],scope=r['scope'],
                 original_supplier=r['original_supplier'],original_mpn=r['original_mpn'],
                 manufacturer=r['manufacturer'],manufacturer_mpn=r['manufacturer_mpn'],distributor_sku=r['distributor_sku'],
                 package=m.get('package','Exact connector housing/contact'),footprint=m.get('actual_kicad_footprint','Harness; not PCB-mounted'),
                 fitted_quantity=r['fitted_quantity'],desired_before_MOQ=desired,
                 spares_planned=0 if gid=='H03' else r['spares'],alternative_R5_stock=r['alternative_R5_stock'],
                 MOQ=moq,multiple=multiple,purchase_quantity=qty,unit='pcs',MOQ_or_tier_excess=qty-desired,
                 observed_stock=stock,stock_freshness=freshness,observation_date=obs_time,
                 unit_price=str(unit),extended_price=str(unit*qty),currency='USD',
                 price_basis='PUBLIC_NET_ALLOWANCE_NOT_QUOTE; excludes tax/freight/import',
                 approval=r['phase5_5_approval'],direct_url=r['direct_url'],evidence=evidence,notes=note)
        rows.append(row)
    # Separate comparison stock adds NO fitted positions.
    rows.append(dict(supplier='TME',group_id='C32-COMPARE',references='C32 comparison stock only',scope='OPTIONAL_COMPARISON',
        original_supplier='DigiKey',original_mpn='C2012X7R1H225K125AC',manufacturer='TDK',manufacturer_mpn='C2012X7R1H225K125AC',
        distributor_sku='C2012X7R1H225KAC',package='0805 2.0x1.25x1.25mm',footprint='Capacitor_SMD:C_0805_2012Metric',fitted_quantity=0,
        desired_before_MOQ=10,spares_planned=0,alternative_R5_stock=0,MOQ=1,multiple=1,purchase_quantity=10,unit='pcs',MOQ_or_tier_excess=0,
        observed_stock=22076,stock_freshness='CACHED today, retrieved2026-10-20; live TME unavailable',observation_date='2026-10-20',
        unit_price='0.31',extended_price='3.10',currency='USD',price_basis='PUBLIC_NET_ALLOWANCE_NOT_QUOTE; ten-piece tier',
        approval='OPTIONAL_COMPARISON_OWNER_APPROVAL_REQUIRED',direct_url='https://www.tme.eu/en/details/c2012x7r1h225kac/mlcc-smd-capacitors/tdk/c2012x7r1h225k125ac/',
        evidence='../evidence/phase5-5-sourcing/research-26.json; research-27.json; research-28.json; retained Phase5.4 manufacturer bias evidence',notes='Keep approved C32 Yageo x10. Extra TDK x10 is separate, unapproved comparison stock; zero extra assembly positions.'))
    wire=[('H09','BQ CABLE','FLRY-B0.50-RD/1',5,'m','0.92',1533,'4 months','flry-b0.50-rd_1/car-instalation-cables/bq-cable/','Red Cu stranded0.5mm2; OD1.4..1.6mm,60V,-40..105C; closest metric AWG20 class for accepted Nano-Fit contact'),
          ('H10','BQ CABLE','FLRY-B0.50-BK/1',5,'m','0.93',2109,'4 months','flry-b0.50-bk_1/car-instalation-cables/bq-cable/','Black same construction; cached Norway USD page, Czech price unconfirmed'),
          ('H11','DONAU ELEKTRONIK','118-5',2,'10m roll','2.99',6,'3 weeks','d-118-5/single-core-cable-strand/donau-elektronik/118-5/','White Cu stranded0.14mm2,OD1mm,60V,-10..85C; 20m covers11m length allowance; identify each signal at both ends')]
    for gid,maker,mpn,qty,unit,price,stock,age,route,note in wire:
        rows.append(dict(supplier='TME',group_id=gid,references='Harness wire',scope='HARNESS_MATERIAL',original_supplier='Deferred',original_mpn='No exact MPN previously selected',
            manufacturer=maker,manufacturer_mpn=mpn,distributor_sku='D-118-5' if gid=='H11' else mpn,package='Wire; no PCB footprint',footprint='Not applicable',fitted_quantity=0,
            desired_before_MOQ=qty,spares_planned=0,alternative_R5_stock=0,MOQ=1,multiple=1,purchase_quantity=qty,unit=unit,MOQ_or_tier_excess=0,observed_stock=stock,
            stock_freshness='CACHED '+age+'; retrieved2026-10-20; live TME unavailable',observation_date='2026-10-20',unit_price=price,extended_price=str(D(price)*qty),currency='USD',
            price_basis='PUBLIC_NET_ALLOWANCE_NOT_QUOTE; regional price must be refreshed',approval='PROPOSED_HARNESS_MATERIAL_OWNER_APPROVAL_REQUIRED',
            direct_url='https://www.tme.eu/'+('no/en/' if gid=='H10' else 'en/')+'details/'+route,evidence='../evidence/phase5-5-sourcing/research-66.json',notes=note))
    rows.sort(key=lambda r:(r['supplier'],r['group_id']))
    csv_write(BASE/'PHASE5_5_SHOPPING_LIST.csv',rows)
    totals={s:sum(D(r['extended_price']) for r in rows if r['supplier']==s) for s in ['LCSC','TME']}
    summary=dict(rows=len(rows),core_rows=len(plan),electronic_rows=sum(r['scope']=='PCB_ELECTRONICS' for r in plan),
                 core_fitted=sum(int(r['fitted_quantity']) for r in plan if r['scope']=='PCB_ELECTRONICS'),
                 supplier_rows=dict(Counter(r['supplier'] for r in rows)),goods_USD={k:str(v) for k,v in totals.items()},
                 total_goods_USD=str(sum(totals.values())),
                 proposed_MPN_changes=[r['group_id'] for r in rows if r['approval']=='PROPOSED_REPLACEMENT_OWNER_APPROVAL_REQUIRED'],
                 external_supplier_lines_resolved=[r['group_id'] for r in rows if r['original_supplier'] not in ['LCSC','TME','Deferred']])
    (EV/'basket-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    md=['# Phase 5.5 — proposed LCSC + TME baskets','',
        'Quick start: review the [substitutions](PHASE5_5_SUBSTITUTION_REVIEW.md), then the grouped rows below. '+
        'Approve replacements and final quantities together before ordering. These are documentary baskets; no supplier cart exists.',
        '',f'Five F5 boards: **655 fitted PCB parts, 66 electronic planning rows, eight exact connector/harness rows**. The CSV adds one optional C32 comparison row and three wire rows: **{len(rows)} rows total**.',
        '', 'All prices are USD net public allowances, not supplier quotations. Stock is unallocated. '+
        'Every LCSC line was observed live on20Oct2026; TME remains explicitly cached. '+
        'See [cost and unknowns](PHASE5_5_DELIVERED_COST.md) and [full CSV](PHASE5_5_SHOPPING_LIST.csv).','']
    for supplier in ['LCSC','TME']:
        group=[r for r in rows if r['supplier']==supplier]
        md.extend([f'## {supplier} — {len(group)} lines, USD {totals[supplier]:.4f} net goods','',
            '| ID / refs | Manufacturer MPN / supplier SKU | Buy | Stock | Unit USD | Extended USD | Observation |',
            '|---|---|---:|---:|---:|---:|---|'])
        for r in group:
            label=f"{r['manufacturer_mpn']} / {r['distributor_sku']}"
            md.append(f"| {r['group_id']} / {r['references']} | [{label}]({r['direct_url']}) | {r['purchase_quantity']} {r['unit']} | {r['observed_stock']} | {r['unit_price']} | {r['extended_price']} | {'Live20Oct' if supplier=='LCSC' else r['stock_freshness']} |")
        md.append('')
    md.extend(['## Quantity decisions','',
        '- H03 exact key-B housing: buy the five required, with no optional spare; only five live pieces. No key substitution.',
        '- R33: ten cost USD4.2820, slightly less than eight at the lower tier (USD4.2856).',
        '- R5 requested working stock is ten per 2S/3S/4S profile; supplier MOQ rounds each to100. Extra stock does not add fitted positions.',
        '- Exactly five BQ25798RQMR; approved C32 Yageo x10 and TDK bank x30 retained; additional C32 TDK x10 remains optional.',
        '- C8 buy50 after live MOQ/multiple50 resolved the older cache conflict. All pack excess is explicit in the CSV.',
        '', '**STOP — replacements and final baskets await owner approval. No purchases, checkout, CAD, firmware, commit or push.**',''])
    (BASE/'PHASE5_5_SUPPLIER_BASKETS.md').write_text('\n'.join(md),encoding='utf-8')
    # Complete audit of every former external-supplier line, including unchanged exact MPNs.
    audit=['# Phase 5.5 external-line reconciliation','',
           '| ID / refs | Phase5.4 supplier | Original MPN | Proposed MPN | Supplier / SKU | Result |',
           '|---|---|---|---|---|---|']
    for r in rows:
        if r['original_supplier'] in ['LCSC','TME','Deferred']:continue
        audit.append(f"| {r['group_id']} / {r['references']} | {r['original_supplier']} | {r['original_mpn']} | {r['manufacturer_mpn']} | {r['supplier']} / {r['distributor_sku']} | {'Exact identity' if r['original_mpn']==r['manufacturer_mpn'] else 'Proposed replacement'} |")
    (BASE/'PHASE5_5_EXTERNAL_LINES.md').write_text('\n'.join(audit)+'\n',encoding='utf-8')
    print(json.dumps(summary))

if __name__=='__main__':main()
