# UPS V4 purchasing preparation

Quick start:

1. Read SOURCING_SUMMARY.md, then OPEN_DECISIONS.md.
   Active checkpoint is Phase5.2; PHASE5_2_COMPATIBILITY_REVIEW.md and
   PHASE5_2_COMMERCIAL_REVIEW.md contain qualification and exact quote gaps.
2. Recalculate the accepted purchasing basis without ordering:
   `python -B hardware/v4/sourcing/build_purchasing_bom.py --n-f0 0 --n-f5 5`, then
   `python -B hardware/v4/sourcing/write_sourcing_reports.py`.
3. Review MASTER_PURCHASING_BOM.csv and HARNESS_AND_ASSEMBLY_BOM.csv.
   Blank price/quantity terms mean **unverified**, never zero cost.
4. Resolve blocked exact parts and conditional proposals, confirm owned stock,
   then compare delivered supplier quotes. This checkpoint authorizes no purchase.

Phase5.2 raw read-only web responses are saved under evidence/phase5-2-sourcing.
`python -B hardware/v4/sourcing/refresh_phase5_2.py` parses these **offline** into
phase5_2_observations.json; it never refreshes live stock or sends supplier messages.
Reviewed exceptions are in phase5_2_reviewed_overrides.json. The builder overlays
these after Phase5.1 observations and writes fresh Phase5.2 consistency evidence.
The report entrypoint now renders Phase5.2. Run the independent checker afterwards:
`python -B hardware/v4/evidence/phase5-2-sourcing/verify_phase5_2.py`.
PROPOSED_ORDERING_CHECKLIST.csv groups all67rows with explicit HOLD states;
APPROVED_PURCHASING_BASKET.csv remains only the accepted dated-price subset.

N_F0/N_F5 are nonnegative integers with total≤5. The CSVs contain coefficients,
fitted quantities, spares, MOQ/multiple rounding and six illustrative five-board
splits. Change counts by rerunning the script, not editing fitted quantities.
Defaults are0F0+5F5, explicitly selected by the owner for purchase capacity.
R5_PROFILE_PURCHASES.csv holds10each8.2k/13.7k/27k; only five fitted positions.
IC1 is exactly5 BQ25798RQMR, no spare. Do not reduce the purchase scenario merely
because initial assembly might use fewer boards. Other coefficients permit
what-if calculations; changing a purchase decision still requires owner review.

REFERENCE_POPULATION.csv includes all154 references, not just purchased parts.
State authority is the reviewed Phase4.22A population, not legacy symbol DNP
properties (notably R11's historical text). Four always-DNP capacitors and16
PCB-only features have no purchasing group. TP1/TP3/TP4 are fitted hardware.

selections.json contains explicit proposed/retained/owner-approved identities.
supplier_observations.json contains dated commercial observations; cache age is
explicit. observation_overrides.json records reviewed supplier choices and
retained exact fallback identities. collect_page_observations.py can rebuild that
file **offline** from saved supplier responses; it does not refresh stock.
The full observations and preservation/consistency evidence are under
`../evidence/phase5-0-sourcing/` and `../evidence/phase5-1-sourcing/`.
phase5_1_observations.json overlays the old offline observations with dated new
evidence. The collector remains a Phase5.0 evidence parser, not a live stock lookup.
replacement_candidates.json generates UNAPPROVED_ALTERNATIVES.csv with zero
automatic purchase quantities. APPROVED_PURCHASING_BASKET.csv is only an explicitly
owner-accepted and dated-quoted subset, not a complete ready-to-order basket.
The entry Phase5.0 deliverables are preserved under Phase5.1 evidence for comparison.

No supplier-import CSV is supplied: current distributor import schemas were not
established reliably. These are review/purchasing documents, not claimed carts or
an instruction to upload an unfinished BOM. No CAD/library/manufacturing files,
firmware, commits or remote state are changed by these scripts.
