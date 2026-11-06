"""Apply explicit Phase5.4 owner decisions and reviewed commercial evidence only."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
EV = BASE.parent / 'evidence/phase5-4-sourcing'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')


def main():
    observations = read(BASE/'phase5_4_observations.json')
    for key, changes in {
        'BZT52C12-TP': dict(sku='BZT52C12-TPMSCT-ND',
            notes='Exact MCC cut-tape SKU verified from DigiKey identity header; no substitution. Public dated stock/price, not a reservation.',
            evidence='../evidence/phase5-4-sourcing/refresh-P013.json; ../evidence/phase5-4-sourcing/research-25.json'),
        'GCM1555C1H102JA16D': dict(stock=42600, moq=100, multiple=100,
            unit_price_usd=.0094, price_break_qty=100, price_tiers_usd=[dict(qty=100,price=.0094)],
            availability='PAGE_IN_STOCK', refresh_status='PHASE5_4_REVIEWED_CONFLICTING_CACHED_TERMS',
            freshness='Retrieved 2026-10-19; provider cache 4 months ago; older than prior 50-piece listing; conflict explicit',
            evidence='../evidence/phase5-4-sourcing/research-14.json',
            notes='English page now shows MOQ/multiple100 and stock42600; earlier newer-cache quote was MOQ50/stock8450/USD.0133. Conservative order100 at cached USD.0094; verify regional terms before purchase.'),
        'BAS116H,115': dict(stock=55050,moq=10,multiple=10,unit_price_usd=.0669,
            price_break_qty=10,price_tiers_usd=[dict(qty=10,price=.0669),dict(qty=100,price=.0524)],
            availability='PAGE_IN_STOCK',refresh_status='PHASE5_4_REVIEWED_GERMAN_USD_PAGE',
            freshness='Retrieved 2026-10-19; provider cache today; not reserved inventory',
            evidence='../evidence/phase5-4-sourcing/research-15.json',
            notes='Exact Nexperia BAS116H,115; German-language LCSC page quotes USD; quantity20 retained.'),
        'XAL5050-682MEC': dict(moq=1,multiple=1,unit_price_usd=None,price_tiers_usd=[],
            supplier='Coilcraft Europe (quote needed)',
            availability='UNVERIFIED',stock=None,refresh_status='PHASE5_4_LIVE_UK_EUR_NO_ALLOCATION',
            notes='UK/EUR live quantity5: EUR2.62/pc indication, stock blank. No dispatch/freight/lead-time commitment. DigiKey Marketplace newer page says no longer available; older USD4.53/3944stock/$10 freight offer rejected. Exact source hold; do not substitute.'),
        'RN73C1E31K6BTD': dict(moq=1,multiple=1,unit_price_usd=None,price_tiers_usd=[],
            unit_price_native=.80,currency_native='EUR',price_tiers_native=[dict(qty=1,price=.80),dict(qty=10,price=.562)],
            url='https://www.mouser.lt/en/ProductDetail/TE-Connectivity-AMP/RN73C1E31K6BTD?qs=sGAEpiMZZMtlubZbdhIBIFl9NVT0tk6Fnfv9LT%252Bs5DY%3D',
            availability='PAGE_IN_STOCK',stock=3207,refresh_status='PHASE5_4_EU_EUR_ALLOWANCE_CZ_DELIVERY_OPEN',
            freshness='Retrieved 2026-10-19; Mouser Lithuania provider cache last month; not a Czech quotation or reservation',
            evidence='../evidence/phase5-4-sourcing/research-23.json',
            notes='Exact Mouser279-RN73C1E31K6BTD; LT dated offer stock3207, MOQ/multiple1, EUR.80 at1 (8=EUR6.40);10tier.562 (10=EUR5.62) optional only. Czech price/dispatch/freight not verified. No exact DigiKey/TME/LCSC/Farnell small-order offer found; no 25ppm substitution. HU HUF2288.80/8 retained in research as cross-region evidence only.'),
    }.items():
        observations[key].update(changes)
    save(BASE/'phase5_4_observations.json', observations)
    selections = read(BASE/'selections.json')
    for refs, status, note in [
        (['C32'],'OWNER_APPROVED_PROTOTYPE','Owner Phase5.4 approves Yageo CC0805KKX7R9BB225 quantity10 for prototype with known DC-bias loss; additional TDK alternative stays separate and pending approval.'),
        (['C33','C45','C64','C65'],'OWNER_APPROVED_PROTOTYPE','Owner Phase5.4 approves TDK C3216X5R1V226MTJ00E/C342620 quantity30 for prototype; documented DC-bias uncertainty accepted, original25uF bank basis NOT guaranteed. Preserve Phase5.3 bring-up observations.'),
        (['C63'],'OWNER_APPROVED','Owner Phase5.4 approves Yageo CC0603KRX7R9BB333 quantity8 replacing obsolete Murata GRM188R71H333KA61D in purchasing only.'),
    ]:
        for ref in refs:
            selections[ref]['status']=status
            selections[ref]['notes']=note
            selections[ref]['basis']='Explicit owner Phase5.4 purchasing approval; no CAD changes'
    save(BASE/'selections.json', selections)
    harness = read(BASE/'harness_inputs.json')
    for r in harness:
        o = observations.get(r['mpn'])
        if not o or not r['direct_product_url']:
            continue
        for target, source in [('unit_price_usd','unit_price_usd'),('observed_stock','stock'),
            ('MOQ','moq'),('multiple','multiple'),('commercial_freshness','freshness'),
            ('commercial_evidence','evidence'),('supplier_packaging','packaging')]:
            if source in o:
                r[target]=o[source]
        r['phase5_2_refresh_status']=o['refresh_status']
        r['verification_date']='2026-10-19'
    save(BASE/'harness_inputs.json',harness)
    alternative = dict(line_id='C32-ALT',references='C32 alternative stock only',
        manufacturer='TDK',mpn='C2012X7R1H225K125AC',
        specifications='2.2uF +/-10%;50V;X7R;-55..125C;0805;2.0+/-0.2 x1.25+/-0.2 x1.25+/-0.2mm',
        footprint='Capacitor_SMD:C_0805_2012Metric',supplier='DigiKey',
        sku='445-5968-1-ND',url='https://www.digikey.com/en/products/detail/tdk-corporation/C2012X7R1H225K125AC/2443446',
        fitted_quantity=0,comparison_stock=10,spares=0,moq=1,multiple=1,order_quantity=10,
        unit_price=.322,extended_price=3.22,currency='USD',stock=476200,
        price_status='Dated public page allowance; cache last week; not a firm quote; freight/tax extra',
        approval='PENDING_OWNER_APPROVAL; additional stock, not a selected replacement',
        evidence='../evidence/phase5-4-sourcing/research-08.json',
        dc_bias_csv='../evidence/phase5-4-sourcing/TDK-C32-dc-bias.csv')
    save(BASE/'phase5_4_c32_alternative.json',alternative)
    print('Applied three explicit approvals, reviewed evidence, refreshed harness; separate C32 alternative pending.')


if __name__ == '__main__':
    main()
