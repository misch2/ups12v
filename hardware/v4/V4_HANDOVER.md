# UPS V4 handover — ESP32-C3 and power-domain schematic phase

Updated 2026-10-10. Resume from this file and `AGENTS.md`; conversation history is not required.

**STOPPED BY OWNER — Phase 3.2 is incomplete.** The authoritative stopped-state
snapshot is [phase3-2-state-snapshot-2026-10-10.md](evidence/phase3-2-state-snapshot-2026-10-10.md).
Latest saved schematic SHA256 is `ac7e0d19e90848bf7f04c9c2aef9e4deadbb502559a12af42d7e5e65e83f4e1a`.
New latch, live-arm gating, slew switch and MCU reset-supervision changes await
final independent review. ERC and render below are stale against this hash;
the XML is newer but has not received final independent preservation review.
The intermediate descriptions and hashes below must not be treated as current
acceptance evidence. Git has staged and unstaged uncommitted changes; preserve
the index. No PCB work or hardware power-up was performed.

**Current state: Phase 3.2 MCU power-domain/isolation schematic checkpoint in progress.** U3/U4 are separate 3 A TPS62933 candidate bucks, U5 is a normal-priority TPS2116 mux, U6 is the original Rev.D TCA9517 buffer, U7 is a MAIN-powered TPS389033 3.17 V supervisor for PR1, and charger requests are gated by both normal-domain validity and firmware authorization. USB-only programming remains USB_VBUS -> USB3V3 -> U5 VIN2 -> MCU3V3; USB must not feed SYS, BATTERY, REGN or MAIN_3V3. No schematic freeze, purchase, real PCB layout, fabrication or hardware power-up approval.

**VAC1 transient concern remains OPEN and is a fabrication/power-up gate.** IC1 pin 9 is directly on VIN1 and has a 30 V absolute maximum (TI Rev. C section 6.1); the prior hypothetical model reaches 39.725 V. Bounded assessment: `evidence/phase3-vac1-review.md`. Ordinary powered-adapter hot plugging can cause this mechanism, but the exact predicted peak is not established for this two-node/FET circuit. Qualify/tune passive damping if needed; no unnecessary active OVP and no renewed broad sourcing research. No mitigation or safe-power-up result is claimed.

## Repository and exact targets

- Verified branch: `codex/v4-phase2-power-stage`; HEAD `1c2d99984cf8ccd92de2aee343e6068634003ed7`. Phase 3.2 changes remain uncommitted. The shared checkout currently contains both index-staged and working-tree changes across the schematic, evidence and handover/BOM files; no commit, push or tag was made for this checkpoint. Preserve unrelated edits and refresh Git status before acting.
- CAD target: `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_sch` and `.kicad_pro`; local fuse library `ups_v4.pretty/Littelfuse_451_2410.kicad_mod`. No real V4 `.kicad_pcb` exists. Disposable fuse fixture is ignored under `.validation/phase2-6/fuse-check/`.
- Current schematic SHA256 `16fac2064661cb20d4dc02f98dfe73389b993f50588e46b57c967e7c445d651a`. Current evidence is `evidence/phase3-2-mcu-power-checkpoint.md`, `phase3-2-erc-clean.json`, `phase3-2-mcu-power.net.xml`, `phase3-2-preservation.json`, `phase3-2-independent-preservation.json`, `phase3-2-esp32c3-footprint-readback.json` and `phase3-2-mcu-power-a1.png`; historical Phase 2.6 evidence remains the prior baseline.
- KiCad CLI 10.0.7 and Konnect saved-schematic edit/ERC/render/export operations verified. No GUI process, IPC `not_configured`; live real-board access is NOT established. Component catalog database unavailable. Never bypass an editor lock or the live real-board path gate.
- Uncommitted work: Phase 3.2 schematic, custom supervisor symbols, project-local N4X footprint, BOM/evidence and this handover. Production V2/V3, firmware and credentials unchanged. Documentation/CAD only: no firmware build needed or run. Review `git status` rather than blindly adding files.

