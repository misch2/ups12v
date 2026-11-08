# UPS V4 handover

## Native DNP fields and tooling - 2026-11-08

Removed legacy custom DNP properties from the schematic. Native schematic DNP
is now set for C20, C22, C24, C25 and R11 (R11 was already checked by the owner).
The completed schematic migration preserved 104 nets / 445 pin memberships;
ERC remained 0 errors / 4 warnings. Separately removed 20 redundant `DNP=NO`
property blocks from the PCB by owner-authorized S-expression removal; native
PCB DNP attributes were not synchronized. This later PCB metadata cleanup did
not trigger another full validation run. Evidence: `evidence/native-dnp-2026-11-08/`.
Reusable read-only helpers now live in `tools/kicad/`, documented in its README.
One-off baseline-specific migration scripts remain historical evidence.
Owner requests proportionate, batched checks and reuse of Git comparison points.

## Schematic Value/Purpose fields - 2026-11-08

Owner-authorized field separation completed on the current saved schematic.
All 178 symbols reviewed; 118 have planned Value/field changes and 83 now have
a separate visible Purpose. Values retain electrical ratings; capacitance units
are consistent. The prior wired functional-block layout is retained, with text
placement adjustments only. Symbol positions, wires, labels and all 104 nets /
445 connected pin memberships are unchanged. ERC: 0 errors / same 4 warnings.
PCB/project are hash-identical to this task's baseline. PCB Value/custom-field
metadata has not been synchronized; a later normal SCH-to-PCB metadata update
is required before using PCB BOM fields or claiming fresh metadata parity.
Approved assembly/sourcing decisions and hardware boundaries remain unchanged.
Final schematic SHA256: `32ca33ac8a161dd014890f61869f5c20733134706b4301ac60bfda2eb6e14a97`.
See [field migration, previews and verification](evidence/symbol-fields-2026-11-08/RESULT.md).

## Owner-replaced mounting holes — DRC checkpoint 2026-11-07

Owner installed the project mounting-hole footprints. Fresh live-IPC refill,
save and project-context DRC completed: **4 errors**, 0 unconnected, 18 original
library-mismatch warnings plus 4 schematic-parity warnings. Each H1–H4 rule area
forbids its own NPTH pad because the prepared library enabled pad keepout without
excluding the hole. This is a defect in the prepared footprint, not an owner
placement error. Each H1–H4 also lacks the schematic `Bought` field. No corrective
CAD changes performed during this check; resolution and fresh DRC remain pending.
Full report: [owner-final-drc.json](evidence/mounting-hole-2026-11-07/owner-final-drc.json).

## PCB reference readability checkpoint — 2026-11-07

Owner-authorized label-only update completed on the open production V4 board:
121 visible reference positions/angles changed through native KiCad IPC; no
font-size, footprint placement/definition, copper or connectivity changes.
All 151 visible references checked without glyph-box overlaps against other
references, physical footprint envelopes, pads or fixed board silk. Orientations
are 0°/90°; SW1/SW2/C24 preserved. Exact native preservation and focused Git diff
verified. DRC: 0 errors/opens/parity, same 18 existing warning identities;
schematic/project/rules hash-identical. No ERC rerun or manufacturing regeneration.
Saved board SHA256: `80c8bc9b413de26d61cd1de42df50f0c1ce5ce6036e430e7f900b8de1c105459`.
See [result and evidence](evidence/silkscreen-2026-11-07/RESULT.md).
The historical Phase4.24W baseline below predates this silkscreen-only update.
The hardware bring-up boundary remains as recorded below.

## Active checkpoint — hardware bring-up Phase 1, 2026-11-06

Owner reports the first PCB manufactured and fully assembled as F5, passive
electrical checks passed. USB-only observations: USB3V3=3.3 V, MCU3V3=3.3 V,
MAIN_3V3=0 V, approximately 8 mA from 5 V USB before application firmware.
Native USB Serial/JTAG is stable; owner's esptool 5.1.0 identifies ESP32-C3
revision 1.1 and XMC 4 MB flash. These observations were not repeated by Codex.
This explicit owner task supersedes the earlier purchase-preparation stop only
for preparing/building the minimal diagnostic; it does not authorize flashing.

Current branch: `v4-with-mcp-help`. Diagnostic prepared on the earlier bring-up branch;
pre-existing edits retained. Existing project `software/i2c_test` now has a
separate default `v4_usb_bringup` environment. Production `software/ups` and
legacy Arduino charger-test source are preserved. The Arduino diagnostic source
is selected by build_src_filter, with no external libraries. Owner explicitly
requested plain `platform = espressif32`, no pinned versions, no ESP-IDF/CMake
project, and accepted default serial-port behavior. Native USB Serial/JTAG uses
ARDUINO_USB_MODE=1 and ARDUINO_USB_CDC_ON_BOOT=1. Target: compatible C3-MINI,
160 MHz CPU, DIO/40 MHz/4 MB flash. No application GPIO/LED/I2C/charger/CE/power
or radio initialization. BOOT/RESET remain available. Earlier IDF/CMake attempt
was abandoned and its project files removed; old build logs are historical.

