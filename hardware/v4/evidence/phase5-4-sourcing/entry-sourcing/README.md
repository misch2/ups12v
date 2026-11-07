# UPS V4 purchasing preparation

Quick start:

1. Read SOURCING_SUMMARY.md and OPEN_DECISIONS.md. Active checkpoint is Phase5.3.
2. Recalculate offline, without ordering:
   `python -B hardware/v4/sourcing/build_purchasing_bom.py --n-f0 0 --n-f5 5`
3. Render active reports:
   `python -B hardware/v4/sourcing/write_sourcing_reports.py`
4. Verify counts, identities, costs and preserved source hashes:
   `python -B hardware/v4/evidence/phase5-3-sourcing/verify_phase5_3.py`
5. Review MASTER_PURCHASING_BOM.csv, PROPOSED_ORDERING_CHECKLIST.csv and the separate
   HARNESS_AND_ASSEMBLY_BOM.csv before any future owner-approved purchase.

Blank price means unverified, never free. No cart/order/import file is provided.
The owner-approved dated-price subset is incomplete and is not purchase authorization.

## Current authority and counts

All 154 references remain in REFERENCE_POPULATION.csv. `authoritative_*` columns
preserve Phase4.22A CAD/manufacturing counts and states. The active `qty_per_F0/F5`
and state columns include the explicit Phase5.3 owner assembly override for
TP1/TP3/TP4: existing probe pads/holes, no purchased or obligatorily fitted hardware.
There are no testpoint wire fabrication, purchase, spare or fit requirements.
Actual F0/F5 counts are112/131; historical CAD counts115/134 remain unchanged.
Five F5 boards therefore have655 physical components, versus670 historical positions.
The master has64 physical purchase groups plus2 additional R5 stock lines =66.
Four always-DNP capacitors,16 original PCB features and3 probe pads buy nothing.

Defaults remain owner-selected0F0+5F5. Exactly5 BQ25798RQMR, no spare. R5_PROFILE_PURCHASES.csv
requests10 each8.2k/13.7k/27k for5 mutually exclusive fitted positions. Spares/MOQ
excess are stock, not assembly. Six five-board splits have totals560/579/598/617/636/655.
Changing the purchase scenario still needs owner review; do not reduce capacity
because initial assembly may use fewer boards.

## Inputs and reproducibility

selections.json carries exact proposed/retained/approved identities and original
MPN traceability. The builder overlays supplier_observations.json, then
phase5_1_observations.json, phase5_2_observations.json and phase5_3_observations.json.
Each observation retains date, cache age, packaging, MOQ/multiple, source and limits.
apply_phase5_3_decisions.py reproduces the recorded owner decisions and reviewed
offline inputs; it does not browse, send messages or refresh live inventory.
replacement_candidates.json keeps nonselected alternatives out of automatic purchases.
The active master already contains clearly unapproved TDK prototype and C63 proposals;
their presence is not an approval. Approved prototype C35/C36 remain qualified as such.

Raw evidence, downloaded TDK mapping PDF, live Coilcraft check, entry snapshots,
consistency/preservation checks and generator logs are under evidence/phase5-3-sourcing.
Older refresh/report/check scripts are historical: they do not produce the active
Phase5.3 deliverables and must not be used to overwrite this checkpoint.

PHASE5_3_COMPATIBILITY_REVIEW.md separates datasheet facts, calculations and later
hardware tests. PHASE5_3_COMMERCIAL_REVIEW.md lists the real L3/R32 quote gaps,
regional supplier consolidation and unsent requests. No supplier contact, CAD,
native KiCad, firmware, manufacturing regeneration, checkout, purchase, commit or push.

**STOP for owner review before purchases.**
