"""Reconcile approved purchase data into CSV-table intermediates and checklist.

Read-only supplier observations; never imports CAD APIs or submits orders.
The companion artifact builder writes the three final CSVs.
"""
import csv
import json
import re
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'hardware/v4/sourcing'
EV = ROOT/'hardware/v4/evidence/phase5-6-sourcing'
OLD_MASTER = ROOT/'hardware/v4/evidence/phase5-1-sourcing/entry-phase5-0-sourcing/MASTER_PURCHASING_BOM.csv'

def read_csv(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig',newline='')))

def money(v):
    return str(v.quantize(D('.01'), rounding=ROUND_HALF_UP))

SPECS = {
 'L2':'4.7uH +/-20%; Coilank AAPS0530M4R7F; nonpolar',
 'L3':'6.8uH +/-20%; Bourns SRP5050FA-6R8M; nonpolar',
 'R32':'31.6kohm +/-0.1%; 25ppm/K; 0402',
 'R33':'10kohm +/-0.02%; 10ppm/K; 0402',
 'R60':'16kohm +/-0.1%; 25ppm/K; 0603',
 'R61':'3.01kohm +/-0.1%; 25ppm/K; 0603',
 'U1':'ESP32-C3-MINI-1-H4X; 4MB quad flash; PCB antenna; -40..105C',
 'C39':'33nF +/-10%; 50V X7R; 0402',
 'R5':'27kohm +/-1%; 100ppm/K; 0.125W; 0805; default 4S only',
 'R23':'8.2kohm +/-1%; 100ppm/K; 0.0625W; 0402',
 'R63':'38.3kohm +/-1%; 100ppm/K; 0.1W; 0603',
}
PAIRS = {'R32':'MAIN_FB_PAIR_R32_R33','R33':'MAIN_FB_PAIR_R32_R33',
         'R60':'F5_FB_PAIR_R60_R61','R61':'F5_FB_PAIR_R60_R61'}

def lcsc_observation(row, obs):
    text = (EV/(row['group_id']+'.txt')).read_text(encoding='utf-8')
    assert row['distributor_sku'] in obs['url'], row['group_id']
    assert row['manufacturer_mpn'] in text, (row['group_id'], 'MPN not on page')
    body = text.split('In-Stock:',1)[1].split('Standard Packaging',1)[0]
    tiers = [(int(q.replace(',','')),D(p)) for q,p in re.findall(r'(\d[\d,]*)\+\s*\$\s*([\d.]+)',body)]
    assert tiers
    qty = int(row['purchase_quantity'])
    price = max((t for t in tiers if t[0]<=qty),key=lambda t:t[0])[1]
    return dict(stock=int(obs['stock'].replace(',','')), MOQ=int(obs['minimum']),
                multiple=int(obs['multiple']),unit_price=price,currency='USD',
                date=obs['time'],url=obs['url'],file=row['group_id']+'.txt',tiers=tiers)

def tme_observation(row, obs):
    text = (EV/obs['text_file']).read_text(encoding='utf-8')
    assert row['manufacturer_mpn'] in text
    assert 'CZK' in text and '/cz/' in obs['url']
    stock = re.search(r'([\d\s\u00a0]+) skladem v TME',text)
    assert stock
    body = text.split('Cena bez DPH [CZK/',1)[1].split('Zeptejte se na cenu',1)[0]
    tiers = [(int(re.sub(r'\s','',q)),D(p)) for q,p in re.findall(r'(\d[\d \u00a0]*)\+\s*\n([\d.]+)',body)]
    qty=int(row['purchase_quantity'])
    price=max((t for t in tiers if t[0]<=qty),key=lambda t:t[0])[1]
    multiple=int(re.search(r'Násobnost:\s*(\d+)',text).group(1))
    return dict(stock=int(re.sub(r'\D','',stock.group(1))),MOQ=multiple,multiple=multiple,
                unit_price=price,currency='CZK',date=obs['time'],url=obs['url'],
                file=obs['text_file'],tiers=tiers)

def main():
    rows=read_csv(EV/'entry-sourcing/PHASE5_5_SHOPPING_LIST.csv')
    pop=read_csv(EV/'entry-sourcing/REFERENCE_POPULATION.csv')
    harness={r['item_id']:r['notes'] for r in read_csv(EV/'entry-sourcing/HARNESS_AND_ASSEMBLY_BOM.csv')}
    original={r['references']:r['group_id'] for r in read_csv(OLD_MASTER)}
    live={r['id']:r for r in json.loads((EV/'browser-live.json').read_text(encoding='utf-8'))}
    tme={r['id']:r for r in json.loads((EV/'tme-live.json').read_text(encoding='utf-8'))}
    result=[]
    observations=[]
    for r in rows:
        gid=original.get(r['references'],r['group_id']) if r['scope']=='PCB_ELECTRONICS' else r['group_id']
        o=lcsc_observation(r,live[r['group_id']]) if r['supplier']=='LCSC' else tme_observation(r,tme[r['group_id']])
        q=int(r['purchase_quantity'])
        assert q>=o['MOQ'] and q%o['multiple']==0 and q<=o['stock'],(gid,q,o)
        pair=PAIRS.get(r['references'],'')
        if pair:
            note='FIT BOTH MEMBERS TOGETHER: '+pair
        elif r['group_id']=='C32-COMPARE':
            note='APPROVED comparison stock only; default assembly remains Yageo C125847; never fit both at C32'
        elif r['group_id'] in ('R5-2S','R5-3S','P037'):
            note='R5 mutually exclusive profiles: 2S=8.2k; 3S=13.7k; 4S=27k. Buy all three; fit exactly one per board.'
        elif r['references']=='Q3 Q8 Q9':
            note='Fit approved AO3400A; CAD still names PMV16UN'
        else:
            note='Approved exact purchase; preserve original ordered PCB.'
        if r['group_id']=='H03': note+=' EXACT key-B housing; five required; no spare; stock not reserved.'
        if gid in ('H09','H10'): note+=' Unit=m; order 5 metres, not 5 rolls.'
        if gid=='H11': note+=' Unit=one 10m roll; order 2 rolls=20m, not 2m or 20 rolls.'
        if gid in harness and gid in {'H01','H02','H03','H04','H05','H06','H07','H08'}:
            note+=' Harness assembly: '+harness[gid]
        if gid=='P053': note+=' Fit 16k, despite unchanged 53k schematic metadata.'
        if gid=='P054': note+=' Fit 3.01k, despite unchanged 10k schematic metadata.'
        line = dict(supplier_sku=r['distributor_sku'],quantity=q,unit=r['unit'],direct_product_url=o['url'],
          manufacturer=r['manufacturer'],manufacturer_mpn=r['manufacturer_mpn'],group_id=gid,
          phase5_5_group_id=r['group_id'],references=r['references'],scope=r['scope'],
          fitted_quantity_five_F5=int(r['fitted_quantity']),desired_before_MOQ=int(r['desired_before_MOQ']),
          spares_planned=int(r['spares_planned']),alternative_profile_stock=int(r['alternative_R5_stock']),
          MOQ=o['MOQ'],multiple=o['multiple'],MOQ_or_tier_excess=int(r['MOQ_or_tier_excess']),
          observed_stock=o['stock'],unit_price_net=str(o['unit_price']),
          line_total_net=str(o['unit_price']*q),currency=o['currency'],
          price_status='LIVE_PUBLIC_PRODUCT_PRICE_NOT_BINDING_QUOTE',price_region='International USD' if r['supplier']=='LCSC' else 'Czech Republic CZK',
          observed_utc=o['date'],stock_status='IN_STOCK_PUBLIC_UNRESERVED',
          approval='OWNER_APPROVED_2026-10-20_FINAL',pair_or_profile=pair,
          prior_purchasing_mpn=r['original_mpn'],notes=note,
          evidence='../evidence/phase5-6-sourcing/'+o['file'])
        result.append((r['supplier'],line))
        observations.append(dict(group_id=gid,phase5_5_group_id=r['group_id'],supplier=r['supplier'],
                                 **{k:(str(v) if isinstance(v,D) else v) for k,v in o.items() if k!='tiers'},
                                 tiers=[[q,str(p)] for q,p in o['tiers']]))
    assert len(result)==78
    tables={}
    for supplier in ('LCSC','TME'):
        selected=sorted([r for s,r in result if s==supplier],key=lambda r:r['group_id'])
        tables['FINAL_'+supplier+'_ORDER.csv']=dict(columns=list(selected[0]),rows=selected)
    byref={ref:r for s,r in result if r['scope']=='PCB_ELECTRONICS' and r['fitted_quantity_five_F5'] for ref in r['references'].split()}
    assembly=[]
    for p in pop:
        ref=p['reference']; fitted=int(p['qty_per_F5']); r=byref.get(ref)
        assert bool(r)==bool(fitted),(ref,fitted)
        spec=SPECS.get(ref,p['value_ratings_tolerance']) if fitted else 'DO NOT FIT / NO PURCHASE'
        pair=PAIRS.get(ref,'')
        notes=r['notes'] if fitted else ('DNP: leave empty' if p['F5_state']=='DNP' else 'PCB feature or probe geometry only; no separately fitted hardware')
        old=p['original_recorded_mpn']
        diff='PURCHASING_SPEC_ASSIGNED; CAD MPN unresolved' if old in ('OPEN','') or old.startswith('OPEN:') else ('MPN_DIFFERS_FROM_CAD' if r and old!=r['manufacturer_mpn'] else 'RETAINED_MPN')
        if ref in ('R60','R61'): diff='VALUE_DIFFERS_FROM_CAD: '+p['functionality']+' -> '+spec
        if not fitted: diff='NO_ASSEMBLY_PART'
        assembly.append(dict(reference=ref,scope='PCB_REFERENCE',group_id=r['group_id'] if r else ('P058' if ref in ('TP1','TP3','TP4') else ''),
          phase5_5_group_id=r['phase5_5_group_id'] if r else '',population='FIT_F5' if fitted else p['F5_state'],
          quantity_per_F5=fitted,quantity_five_F5=5*fitted,unit='pcs',schematic_value_metadata=p['functionality'],
          schematic_MPN_metadata=old,prior_purchasing_MPN=p['selected_mpn'],assembly_value_and_ratings=spec,
          approved_manufacturer=r['manufacturer'] if r else '',approved_assembly_MPN=r['manufacturer_mpn'] if r else '',
          supplier=('LCSC' if r['currency']=='USD' else 'TME') if r else '',supplier_sku=r['supplier_sku'] if r else '',
          direct_product_url=r['direct_product_url'] if r else '',ordered_group_quantity=r['quantity'] if r else 0,
          actual_ordered_footprint=p['actual_kicad_footprint'],metadata_difference=diff,
          paired_fit_requirement=pair,approval='OWNER_APPROVED_2026-10-20_FINAL' if fitted else 'APPROVED_EXCLUSION',notes=notes))
    # Distinct off-board harness and alternative stock: never inflate PCB count.
    for s,r in result:
        if r['scope']=='PCB_ELECTRONICS' and r['fitted_quantity_five_F5']: continue
        stock=r['group_id'] in ('R5-2S','R5-3S','C32-COMPARE')
        quantity=r['fitted_quantity_five_F5'] if not stock else 0
        spec={'R5-2S':'8.2kohm +/-1%; 100ppm/K; 0805; 2S profile only',
              'R5-3S':'13.7kohm +/-1%; 100ppm/K; 0805; 3S profile only',
              'C32-COMPARE':'2.2uF +/-10%; 50V X7R; 0805; comparison stock only'}.get(r['group_id'],r['manufacturer_mpn'])
        assembly.append(dict(reference=r['references'],scope='ALTERNATIVE_STOCK' if stock else r['scope'],group_id=r['group_id'],
          phase5_5_group_id=r['phase5_5_group_id'],population='STOCK_ONLY_DO_NOT_ADD_POSITION' if stock else 'HARNESS_NOT_PCB',
          quantity_per_F5=quantity//5 if quantity else 0,quantity_five_F5=quantity,unit=r['unit'],
          schematic_value_metadata='Not an additional PCB position',schematic_MPN_metadata='',prior_purchasing_MPN=r['prior_purchasing_mpn'],
          assembly_value_and_ratings=spec,approved_manufacturer=r['manufacturer'],approved_assembly_MPN=r['manufacturer_mpn'],
          supplier=s,supplier_sku=r['supplier_sku'],direct_product_url=r['direct_product_url'],ordered_group_quantity=r['quantity'],
          actual_ordered_footprint='Off-board / stock only',metadata_difference='APPROVED_OFF_BOARD_OR_STOCK',
          paired_fit_requirement='',approval='OWNER_APPROVED_2026-10-20_FINAL',notes=r['notes']))
    assert len(assembly)==168
    assert sum(r['quantity_five_F5'] for r in assembly if r['scope']=='PCB_REFERENCE')==655
    tables['FINAL_ASSEMBLY_BOM.csv']=dict(columns=list(assembly[0]),rows=assembly)
    (EV/'final-tables.json').write_text(json.dumps(tables,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (EV/'observations.json').write_text(json.dumps(observations,indent=2)+'\n',encoding='utf-8')
    totals={s:sum(D(r['line_total_net']) for ss,r in result if ss==s) for s in ('LCSC','TME')}
    changes=[(r['group_id'],r['manufacturer_mpn'],r['unit_price_net']) for s,r in result if s=='LCSC' and D(r['unit_price_net']) != D(next(x['unit_price'] for x in rows if x['group_id']==r['phase5_5_group_id']))]
    summary=dict(rows={s:sum(ss==s for ss,r in result) for s in totals},LCSC_goods_net_USD=str(totals['LCSC']),TME_goods_net_CZK=str(totals['TME']),
       TME_goods_VAT21_CZK=money(totals['TME']*D('.21')),TME_goods_gross_CZK=money(totals['TME']*D('1.21')),
       TME_goods_plus_standard_delivery_gross_CZK=money((totals['TME']+140)*D('1.21')),LCSC_price_changes=changes,
       landed_total=None,all_prices_live_public_not_quote=True,all_quantities_stock_covered=True)
    (EV/'cost-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))

if __name__=='__main__': main()
