"""Render reviewed Phase5.4 purchasing files; offline, no supplier/CAD operations."""
import csv
import json
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent
EV = OUT.parent/'evidence/phase5-4-sourcing'


def read(name):
    with (OUT/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def save(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def money(x):
    return f'{float(x):.4f}'.rstrip('0').rstrip('.') if x not in ('',None) else 'UNKNOWN'


def main():
    master=read('MASTER_PURCHASING_BOM.csv')
    harness=read('HARNESS_AND_ASSEMBLY_BOM.csv')
    alternative=json.loads((OUT/'phase5_4_c32_alternative.json').read_text())
    checklist=[]
    for r in master:
        approved=r['selection_status'] in ('OWNER_APPROVED','OWNER_APPROVED_PROTOTYPE')
        price=r['quoted_extended_price_native']
        status='OWNER_REVIEW_READY' if price else 'HOLD_EXACT_SUPPLY'
        if r['references']=='R32':status='EU_INDICATIVE_PRICE_CZ_DELIVERY_OPEN'
        alt='None selected; retain exact MPN'
        if r['references']=='C32':alt='Additional TDK C2012X7R1H225K125AC/445-5968-1-ND,10pcs/USD3.22, pending owner approval; separate stock line'
        if r['references']=='L2':alt='Exact same MPN at Coilcraft UK:5xEUR2.38=EUR11.90 indication; stock/freight open'
        if r['references']=='L3':alt='Exact Farnell2289071 backorder; full-reel5131621 MOQ250 rejected; stale DigiKey2457-XAL5050-682MEC-ND offer rejected'
        if r['references']=='D2':alt='Exact last-stock preferred; no substitute needed while available; no compatible alternative is approved'
        if r['references']=='R32':alt='Exact Mouser8xEUR.80=EUR6.40; optional10xEUR.562=EUR5.62; existing-supplier exact offer not found'
        checklist.append(dict(supplier=r['candidate_supplier'],group_id=r['group_id'],references=r['references'],
            manufacturer=r['manufacturer'],manufacturer_mpn=r['mpn'],distributor_sku=r['distributor_sku'],
            fitted_quantity=r['fitted_qty_scenario'],spares=r['suggested_spares'],
            alternative_R5_stock=r['alternative_profile_stock_qty'],MOQ=r['supplier_MOQ'],multiple=r['purchase_multiple'],
            purchase_quantity=r['proposed_purchase_qty'],MOQ_excess=r['MOQ_rounding_excess'],
            unit_price=r['quoted_unit_price_native'],extended_price=price,currency=r['quoted_currency'],
            selection_status=r['selection_status'],exact_identity_approval='APPROVED' if approved else 'REVIEW_EXACT_IDENTITY_WITH_OWNER',
            checklist_status=status,observed_stock=r['page_observed_stock'],observation_date='2026-10-19',
            freshness=r['stock_freshness'],quote_type='PUBLIC_PAGE_ALLOWANCE; no firm quotation',
            direct_url=r['direct_product_url'],alternatives=alt,evidence=r['evidence'],
            remaining_notes=r['outstanding_uncertainties']))
    checklist.sort(key=lambda r:(r['supplier'],r['group_id']))
    save('PROPOSED_ORDERING_CHECKLIST.csv',checklist)
    shopping=[dict(r,scope='PCB_ELECTRONICS') for r in checklist]
    for r in harness:
        if not r['direct_product_url']:continue
        row={k:'' for k in checklist[0]}
        row.update(supplier=r['candidate_supplier'],group_id=r['item_id'],references=r['associated_refs'],
            manufacturer=r['manufacturer'],manufacturer_mpn=r['mpn'],distributor_sku=r['distributor_sku'],
            fitted_quantity=r['required_scenario_qty'],spares=r['suggested_spares'],alternative_R5_stock=0,
            MOQ=r['MOQ'],multiple=r['multiple'],purchase_quantity=r['proposed_purchase_qty'],MOQ_excess=r['MOQ_rounding_excess'],
            unit_price=r['unit_price_usd'],extended_price=r['extended_scenario_cost_usd'],currency='USD',
            selection_status=r['selection_status'],exact_identity_approval='APPROVED' if r['selection_status'].startswith('OWNER_APPROVED') else 'REVIEW_EXACT_IDENTITY_WITH_OWNER',
            checklist_status='OWNER_REVIEW_READY',observed_stock=r['observed_stock'],observation_date='2026-10-19',
            freshness=r['commercial_freshness'],quote_type='PUBLIC_PAGE_ALLOWANCE; no firm quotation',
            direct_url=r['direct_product_url'],alternatives='None selected; retain exact mating system',
            evidence=r['commercial_evidence'],remaining_notes=r['notes'])
        shopping.append(dict(row,scope='SEPARATE_HARNESS'))
    save('SHOPPING_LIST_BY_SUPPLIER.csv',sorted(shopping,key=lambda r:(r['supplier'],r['group_id'])))
    save('C32_ALTERNATIVE_PENDING.csv',[alternative])
    pending=[r for r in checklist if r['exact_identity_approval']!='APPROVED']
    save('EXACT_IDENTITIES_FOR_OWNER_REVIEW.csv',pending)
    deferred=[r for r in harness if not r['direct_product_url']]
    save('DEFERRED_AND_OWNER_INVENTORY.csv',deferred)
    totals=defaultdict(float)
    for r in shopping:
        if r['extended_price']:totals[(r['supplier'],r['currency'])]+=float(r['extended_price'])
    (EV/'supplier-totals.json').write_text(json.dumps([dict(supplier=s,currency=c,goods_allowance=round(v,4)) for (s,c),v in sorted(totals.items())],indent=2)+'\n')
    text=['# Phase5.4 — shopping list by supplier','',
        'Quick start: review the exact identities and quantities below, then close L3 allocation and Czech delivery terms before ordering. See [decisions](OPEN_DECISIONS.md) and [cost comparison](PHASE5_4_COMMERCIAL_REVIEW.md).', '',
        'Dated 19 October 2026. 66 electronics planning lines + 8 exact harness lines. Additional C32 stock is separate below: it would be electronics line 67 after approval. Five F5 boards contain 655 actual physical components. No testpoint hardware or always-DNP purchases.', '',
        '**All prices are public page allowances, excluding freight, VAT and import/handling unless explicitly stated. None is a firm supplier quotation or allocated stock.** Each exact URL, cache age, alternative and remaining note is retained in [the CSV](SHOPPING_LIST_BY_SUPPLIER.csv).', '',
        'Fit/spare/excess are distinct; R5 stock rows have zero additional fitted positions. A = owner approved; P = approved for prototype; R = exact identity for owner review; Q = supply/delivery open. A/P do not authorize an order. Ordinary R rows can be approved together using EXACT_IDENTITIES_FOR_OWNER_REVIEW.csv; no new engineering audit is required.', '']
    for supplier in sorted({r['supplier'] for r in shopping}):
        text+=['## '+supplier,'', '| Refs / line | Manufacturer and exact MPN | Supplier SKU / buy link | Fit | Spare | MOQ × multiple | Order | Excess | Unit | Extended | Stock / review |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|']
        for r in [x for x in shopping if x['supplier']==supplier]:
            status='P' if r['selection_status']=='OWNER_APPROVED_PROTOTYPE' else 'A' if r['exact_identity_approval']=='APPROVED' else 'R'
            if r['checklist_status'] in ('HOLD_EXACT_SUPPLY','EU_INDICATIVE_PRICE_CZ_DELIVERY_OPEN'):status+=';Q'
            stock=r['observed_stock'] or 'unknown'
            text.append(f"| {r['references']} ({r['group_id']}) | {r['manufacturer']} {r['manufacturer_mpn']} | [{r['distributor_sku']}]({r['direct_url']}) | {r['fitted_quantity']} | {r['spares']} | {r['MOQ']} × {r['multiple']} | {r['purchase_quantity']} | {r['MOQ_excess']} | {money(r['unit_price'])} {r['currency']} | {money(r['extended_price'])} {r['currency']} | {stock}; {status} |")
        subtotal=' + '.join(f'{money(v)} {c}' for (s,c),v in sorted(totals.items()) if s==supplier) or 'UNKNOWN'
        text+=['', 'Goods allowance: '+subtotal+ ('; exact L3 remains unpriced/unallocated.' if 'Coilcraft' in supplier else '.'),'']
    text+=['## Additional C32 comparison stock — PENDING OWNER APPROVAL','',
        '| Refs | Exact part | Supplier / SKU | Fit | Comparison stock | MOQ / multiple | Order | Unit | Extended | Observed stock |','|---|---|---|---:|---:|---|---:|---:|---:|---:|',
        f"| C32 alternative only | TDK {alternative['mpn']} | [DigiKey {alternative['sku']}]({alternative['url']}) | 0 | 10 | 1 / 1 | 10 | USD0.322 | USD3.22 | 476200; last-week cache |",'',
        '2.2 µF ±10%, 50 V, X7R, 0805; same 2.0×1.25×1.25 mm nominal body as Yageo. Manufacturer CSV supports about 1.19 µF typical at 18 V by interpolation, compared with Yageo 0.5–0.6 µF typical. Both are 50 V: the recommendation follows bias evidence. See [exact evidence](PHASE5_4_C32_COMPARISON.md). No replacement or additional purchase is approved.', '',
        'Alternatives: L2 exact Coilcraft combined-order indication EUR 11.90 / 5; R32 optional ten-piece tier EUR 5.62 instead of EUR 6.40 / 8. Neither changes default quantities. C63 stays eight and each R5 profile stays ten as explicitly approved. D2 exact supply is still advertised; no substitute is needed at this checkpoint.', '',
        'External cells/BMS, pack thermistor/profile, external PD converter, unselected wire/consumables and owned tools remain in [the separate deferred list](DEFERRED_AND_OWNER_INVENTORY.csv). These unknown costs are excluded, never treated as zero. Already ordered PCB/stencil is not ordered again. **STOP for owner review; no checkout or order.**','']
    (OUT/'SUPPLIER_BASKETS.md').write_text('\n'.join(text),encoding='utf-8')
    approved_sum=sum(float(r['extended_scenario_cost_usd']) for r in master if r['approved_basket_qty']!='0')
    summary=f'''# Phase 5.4 — final sourcing and purchasing preparation

Quick start:

1. Review [supplier shopping list](SUPPLIER_BASKETS.md) or [full CSV](SHOPPING_LIST_BY_SUPPLIER.csv).
2. Review [remaining decisions](OPEN_DECISIONS.md) and [supplier combinations](PHASE5_4_COMMERCIAL_REVIEW.md).
3. Approve or decline the separate [C32 comparison stock](PHASE5_4_C32_COMPARISON.md).
4. Close exact L3 stock/dispatch and Czech supplier charges before placing orders yourself.

Five F5 capacity is unchanged: **655 assembled parts and 66 electronics planning lines**, plus a possible 67th C32 stock line. IC1 is exactly five BQ25798RQMR; R5 is ten pieces each for 2S/3S/4S. No TP hardware or always-DNP purchases.

Owner approvals applied: C32 Yageo ×10, mapped TDK output capacitors ×30 and C63 Yageo ×8. The TDK bank's original 25 µF basis remains unguaranteed; accepted prototype limitations stay in bring-up documentation and do not block these purchases.

All 66 electronics and eight exact harness lines had public-page refresh attempts. Sixty-four electronics lines have USD allowances; R32 has a dated EU EUR allowance; L3 remains without an allocatable offer. Cache ages are explicit. C8 has conflicting MOQ observations; the list conservatively requests 100 from the visible MOQ 100 offer.

Partial electronics goods: **USD 243.0236 + EUR 6.40**, excluding L3. Separate exact harness: **USD 16.7510**. Combined known-price goods: **USD 259.7746 + EUR 6.40**, plus unpriced L3, freight, VAT/import, FX and unselected materials. The 18 approved USD rows total USD {approved_sum:.4f}; this is an incomplete subset, not an order release. The extra C32 stock adds USD 3.22 only after approval.

L3: direct Coilcraft UK shows EUR 13.10 / 5 arithmetic but blank stock. Combined L2+L3 EUR 25.00 is indicative and unallocated. Farnell is a dated backorder lead; DigiKey Marketplace's newer unavailable page overrides its older stock/price snapshot. R32: exact Mouser eight × EUR 0.80 = EUR 6.40 from a Lithuania cached listing. Czech delivered quote and consolidation remain open; no exact existing-supplier small-order offer was verified.

Independent checks passed counts, prices, approvals, 196 protected CAD/library/manufacturing hashes and preservation of the unrelated config. No CAD, native KiCad, ERC/DRC rerun, manufacturing, firmware, hardware power-up, cart, supplier contact, order, checkout, commit or push. **STOP for owner review.**
'''
    (OUT/'SOURCING_SUMMARY.md').write_text(summary,encoding='utf-8')
    print(json.dumps(dict(electronics=len(checklist),exact_harness=len(shopping)-len(checklist),approved_USD=round(approved_sum,4),batch_identity_review=len(pending),additional_C32='PENDING')))


if __name__=='__main__':main()
