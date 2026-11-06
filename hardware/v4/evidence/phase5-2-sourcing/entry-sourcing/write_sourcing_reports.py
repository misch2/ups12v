"""Render the Phase5.1 five-F5 purchasing proposal from documentary CSVs."""
import csv
import json
from collections import defaultdict
from pathlib import Path


def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def main():
    out=Path(__file__).resolve().parent
    ev=out.parent/'evidence/phase5-1-sourcing'
    rows=read_csv(out/'MASTER_PURCHASING_BOM.csv')
    harness=read_csv(out/'HARNESS_AND_ASSEMBLY_BOM.csv')
    s=json.loads((ev/'consistency.json').read_text())
    candidates=json.loads((out/'replacement_candidates.json').read_text())
    for candidate in candidates:
        candidate['evidence']='; '.join('../evidence/phase5-1-sourcing/'+name.strip() for name in candidate['evidence'].split(';'))
    with (out/'UNAPPROVED_ALTERNATIVES.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(candidates[0]));w.writeheader();w.writerows(candidates)
    by=defaultdict(list)
    for r in rows:
        supplier=r['candidate_supplier']
        key=supplier if supplier in ('LCSC','TME','DigiKey') else 'Coilcraft Europe' if supplier.startswith('Coilcraft') else 'Unresolved exact supply'
        by[key].append(r)
    subtotal=s['priced_purchase_scenario_subtotal_usd']
    htotal=s['priced_harness_scenario_subtotal_usd']
    extra=sum(c['conditional_extended_usd'] for c in candidates if isinstance(c['conditional_extended_usd'],(int,float)))
    approved=[r for r in rows if r['approved_basket_qty'] not in ('','0')]
    approved_cost=sum(float(r['extended_scenario_cost_usd'] or 0) for r in approved)
    missing=[r for r in rows if not r['extended_scenario_cost_usd']]
    text=f'''# Phase5.1 supplier baskets — STOP before purchasing

2026-10-19. Owner purchasing basis **N_F0=0,N_F5=5**. Assembly split remains open;
purchase capacity is all five F5 PCBs. No cart, RFQ transmission or order created.

Quick start: review OPEN_DECISIONS.md, then the master CSV and separate R5 file.
**67 planning lines =65 reference groups +2 extra R5 stock options**. The five R5
positions are counted once; purchase10 each8.2k/13.7k/27k,30 pieces total. IC1 is
exactly5 BQ25798RQMR, no automatic spare or deduction for owned BQ25792.

## Cost boundary

The planning worksheet has **USD{subtotal:.4f} priced/indicative PCBA subtotal**
and **{len(missing)} unpriced lines**. Fitted-only partial F0/F5 costs are
USD{s['priced_fitted_F0_subtotal_usd']:.4f}/USD{s['priced_fitted_F5_subtotal_usd']:.4f}.
These are incomplete estimates, not complete board prices. Keep all missing parts,
tax, freight, handling and FX outside the subtotal. Price/cache dates in the CSV
control; historical page stock is not presented as today's stock. Coilcraft's
USD28.80 for5+5 inductors is a retained indicative allowance without a current
stock/delivery quote. Plain cut tape avoids Digi-Reel service fees; none selected.

Separate harness known/indicative connector/contact subtotal **USD{htotal:.4f}**;
wire, XT30, labels, paste, flux, tools and other blank quotes are additional.
Combined documented partial allowance is **USD{subtotal+htotal:.4f} before tax/freight**.
Applying21% solely as an illustrative VAT calculation gives USD{(subtotal+htotal)*1.21:.4f};
this is not a delivered quote or a claim that every supplier collects tax this way.

APPROVED_PURCHASING_BASKET.csv contains only **{len(approved)} explicitly owner-accepted
exact identities with dated price/quantity observations**, subtotalUSD{approved_cost:.4f}.
It is a subset, not a complete assembly basket or authorization to order. Its stock
freshness still needs checkout-time verification. All remaining master rows stay
on hold for engineering selection or procurement closure. Owner review of Phase5.0
did not silently approve its many PROPOSED identities.

## Delivered strategies to compare

| Strategy | Allocation and suppliers | Verified delivered-cost terms | Missing quote / practical assessment |
|---|---|---|---|
| A: preferred TME+LCSC with exact fallbacks | TME:11 current master lines; LCSC:main semiconductor/passive lines; DigiKey:Nano-Fit headers/mates,N4X,R5 cut tape,precision parts; Coilcraft Europe:L2/L3 | TME standard <=20kg CZK140 net/169.40 gross, indicative1–2working days. DigiKey Czech standard UPS DDP:free atCZK1800+,otherwiseCZK600, typical48h | Four supplier shipments plus unresolved exact items; LCSC freight/VAT/duty/handling and Coilcraft UK delivery not quoted. Do not combine with already-submitted JLCPCB shipment |
| B: fewer shipments, conditional recommendation | LCSC+DigiKey+Coilcraft; move TME exact switch/diodes/L1/passives into DigiKey shipment if exact stock/price confirmed | Avoiding TME can save its169.40CZK gross shipment, subject to package terms. DigiKey fee threshold as above | Three suppliers is a quote target, not verified complete availability. Accept a DigiKey line-price premium only if below avoided TME delivered charge after FX/tax. Exact transfer prices absent; no defensible cheapest-total claim |
| C: EU consolidation quote target | LCSC+DigiKey+Farnell, with Farnell2289069/2289071 exact Coilcraft cut-tape lines plus eligible TME parts | Exact Coilcraft family/distributor identities established; current Czech cut-tape quote not captured | May eliminate UK direct freight/import handling. Farnell freight/stock and5-piece line prices missing. Full-reel Farnell5131620 MOQ400 is rejected for this order |

TME line count above is checked against the allocation table below; use its generated
count if source allocation changes. No separate Mouser shipment is justified by
verified current supply in this checkpoint. Mouser remains a fallback quote source.

Sources: [TME Czech shipping](https://www.tme.eu/cz/how-to-buy/7328/zpusoby-a-ceny-dopravy/),
[DigiKey Czech delivery](https://www.digikey.cz/cs/help-support/delivery-information).
DigiKey's UPS DDP option differs from its FedEx/DHL CPT options; obtain the actual
Czech VAT invoice and choose standard distributor stock. Marketplace extra freight
is unquoted, so no marketplace offer is used as a confirmed fallback.
[LCSC's current EU import notice](https://www.lcsc.com/help-center/notice/eu-low-value-import-regulations-2026)
flags VAT and low-value import duty changes. The category count, duty collection,
carrier brokerage and tax base for this basket are **unknown**; do not assume the
old duty-free allowance or invent a fixed charge. LCSC shipping method/transit,
IOSS/DDP applicability and final tax must be quoted. No customs-law determination
is made from a supplier notice. Czech currency conversion/card FX fees unknown.
[Coilcraft Europe](https://www.coilcraft.com/de-de/contact/saleslocations/europe-and-africa/)
states no minimum order and UK warehouse stock generally; this does not establish
stock of either selected part. Quote5 each exact MEC suffix together, incoterms,
VAT/import/clearance and delivery. All arrival dates remain supplier estimates.

## Conditional replacements — excluded from accepted basket

| References | Proposed exact candidate | Fit/spare/MOQ excess -> conditional order | USD page allowance | Disposition |
|---|---|---|---:|---|
'''
    for c in candidates:
        text+=f"| {c['references']} | [{c['candidate_mpn']}]({c['url']}) {c['sku']} | {c['conditional_min_fitted']}+{c['conditional_spares']}+{c['conditional_MOQ_excess']} -> {c['conditional_order_qty'] or 'unquoted'} | {c['conditional_extended_usd'] or 'unquoted'} | {c['approval_status']} |\n"
    text+=f'''
The four priced candidates addUSD{extra:.4f} only if their original unpriced lines
are replaced after the listed approval/evidence gates. This makes an illustrative
partial PCBA allowanceUSD{subtotal+extra:.4f}, still{len(missing)-4}unpriced lines;
with the priced harness portion, USD{subtotal+extra+htotal:.4f} before tax/freight.
PMV16XN is an alternative to AO3400A, never a second purchase. Exact TDK suffix
equivalence remains unvalidated, so even this conditional sum is not an approved
basket. C32 qualification is not repaired by adding these candidate costs.

## Complete planning allocation

Quantities: fitted + spare + alternative-profile stock = desired, then separately
MOQ-rounded requested purchase. A blank order means terms missing; use the desired
quantity for obtaining the quote. An unavailable line's numeric quantity is a
planning target only. Prices do not authorize PROPOSED parts.
'''
    for supplier,rr in by.items():
        total=sum(float(r['extended_scenario_cost_usd'] or 0) for r in rr)
        text+=f'\n### {supplier}: {len(rr)} lines, USD{total:.4f} priced/indicative\n\n'
        text+='| ID / refs | Exact selected MPN / SKU | Fit+spare+option | Order / MOQ excess | USD extended | State |\n|---|---|---:|---:|---:|---|\n'
        for r in rr:
            identity=f"[{r['mpn']}]({r['direct_product_url']})" if r['direct_product_url'] else r['mpn']
            text+=f"| {r['group_id']} {r['references']} | {identity};{r['distributor_sku'] or 'SKU missing'} | {r['fitted_qty_scenario']}+{r['suggested_spares']}+{r['alternative_profile_stock_qty']} | {r['proposed_purchase_qty'] or 'quote needed'} / {r['MOQ_rounding_excess'] or ('0' if r['MOQ_rounding_excess']=='0' else '?')} | {r['extended_scenario_cost_usd'] or 'unpriced'} | {r['availability']};{r['selection_status']} |\n"
    text+='\n## Quotes still missing\n\n'
    text+='| ID / refs | Exact MPN | Requested minimum with spares | Gap |\n|---|---|---:|---|\n'
    for r in missing:
        text+=f"| {r['group_id']} {r['references']} | {r['mpn']} | {r['desired_qty_before_MOQ']} | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |\n"
    text+='''
Also refresh R5 cached quotes, exact Coilcraft stock/lead times and all shipment
charges. No supplier-import CSV is generated: supported import schema remains
unverified. REVIEW worksheets are not claimed shopping carts.
'''
    text=text.replace('TME:11 current master lines',f"TME:{len(by['TME'])} current master lines")
    (out/'SUPPLIER_BASKETS.md').write_text(readable_prose(text),encoding='utf-8')
    text=f'''# Phase5.1 sourcing summary — five F5 purchase capacity

Quick start: read [open decisions](OPEN_DECISIONS.md), review the
[master BOM](MASTER_PURCHASING_BOM.csv) and [supplier baskets](SUPPLIER_BASKETS.md).
This is procurement preparation; **STOP for owner review before purchasing**.

- **67 purchasing planning lines**, covering65 reference groups plus two additional
  R5 profile stock lines. Five F5 boards require **670 fitted parts**. Counts115F0/
  134F5 and19F5-only preserved; four DNP and16 PCB-only refs excluded.
- **5×TI BQ25798RQMR**, LCSC C2876593, displayed2913 on2026-10-19;
  5×USD2.8576=**USD14.2880**, MOQ/multiple1. Owned BQ25792 is separate inventory.
- R5: **10each8.2k/13.7k/27k0805 1%**,750kHz. DigiKey exact Yageo CT codes
  proposed, indicativeUSD0.34 per10/totalUSD1.02. Cached stock ages5days–2months
  are explicit. Thirty purchased resistors represent **five positions**, not30fits.
- Priced/indicative PCBA subtotal **USD{subtotal:.2f}** with **{len(missing)}unpriced lines**;
  partial fitted F0/F5 **USD{s['priced_fitted_F0_subtotal_usd']:.2f}/USD{s['priced_fitted_F5_subtotal_usd']:.2f}**.
  This excludes unknown parts/tax/freight/handling. Separate priced harness portion
  **USD{htotal:.2f}**; combined incomplete allowance **USD{subtotal+htotal:.2f}**.
- Four held priced candidates would addUSD{extra:.2f}, taking the conditional PCBA
  allowance toUSD{subtotal+extra:.2f}, still{len(missing)-4}unpriced lines. They remain excluded from
  the accepted basket. **No complete delivered total can yet be quoted.**
- Preferred split: LCSC{len(by['LCSC'])}lines/TME{len(by['TME'])}/DigiKey{len(by['DigiKey'])}/
  Coilcraft2, plus{len(by['Unresolved exact supply'])}unresolved-supply groups. Recommended
  consolidation quote target: LCSC+DigiKey+Coilcraft or Farnell; transfer exact TME
  parts only if delivered savings are demonstrated. TME Czech standard shipment
  CZK169.40gross; DigiKey free atCZK1800,otherwiseCZK600. Other freight/import costs unknown.

U8 DBVTQ1 is an available, verified package-ordering option awaiting owner acceptance.
C70/C71 TDK in-production nominal/package candidate also awaits acceptance.
PMV16UN is EOL; AO3400A is a sourced static/package candidate, PMV16XN has no verified
small-order source. C33/45/64/65 exact TDK suffix equivalence and Ceff remain open.
TP1/3/4 exact hardware remains open:1.00mm PCB drill versus1.02mm recommended holes
for common beaded parts. Do not force-fit or enlarge ordered boards.

Bias evidence is now saved: C35/C36 roughly12–14uF typical at3.3V; an explicitly
assumed conservative screen gives4.71uF, above C35's2.2uF floor, not a guaranteed
combined manufacturer bound. C32 proposed2.2uF falls to roughly0.5–0.6uF typical
at18V; hold its selection pending a justified input-network requirement or a
qualified same-footprint part. See [compatibility review](PHASE5_1_COMPATIBILITY_REVIEW.md).

Harness capacity:20Nano-Fit power harnesses,40tin power contacts+10trial spares;
5each exact mating housing+1spare (MOQ excess separate);5J4/J6 cable pairs and
40JST contacts+10spares (MOQ100 creates50excess). Illustrative5mred+5mblack20AWG,
11msignal wire include spares; lengths/OD/tool ownership still need confirmation.
Battery cells,2S/3S/4S BMS andNTC remain separate decisions. SYS reset on exceptional
pack disconnection is accepted; no architecture changes. External SYS PD converter
and3S firmware are deferred. No battery configuration selected.

Only{len(approved)}explicitly accepted exact/dated-quoted lines are in
APPROVED_PURCHASING_BASKET.csv; all selection/quote holds remain visible elsewhere.
No order/cart/CAD/firmware/manufacturing/commit/push. Protected196files unchanged;
full population/group/owner-quantity checks pass in
[consistency evidence](../evidence/phase5-1-sourcing/consistency.json).
'''
    (out/'SOURCING_SUMMARY.md').write_text(readable_prose(text),encoding='utf-8')
    print(f'Rendered Phase5.1: {len(rows)} planning lines; {len(missing)}unpriced; USD{subtotal:.4f}+harnessUSD{htotal:.4f}; candidate additionsUSD{extra:.4f}')


def readable_prose(text):
    # Expand compact prose tokens without altering exact part-number strings.
    replacements={
        'covering65':'covering 65', 'Counts115F0/':'Counts 115 F0 / ',
        '134F5 and19F5-only':'134 F5 and 19 F5-only', 'displayed2913':'displayed 2913',
        'purchase10 each':'purchase 10 each ', '10each8.2k/13.7k/27k0805 1%':'10 each: 8.2 kΩ / 13.7 kΩ / 27 kΩ, 0805, 1%',
        '750kHz':'750 kHz', 'not30fits':'not 30 fitted parts',
        '19unpriced':'19 unpriced', '15unpriced':'15 unpriced',
        'addUSD':'add USD ', 'toUSD':'to USD ', 'subtotalUSD':'subtotal USD ', 'allowanceUSD':'allowance USD ',
        'LCSC36lines/TME11/DigiKey14/':'LCSC 36 lines / TME 11 / DigiKey 14 / ', 'Coilcraft2, plus4':'Coilcraft 2, plus 4 ',
        'CZK169.40gross':'CZK 169.40 gross', 'atCZK1800,otherwiseCZK600':'at CZK 1800, otherwise CZK 600',
        'roughly12–14uF':'roughly 12–14 µF', 'at3.3V':'at 3.3 V', 'gives4.71uF':'gives 4.71 µF',
        "C35's2.2uF":"C35's 2.2 µF", 'proposed2.2uF':'proposed 2.2 µF',
        'roughly0.5–0.6uF':'roughly 0.5–0.6 µF', 'at18V':'at 18 V',
        'capacity:20Nano-Fit':'capacity: 20 Nano-Fit', 'harnesses,40tin':'harnesses, 40 tin',
        'contacts+10trial':'contacts + 10 trial', '5each':'5 each', '5J4/J6':'5 J4/J6',
        '40JST':'40 JST', 'contacts+10spares':'contacts + 10 spares', 'MOQ100 creates50excess':'MOQ 100 creates 50 excess',
        'Illustrative5mred+5mblack20AWG':'Illustrative 5 m red + 5 m black 20 AWG', '11msignal':'11 m signal',
        'cells,2S/3S/4S BMS andNTC':'cells, 2S/3S/4S BMS and NTC', 'and3S firmware':'and 3S firmware',
        'Only10explicitly':'Only 10 explicitly', 'Protected196files':'Protected 196 files',
        'Applying21%':'Applying 21%', 'exactly5':'exactly 5', 'TME:11':'TME: 11',
        'LCSC:main':'LCSC: main', 'DigiKey:Nano-Fit':'DigiKey: Nano-Fit', 'Coilcraft Europe:L2/L3':'Coilcraft Europe: L2/L3',
        'indicative1–2working':'indicative 1–2 working', 'CZK1800+,otherwiseCZK600':'CZK 1800+, otherwise CZK 600',
        'typical48h':'typical 48 h', 'its169.40CZK':'its 169.40 CZK', 'Quote5 each':'Quote 5 each',
        'and5-piece':'and 5-piece', 'MOQ400':'MOQ 400', 'USD1.02':'USD 1.02',
        'indicativeUSD0.34':'indicative USD 0.34', 'stock ages5days–2months':'stock ages 5 days–2 months',
        '1.00mm':'1.00 mm', '1.02mm':'1.02 mm', 'for5+5':'for 5 + 5'
    }
    for old,new in replacements.items():
        text=text.replace(old,new)
    return text


if __name__=='__main__':
    main()
