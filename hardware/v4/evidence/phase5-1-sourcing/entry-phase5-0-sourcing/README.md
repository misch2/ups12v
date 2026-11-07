# UPS V4 purchasing preparation

Quick start:

1. Read SOURCING_SUMMARY.md, then OPEN_DECISIONS.md.
2. Choose provisional counts without ordering: e.g.
   `python -B hardware/v4/sourcing/build_purchasing_bom.py --n-f0 1 --n-f5 1`.
3. Review MASTER_PURCHASING_BOM.csv and HARNESS_AND_ASSEMBLY_BOM.csv.
   Blank price/quantity terms mean **unverified**, never zero cost.
4. Resolve blocked exact parts and conditional proposals, confirm owned stock,
   then compare delivered supplier quotes. This checkpoint authorizes no purchase.

N_F0/N_F5 are nonnegative integers with total≤5. The CSVs contain coefficients,
fitted quantities, spares, MOQ/multiple rounding and six illustrative five-board
splits. Change counts by rerunning the script, not editing fitted quantities.
The default1+1 scenario is explicitly provisional. Markdown summaries reflect
the delivered1+1 snapshot and must be refreshed if the scenario changes.

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
`../evidence/phase5-0-sourcing/`.

No supplier-import CSV is supplied: current distributor import schemas were not
established reliably. These are review/purchasing documents, not claimed carts or
an instruction to upload an unfinished BOM. No CAD/library/manufacturing files,
firmware, commits or remote state are changed by these scripts.
