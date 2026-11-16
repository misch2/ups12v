"""Parse saved read-only web observations. No network, carts, CAD or messages.

The raw responses are the evidence; missing fields stay unknown. Run before build.
"""
import csv
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
EV = OUT.parent / 'evidence/phase5-2-sourcing'
DATE = '2026-10-19'


def norm(s):
    return re.sub(r'[^A-Z0-9]', '', s.upper())


def main():
    selected = json.loads((OUT/'selections.json').read_text(encoding='utf-8'))
    old = json.loads((OUT/'supplier_observations.json').read_text(encoding='utf-8'))
    old.update(json.loads((OUT/'phase5_1_observations.json').read_text(encoding='utf-8')))
    extra = ['LM74700QDBVTQ1', 'C1608X7R1C105K080AC', 'PMV16XNR', 'AO3400A',
             'C3216X5R1V226MTJ00E']
    harness = json.loads((OUT/'harness_inputs.json').read_text(encoding='utf-8'))
    extra += [r['mpn'] for r in harness if r['direct_product_url']]
    mpns = sorted({s['mpn'] for s in selected.values()} | set(old) | set(extra), key=len, reverse=True)
    records = []
    for path in sorted(EV.glob('*.txt')):
        raw = path.read_text(encoding='utf-8')
        for block in re.split(r'(?m)(?=^[^\n]+ \(https://)', raw):
            h = re.match(r'([^\n]+) \((https://[^\n]+)\)\n', block)
            if not h or 'Source: ' not in block:
                continue
            title, url = h.groups()
            if not any(x in url for x in ('lcsc.com/product-detail/', 'digikey.com/', 'tme.eu/', 'tme.com/')):
                continue
            exact = [m for m in mpns if norm(m) in norm(title)]
            if not exact:
                continue
            # PMV16XN product type is not the PMV16XNR procurement identity.
            mpn = exact[0]
            lines = re.sub(r'(?m)^L\d+(?:@P\d+(?:-\d+)?)?: ?', '', block)
            cache = re.search(r'Crawled: ([^;\n]+)', block)
            cache = cache.group(1) if cache else 'not supplied'
            o = dict(mpn=mpn, url=url, date=DATE,
                     evidence=f'../evidence/phase5-2-sourcing/{path.name}',
                     freshness=f'Retrieved {DATE}; provider cache {cache}; not reserved/live checkout inventory',
                     refresh_status='PAGE_RETRIEVED_CACHED_OBSERVATION', availability='UNVERIFIED',
                     price_basis='Cached USD page tier excluding tax, freight and handling; not an executable quote',
                     notes='Refresh attempted Phase5.2. Stock, regional price and delivery must be reconfirmed before order')
            stock = re.search(r'In-Stock:\s*([\d,]+)', lines)
            if 'lcsc.com' in url:
                o.update(supplier='LCSC', sku=re.search(r'C\d+', url).group(),
                         packaging='Loose small-quantity supply; standard reel size is not MOQ')
                terms = re.search(r'Minimum:\s*(\d[\d,]*) Multiple:\s*(\d[\d,]*)', lines)
                if terms:
                    o['moq'], o['multiple'] = (int(x.replace(',', '')) for x in terms.groups())
                tiers = re.findall(r'(?m)^(\d[\d,]*)\+\s*\|\s*\$\s*([\d.]+)', lines)
                # Legacy page layout: 100+$ 0.0094$ 0.94.
                if not tiers:
                    tiers = re.findall(r'(?m)^(\d[\d,]*)\+\$\s*([\d.]+)\$', lines)
                pack = re.search(r'Standard Packaging ([^\n]+)', lines)
                if pack:
                    o['packaging'] = 'Small-quantity pieces; standard packaging '+pack.group(1)
            elif 'digikey.com' in url:
                o.update(supplier='DigiKey', packaging='Plain cut tape / bulk as listed; no Digi-Reel service')
                sku = re.search(r'DigiKey Part Number\s*(?:\|\s*)?([^\n]+(?:\n[^\n]+){0,7})', lines)
                if sku:
                    ct = re.search(r'([A-Za-z0-9.,-]+(?:CT-ND|-1-ND))', sku.group(1))
                    if ct:
                        o['sku'] = ct.group(1)
                # Do not collect alternative-product prices or full-reel tiers.
                pricing = lines.split('All prices are in USD')[-1].split('Tape & Reel')[0]
                tiers = re.findall(r'(?m)^(\d[\d,]*)\s*\|\s*\$([\d.]+)', pricing)
                if tiers and tiers[0][0] == '1':
                    o.update(moq=1, multiple=1)
            else:
                o.update(supplier='TME', sku=re.search(r'/details/([^/]+)',url).group(1).upper(),
                         packaging='Piece quantities / manufacturer reel; confirm supplied cut tape')
                stock = re.search(r'([\d, ]+) in TME stock', lines)
                terms = re.search(r'Minimum order quantity: (\d+)', lines)
                multiple = re.search(r'Multiplicity: (\d+)', lines)
                if terms and multiple:
                    o.update(moq=int(terms.group(1)), multiple=int(multiple.group(1)))
                tiers = re.findall(r'Net price for quantities from (\d+) pcs - ([\d.]+) USD', lines)
            if stock:
                o['stock'] = int(re.sub(r'\D','',stock.group(1)))
                o['availability'] = 'PAGE_IN_STOCK' if o['stock'] else 'OUT_OF_STOCK'
            if 'Not available now' in lines or 'no longer available at DigiKey' in lines:
                o['availability'] = 'NOT_AVAILABLE'
            if 'out of stock and can be placed' in lines:
                o['availability'] = 'OUT_OF_STOCK'
                o['stock'] = 0
            if tiers:
                o['price_tiers_usd'] = sorted([dict(qty=int(q.replace(',','')),price=float(p)) for q,p in tiers],key=lambda t:t['qty'])
                o['unit_price_usd'] = o['price_tiers_usd'][0]['price']
                o['price_break_qty'] = o['price_tiers_usd'][0]['qty']
                # Never interpret a supplier's two-decimal rounded 0.00 as free.
                if o['unit_price_usd'] == 0:
                    o.pop('unit_price_usd')
                o['price_tiers_usd'] = [t for t in o['price_tiers_usd'] if t['price']>0]
            score = 20*('stock' in o)+10*('moq' in o)+10*bool(tiers)+5*(cache=='today')
            records.append((mpn,score,o))
    result = {}
    for mpn in mpns:
        candidates = [(score,o) for m,score,o in records if m==mpn]
        if candidates:
            _,chosen = max(candidates,key=lambda x:x[0])
            # Carry old identity-only fields; never imply an old field was refreshed.
            o = dict(chosen)
            if not o.get('sku') and old.get(mpn,{}).get('sku') and old[mpn].get('supplier')==o.get('supplier'):
                o['sku'] = old[mpn]['sku']
                o['notes'] += '; SKU retained from preceding evidence'
            result[mpn] = o
    overrides=OUT/'phase5_2_reviewed_overrides.json'
    if overrides.exists():
        for mpn,o in json.loads(overrides.read_text(encoding='utf-8')).items():
            result.setdefault(mpn,{}).update(o)
    (OUT/'phase5_2_observations.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (EV/'parsed-observations.json').write_text(json.dumps([o for _,_,o in records],indent=2)+'\n',encoding='utf-8')
    for row in harness:
        o=result.get(row['mpn'])
        row['phase5_2_refresh_status'] = o['refresh_status'] if o else 'NO_EXACT_QUOTE; generic/unselected/out-of-scope material'
        if not o:
            continue
        for target,source in [('candidate_supplier','supplier'),('distributor_sku','sku'),('direct_product_url','url'),('MOQ','moq'),('multiple','multiple'),('observed_stock','stock'),('verification_date','date')]:
            if source in o:
                row[target]=o[source]
        quantity = row['qty_per_F5']*5+row['qty_per_batch']+row['spare_qty']
        if o.get('moq') and o.get('multiple'):
            import math
            quantity=math.ceil(max(quantity,o['moq'])/o['multiple'])*o['multiple']
        tier=next((t['price'] for t in reversed(o.get('price_tiers_usd',[])) if quantity>=t['qty']),None)
        if tier is not None:
            row['unit_price_usd']=tier
        row['commercial_freshness']=o['freshness']
        row['commercial_evidence']=o['evidence']
        row['supplier_packaging']=o.get('packaging','UNVERIFIED')
    (OUT/'harness_inputs.json').write_text(json.dumps(harness,indent=2)+'\n',encoding='utf-8')
    print(f'{len(result)} exact identities parsed; {sum("moq" in o and "unit_price_usd" in o for o in result.values())} with terms and price')


if __name__ == '__main__':
    main()
