"""Parse saved public supplier responses. No network, CAD, cart or order operations."""
import csv
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
EV = BASE.parent / 'evidence/phase5-4-sourcing'


def parse(block, row, evidence):
    clean = re.sub(r'L\d+: ?', '', block)
    age = re.search(r'Crawled: ([^;\n]+)', clean)
    stock = re.search(r'In-Stock:\s*([\d,]+)', clean)
    if not stock:
        stock = re.search(r'([\d, ]+) in TME stock', clean)
    terms = re.search(r'Minimum:\s*([\d,]+) Multiple:\s*([\d,]+)', clean)
    prices = [(int(q.replace(',', '')), float(p)) for q, p in
              re.findall(r'(?m)^(\d[\d,]*)\+?\s+\|\s*\$\s*([\d.]+)', clean)]
    if not prices:
        prices = [(int(q.replace(',', '')), float(p)) for q, p in
                  re.findall(r'(?m)^(\d[\d,]*)\+?\$\s*([\d.]+)\$', clean)]
    if row['candidate_supplier'] == 'TME':
        prices = [(int(q), float(p)) for q, p in re.findall(
            r'Net price for quantities from (\d+) pcs - ([\d.]+) USD', clean)]
    qty = int(row['proposed_purchase_qty'])
    eligible = [(q, p) for q, p in prices if q <= qty]
    o = dict(mpn=row['mpn'], supplier=row['candidate_supplier'],
             url=row['direct_product_url'], sku=row['distributor_sku'],
             date='2026-10-19', evidence=evidence,
             freshness='Retrieved 2026-10-19; provider cache ' + (age.group(1) if age else 'not supplied') + '; not reserved inventory',
             refresh_status='PHASE5_4_PAGE_REFRESH' if stock and eligible else 'PHASE5_4_REFRESH_INCOMPLETE',
             availability='PAGE_IN_STOCK' if stock else 'UNVERIFIED',
             notes='Public page observation only; confirm regional stock, tier, dispatch, freight and taxes when owner orders; no stock reserved',
             price_basis='Dated public USD page allowance, net of freight/tax/handling; not a firm quotation',
             price_tiers_usd=[dict(qty=q, price=p) for q, p in prices])
    if stock:
        o['stock'] = int(re.sub(r'\D', '', stock.group(1)))
    if eligible:
        q, p = max(eligible)
        o.update(unit_price_usd=p, price_break_qty=q)
    if terms:
        o.update(moq=int(terms.group(1).replace(',', '')), multiple=int(terms.group(2).replace(',', '')))
    elif row['candidate_supplier'] == 'DigiKey' and prices and prices[0][0] == 1:
        o.update(moq=1, multiple=1)
    elif row['candidate_supplier'] == 'TME':
        m = re.search(r'Minimum order quantity: (\d+)', clean)
        n = re.search(r'Multiplicity: (\d+)', clean)
        if m and n:
            o.update(moq=int(m.group(1)), multiple=int(n.group(1)))
    if 'no longer available at DigiKey' in clean:
        o['availability'] = 'NO_LONGER_AVAILABLE'
    packaging = re.search(r'Standard Packaging ([^\n]+)', clean)
    o['packaging'] = ('Small-quantity pieces; standard packaging ' + packaging.group(1)) if packaging else 'Plain cut tape / bulk; no paid reeling'
    if not o['sku'] and row['candidate_supplier'] == 'DigiKey':
        sku = re.search(r'DigiKey Part Number\s*\|\s*(.+)', clean)
        if sku:
            candidates = re.findall(r'[A-Za-z0-9.,-]+(?:CT-ND|-1-ND|-ND)', sku.group(1))
            o['sku'] = next((x for x in candidates if x.endswith(('CT-ND', '-1-ND'))), candidates[0] if candidates else '')
    return o


def main():
    observations = {}
    ledger = []
    for path in sorted(EV.glob('refresh-*.json')):
        if path.name == 'refresh-ledger.json':
            continue
        saved = json.loads(path.read_text(encoding='utf-8-sig'))
        blocks = saved['response'].split('-' * 80 + '\n')
        assert len(blocks) == len(saved['rows']), (path.name, len(blocks), len(saved['rows']))
        for block, row in zip(blocks, saved['rows']):
            o = parse(block, row, '../evidence/phase5-4-sourcing/' + path.name)
            observations[row['mpn']] = o
            ledger.append(dict(line=row.get('group_id', row.get('item_id')), **o))
    (BASE/'phase5_4_observations.json').write_text(json.dumps(observations, indent=2)+'\n', encoding='utf-8')
    (EV/'refresh-ledger.json').write_text(json.dumps(ledger, indent=2)+'\n', encoding='utf-8')
    incomplete = [x['line'] for x in ledger if x['refresh_status'].endswith('INCOMPLETE')]
    print(json.dumps(dict(lines=len(ledger), incomplete=incomplete)))


if __name__ == '__main__':
    main()