See [firmware and upload procedure](../../software/i2c_test/V4_USB_BRINGUP.md).
Build/configuration evidence: `evidence/phase1-usb-bringup/`.
Arduino build PASSED (14.08 s), using plain `pio run -d software/i2c_test
-e v4_usb_bringup`. Local nested RISC-V toolchain layout repaired with directory
junctions; original tool files retained in `_original_layout`. No PATH override
or project build scripts are required. Platform/library versions are unpinned.
Hardware runtime, application current, USB/recovery and back-power validation
remain pending. No COM4 access, upload, CAD change, UPS-function implementation,
hardware measurement, purchase, commit or push is authorized/performed here.
**STOP before flashing: await explicit owner approval.** Use a fresh session
for the next substantive hardware bring-up checkpoint.

## First main-input power preparation

Use the [first-main-power procedure](evidence/FIRST_MAIN_POWER_F5_REVIEW_2026-11-06.md)
and [technical rationale](evidence/FIRST_MAIN_POWER_F5_TECHNICAL_NOTES_2026-11-06.md).
These are preparation/review records, not evidence of main-input energizing.
Confirm the actual assembled population against the final assembly BOM; approved
purchasing substitutions do not prove which components were physically fitted.
No cleanup operation authorizes flashing, energizing or hardware changes.

## Engineering and accepted production references

- [Requirements and owner decisions](V4_REQUIREMENTS.md),
  [architecture](V4_ARCHITECTURE.md), [variants](V4_VARIANTS.md),
  [BOM review](V4_BOM_REVIEW.md), [charger package map](V4_CHARGER_PACKAGE_MAP.md).
- [Safety/design decisions](evidence/v4-safety-design-review-2026-10-11.md).
- [Accepted Phase4.24W production result](evidence/phase4-24w-production-native-adoption/RESULT.md)
  and [installed baseline](evidence/phase4-24w-production-native-adoption/accepted-installed-baseline.json).
  Accepted PCB SHA256: `d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b`.
  Recorded final checks: DRC 0 errors/opens/parity, 18 accepted warning identities;
  ERC 0 errors/4 accepted warnings. These are historical CAD checks, not hardware
  qualification or a fresh validation of subsequent edits.
- [Recorded manufacturing configuration](evidence/phase4-24-owner-gerber-review/ORDER_CONFIGURATION.md)
  and [manufacturer notes](evidence/phase4-24-owner-gerber-review/MANUFACTURER_NOTES.md).
  These document reviewed settings, not a supplier's as-manufactured certificate.
- [Reusable guarded tools](tools/README.md). Historical migration plans and
  accepted manifests are not permission to replay completed transactions.

## Final purchasing and assembly references

Owner approved all Phase5.5 substitutions and the final five-F5 quantities,
including both inductors, both resistor pairs, all three R5 profiles, wires,
additional C32 stock and MOQ excess. Final reference files:

- [LCSC order](sourcing/FINAL_LCSC_ORDER.csv), [TME order](sourcing/FINAL_TME_ORDER.csv).
- [Assembly BOM](sourcing/FINAL_ASSEMBLY_BOM.csv) and
  [purchase/assembly checklist](sourcing/FINAL_PURCHASE_CHECKLIST.md).
- [Sourcing guide](sourcing/README.md) and
  [substitution electrical/fit review](sourcing/PHASE5_5_SUBSTITUTION_REVIEW.md).

The approved assembly plan pairs R60=16k with R61=3.01k despite unchanged 53k/10k
schematic metadata, and R32 Viking with R33 RESI. R5 profiles are alternative
stock: fit only the selected profile per board. Consult the final CSVs for exact
MPNs, DNP exclusions and quantities. Historical supplier prices/stock are dated
observations, not current availability, reservations or delivered quotations.

## Repository cleanup - 2026-11-07

Owner authorized removing obsolete evidence, temporary outputs and session notes.
The first pass removed repeated exports, scratch copies, caches and logs; the
second removed superseded checkpoints/STOP records, old execution summaries and
their unused illustrations. This handover replaces the former session diary.
[Evidence index](evidence/README.md) describes the retained material.

Keep source tools, downloaded documentation/dependencies, raw sourcing inputs,
electrical calculations, accepted production proofs, hardware/bring-up records
and offline regression fixtures. Removed operational artifacts are in Git
history; some historical scripts require their matching old context to reproduce
an old run. Do not weaken hash guards or overwrite final purchasing files by
replaying old builders. Use fresh authorized contexts for further CAD changes.

Production CAD, libraries, manufacturing/order data, firmware and final sourcing
files were not changed by cleanup. No hardware measurements or fresh ERC/DRC
were performed. The authorized hardware checkpoint remains unchanged.
