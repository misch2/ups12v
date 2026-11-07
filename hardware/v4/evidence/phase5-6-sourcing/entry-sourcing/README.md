# UPS V4 purchase preparation — active Phase 5.5

Quick start:

1. Read the [replacement review](PHASE5_5_SUBSTITUTION_REVIEW.md).
2. Use [LCSC + TME baskets](PHASE5_5_SUPPLIER_BASKETS.md) and
   [78-row CSV](PHASE5_5_SHOPPING_LIST.csv):66 electronics,eight exact harness,
   optional C32 comparison stock and three wire rows.
3. Check [delivered cost](PHASE5_5_DELIVERED_COST.md) and
   [two-supplier exceptions](PHASE5_5_EXCEPTIONS.md).
   Unknown costs are never zero. All product prices remain public allowances,
   not firm supplier quotations or allocated stock.
4. No purchase, checkout, supplier contact or CAD operation is authorized here.

Reproduce the Phase5.5 baskets offline from saved observations:

```text
python -B hardware/v4/sourcing/phase5_5_plan.py
python -B hardware/v4/sourcing/phase5_5_calculations.py
python -B hardware/v4/sourcing/build_phase5_5.py
python -B hardware/v4/evidence/phase5-5-sourcing/verify_phase5_5.py
```

These commands do not refresh stock or create supplier carts. Handwritten review
and cost documents retain the owner-approval boundary. Phase5.4 files below are
historical; do not regenerate them as an active Phase5.5 basket.

Historical Phase5.4 reproduction:

```text
python -B hardware/v4/sourcing/refresh_phase5_4.py
python -B hardware/v4/sourcing/apply_phase5_4_decisions.py
python -B hardware/v4/sourcing/build_purchasing_bom.py --n-f0 0 --n-f5 5
python -B hardware/v4/sourcing/write_sourcing_reports.py
python -B hardware/v4/evidence/phase5-4-sourcing/verify_phase5_4.py
```

These commands parse saved supplier responses and regenerate project-local
procurement evidence. They do not refresh live stock, create carts or contact
suppliers. Historical Phase 5.0–5.3 scripts/checks are retained as history and
must not overwrite the active checkpoint. Entry snapshots are in
evidence/phase5-4-sourcing/entry-sourcing.

Counts remain 154 covered references, 112/131 actual parts per F0/F5, 655 for
five F5 boards. Authoritative historical CAD counts 115/134 are preserved in
separate columns. Sixty-four physical purchase groups plus two extra R5 stock
rows give 66 electronics lines. R5 is ten each of three mutually exclusive
profiles; IC1 exactly five BQ25798RQMR; no optional TP hardware or always-DNP
purchases. No source-CAD or manufacturing population is changed.

selections.json records owner approvals and exact identity proposals.
phase5_4_observations.json overlays older dated observations, including native
EUR fields for R32. MASTER_PURCHASING_BOM.csv retains USD fields for backward
compatibility; use quoted_*_native fields for multi-currency comparisons.
HARNESS_AND_ASSEMBLY_BOM.csv is separate from the 655 PCB components.

The manufacturer C32 bias CSV and complete supplier responses are saved under
evidence/phase5-4-sourcing. The separate candidate has zero extra fitted parts
and cannot be included in an automatic basket before owner approval.

**STOP for owner review before purchases.**