## Phase 2.6 completed work and verification

Owner explicitly prioritizes a technically sound provisional prototype schematic over exhaustive pre-prototype qualification. Phase 2.5 research is sufficient for provisional choices with essential electrical/pulse/package/sourcing support. Adapter model and cable are **not fixed**. No guaranteed minimum Ceff is imposed when TI specifies none; physical damping acceptance stays open.

- Implemented TI Fig.8-1 series RC shunt through Konnect: R12 Vishay CRCW12062R00JNEAHP (2 ohm, 5%, 1206), C26 KEMET C1210C225K1RACTU (2.2 uF, 100 V X7R, 1210). R12.1 -> fused VIN1 ahead of input FETs; R12.2/C26.1 isolated midpoint; C26.2 -> PGND. One each in every initial VSYS variant, both **PROPOSED**. Basis/package/sourcing/test plan: `evidence/phase2-6-hotplug-envelope.md`. Generic passive-land differences documented for PCB library freeze.
- Parameterized 144-point RLC sensitivity model and independent equation/energy/closed-form checks: `calculate_hotplug_rlc.py`, `phase2-6-hotplug-rlc.json`. Estimated Ceff sensitivity 1.226–2.783 uF is not a guaranteed range. Hypothetical selected corners reach 39.725 V / 482.54 W peak resistor / 1.7904 mJ resistor energy (different corners): the earlier ideal-step screen does NOT bound cable ringing or guarantee immunity. These are neither measured source limits nor an approved operating point. Validate actual FET/clamp behavior, bounce, repetitive pulse stress and damping on the chosen setup.
- Corrected F1 custom lands through Konnect to manufacturer inch-derived dimensions: 1.9558 x 3.1496 mm at +/-2.4511 mm. Retained 0451005.MRL 5 A, PROPOSED. `evidence/phase2-6-fuse-land-review.md` records current manufacturer revision/section, physical map, render, readback and limits. Disposable DRC: 1 invalid-outline error / 1 extra-footprint warning / 0 unconnected; fixture has no outline and blank schematic. No reported pad/courtyard/silk violations, but **not a real-board DRC/parity pass**. Instance pad tool failed 'F1 not found'; saved failure plus independent read-only geometry check, not concealed as live readback success.
- Essential BQ25792 Rev.D / BQ25798 Rev.C 29-pin/package comparison complete for provisional shared PCB. PROG 8.2k/27k 1%, 750 kHz; 792 2S POR 2 A risk retained. Bounded PN, backup, MPPT/reserved-bit and reset/CE firmware requirements in `V4_CHARGER_PACKAGE_MAP.md`; no exhaustive register equivalence claim. Fresh symbol/pad readbacks and `phase2-6-package-verification.json` support the preserved map.
- Supported visual cleanup moved IC1/stubs/fields and J2 inside the output box. Relocated the existing VBUS power flag, preserved F01/CE connectivity; no extra masking flag. Final render inspected. Manual cosmetic tasks below remain; visual acceptance is not silently granted.
- Final `phase2-6-review-erc.json`: **0 errors / 0 warnings**. Fresh `phase2-6-review.net.xml` and `phase2-6-review-verification.json`: every pin partition matches explicit expected changes, IC1 pins 1–29, F01/CE, fuse path and new RC shunt pass. Explicit baseline/source diff `phase2-6-review-schematic.diff` inspected; BOM regenerated from this XML (42 groups). `phase2-6-review.png` and `.pdf` are final owner-review exports.
- Git whitespace check is not clean: generated diff artifacts contain literal context-line whitespace and Konnect schematic has one whitespace-only line. Source CAD was not hand-edited to satisfy formatting. Fuse SVG export whitespace normalized only in the review artifact. See `phase2-6-diff-check.txt`; electrical verification passes independently.

## Open items and authorized next milestone

