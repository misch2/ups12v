# Phase 5.6 final purchase preparation — PASS

2026-10-20; branch `codex/v4-phase5-component-sourcing`.

Four final deliverables are under `hardware/v4/sourcing/`:
`FINAL_LCSC_ORDER.csv`, `FINAL_TME_ORDER.csv`, `FINAL_ASSEMBLY_BOM.csv`,
`FINAL_PURCHASE_CHECKLIST.md`.

71 LCSC +7 TME order rows; all78 approved quantities retained. Original master
group identifiers restored, with Phase5.5 mapping retained.154 PCB references,
131 fitted parts perF5,655 across five boards;23 excluded references. Harness,
wire,alternative R5 profiles and comparison capacitors remain separate records.
Both R32/R33 and R60/R61 pairs explicitly require joint assembly. R60/R61
assembly values16k/3.01k override unchanged53k/10k schematic metadata.

All78 exact supplier products have saved live public observations20Oct2026.
Initial TME product errors and unhydrated null stock were resolved through its
visible Czech/CZK settings and supported page refresh/search navigation. Final
TME values come from populated Czech/CZK price tables, not initial placeholders
or international caches. LCSC main offer price tiers were isolated from other
supplier offers. All approved quantities satisfy observed MOQ/multiples/stock.
J3 housing1053072202/C17689101:5 stock,5 essential; unreserved.

Confirmed displayed goods prices:LCSC USD230.6740 net;TME CZK532.1356 net.
Derived TME goods+VAT+standard delivery approximatelyCZK813.28;final invoice
rounding/service must be checked by owner. LCSC freight/import/tax collection,
carrier handling and FX remain unknown and are not costed as zero.

Independent verification PASS (`verification.json`):197 protected hashes match,
30 historical sourcing input artifacts byte-identical,all references/quantities/
exact substitutions/connector identities checked. Artifact-tool authored cell
round trips pass for all three CSVs (`artifact-verification.json`). The artifact
tool's documented exporter lacks CSV output; verified cell values were serialized
as RFC4180 UTF-8 BOM CSV. CSV layout has no workbook visual features to render.
Whitespace checks pass for updated tracked documentation. No CAD/native KiCad
operations,ERC/DRC,firmware build,carts,checkout,purchase,payment,commit or push.
CAD and firmware checks/builds were unnecessary for this documentary milestone.

STOP. Next action is owner stock-allocation/delivered-charge verification and
actual purchase; no further sourcing or engineering qualification phase.
