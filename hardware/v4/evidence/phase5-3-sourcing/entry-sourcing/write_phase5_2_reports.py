"""Phase5.2 documentary checklists. No network, cart, CAD or order operations."""
import csv
import json
from collections import defaultdict
from pathlib import Path

OUT=Path(__file__).resolve().parent
EV=OUT.parent/'evidence/phase5-2-sourcing'


def read(name):
    with (OUT/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def save(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    rows=read('MASTER_PURCHASING_BOM.csv')
    s=json.loads((EV/'consistency.json').read_text())
    c=json.loads((OUT/'replacement_candidates.json').read_text())
    save('UNAPPROVED_ALTERNATIVES.csv',c)
    checklist=[]
    for r in rows:
        short=bool(r['page_observed_stock'] and r['proposed_purchase_qty'] and int(r['page_observed_stock'])<int(r['proposed_purchase_qty']))
        checklist.append(dict(supplier=r['candidate_supplier'],group_id=r['group_id'],references=r['references'],
            manufacturer=r['manufacturer'],manufacturer_mpn=r['mpn'],original_procurement_mpns=r['original_procurement_mpns'],
            distributor_sku=r['distributor_sku'],fitted_quantity=r['fitted_qty_scenario'],spares=r['suggested_spares'],
            alternative_R5_stock=r['alternative_profile_stock_qty'],desired_quantity=r['desired_qty_before_MOQ'],
            MOQ=r['supplier_MOQ'],multiple=r['purchase_multiple'],purchase_quantity=r['proposed_purchase_qty'],
            MOQ_excess=r['MOQ_rounding_excess'],packaging=r['supplier_packaging'],unit_price=r['page_unit_price'],
            currency=r['currency'],extended_price=r['extended_scenario_cost_usd'],selection_status=r['selection_status'],
            checklist_status='HOLD_INSUFFICIENT_OBSERVED_STOCK' if short else r['order_readiness'],
            observed_stock=r['page_observed_stock'],observation_date=r['verification_date'],freshness=r['stock_freshness'],
            direct_url=r['direct_product_url'],evidence=r['evidence']))
    checklist.sort(key=lambda r:(r['supplier'],r['group_id']))
    save('PROPOSED_ORDERING_CHECKLIST.csv',checklist)
    approved=[r for r in rows if r['approved_basket_qty'] not in ('','0')]
    ac=sum(float(r['extended_scenario_cost_usd']) for r in approved)
    total=s['priced_purchase_scenario_subtotal_usd'];ht=s['priced_harness_scenario_subtotal_usd']
    missing=[r for r in rows if not r['extended_scenario_cost_usd']]
    unknown=[r for r in rows if not r['proposed_purchase_qty']]
    intro=f'''# Phase5.2 — proposed supplier ordering checklist; owner review STOP

2026-10-19. Quick start: OPEN_DECISIONS.md → PHASE5_2_COMPATIBILITY_REVIEW.md →
this checklist and PROPOSED_ORDERING_CHECKLIST.csv. No cart, checkout, RFQ or order.

Purchase capacity **0F0+5F5**:670fitted components;65physical groups plus2extraR5
stock rows. Exactly5TI BQ25798RQMR/C2876593. R5:10each8.2k/13.7k/27k0805/1%,
30pieces;5mutually exclusive fitted positions counted once. Spares/MOQ excess
separate. C20/C22/C24/C25 and16PCB-only features buy zero. External cells/BMS,
external PD converter and firmware remain out of scope.

## Cost boundary

**Incomplete electronics allowance USD{total:.4f}**, {len(missing)}lines without a
usable USD extended total; {len(unknown)}lines lack confirmed MOQ-derived quantities.
Includes cached prices, proposed identities, unquoted Coilcraft L3USD15.10
indication, and D3/D4 price despite stock3versus11required. It is not an executable
complete basket. Separate priced harness portionUSD{ht:.4f}; combined partial
USD{total+ht:.4f}. Missing parts/materials, VAT, freight, import/handling and FX
remain additional unknowns. No complete delivered total or cheapest-route claim.
R12 historical10October2026quote7.47CZKnet/pc,6=44.82CZK, remains separate; no FX
conversion or double count. Current quote still needed.

## Explicitly accepted exact identities with dated price observations

**{len(approved)}-line subset, USD{ac:.4f}**. U8/C70/C71 are incorporated with
original MPN traceability. No other substitute was promoted. This subset is
incomplete and is not purchase authorization. Cached stock is not reserved;
confirm regional stock/terms before purchasing. Unapproved parts are excluded.

| Supplier / refs | Manufacturer MPN / SKU / direct URL | Fit+spare | Order | Unit USD | Extended USD |
|---|---|---:|---:|---:|---:|
'''
    for r in sorted(approved,key=lambda r:(r['candidate_supplier'],r['group_id'])):
        intro+=f"| {r['candidate_supplier']} / {r['references']} | [{r['manufacturer']} {r['mpn']}]({r['direct_product_url']});{r['distributor_sku']} | {r['fitted_qty_scenario']}+{r['suggested_spares']} | {r['proposed_purchase_qty']} | {r['page_unit_price']} | {r['extended_scenario_cost_usd']} |\n"
    intro+='\n## Complete conditional planning allocation\n\n**All rows below are conditional proposals**, including unapproved selections and engineering holds. A price does not approve an MPN. Blank means unknown, never zero. CSV includes packaging, cache age, evidence, original MPN and per-line readiness.\n'
    by=defaultdict(list)
    for r in checklist:
        by[r['supplier']].append(r)
    for supplier,rr in sorted(by.items()):
        subtotal=sum(float(r['extended_price'] or 0) for r in rr)
        intro+=f'\n### {supplier}: {len(rr)}lines; partial USD{subtotal:.4f}\n\n| Refs | Manufacturer MPN / SKU / URL | Fit+spare+R5 stock | MOQ/multiple | Order/excess | Unit USD | Ext USD | Selection / commercial gate |\n|---|---|---:|---:|---:|---:|---:|---|\n'
        for r in rr:
            identity=f"{r['manufacturer']} {r['manufacturer_mpn']}"
            if r['direct_url']:
                identity=f"[{identity}]({r['direct_url']})"
            intro+=f"| {r['references']} | {identity};{r['distributor_sku'] or 'SKU missing'} | {r['fitted_quantity']}+{r['spares']}+{r['alternative_R5_stock']} | {r['MOQ'] or '?'}/{r['multiple'] or '?'} | {r['purchase_quantity'] or 'quote'}/{r['MOQ_excess'] if r['MOQ_excess'] else '?'} | {r['unit_price'] or 'unquoted'} | {r['extended_price'] or 'unpriced'} | {r['selection_status']}; {r['checklist_status']} |\n"
    intro+='\n## Missing usable USD totals\n\n| Refs | Exact MPN | Desired request |\n|---|---|---:|\n'
    for r in missing:
        intro+=f"| {r['references']} | {r['mpn']} | {r['desired_qty_before_MOQ']} |\n"
    intro+='\n[Commercial gaps and delivery comparison](PHASE5_2_COMMERCIAL_REVIEW.md) explains every missing quote, shortage, cached observation and shipment strategy. [Compatibility](PHASE5_2_COMPATIBILITY_REVIEW.md) controls engineering holds.\n\n## Unapproved alternatives\n\n| Refs | Candidate / SKU / URL | Conditional order | USD | Gate |\n|---|---|---:|---:|---|\n'
    for r in c:
        intro+=f"| {r['references']} | [{r['candidate_mpn']}]({r['url']});{r['sku']} | {r['conditional_order_qty']} | {r['conditional_extended_usd']} | {r['approval_status']} |\n"
    intro+='\nAO3400A and PMV16XNR are mutually exclusive; never add both costs/quantities. TDK candidate stays on engineering hold. Harness materials remain separate in HARNESS_AND_ASSEMBLY_BOM.csv. **STOP for owner review.**\n'
    (OUT/'SUPPLIER_BASKETS.md').write_text(intro,encoding='utf-8')
    summary=f'''# UPS V4 — Phase5.2 purchasing review STOP

2026-10-19. Quick start: [decisions](OPEN_DECISIONS.md),
[qualification](PHASE5_2_COMPATIBILITY_REVIEW.md), [supplier checklist](SUPPLIER_BASKETS.md),
[commercial gaps](PHASE5_2_COMMERCIAL_REVIEW.md).

**Approved and incorporated:** U8 TI LM74700QDBVTQ1/C2653623 and C70/C71 TDK
C1608X7R1C105K080AC/C2167399. Original MPNs remain traceable; CAD unchanged.
No other substitute is owner-approved.

5fully populatedF5:134×5=670fitted;65physical groups+2R5stock rows. IC1 exactly5
BQ25798RQMR. R5:10each8.2k/13.7k/27k0805/1%;5fitted positions once.4always-DNP
capacitors buy zero. Spares/MOQ excess separate; external battery/BMS/PD/firmware excluded.

Recommend AO3400A pending owner selection; PMV16XNR now has real LCSC small-order
supply but more typical gate charge. Neither has a complete published hot-leakage
bound for all intended temperatures. Static OFF truth states are documented;
prototype ramps/temperature remain unmeasured. C32 input-network ripple analysis
does not establish a numerical Cmin without an approved ripple/source-impedance
basis. TDK exactTJ00E mapping remains unproven; new official CSV gives25.7182µF
typical for5Vpair, insufficient to establish retained25µF across conditions.
C35/C36 typical curves and4.7124µF assumed screen are not joint guarantees.
Concrete0.30mm tinned-wire loop proposal fits the1.00mm-hole envelope, pending
owner selection/exact wire quote. L2 exact5-piece LCSC supply established;
L3 stock/lead-time and combined Coilcraft/Farnell delivered quote remain open.

**Incomplete costs:** electronicsUSD{total:.4f} priced/cached/indicative,
{len(missing)}unpriced USD lines; harnessUSD{ht:.4f}; combined partialUSD{total+ht:.4f}
before unknown taxes/shipping/materials. Includes unquotedL3USD15.10 and shortage
line D3/D4. Accepted exact dated-price subset{len(approved)}lines USD{ac:.4f},
not a complete basket or authorization to order. Three-shipment consolidation is
a quote target, not a verified cheapest strategy.67master lines refreshed/attempted;
cache age and unknown fields explicit. D2 manufacturer discontinued; TME D3/D4
stock3does not cover11. All missing quotes listed in commercial review.

[Consistency/preservation](../evidence/phase5-2-sourcing/verification.json):
196protectedCAD/library/manufacturing files unchanged. No native operation,
ERC/DRC rerun or firmware build needed for documentary-only changes. No physical
assembly, checkout, purchase, commit or push. **STOP for owner review.**
'''
    (OUT/'SOURCING_SUMMARY.md').write_text(summary,encoding='utf-8')
    print(f'Checklist67; accepted subset{len(approved)} USD{ac:.4f}; partialUSD{total:.4f}; {len(missing)}unpriced')


if __name__=='__main__':
    main()
