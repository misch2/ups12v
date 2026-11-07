# Phase 5.0 validation and evidence limits

2026-10-19. Branch `codex/v4-phase5-component-sourcing`, entry clean. No subagents,
CAD editor/native KiCad operation, manufacturing regeneration, firmware change,
purchase/cart, commit or push.

Inputs: accepted Phase4.22A F0/F5 reference population CSVs and detailed raw fields;
Phase4.19 sourcing; Phase4.22 assembly/pinmap; current BOM and handover; retained
Phase4.24S manufacturer/package evidence and accepted Phase4.24W preservation.
Current production schematic hash matches the population authority. Later paste
adoption preserved all component identities/footprints; PCB hash matches accepted W.
Owner's Phase5.0 exact choices and manufacturing-order update take precedence over
older OPEN/pending-export wording. No old audit/engineering phase was restarted.

PASS:

- All154 reference rows match both reviewed state/quantity lists exactly.
- F0=115; F5=134; exact19-reference F5 delta; four always-DNP;16 PCB features.
- Exactly one purchasing group for every fitted reference, no group for excluded
  references; TP1/TP3/TP4 real hardware retained; bare pads/holes/net ties excluded.
- Group totals equal reference totals; identities, selected grades and actual
  footprints agree within every group.65 purchasing lines.
- Eight quantity scenarios:0+0,5+0,4+1,3+2,2+3,1+4,0+5,1+1. Zero-fit groups have
  zero spares/order quantity, even if supplier terms unknown. All six five-board
  column calculations agree;575+19*N_F5 fitted pieces across five boards.
- Negative counts, total6 and other over-five input rejected before output mutation.
- MOQ/multiple rounding is separate from fitted quantities and deliberate spares;
  unknown terms remain blank. All CSV row/column shapes pass, including alternatives.
- Importing the three sourcing tools creates/modifies no outputs. No CAD import.
-196 protected CAD/library/manufacturing files retain exact pre-task hashes.
- `git diff --check` passes; final delivered scenario restored to provisional1+1.

Detailed results: `consistency.json`, `independent-consistency.json`,
`protected-before.json`; source hashes are retained. Raw supplier responses and
extraction are here; evidence paths in the BOM identify individual observations.
Manufacturer sources/revisions/actual package relationships are summarized in
`../../sourcing/PACKAGE_AND_SELECTION_REVIEW.md`.

Commercial limits: no complete basket quote, actual checkout, reservation or
delivered-cost optimum established. Source cache ages are explicit; retrieval on
2026-10-19 does not make historical stock current. Unavailable reference-only
prices are excluded. Missing fields are unverified, not zero. Partial subtotals
include some cached/indicative observations and unconfirmed Coilcraft prices;
they must not be described as complete/current costs. Shipping/VAT/handling/import
rules are quoted only where directly observed; actual basket charges remain open.

Engineering limits: no physical fit, crimp, reflow, bias, thermal, power-up or
electrical measurement. Conditional/unapproved parts are not promoted to accepted
selections. Accepted prototype copper/land deviations are retained. No firmware
build or ERC/DRC rerun for sourcing documentation/CSV-only work; accepted release
checks are reused, not newly claimed. **STOP at procurement proposal for review.**
