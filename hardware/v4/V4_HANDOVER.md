# UPS V4 handover — Phase 2 charger/power-stage review candidate

Updated 2026-10-10. Resume from this file and `AGENTS.md`; conversation history is not required.

**The charger/power-stage milestone has advanced but is NOT complete or accepted. Stop at the owner review checkpoint. Hot-plug damping, fuse land-pattern confirmation, variant checks and schematic presentation remain open. No MCU/USB integration, real PCB work, fabrication or power-up approval.**

## Repository and exact targets

- Branch: `codex/v4-phase2-power-stage`.
- Current HEAD: `1c76302d4bac77c0e1c3b6dedf370d1f888208c7` (`update agents.md for component source`). The owner changed supplier/BOM instructions during this session; the current AGENTS.md governs.
- Resume HEAD was `fd73fe4cf89fc02d8de28f090762ac8d0bfd75cf` (`Phase 2b`). Earlier documentation baseline `5dea83068f5428c3bbce3b4efd9c22399f11d9f5`; hardware baseline `9065cace5a7a7f95a39692a55897cd89e01024ea`.
- No agent commit, staging, push or tag. HEAD alone still does not reproduce the V4 CAD: preserve untracked files.
- Only CAD target: `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_sch` and `.kicad_pro`. Local `fp-lib-table` and `ups_v4.pretty/Littelfuse_451_2410.kicad_mod` were created through Konnect. No matching real `.kicad_pcb` exists.
- Tracked uncommitted change: this handover. Untracked: `ups_v4/`, `V4_BOM_REVIEW.md`, `V4_CHARGER_PACKAGE_MAP.md`, `V4_PROCUREMENT_RESUME.md`, historical `evidence/phase2-*`, new power-stage exports/renders/checks, and verification/BOM scripts. Use `git status --short` for the exact list; do not blindly add everything.
- Production V2/V3 and firmware unchanged. No firmware build was needed or run. Preserve local credentials under `software/ups/include/secret/`.
- Ignore disposable `.validation/`, `.konnect/`, `.kicad_prl`, locks/backups and downloaded `evidence/references/`. Keep review evidence distinct from scratch source.

## Preserved owner decisions

1. Reliability, electrical correctness, battery safety and maintainability take priority. Preserve production hardware.
2. Exactly one physical PCB with BQ25792/BQ25798 and 2S/4S population variants. See requirements, architecture and variants documents for detailed decisions; do not redesign completed architecture.
3. Supported regulated adapter envelope is up to 20 V nominal, assumed +5% = 21 V. Basic polarity protection, appropriate component ratings, BMS and fusing are required. No complex active OVP/eFuse or accidental 25/30 V adapter survival requirement.
4. CE defaults HIGH, with normally-off open-drain MCU sink. No external 250 ms lease/watchdog. Preserve the BQ25792 charger-only reset risk.
5. Initial design and qualification exclusively VSYS. PMID backup development/qualification is deferred. Optional DNP/test provisions do not approve backup operation.
6. Future USB 3.3 V buck and power mux remain mandatory for USB-only programming, with reverse-current and signal back-power isolation. Not integrated in this milestone.
7. Present charger/power-stage schematic for owner review before ESP32/USB integration or routing. F01 acceptance is not acceptance of subsequent changes.
8. KiCad 10 and Konnect only for serialized CAD/library/table changes. Do not hand-edit these files.
9. Real-board changes require exact full-path live IPC confirmation. Closed disposable footprint checks under `.validation/` are separately permitted; they do not pass the real-board gate.

## Completed work and evidence history