1. **Owner accepted the Phase 2.6 provisional charger/power-stage schematic and explicitly authorized ESP32-C3/power-domain schematic development.** Proceed in bounded verified checkpoints. Do not reopen completed charger research without a specific technical reason. Real PCB layout remains unauthorized. VAC1 transient evidence remains unresolved as stated above.
2. Small manual KiCad 10 presentation task, because exposed Konnect operations cannot edit title blocks or existing free text: change title to `UPS V4 charger / power stage`, revision to a V4 prototype identifier chosen by owner, update legacy Phase 2b heading, replace old 'exact parts pending procurement' damping note with R12/C26 PROPOSED status, and move the new hot-plug note out of the Grounds box (suggested clear position near x279.4/y171.45 mm). Save via KiCad; then fresh ERC/export/partition verification/render/hash and BOM/handover refresh. Do not hand-edit serialized files. Existing title currently `BQ25798 UPS module`, revision `2.1`; do not mistake it for board identity/release approval.
3. Procurement/BOM freeze: R12/C26/F1 remain PROPOSED. Exact preferred-supplier resistor listing/manufacturer lifecycle, current TME prices/stock/MOQ, C3/Q3/passive/connector/NTC/harness final order identities and critical-part sourcing remain open. DigiKey cut-tape fallback and earlier LCSC capacitor observation establish provisional sourcing feasibility; shipping makes consolidated orders preferable. TME browser request was denied by automatic permission review; no alternate route attempted. Ordinary passive purchasing details may finish at BOM freeze, without blocking this review.
4. Prototype qualification, separate from schematic verification: choose/document adapter and cable; test VIN1 and VBUS overshoot, FET VDS/VGS/SOA and clamp stress, R12 pulse/repetition/temperature and actual damping/Ceff, all retained bulk-capacitance/ripple/thermal limits, fuse fault/cable/BMS coordination, charger/PROG/reset/CE behavior. Record exact revision/BOM, cells, source/cable, load, ambient, waveform/logs and pass criteria. No measurements or safe power-up claim exist yet. See hot-plug test plan and historical CE risk below.
5. Real PCB DRC/parity and manufactured fit remain later mandatory gates. No real PCB exists. Real-board edits require subsequent authorization plus exact full-path live IPC read confirmation. Preserve single physical PCB variants, VSYS-only initial scope, default-disabled CE and no unnecessary active OVP.

## Current Phase 3.2 checkpoint

The current saved schematic has two independent TPS62933DRLR 3 A candidates:
U3 converts SYS to MAIN_3V3; U4 converts USB_VBUS to USB3V3. Each has
4.7 uH, 2.2 uF plus 100 nF input bypass, 100 nF 25 V bootstrap, 33 nF
soft-start and two 22 uF output candidates. U5 TPS2116 selects normal power
through VIN1/MODE or USB power through VIN2 and supplies MCU3V3. The earlier
19.1 kOhm/10 kOhm PR1 divider was removed; R23 is now a 10 kOhm MAIN_3V3
pull-up on the digital MUX_PR1/MAIN_VALID node. U7 TPS389033DSET is powered
from MAIN_3V3, with SENSE and MR also on
MAIN_3V3, and sinks PR1 while MAIN is below 3.17 V. This removes the earlier
comparator reference-to-MCU3V3 flaw and avoids a normal-only startup deadlock;
source-removal, hold-up and startup timing still require matching-hardware
qualification.

U6 is the original TCA9517DGKR Rev. D, with the main domain on VCCA/A and
MCU3V3 on VCCB/B, and 4.7 kOhm pull-ups on both sides. The original revision
does not carry the later VCCA <= VCCB restriction, so the normal TPS2116 drop
is covered. EN is isolated through Q8/Q9 PMV16UN with R51/R52: MAIN_VALID
drives Q8, Q8 pulls NEN low, and Q9 releases TCA_EN only when MAIN_VALID is
valid; otherwise TCA_EN is forced low. This blocks the MCU-powered internal EN
pull-up from back-biasing MAIN during USB-only operation. Partial-power leakage,
FET gate leakage and aggregate R07 limits remain open.

