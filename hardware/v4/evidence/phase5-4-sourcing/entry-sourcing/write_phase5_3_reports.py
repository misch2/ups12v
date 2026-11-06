"""Render active Phase5.3 purchasing documents from the reviewed offline inputs."""
import csv
import json
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent
EV = OUT.parent/'evidence/phase5-3-sourcing'


def read(name):
    with (OUT/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def save(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    rows = read('MASTER_PURCHASING_BOM.csv')
    s = json.loads((EV/'consistency.json').read_text())
    c = json.loads((OUT/'replacement_candidates.json').read_text())
    save('UNAPPROVED_ALTERNATIVES.csv', c)
    checklist = []
    for r in rows:
        short = bool(r['page_observed_stock'] and r['proposed_purchase_qty'] and int(r['page_observed_stock']) < int(r['proposed_purchase_qty']))
        status = ('HOLD_SUPPLY_OR_QUOTE' if not r['extended_scenario_cost_usd'] else
                  'HOLD_INSUFFICIENT_OBSERVED_STOCK' if short else r['order_readiness'])
        checklist.append(dict(supplier=r['candidate_supplier'], group_id=r['group_id'], references=r['references'],
            manufacturer=r['manufacturer'], manufacturer_mpn=r['mpn'], original_procurement_mpns=r['original_procurement_mpns'],
            distributor_sku=r['distributor_sku'], fitted_quantity=r['fitted_qty_scenario'], spares=r['suggested_spares'],
            alternative_R5_stock=r['alternative_profile_stock_qty'], desired_quantity=r['desired_qty_before_MOQ'],
            MOQ=r['supplier_MOQ'], multiple=r['purchase_multiple'], purchase_quantity=r['proposed_purchase_qty'],
            MOQ_excess=r['MOQ_rounding_excess'], packaging=r['supplier_packaging'], unit_price=r['page_unit_price'],
            currency=r['currency'], extended_price=r['extended_scenario_cost_usd'], selection_status=r['selection_status'],
            checklist_status=status, observed_stock=r['page_observed_stock'], observation_date=r['verification_date'],
            freshness=r['stock_freshness'], direct_url=r['direct_product_url'], evidence=r['evidence'],
            remaining_notes=r['outstanding_uncertainties']))
    checklist.sort(key=lambda r: (r['supplier'], r['group_id']))
    save('PROPOSED_ORDERING_CHECKLIST.csv', checklist)
    approved = [r for r in rows if r['approved_basket_qty'] not in ('', '0')]
    accepted_total = sum(float(r['extended_scenario_cost_usd']) for r in approved)
    total = s['priced_purchase_scenario_subtotal_usd']
    harness = s['priced_harness_scenario_subtotal_usd']
    intro = f'''# Phase5.3 — consolidated purchasing checklist; owner review STOP

2026-10-19. Quick start: OPEN_DECISIONS.md, PHASE5_3_COMPATIBILITY_REVIEW.md,
then the supplier groups below and PROPOSED_ORDERING_CHECKLIST.csv.
No cart, checkout, supplier message or order has been created.

## Assembly and purchasing quantities

| Basis | F0 per board | F5 per board | Five F5 boards |
|---|---:|---:|---:|
| Preserved authoritative CAD/manufacturing reference population |115|134|670|
| TP1/TP3/TP4 hardware omitted by explicit owner decision |−3|−3|−15|
| Actual physical component assembly target |112|131|655|

All154reference identities remain tracked. F5 has131physical parts +4always-DNP
capacitors +16pre-existing PCB-only features +3probe pads without hardware.
There are64physical purchasing groups plus2additional R5 stock rows =66lines.
The old67lines included one grouped TP hardware line, now removed. Original
manufacturing counts/files remain historical evidence; no regeneration occurred.
Spares and MOQ excess are purchased stock, not additional fitted positions.
Exactly5TI BQ25798RQMR; R5 exactly10each8.2k/13.7k/27k,30stock pieces for5positions.
TP hardware/wire/spares: zero. Existing owner loops may be used optionally later.

## Commercial scope

**Partial electronics USD{total:.4f}**, excluding2unpriced lines (L3 and R32).
Separate harness USD{harness:.4f}; combined partial USD{total+harness:.4f}.
These are dated/cached page observations for proposed quantities; they are not
a complete delivered quote. VAT, freight, import/handling, FX and unselected
wire/tools/consumables remain outside the total. Unconfirmed L3USD15.10 has been
removed from the subtotal. R12's separate oldCZK quote is not added toUSD.
All66planning quantities now have recorded MOQ/multiple support; L3MOQ1 is a
supported order size, **not** an available allocation. R32MOQ1 is from an
AustraliaMouser page, **not** a Czech delivery commitment.

**Owner-accepted exact dated-price subset: {len(approved)}lines, USD{accepted_total:.4f}.**
This includes the newly approved AO3400A and prototype-approved C35/C36, as well
as prior approvals. It remains incomplete and conveys no authorization to buy.

## Complete proposed allocation

Rows retain exact MPN/SKU, original identity, spares and excess. A price does not
approve a proposed MPN. Refresh regional availability before any later purchase.
The C33bank line uses the now manufacturer-mapped TJ00E identity but still needs
owner prototype risk acceptance. C63Yageo is a new **proposal**, not an approval.
'''
    by = defaultdict(list)
    for r in checklist:
        by[r['supplier']].append(r)
    for supplier, rr in sorted(by.items()):
        cost = sum(float(r['extended_price'] or 0) for r in rr)
        intro += f'\n### {supplier}: {len(rr)}lines; partial USD{cost:.4f}\n\n| Refs | MPN / SKU / source | Fit + spare + R5 stock | MOQ / multiple | Buy / excess | Unit USD | Ext USD | Status |\n|---|---|---:|---:|---:|---:|---:|---|\n'
        for r in rr:
            identity = f"[{r['manufacturer_mpn']}]({r['direct_url']})" if r['direct_url'] else r['manufacturer_mpn']
            intro += f"| {r['references']} | {identity}; {r['distributor_sku'] or 'SKU quote needed'} | {r['fitted_quantity']} + {r['spares']} + {r['alternative_R5_stock']} | {r['MOQ'] or '?'}/{r['multiple'] or '?'} | {r['purchase_quantity'] or '?'}/{r['MOQ_excess'] or '0'} | {r['unit_price'] or 'quote'} | {r['extended_price'] or 'unpriced'} | {r['selection_status']}; {r['checklist_status']} |\n"
    intro += '''
## Practical consolidation before owner release

1. Use LCSC for the main electronics including exactD3/D4 and mappedTDKbank;
   L2fallback is5×C7432409. No need to substitute the low-leakage diodes.
2. Keep DigiKey cut tape for R5, exactL1, R12 and quoted precision/header lines.
   ProposedC63 also fits this shipment. Compare10-piece tiers for R6/R23/C63:
   their totalsUSD0.34/0.21/0.65 are lower than8-piece totalsUSD0.80/0.80/0.96.
   Current master conservatively retains8each; this optional3-line optimization
   savesUSD1.36 while adding6stock pieces, with655assembly components unchanged.
3. Retain the exactD2 TME last-stock offer,8pieces; refresh it before any purchase.
   If this is the onlyTME line left, compare its whole shipment cost with a reviewed
   same-footprint LED proposal; no replacement is needed while exact stock exists.
4. Request an exact5L3 plus optional5L2 CoilcraftEurope delivered quote. L2's
   direct price indication isUSD15.9675lower than itsLCSC line, before shipping.
   FarnellEU L3backorder is not timely confirmed supply. No unwanted full reels.
5. Quote R32Mouser8pieces with Czech delivery, and compare exactR32/R33 transfer
   to an existing shipment. Do not relax0402/0.1%/10ppm or add a parcel merely
   because a catalog source was found. Keep currencies separate until actualFX.

See PHASE5_3_COMMERCIAL_REVIEW.md for exact gaps and unsent requests; see
HARNESS_AND_ASSEMBLY_BOM.csv for separate materials. All other unapproved exact
identities can be reviewed together as the complete master list. **STOP before purchases.**
'''
    (OUT/'SUPPLIER_BASKETS.md').write_text(intro, encoding='utf-8')
    summary = f'''# UPS V4 — Phase5.3 purchasing preparation; owner review STOP

2026-10-19. Quick start: [remaining decisions](OPEN_DECISIONS.md),
[prototype assessment](PHASE5_3_COMPATIBILITY_REVIEW.md),
[complete ordering checklist](SUPPLIER_BASKETS.md),
[commercial gaps](PHASE5_3_COMMERCIAL_REVIEW.md).

Owner decisions applied: **AO3400A/C20917 forQ3/Q8/Q9,20pieces**;
**MurataGRM21BR61E226ME44L forC35/C36 approved for prototype,15pieces**;
**no TP1/TP3/TP4 hardware or wire fabrication/purchase requirement**.
Existing testpoint inventory is optional; all pads/holes remain unchanged.

**0F0+5F5:131×5=655physical assembly components**. Preserved historical
CAD/manufacturing population134×5=670 includes15optional loops now omitted.
154references remain covered;64physical groups +2extraR5stock rows =66lines.
IC1exactly5BQ25798RQMR; R5exactly10each8.2k/13.7k/27k,5fitted positions once.
4always-DNP capacitors buy zero; spares/MOQ excess never count as fitted parts.

**Progress:** TDK's12Jan2023manufacturer documentp12 explicitly maps160ACtoTJ00E;
exact ordering identity is closed. LCSCC342620order30 is a concrete supply proposal.
Retained25µFbank basis is not guaranteed by typical data; propose bounded prototype
acceptance for owner review, with no silent design-basis waiver. C32retainedYageo
has known bias loss and a specific10-piece purchase/prototype-test proposal.
D3/D4exactBAS116H,115 sourced atLCSCC74210,20pieces; no substitute needed.
L2exact5-piece offer remains. L1,C8,R6,R23,R12quotes/terms supplemented.
C63originalMurata now obsolete; proposedYageoCC0603KRX7R9BB333 has primary
nominal/mechanical evidence and a cut-tape quote, owner selection pending.

**Still unresolved:** exact5-pieceL3allocation/dispatch and delivered quote;
R32exactMouser source identified but usableUSD/Czech delivered price missing;
owner acceptance ofC32/TDKbank prototype uncertainty and proposed exact identities;
final regional supplier totals/material selection. Closed decisions stay closed.

Partial electronicsUSD{total:.4f},2unpriced lines; harnessUSD{harness:.4f};
combined partialUSD{total+harness:.4f} before unknown charges/materials.
{len(approved)}-line accepted dated-price subsetUSD{accepted_total:.4f} is incomplete.
L3's unquotedUSD15.10 is excluded. No complete executable total or cheapest
shipment claim. Quantities/MOQ are recorded; public stock is not reserved.

[Verification](../evidence/phase5-3-sourcing/verification.json) records independent
population/quantity/identity/cost checks and196protected-file hashes. No CAD,
manufacturing, firmware, nativeKiCad, physical test, cart, checkout, order,
commit or push. **STOP for owner review before purchases.**
'''
    (OUT/'SOURCING_SUMMARY.md').write_text(summary, encoding='utf-8')
    print(f'Checklist {len(checklist)}; fitted655; partialUSD{total:.4f}; accepted{len(approved)} USD{accepted_total:.4f}')


if __name__ == '__main__':
    main()
