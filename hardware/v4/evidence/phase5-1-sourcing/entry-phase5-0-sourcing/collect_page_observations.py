"""Extract dated supplier page observations from saved research, never fetch or order."""
import csv
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
EV = BASE.parent / 'evidence/phase5-0-sourcing'
def main():
    selected = json.loads((BASE/'selections.json').read_text())
    mpns = {s['mpn'] for s in selected.values()}


    def norm(s):
        return re.sub('[^A-Z0-9]', '', s.upper())


    records = []
    for path in sorted(EV.glob('*.txt')):
        raw = path.read_text(encoding='utf-8')
        for block in re.split(r'(?m)(?=^[^\n]+ \(https://)', raw):
            h = re.match(r'([^\n]+) \((https://[^\n]+)\)\n', block)
            if not h:
                continue
            title, url = h.groups()
            if not any(host in url for host in ('lcsc.com/product-detail/', 'digikey.', 'tme.eu/', 'tme.com/', 'coilcraft.com/')):
                continue
            if '/models/' in url or 'product-image' in url:
                continue
            exact = [m for m in mpns if norm(m) in norm(title)]
            if len(exact) != 1:
                continue
            mpn = exact[0]
            direct = bool(re.search(r'Source: (?:find|open)\(', block))
            freshness = re.search(r'Crawled: ([^;\n]+)', block)
            freshness = freshness.group(1) if freshness else 'not supplied'
            # Search/index snippets locate identities only. Never promote snippet stock.
            lines = re.sub(r'(?m)^L\d+: ?', '', block)
            o = dict(mpn=mpn, url=url, date='2026-10-19', evidence=f'../evidence/phase5-0-sourcing/{path.name}',
                     freshness=f'Retrieved 2026-10-19; provider cache: {freshness}; page observation, not reservation',
                     availability='UNVERIFIED', supplier='', sku='',
                     notes='Checkout stock, tax, freight, lead time and actual tier require recheck; no cart created')
            if 'lcsc.com' in url:
                o['supplier']='LCSC'
                sku=re.search(r'(C\d{3,})(?:[.\/?_]|$)',url)
                if sku:
                    o['sku']=sku.group(1)
            elif 'digikey.' in url:
                o['supplier']='DigiKey'
                sku=re.search(r'DigiKey Part Number\s*\|\s*([^\n]+)',lines)
                if sku:
                    # Prefer cut tape over full reel / Digi-Reel.
                    cut=re.search(r'([A-Za-z0-9,.-]+(?:CT-ND|\-1-ND))',sku.group(1))
                    o['sku']=cut.group(1) if cut else sku.group(1).split(' - ')[0]
            elif 'tme.' in url:
                o['supplier']='TME'
                slug=re.search('/details/([^/]+)/',url)
                o['sku']=slug.group(1).upper() if slug else ''
            elif 'coilcraft.com' in url:
                o['supplier']='Coilcraft Europe (direct quote)'
                o['sku']=mpn
            if direct:
                stock=re.search(r'In-Stock:\s*([\d,]+)',lines)
                tme_stock=re.search(r'([\d, ]+) in TME stock',lines)
                if stock or tme_stock:
                    o['stock']=int(re.sub(r'\D','',(stock or tme_stock).group(1)))
                    o['availability']='PAGE_IN_STOCK' if o['stock'] else 'OUT_OF_STOCK'
                if re.search(r'Out of Stock|In Stock: 0|out of stock and can be placed', lines, re.I):
                    o['availability']='OUT_OF_STOCK'; o['stock']=0
                if 'Not available now' in lines:
                    o['availability']='NOT_AVAILABLE'
                if 'no longer available at DigiKey' in lines:
                    o['availability']='NO_LONGER_AVAILABLE'
                terms=re.search(r'Minimum:\s*([\d,]+) Multiple:\s*([\d,]+)',lines)
                if terms:
                    o['moq'],o['multiple']=[int(x.replace(',','')) for x in terms.groups()]
                prices=re.findall(r'(?m)^(\d[\d,]*)\+?\s+\|\s*\$\s*(\d+\.\d+)',lines)
                if prices:
                    q,p=prices[0];o['unit_price_usd']=float(p);o['price_break_qty']=int(q.replace(',',''))
                    o['price_basis']='Supplier page USD tier; excludes tax/freight; indicative if cached; not an executable quote'
                if o['supplier']=='DigiKey' and q=='1' and 'Cut Tape' in lines:
                    o['moq']=1
                    o['multiple']=1
                if 'Reference Only' in lines:
                    o['price_basis']='REFERENCE ONLY - unavailable; excluded from usable subtotal'
                # TME English USD table. Other currencies remain unquoted in this model.
                tme_price=re.search(r'Net price for quantities from (\d+) pcs - ([\d.]+) USD',lines)
                if tme_price:
                    o['unit_price_usd']=float(tme_price.group(2));o['price_break_qty']=int(tme_price.group(1))
                    o['price_basis']='TME USD net page observation, cache dated; Czech VAT/freight not quoted'
                minq=re.search(r'Minimum order quantity: (\d+)',lines)
                mult=re.search(r'(?:Multiples|Multiplicity): ([\d ]+)',lines)
                if minq:
                    o['moq']=int(minq.group(1))
                if mult:
                    o['multiple']=int(mult.group(1).replace(' ',''))
                if tme_price and 'multiple' in o and 'moq' not in o:
                    o['moq']=int(tme_price.group(1))
            preferred = o['supplier'] in ('TME','LCSC')
            score=(100 if direct else 0)+(30 if freshness=='today' else 20 if freshness=='yesterday' else 0)+(10 if 'moq' in o else 0)+(10 if 'unit_price_usd' in o else 0)+(5 if preferred else 0)
            records.append((mpn,score,o))

    result={}
    for mpn in sorted(mpns):
        candidates=[(sc,o) for m,sc,o in records if m==mpn]
        if candidates:
            _,chosen=max(candidates,key=lambda x:x[0])
            alternates=[o['url'] for _,o in candidates if o['url']!=chosen['url']]
            chosen['alternate_url']=next(iter(dict.fromkeys(alternates)),'')
            result[mpn]=chosen

    # Preserve exact pre-existing distributor links when a lookup did not yield a page.
    # These are identity candidates, never fresh stock or price observations.
    with (BASE.parent/'evidence/phase4-22a-manufacturing-preparation/F5-population-review.csv').open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            if row['reference'] not in selected:
                continue
            mpn=selected[row['reference']]['mpn']
            u=row['recorded_source']
            if mpn in result or not u.startswith('https://') or not any(x in u for x in ('tme.eu/','digikey.')) or row['reference']=='J6':
                continue
            supplier='TME' if 'tme.eu/' in u else 'DigiKey'
            result[mpn]=dict(supplier=supplier,url=u,sku='',availability='UNVERIFIED',
                             date='',freshness='Retained historical identity link only; current commercial fields unverified',
                             evidence='../evidence/phase4-22a-manufacturing-preparation/F5-population-review.csv',
                             notes='Historical Bought is not owner inventory; fresh exact quote required')

    # Explicit review overrides, always traceable to saved pages / retained selections.
    overrides=json.loads((BASE/'observation_overrides.json').read_text())
    for mpn,data in overrides.items():
        result.setdefault(mpn,{}).update(data)
    (BASE/'supplier_observations.json').write_text(json.dumps(result,indent=2)+'\n')
    (EV/'all-page-observations.json').write_text(json.dumps([o for _,_,o in records],indent=2)+'\n')
    print(f'{len(result)} identities with at least a source candidate; {sum("unit_price_usd" in o for o in result.values())} USD page prices; stock freshness remains explicit')


if __name__ == '__main__':
    main()