Charger U7-released MUX_PR1 (MAIN_VALID) drives Q6 through R50, and
MCU_CHG_ARM drives Q7, so Q6/Q7 form a series authorization path into the Q5
main-domain source. R53 limits Q5 base current; R47 pulls the firmware base
low. R11.2 is a no-connect DNP service sense, so external J4 CHG_REQ cannot
enable charging. MCU_CHG_ARM is GPIO0/pad 12; GPIO7/pad 21 is reserved as
MCU_GPIO7. The USB D+/D- ESD shunt remains on the connector-side logical pair,
and R48/R49 are 0 Ohm default series links with 22 Ohm optional values before
the U1 pins. U2 is the TI TPD2EUSB30A with the exact Texas DRT-3 footprint
and D+/D-/GND pin map. Native recovery/strap footprints remain from Phase 3.1. U1 uses the project-local N4X
footprint with 61 physical pads, 53 unique numbers, and nine segmented pad-49
center lands at +/-1.975 mm centers (5.4 mm array). Compare it against
Espressif v2.2 Section 11.1 Figure 11-1 and the saved reference files before
PCB placement.

Fresh KiCad 10.0.7 ERC: **0 errors / 6 intentional isolated-label warnings**
(UART_RX, UART_TX, MCU_STATUS_LED, MCU_GPIO7, MCU_GPIO1, MCU_GPIO10). Konnect
connectivity validation: 0 floating wire ends and 0 unconnected component pins.
The Phase 3.2 preservation verifier compares every Phase 2.6 connected-pin
partition, records the intentional R11.2 service no-connect and the R50
MAIN_VALID addition, and reports the six documented isolated-label warnings.
No PCB exists, so DRC/parity and physical layout checks remain later gates.

The TPS62933 effective output capacitance, inductor current/thermal margin,
USB input inrush, C49 470 uF hold-up ESR/effective capacitance,
TPS2116 switchover/reset-free behavior, TCA9517 leakage and the exact N4X
land-pattern comparison are unresolved qualification items.
Keep VAC1 hot-plug transient evidence OPEN as a later fabrication/power-up gate.

The remaining sections retain earlier decisions and evidence history. Where a historical phase statement conflicts, **the current Phase 3.2 state above takes precedence**.

## Preserved owner decisions

1. Reliability, electrical correctness, battery safety and maintainability take priority. Preserve production hardware.
2. Exactly one physical PCB with BQ25792/BQ25798 and 2S/4S population variants. See requirements, architecture and variants documents for detailed decisions; do not redesign completed architecture.
3. Supported regulated adapter envelope is up to 20 V nominal, assumed +5% = 21 V. Basic polarity protection, appropriate component ratings, BMS and fusing are required. No complex active OVP/eFuse or accidental 25/30 V adapter survival requirement.
4. CE defaults HIGH, with normally-off open-drain MCU sink. No external 250 ms lease/watchdog. Preserve the BQ25792 charger-only reset risk.
5. Initial design and qualification exclusively VSYS. PMID backup development/qualification is deferred. Optional DNP/test provisions do not approve backup operation.
6. USB 3.3 V buck and power mux remain mandatory for USB-only programming, with reverse-current and signal back-power isolation; now authorized for schematic integration.
7. Charger/power-stage owner review is complete. ESP32/USB schematic integration is authorized; routing remains a later gate. F01 acceptance is not acceptance of subsequent changes.
8. KiCad 10 and Konnect only for serialized CAD/library/table changes. Do not hand-edit these files.
9. Real-board changes require exact full-path live IPC confirmation. Closed disposable footprint checks under `.validation/` are separately permitted; they do not pass the real-board gate.

## Completed work and evidence history (pre-Phase 2.6)

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

## Historical verification and acceptance limits

The final fresh verification record is appended below after CAD is frozen. Earlier `phase2-3-power-final*` renders/exports and `phase2-3-power-verification.json` may describe intermediate hashes; do not assume they represent current CAD.

