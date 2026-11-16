"""Render procurement report tables from the calculated CSVs. No network/CAD."""
import csv
import json
from collections import defaultdict
from pathlib import Path


def main():
    out=Path(__file__).resolve().parent
    ev=out.parent/'evidence/phase5-0-sourcing'
    with (out/'MASTER_PURCHASING_BOM.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    summary=json.loads((ev/'consistency.json').read_text())
    n0,n5=summary['scenario']['N_F0'],summary['scenario']['N_F5']
    by=defaultdict(list)
    for r in rows:
        name=r['candidate_supplier']
        bucket='LCSC' if name=='LCSC' else 'TME' if name=='TME' else 'DigiKey' if name=='DigiKey' else 'Coilcraft direct' if name.startswith('Coilcraft') else 'Unresolved / backorder'
        by[bucket].append(r)
    subtotal=summary['priced_purchase_scenario_subtotal_usd']
    unpriced=len(summary['groups_without_usable_cost'])
    baskets=f'''# Phase 5.0 supplier baskets — proposal only

2026-10-19. Scenario **{n0}×F0 + {n5}×F5**, provisional, not the final assembly
quantity. Five bare PCBs and one0.10mm top stencil are already ordered according
to the owner. No component cart, RFQ transmission, order or import upload was made.

## Use and price limits

The64 named manufacturer identities plus one unresolved loop-testpoint group make
**65 PCBA purchasing lines**. Every line is allocated below, including unquoted
and blocked parts. Quantities in the table are fitted + suggested spare = desired;
the last numeric quantity is the separately MOQ-rounded proposed order. An em dash
means unverified terms, not zero pieces or zero cost. Sources are exact pages or
retained identity links. Source-cache age and all quote limitations remain in the
master CSV/evidence. Search snippets were used for identity discovery, not current
stock. A page observation is not a reservation or guaranteed delivery.

Known/indicative electronics purchase subtotal is **USD{subtotal:.2f}**;
**{unpriced} lines lack a usable extended quote**. This subtotal includes spares,
MOQ excess and cached manufacturer indicative prices; unavailable reference-only
quotes are excluded. It is not a complete basket or a current delivered-price
estimate. The CSV's per-F0/F5 costs allocate known unit prices to fitted parts;
they exclude spares and MOQ excess. Unknown currency conversion is not invented.

## Strategy A — preferred TME + LCSC, exact secondary sources where needed

Use LCSC for verified exact semiconductor/MLCC/YAGEO groups. Hundred-piece resistor
MOQs cost cents per line; keep excess separate from intentional spares. Keep TME
for exact parts unavailable at LCSC and its existing mechanical/passive sources
when a refreshed small-order quote is economical. A cached TME stock count is
expressly not confirmed-current inventory. Use one DigiKey standard shipment for
the Nano-Fit headers/housings, N4X module and exact R60 where preferred supply is
unproven/unavailable. Obtain an exact combined Coilcraft Europe L2/L3 quote.

This strategy can involve **four suppliers** (TME, LCSC, DigiKey, Coilcraft), plus
Mouser/Farnell only if an unresolved exact part requires it. It is a supplier
preference strategy, not proof of the lowest delivered cost. Do not split more
shipments merely to save a few cents on resistors. Never replace an exact part
automatically to fill a supplier basket.

## Strategy B — reduce paid shipments

Quote **DigiKey + Coilcraft Europe** for all exact PCBA/harness identities, using
cut tape/bulk rather than Digi-Reel/full reel. This is a concrete consolidation
request keyed by the master MPNs and quantities, not a verified complete two-cart
offer: R32 cut-tape supply, old MLCC order codes and U8 still prevent a ready order.
If all exact parts cannot be supplied there, practical fallback is **LCSC +
DigiKey + Coilcraft**, transferring the small TME allocation only after exact
SKU/stock verification. A necessary Mouser exact R32/R33 purchase would add a
shipment and must be compared with that saving. No secondary-supplier charge is
assumed waived.

Compare the incremental delivered DigiKey price for transferred lines against the
entire extra TME/LCSC shipping, tax/import/handling bill. No complete delivered
quote exists, so no numeric saving or global optimum is claimed. Never add
unneeded components solely to reach free shipping; compare useful inventory only.

## Shipping, VAT, handling and delivery to Czech Republic

- [DigiKey Czech terms](https://www.digikey.cz/en/help-support/delivery-information/delivery-time-and-cost),
  retrieved2026-10-19: standard orders typically48h transit; CZK delivery free
  from1800CZK, otherwise600CZK; EUR threshold75EUR, otherwise25EUR. This is transit,
  not a backorder promise. UPS prepaid is described DDP; FedEx/DHL CPT may collect
  duty/customs/VAT on delivery. Marketplace ships separately, may charge extra,
  and does not count toward standard free-shipping thresholds. Use cut tape,
  not the optional USD7 Digi-Reel service. Actual Czech checkout/VAT remains open.
- [TME Czech delivery terms](https://www.tme.eu/cz/how-to-buy/7328/zpusoby-a-ceny-dopravy/),
  retrieved2026-10-19: carrier/weight/payment-dependent. Express≤10kg is listed
 390CZK net/471.90CZK gross; cash on delivery adds35CZK net/42.35CZK gross.
  These are examples from the official tariff, not the selected cheapest route.
  Small ground freight and actual product net/gross VAT must be quoted together.
  International USD pages sometimes display identical net/gross; do not interpret
  that as Czech VAT exemption. No Czech product checkout was performed.
- [LCSC shipping](https://www.lcsc.com/help-center/shipping-delivering/shipping-methods):
  actual freight, delivery time, handling/fuel surcharge, import/VAT and courier
  clearance costs are **unquoted**. The previously submitted JLCPCB shipment is
  separate. No combined shipping or obsolete coupon is assumed.
  [LCSC's2026 EU import notice](https://www.lcsc.com/pl/help-center/notice/eu-low-value-import-regulations-2026)
  describes a3EUR charge per main category for applicable≤150EUR B2C imports,
  separately from VAT. Have the supplier/courier determine actual categories and
  collection route; do not multiply3EUR by BOM line count or assume zero charges.
- [Coilcraft Europe](https://www.coilcraft.com/de-de/contact/saleslocations/europe-and-africa/)
  states no minimum order. Exact L2/L3 stock, fulfillment of retained MEC codes,
  Czech freight, UK import handling/VAT and delivery estimate remain unquoted.
  The old DigiKey L3 Marketplace listing is **no longer available**; its old
  price/stock is not used as a current fallback. Farnell and Mouser exact listings
  are leads, not secured supplies. Confirm any region restriction before payment.
- Tools, paste/cleaner and wire may be better bought locally with an existing
  shipment. Liquid/paste shipping/storage conditions and expiry need an exact
  quote. No ownership of these items has been assumed.

## Allocation and extended costs

'''
    for bucket in ['LCSC','TME','DigiKey','Coilcraft direct','Unresolved / backorder']:
        rr=by[bucket]
        part=sum(float(r['extended_scenario_cost_usd'] or 0) for r in rr)
        baskets+=f'### {bucket} — {len(rr)} lines; priced subtotal USD{part:.2f}\n\n'
        baskets+='| Group / references | Exact MPN / source SKU | Fitted + spare = desired | MOQ-rounded order | USD extended | Status |\n|---|---|---:|---:|---:|---|\n'
        for r in rr:
            mpn=r['mpn']
            if r['direct_product_url']:
                mpn=f"[{mpn}]({r['direct_product_url']})"
            sku=r['distributor_sku'] or 'SKU unverified'
            ext=f"{float(r['extended_scenario_cost_usd']):.4f}" if r['extended_scenario_cost_usd'] else '—'
            status=r['availability']+'; '+r['selection_status']
            baskets+=f"| {r['group_id']} {r['references']} | {mpn}; {sku} | {r['fitted_qty_scenario']} + {r['suggested_spares']} = {r['desired_qty_before_MOQ']} | {r['proposed_purchase_qty'] or '—'} | {ext} | {status} |\n"
        baskets+='\n'
    baskets+='''## Harness and conditional alternatives

HARNESS_AND_ASSEMBLY_BOM.csv is separate; its priced connector/contact subtotal
is not hidden inside PCBA cost. LCSC1053071202 MOQ5,1053002100 MOQ10 and JST mates/
contacts MOQ20/50/100 are explicit; DigiKey1053071203/2202/2203 can share the header
shipment. Two power contacts per harness;3-position centres remain empty.

If the two capacitor alternatives in UNAPPROVED_ALTERNATIVES.csv are eventually
accepted, their illustrative1+1 purchases would be10×USD0.3642 +10×USD0.0551 =
**USD4.193**, excluding tax/freight. They replace original lines, never add
duplicate capacitors. They currently have automatic purchase quantity0 and are
excluded from every accepted-identity subtotal. Neither option resolves U8,
PMV16UN, testpoint identity or the remaining quote gaps.

Current supplier-import column schemas were not verified; no supplier-import
CSV or cart-creation claim is made. The master CSV is the complete quote/request
worksheet; unapproved/conditional/open rows are not instructions to place an order.
'''
    (out/'SUPPLIER_BASKETS.md').write_text(baskets,encoding='utf-8')
    status=f'''# UPS V4 Phase 5.0 — sourcing proposal

2026-10-19. **65 PCBA purchasing lines;154 reference rows;28 separate harness,
assembly-material and battery-decision rows.** Counts verified: F0=115 fitted,
F5=134,19 F5-only,4 always-DNP and16 PCB-only features. The three real loop
testpoints count as fitted hardware. Accepted PCB/footprints and manufacturing
data are preserved. Owner confirms five bare boards and one0.10mm top stencil
already ordered; components are for manual assembly.

## Quick start

1. Review [open decisions](OPEN_DECISIONS.md) and [package/selection evidence](PACKAGE_AND_SELECTION_REVIEW.md).
2. Set assembly counts with `python -B hardware/v4/sourcing/build_purchasing_bom.py --n-f0 {n0} --n-f5 {n5}`,
   then `python -B hardware/v4/sourcing/write_sourcing_reports.py`.
3. Review [master BOM](MASTER_PURCHASING_BOM.csv), [population](REFERENCE_POPULATION.csv),
   [supplier proposal](SUPPLIER_BASKETS.md) and [harness/assembly BOM](HARNESS_AND_ASSEMBLY_BOM.csv).
   Obtain missing exact quotes before considering an order.

## Quantity and price snapshot

Current **{n0}F0+{n5}F5 is provisional**, not an owner purchasing decision.
Fitted electronics quantity is `115*N_F0+134*N_F5`. For all five boards, with
`N_F0=5-N_F5`, this is `575+19*N_F5`:575,594,613,632,651,670 fitted pieces for
N_F5=0,1,2,3,4,5. Every purchasing row includes all six illustrations.

| Quantity / cost | Dated indicative result |
|---|---:|
| Known-price fitted electronics per F0, excludes unquoted parts | USD{summary['priced_fitted_F0_subtotal_usd']:.2f} + unquoted lines |
| Known-price fitted electronics per F5, excludes unquoted parts | USD{summary['priced_fitted_F5_subtotal_usd']:.2f} + unquoted lines |
| Provisional scenario PCBA purchase subtotal, spares/MOQ included | USD{subtotal:.2f} + {unpriced} lines without usable extended quote |
| Separately priced harness connectors/contacts for scenario | USD{summary['priced_harness_scenario_subtotal_usd']:.2f} + wire/tools/materials and other unquoted items |
| Complete electronics basket / delivered total | **Unknown; no defensible complete estimate yet** |

These are partial dated estimates, including explicitly cached page prices and
unconfirmed Coilcraft indicative prices. Historical stock is never called current;
cache age/date and availability are separate columns. Unavailable reference-only
prices are excluded. No FX rate, VAT, missing price, freight, handling or delivery
promise is invented. The supplier proposal records verified published Czech
shipping terms and the2026 LCSC EU import notice, with actual charges unresolved.

## Supplier split and critical outcome

Preferred split: **TME + LCSC**, with **DigiKey** exact mechanical/module/resistor
fallbacks and an exact **Coilcraft Europe** L2/L3 quote. The alternative is to
quote DigiKey+Coilcraft consolidation, or LCSC+DigiKey+Coilcraft when preferred
semiconductor/passive economics justify the extra shipment. Two-supplier complete
availability and minimum delivered cost are not established; Mouser/Farnell exact
fallbacks may add a shipment. No cart was made.

IC1 is verified **BQ25798RQMR**, not BQ25792. Retained exact N4X module, charger,
TPS62933 and GCT USB connector have useful sourced offers. Owner's EVQP0Q02Q,
DR125-2R2-R, TPD2EUSB30ADRTR and exact Nano-Fit choices govern older OPEN tables.
R60 now has a53.0k0.1%25ppm KOA cut-tape proposal; R61 a10k0.1%25ppm YAGEO
proposal. R62/R63 retain1%100ppm0603 requirements. No relaxed R32/R33 precision.

**Unresolved exact supply:** U8 at LCSC/DigiKey; TDK22uF35V C33/C45/C64/C65;
obsolete ordering code C70/C71; PMV16UN Q3/Q8/Q9. L2/L3 need exact manufacturer
stock/delivery quotes. TP1/TP3/TP4 lack verified exact hardware MPNs. Some ordinary
items have retained identity links but unverified price/MOQ/stock. C32/C35/C36
proposals remain conditional on retained effective-capacitance requirements.
Concrete capacitor alternatives are separate and **unapproved**, never silently
substituted into the master BOM. No accepted land deviation is reopened.

Owner decisions: final board split/spares and actual inventory; disposition of
unavailable retained parts versus reviewed alternatives; cable scope/lengths and
missing tools. Battery cells/BMS/NTC/profile are a separate, still unselected
decision. Routine missing quotes and manufacturer data are recorded as work,
not extra architecture approvals.

## Validation and STOP

Reference coverage/uniqueness, exact F0/F5 populations,19 F5-only references,
always-DNP/PCB-only exclusion, real testpoints, grouping totals, owner identities
and protected source hashes pass. [Machine-readable evidence](../evidence/phase5-0-sourcing/consistency.json).
{summary['protected_files_unchanged']} protected CAD/library/manufacturing files unchanged.
No CAD mutation, new native KiCad run, manufacturing regeneration, firmware build,
purchase, cart, commit or push. ERC/DRC and firmware builds were not rerun for
documentation/CSV-only work; accepted release checks are reused.

**STOP for owner review of this procurement proposal. It is not approval to order.**
'''
    (out/'SOURCING_SUMMARY.md').write_text(status,encoding='utf-8')
    print('Updated SUPPLIER_BASKETS.md and SOURCING_SUMMARY.md from calculated CSVs')


if __name__=='__main__':
    main()