- Accepted stage 2.1 F01: charger-side VBUS joins IC1.2/.3/.8, NT4.1 and C7.1/C13.1/C16.1. `V4_PHASE2.md` and F01 evidence are historical acceptance records.
- Stage 2.2 root cleanup and CE implementation preserved. R9 10k pull-up, BAS116H D3/D4 diode OR from REGN and future MAIN_3V3, PMV16UN Q3 sink, R10 10k gate pulldown and R11 1k request resistor. J2.2 is SYS, not PMID. J4 mapping: 1 MAIN_3V3 input from normal buck, 2 system return, 3 SDA, 4 SCL, 5 CHG_REQ, 6 INT. Incompatible with V3 header wiring. USB 3V3 must not bias CE.
- Fresh resume XML/ERC proved all stage 2.2b pin partitions unchanged. Baseline schematic SHA256 `9e24befb0abd0773dc8e0fef906ce1ee626a21169359d601d055aae8a0e5804c`; ERC then 0 errors / 2 missing custom-library warnings. See `phase2-resume-verification.json`.
- Current stage 2.3 replaces the legacy 33-representation IC1 with official `Battery_Management:BQ25798`, logical pins 1-29, footprint `Package_DFN_QFN:Texas_RQM0029A_VQFN-29_4x4mm_P0.4mm`. Redundant legacy 30/31/32/33 correspond to split corner lands of 1/9/16/24. Package reconciliation and limits: `V4_CHARGER_PACKAGE_MAP.md`.
- System-return migration: C3.2, IC1.10, J4.2, Q3.2, R10.2 and TP1.1 moved GND to PGND. Quiet GND now contains R5.2, R7.1, J6.1 and NT1.1; NT1.2 is PGND. Keep one local quiet-return join near IC1 GND, not a board-wide moat. Basis: TI BQ25798 Rev. C section 8.4.1 and TI grounding support linked in the package record.
- Input/PMID forward ceramics C12/C15/C18 and C13/C16 changed to Murata GRM32ER71H106KA12L 10 uF/50 V, 1210. C6/C7/C9 now GRM155R71H104KE14D 100 nF/50 V, 0402. REGN C3 now GRM21BR71E475KA73L 4.7 uF/25 V, 0805. These assignments do not prove effective capacitance.
- Legacy PMID bulk C20/C22 (20 V) and C24/C25 (25 V) marked DNP for initial VSYS builds. Do not fit without new rating/derating/forward-mode qualification; no PMID backup qualification.
- F1 inserted in positive input: J1.2 -> F1.2; F1.1 -> VIN1/VAC1/C9/input FETs. Saved prototype candidate Littelfuse 0451005.MRL, 5 A. Compared 4 A versus 5 A derating in `V4_PROCUREMENT_RESUME.md`; cable/fault/temperature coordination remains open.
- Fuse footprint created only through Konnect, disposable readback/render `fuse-2410-acceptance.png`. Geometry is PROPOSED, not physically accepted: manufacturer recommended land-pattern confirmation remains outstanding.
- `V4_BOM_REVIEW.md` added under current sourcing rules. TME and LCSC both preferred; manual small-volume assembly. Exact identities/cached observations are separated from current stock/price/MOQ, which remain UNVERIFIED unless expressly dated. Konnect JLC catalog search failed because its local database is absent; do not interpret this as unavailable parts.
- TI's public support attachment recovered BQ25792 SLUSDG1D, April 2026. Link and actual revision recorded in procurement resume; do not rehost the PDF marked confidential. 2S POR charge-current risk remains 2 A; broad register equivalence is not established.

## Verification and current acceptance limits

The final fresh verification record is appended below after CAD is frozen. Earlier `phase2-3-power-final*` renders/exports and `phase2-3-power-verification.json` may describe intermediate hashes; do not assume they represent current CAD.

- `verify_power_stage.py` independently compares every exported pin partition against the resume baseline plus explicit intended changes: remove redundant IC1 pins, move six system returns, insert F1. It also checks named critical nets, logical pins 1-29, source SHA256, export/ERC freshness and zero ERC errors/warnings. It does not validate physical geometry or component suitability.
- `verify_stage2_checkpoint.py` is historical only and now rejects any source hash other than saved stage 2.2b. Do not run it against later CAD as current acceptance.
- `phase2-3-schematic.diff` is an explicit no-index comparison against the read-only V3 source. Konnect reserialization creates a large diff; electrical scope is established by all-pin partition checks, not diff line count.
- Render inspection found remaining collisions around PROG R5, R11, BATP C23 and IC1/output connector box; legacy title/revision also remains. Schematic is not visually accepted merely because ERC passes.
- No real V4 PCB: DRC and schematic/PCB parity not run. No matching-hardware electrical, thermal, hot-plug, cell/load, CE timing or USB partial-power measurements. ERC success alone establishes none of these.

## Unresolved work and next unfinished milestone

Continue **the same charger/power-stage schematic milestone**, not the MCU/PCB phase:

1. Resolve TI's supported-adapter hot-plug provision: BQ25798 Rev. C Figure 8-1 p.130 recommends series 2 Ohm / shunt 2.2 uF above 15 V. Current CAD has a note only, no accepted/populated branch. Select exact pulse-rated parts with manufacturer voltage/pulse/Ceff evidence, practical TME/LCSC sourcing and package acceptance, then implement through Konnect and explicitly extend partition assertions. The ideal-step calculations in procurement resume are not measurements.
2. Confirm F1 manufacturer recommended lands and package geometry before accepting the assigned local footprint. Complete fuse/source/cable/BMS coordination and retained AON7528/12 V clamp hot-plug/SOA analysis for the supported 21 V envelope. Final hardware qualification remains later; no active OVP redesign.
3. Finish BQ25792/BQ25798 pin/package and 2S/4S PROG/POR comparison using actual manufacturer revisions. Separate necessary compatibility from unproven broad register equivalence. 27k/8.2k assembly resistor, 750 kHz; no user cell-count jumper. Shared official footprint disposable render/readback acceptance needs explicit evidence if not yet captured.
4. Reconcile BOM metadata and remaining exact MPNs: C3 package source; BAT/SYS GRJ21BR61E106KE01K dielectric versus inherited X7R; C8 GCM1555C1H102JA16D dielectric; Q3 reel suffix, resistors, NTC, connectors and harness. Quantify forward Ceff across voltage/temp/tolerance/aging; refresh critical sourcing before freeze/order. Preserve historical valid Source/Bought fields.
5. Finish visual cleanup through Konnect. Use free A3 space, correct title/revision, separate fields and boxes, remove only proven floating legacy stubs. Preserve electrical partitions; do not add flags to mask accidental disconnections.
6. Re-export, run ERC, compare all pin partitions, inspect rendered result and explicit diff after each coherent CAD change. Update BOM and this handover.
7. **Stop and present the completed charger/power-stage schematic for owner review.** Do not integrate MCU/USB or begin a real PCB without subsequent authorization and the live IPC gate.

CE hardware qualification remains open: future buck ramp/REGN sequencing, cold diode VF/leakage, reset/brownout/gate discharge, absent battery, unintended charge pulses and no USB injection. BQ25792 charger-only reset can restore 2 A while host wanted 0.5 A if Q3 remains on; firmware must release CE before reconfiguration/on detected fault. No external expiry and no hardware 0.5 A ceiling.

## Konnect and reproduction

Konnect discovery/config/UI/mutation/export/ERC/render calls succeeded; KiCad CLI 10.0.7. No GUI process detected, IPC `not_configured`: file-based schematic editing is available, live real-board editing is not verified. Never delete a live lock or force fallback around an editor. Prior Ping plus `GetOpenDocuments:AS_UNHANDLED` did not establish board access.

For later real PCB authorization, create/open the exact V4 `.kicad_pcb` in PCB Editor and use Konnect `open_project` plus full-path read queries. Require exact path and live source. `save_project` saves live PCB, not a closed schematic; never call blindly.

From repository root, fresh checks only (no serialized source mutation):

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
$v4cli = 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
& $v4cli sch export netlist --format kicadxml --output hardware/v4/evidence/phase2-3-review.net.xml hardware/v4/ups_v4/ups12v_v4.kicad_sch
# Run Konnect run_erc with output hardware/v4/evidence/phase2-3-review-erc.json.
# Capture reviewed CAD SHA256, then run:
python hardware/v4/evidence/verify_power_stage.py --export hardware/v4/evidence/phase2-3-review.net.xml --erc hardware/v4/evidence/phase2-3-review-erc.json --expected-sha256 <reviewed-sha256> --output hardware/v4/evidence/phase2-3-review-verification.json
python hardware/v4/evidence/build_bom_review.py hardware/v4/evidence/phase2-3-review.net.xml
git diff --check
```

Registry warnings in sandbox did not prevent successful parsed exports. Commit/push only when requested; select task files explicitly and exclude credentials/scratch/cache artifacts.

## Frozen final verification snapshot

- Source SHA256: `2938c56c36c49f4124be519d3b6abe003781b3fd3ac0175aa5b8d36854d156de`.
- Fresh [XML](evidence/phase2-3-review.net.xml), [Konnect ERC](evidence/phase2-3-review-erc.json), [independent verification](evidence/phase2-3-review-verification.json), and [render](evidence/phase2-3-review.png) were regenerated after the CAD owner froze all mutations.
- ERC **0 errors / 0 warnings**. All pin partitions matched explicit expected changes; logical IC1 pins 1-29, six return migrations, F1 series path, F01 and CE sets passed. BOM inventory regenerated from this exact XML, 40 groups.
- Full render inspected: remaining visual issues listed above are real and remain open. No fabricated or measured evidence is claimed.
- Explicit no-index schematic diff saved; tracked `git diff --check` passed. V2/V3, firmware and AGENTS.md have no uncommitted changes. Current branch/HEAD remain as recorded above. All CAD/evidence/new review files remain uncommitted; no agent staging/commit.