- `verify_power_stage.py` independently compares every exported pin partition against the resume baseline plus explicit intended changes: remove redundant IC1 pins, move six system returns, insert F1. It also checks named critical nets, logical pins 1-29, source SHA256, export/ERC freshness and zero ERC errors/warnings. It does not validate physical geometry or component suitability.
- `verify_stage2_checkpoint.py` is historical only and now rejects any source hash other than saved stage 2.2b. Do not run it against later CAD as current acceptance.
- `phase2-3-schematic.diff` is an explicit no-index comparison against the read-only V3 source. Konnect reserialization creates a large diff; electrical scope is established by all-pin partition checks, not diff line count.
- Phase 2.4 render inspection confirms R5/R11 fields are horizontal and separated; C23/IC1 fields moved. Input/output connector box and labels near IC1 still need cleanup; legacy title/revision remains. Schematic is not visually accepted merely because ERC passes. Exposed Konnect tools offer add-text but no title-block/annotation-edit operation; do not hand-edit serialized CAD to bypass this limit.
- No real V4 PCB: DRC and schematic/PCB parity not run. No matching-hardware electrical, thermal, hot-plug, cell/load, CE timing or USB partial-power measurements. ERC success alone establishes none of these.

## Historical unresolved list — superseded by Phase 2.6 above

