# UPS V4 handover

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