The previous hot-plug implementation, fuse-land, essential variant and supported
visual-cleanup tasks are completed to provisional review scope. Remaining manual
presentation, procurement/freeze and physical qualification gates are listed
above. Do not repeat Phase 2.5 screening as a prerequisite for owner review.

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
& $v4cli sch export netlist --format kicadxml --output hardware/v4/evidence/phase2-6-review.net.xml hardware/v4/ups_v4/ups12v_v4.kicad_sch
# Run Konnect run_erc with output hardware/v4/evidence/phase2-6-review-erc.json.
# Capture reviewed CAD SHA256, then run:
python hardware/v4/evidence/verify_power_stage.py --export hardware/v4/evidence/phase2-6-review.net.xml --erc hardware/v4/evidence/phase2-6-review-erc.json --expected-sha256 <reviewed-sha256> --output hardware/v4/evidence/phase2-6-review-verification.json
python hardware/v4/evidence/build_bom_review.py hardware/v4/evidence/phase2-6-review.net.xml
git diff --check
```

Registry warnings in sandbox did not prevent successful parsed exports. Commit/push only when requested; select task files explicitly and exclude credentials/scratch/cache artifacts.

## Historical phase 2.3 verification snapshot

- Source SHA256: `2938c56c36c49f4124be519d3b6abe003781b3fd3ac0175aa5b8d36854d156de`.
- Fresh [XML](evidence/phase2-3-review.net.xml), [Konnect ERC](evidence/phase2-3-review-erc.json), [independent verification](evidence/phase2-3-review-verification.json), and [render](evidence/phase2-3-review.png) were regenerated after the CAD owner froze all mutations.
- ERC **0 errors / 0 warnings**. All pin partitions matched explicit expected changes; logical IC1 pins 1-29, six return migrations, F1 series path, F01 and CE sets passed. BOM inventory regenerated from this exact XML, 40 groups.
- Full render inspected: remaining visual issues listed above are real and remain open. No fabricated or measured evidence is claimed.
- Explicit no-index schematic diff saved; tracked `git diff --check` passed at that checkpoint. These files were subsequently committed by the owner in `c211212`; this paragraph is historical, not current working-tree state.

## Current phase 2.4 checkpoint — 2026-10-10

- Resumed the same unfinished charger-stage milestone. Initial hash matched
  phase 2.3 (`2938c56c...`); fresh resume ERC 0/0 and all expected partitions
  passed (`evidence/phase2-4-resume-*`). No completed architecture work repeated.
- Konnect availability verified: 0.13.0, all 21 toolsets loaded, KiCad CLI
  10.0.7. Exact project paths above verified; no PCB. No GUI process and IPC
  `not_configured`; saved-file schematic tools worked. Real-board gate not met.
- Manufacturer-backed metadata corrected for seven BAT/SYS capacitors (Murata
  GRJ21BR61E106KE01K, X5R) and C8 (GCM1555C1H102JA16D, C0G). R5 display now
  27k 1%, fixed 2S/4S populations explicitly recorded. Source/Bought and
  footprints preserved. Field locations changed only for R5/R11/C23/IC1.
  No wires, nets or component placement/topology changed. Details/revisions in
  `V4_STAGE2_PARTS.md`; BOM rebuilt from exact fresh XML (40 groups).
- Actual-revision PROG/POR comparison documented, including unchanged 792 2S
  reset risk. Full pin/package comparison still open.
- Hot-plug discovery advanced with exact resistor/capacitor candidates and
  primary-source pulse conditions, practical sourcing issues and calculation
  limits in `V4_HOTPLUG_REVIEW.md`. No candidate passed all selection gates;
  no branch added. Continue there, not by repeating the earlier ideal-step
  analysis. F1 land-pattern acceptance/coordination still open.
- Current saved schematic SHA256:
  `50842c1c756ed6ebc92b33b9db64ebeb787d378d7b2a22b5386166551052fbea`.
  Current evidence: `phase2-4-metadata.net.xml`, `phase2-4-metadata-erc.json`,
  `phase2-4-metadata-verification.json`, `phase2-4-metadata.png` in `evidence/`.
  Fresh ERC **0 errors / 0 warnings**; all-pin partitions, logical 1-29, six
  returns, F1, F01 and CE assertions passed. Render inspected after final field
  rotation. Explicit working-tree schematic diff inspected: intended metadata
  and field placements plus Konnect serialization formatting.
- `git diff --check` **fails on nine whitespace-only lines generated by Konnect**
  in the schematic. Parsing/ERC/export pass. Do not repair by hand; request/use
  a supported Konnect normalization fix or editor-backed save in a later step,
  then regenerate evidence. No unsupported CAD serialization operation attempted.
- No firmware behavior changed: no build needed/run. No PCB means DRC/parity
  not applicable at this step; mandatory before eventual design release.
  No hardware measurements or electrical/thermal/hot-plug qualification claimed.
- Stopped with the charger-stage completion blockers documented, **before the
  completed-schematic owner review**. This is a resumable partial checkpoint,
  not milestone acceptance. Next action is hot-plug pulse/Ceff/source acceptance,
  followed by remaining items above, then owner review. No MCU/USB or routing.

For fresh reproduction use the commands above with `phase2-4-metadata` filenames
and the current full SHA256; older phase 2.3 commands/evidence are historical.

## Current phase 2.5 checkpoint — source/pulse/Ceff screening

- Completed a bounded read-only hot-plug component screen. Manufacturer curves
  and exact revisions, live versus cached procurement observations and remaining
  gates are in `evidence/phase2-5-source-observations.md`. Do not repeat discovery
  or nominal energy calculations without new evidence.
- Live Murata SimSurfing shows exact `GRM32ER72A225KA35` **NRND**. Reject this
  new-branch candidate; no fitted part was removed. The owner authorized accepting
  SimSurfing's license. Its recovered -12A reference sheet is dated 2026-06-26.
- Vishay 20043 (2026-03-17) pulse curves and 28810 (2023-06-30) waveform method
  now establish a preliminary RC/2 equivalent-rectangle screen. Independent
  tolerance extrema give 236.84 W / 2.981 us / 0.614 mJ, below conservative
  3 us curve reads. This does not qualify contact bounce, cable ringing, peak
  film temperature or service life. Panasonic reference remains conditional;
  its 1% family does not include 2 ohm.
- Exact KEMET C1210C225K1RACTU sheet generated 2026-10-10 includes bias/temp/AC
  simulations and 3%/decade-hour aging. Explicit 10-year sensitivity assumptions
  give 1.226 uF, **not a guaranteed Cmin**. TI's application figure supplies no
  effective-capacitance minimum; actual damping adequacy is still open. Live
  LCSC C2168116: USD 0.2408 at 1+, MOQ/multiple 1, stock 10 on 2026-10-10.
  Manufacturer lifecycle, physical lands and delivered order cost remain open.
- Reproducible script `evidence/calculate_hotplug_screen.py` generated
  `evidence/phase2-5-hotplug-screen.json`, including downloaded-source hashes.
  Full public source PDFs and inspection PNGs remain in ignored
  `evidence/references/`; source URLs/revisions and observations are recorded in
  tracked-candidate files. The script currently expects those cached PDFs for
  hash reproduction; fetch the exact linked sources if the cache is absent.
- No CAD/library/project mutations. `phase2-5-resume-verification.json` binds
  unchanged schematic, XML and ERC hashes to phase 2.4 verification: **59
  components, 35 nets, 153 net nodes**; prior all-pin assertions still apply.
  Source SHA256 remains
  `50842c1c756ed6ebc92b33b9db64ebeb787d378d7b2a22b5386166551052fbea`.
  Prior ERC remains **0 errors / 0 warnings**; no new ERC/export was needed or
  claimed. No PCB, so no DRC/parity. No firmware change/build or hardware test.
- **Partial component-selection review checkpoint, not completed-schematic
  acceptance.** No damping components passed every gate or were drawn. Next
  bounded action is lifecycle/source/physical-land acceptance and a justified
  minimum-Ceff damping envelope; then add the branch and freshly verify it.
  Remaining fuse, full charger package comparison, BOM and visual items above
  remain open. Full charger-stage owner review remains pending. No MCU/USB,
  routing, fabrication or power-up approval.
- Owner `AGENTS.md` changes are preserved. Keep all further outputs compact;
  full evidence belongs on disk. Recommend a fresh session for the next bounded
  acceptance step, using these files alone.
- Final task `git diff --check` passed (only Git LF/CRLF conversion notices).
  This is a check of this session's diff; it does not normalize the historical
  Konnect whitespace noted in phase 2.4. No commit/staging/push was performed.

## Current phase 3.1 checkpoint — ESP32-C3 native USB/recovery boundary

- Bounded CAD checkpoint completed on 2026-10-10. U1 is a custom
  `ESP32-C3-MINI-1` symbol with all 53 module pins mapped from Espressif
  ESP32-C3-MINI-1/MINI-1U Datasheet v2.2 Table 3-1 / Figure 3-1. Native USB
  GPIO18/USB_D- (pin 26) and GPIO19/USB_D+ (pin 27) are routed through U2
  rail-less TI `TPD2EUSB30A` (DRT-3, no VBUS clamp pin) to J7 USB-C; CC1/CC2
  use separate 5.1 kOhm pulldowns. Pin map is TI SLVSAC2G Rev. G §5/Table 5-1.
- BOOT/RESET recovery is drawn with SW1/SW2, GPIO9/EN and GPIO2/GPIO8 strap
  bias, and the module NC/GND lands are explicitly handled. All U1 module
  returns and USB shield/ESD returns use `PGND`; the quiet `GND` domain retains
  its single NT1 tie. C29 is 1 uF provisional for EN timing, and local C30/C31
  provide 10 uF + 100 nF `MCU3V3` bypass with `PGND` returns. `MCU3V3` remains
  an undriven reserved input boundary only. The VSYS buck, USB-derived buck,
  TPS2116 mux and TCA9517 I2C isolation remain the next bounded checkpoint; no
  active power-domain qualification is claimed here.
- Fresh evidence is in `evidence/phase3-1-mcu-usb-checkpoint.md`,
  `phase3-1-mcu-usb.net.xml`, `phase3-1-mcu-usb.bom.csv`,
  `phase3-1-mcu-usb.png`, `phase3-1-mcu-usb.pdf`, `phase3-1-erc.json` and
  `phase3-1-erc-errors.json`. Component connectivity validation reports zero
  unconnected pins and wire validation reports zero floating endpoints. Net
  checks cover USB VBUS, rail-less protected D+/D-, CC1/CC2, BOOT, EN, strap
  nets and local `MCU3V3` bypass. The fresh XML is a true KiCad `kicadxml`
  export, not the Konnect S-expression netlist format.
- ERC remains **open** at this boundary: KiCad 10.0.7 reports one error, the
  expected undriven U1 pin 3 (`MCU3V3`) while its regulator/mux source is
  deferred, plus ten intentional isolated labels for reserved UART/GPIO/service
  interfaces. The avoidable custom-symbol off-grid, dangling no-connect,
  missing-footprint and USB VBUS-clamp warnings were fixed. This is not a
  release-clean ERC result.
- PCB gate remains **blocked pending exact land-pattern comparison**. Readback
  of the existing global `Modules_MCU:ESP32-C3-MINI-1` footprint found 62
  physical pads / 60 unique pad numbers (including duplicate ground numbers)
  and no courtyard. That count alone does not establish invalidity; compare
  every physical land and mechanical feature with the selected Espressif
  suffix before PCB work. No PCB sync, layout, fabrication, power-up or USB
  hardware qualification was performed.
- Source hashes after this checkpoint are recorded below after the final
  fresh exports. The custom symbol pin grid was corrected through Konnect;
  the 53-pin physical footprint readback remains provisional pending exact
  Espressif land-pattern comparison (62 physical pads / 60 unique numbers,
  duplicate ground numbers, no courtyard; count alone is not a rejection).
- Parent final preservation check passed against the fresh true XML and ERC,
  bound to the final schematic hash: all 57 prior references / 157 connected
  pins retain their Phase 2.6 partitions. Existing component values, footprints
  and exported custom fields are unchanged. Evidence:
  `evidence/phase3-1-preservation.json`, `verify_phase3_preservation.py`, and
  full `phase3-1-schematic.diff`. The Q3 gate short found during intermediate
  review was corrected and is absent from this final exported evidence.
- Phase 3.1 is a saved, verified **partial schematic checkpoint**, not completion
  of the authorized MCU/power-domain milestone or approval of the unresolved
  module footprint. No power-domain block was started. Resume in a fresh
  session from this handover with the bounded converter/mux/isolation checkpoint;
  the owner's schematic authorization continues to apply. Candidate qualification
  limits are recorded in `evidence/phase3-domain-candidate-review.md`.
- BOM candidates and unresolved identities are recorded in the Phase 3.1
  section of `V4_BOM_REVIEW.md`; no broad component-sourcing research was
  repeated. No commit or push was made.

Phase 3.1 final evidence hashes (fresh after the gate-short repair and local
MCU bypass addition): schematic `6CF6B607DC14731892FDF7C6E7D092852676A82FE2E949C215D6862545AE9A0C`;
custom symbol `A2651C707051952BD1C94E78AAC3745A5F7128EC152DB42E29A071C9154E92CF`;
`sym-lib-table` `9CA81FF1BD69D09781F46C8A698869DE4E2F1827CC96D789CF14160AE3FB5190`;
true KiCad XML `EFEAFDDA4D30F1F932ECCA59690232072C5143B545F3503D6C3E3F51D4569694`;
warning ERC `E7498848BACEEBDE45172CE58F0A3D360891E525B503CADC1E45B5CA5ED0A5CA`;
error-only ERC `FF797F9974FC4A743F25C4E9B67C05ADA7C2C47603FB8414E3D886A5C802A386`;
BOM `C0B08DC075EA920F73F954D38217B046431291EBF40C392E05FC9224C0406530`;
bounded verifier `53540D7BD665ACB3F1C0591EFF64503C32D6E50F4247565827C0C172A790B804`.
The parent preservation projection reports all 57 old references / 157 old pins
preserved after the gate-short repair. The checkpoint remains **INCOMPLETE**
until the deferred power-domain blocks and MCU footprint land-pattern review
are completed; there is no PCB or power-up authorization.
