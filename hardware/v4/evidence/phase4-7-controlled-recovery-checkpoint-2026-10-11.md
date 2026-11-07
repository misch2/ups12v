# Phase 4.7 — controlled recovery conditions completed

2026-10-11. Owner explicitly approved static audit, failed-session inspection, isolated read-only smoke testing and continuation of the original scratch-only validation. **Completed in that order; STOP for owner review. Production CAD unchanged.**

## Static audit and coding guideline

Before any further native KiCad Python execution, audited all 23 `phase4_7*.py` helpers using source search and Python AST syntax parsing (no native import). The only no-argument GetWidth calls remaining were valid track reads: the preflight's non-via branch, the geometry helper's non-via branch, and the UUID-selected BATTERY track in the old diagnostic. Added an explicit PCB_TRACK/not-PCB_VIA guard to that UUID-selected track read rather than blindly changing its getter.

Refactored the builder/exporter to share **`phase4_7_layer_geometry.inventory_row`**, with an import-safe module entry point. Via handling returns before track handling; it uses GetPosition(), GetDrillValue() and GetWidth(layer) on each of F.Cu/In1.Cu/In2.Cu/B.Cu. Only the checked PCB_TRACK branch calls parameterless GetWidth(), GetStart() and GetEnd(). Thus mixed inventories no longer read via endpoints through track geometry APIs. Existing preflight already uses type-specific access; the plane sampler excludes vias before reading endpoints. Other Phase4.7 native builders only set via widths using explicit layers and do not have unsafe width-query calls.

Added the requested guideline to **AGENTS.md, “KiCad CAD editing and native APIs”**: explicit-layer via width queries, per-layer data where relevant, and concrete-type geometry dispatch for mixed PCB_TRACK/PCB_VIA inventories. Valid track getters are explicitly preserved.

## Abandoned session 61831

Its recorded command was solely the failed `phase4_7_layer_validation.py` diagnostic helper, running KiCad's bundled Python; it did not launch the PCB Editor. Earlier status polling had already returned exit code **1**. Current inspection returns **Unknown process id 61831**. A read-only Win32_Process check restricted to python.exe command lines containing `phase4_7_layer_validation.py` found **no matching process**, including an approved outside-sandbox check after CIM access was denied in the sandbox.

No remaining process required cleanup. **No termination, GUI interaction, editor close/restart/save/revert or production IPC operation occurred.** A tool-session identifier is not treated as an operating-system PID.

## Exact saved baseline and read-only smoke test

Verified accepted Batch1 hashes before native work:

| File | SHA256 |
|---|---|
| ups12v_v4.kicad_pcb | `8dc238f7cccce280b39dafddca967c760805d02cfadf75a1f6c8db2494cd541a` |
| ups12v_v4.kicad_sch | `990d107296d149775884dc2d2512c2e6102b6191e4818e7fcf5bd9268d48c8f6` |
| ups12v_v4.kicad_pro | `477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e` |

Created a byte-for-byte isolated baseline copy **`phase4-7-native-width-smoke.kicad_pcb`**, then loaded only that copy with native KiCad10.0.7. The shared corrected inventory function read one known ordinary BATTERY track and one known BATTERY endpoint via. Confirmed track width0.60mm/endpoints(63.1,65.5)→(63.8,66.9), via position(63.1,65.5), drill0.40mm and copper width0.70mm on all four layers. No mutation or native save was used. Scratch-copy hash and all production hashes remained unchanged. **PASS, no native assertion or unexpected API result.** Evidence: `phase4-7-native-width-smoke.json`.

## Fresh scratch build and native checks

After smoke success, created **`phase4-7-layer-validation-recovery.kicad_pcb`** from accepted saved Batch1. It changes only original BATTERY track UUID`01ab1eb5-ab75-462d-9e54-2d6eab529481`, F.Cu→In2.Cu, preserving0.60mm width, net, endpoints, UUID and both existing Ø0.70/0.40 endpoint vias. Added exactly the original verified BATP/PGND/ILIM_HIZ/TS subset plus proposed **0.10mm/28.651880mm all-F.Cu PROG**, no PROG vias. Board totals310tracks/139vias/154footprints. No R5, NT1, C23 or other footprint adjustment.

Native CLI complete configured DRC with `--all-track-errors --schematic-parity --refill-zones --save-board` completed: **251 unconnected items / 0 other errors / 20 library warnings / 0 schematic-parity issues**. No new copper, via, thermal or zone violation. No design rule was changed; the same six inherited ignored check categories remain, as documented in the prior assessment. The board remains intentionally incompletely routed and has library-context warnings; this is not a release-clean whole board.

After refill/save, native exporter confirms all original vias unchanged; all original tracks unchanged except the named layer; all footprint/pad geometry, values, placements and nets unchanged; PGND In1 still one filled polygon. Recovered candidate tracks/vias/pads/footprints/filled-zone geometry equal the previously assessed original candidate, ignoring newly generated UUIDs on added scratch items. Library warnings and ignored-check settings also match exactly. Evidence: `phase4-7-controlled-recovery-comparison.json`, `phase4-7-layer-validation-recovery-preservation.json` and `phase4-7-layer-validation-recovery-drc.json`. All saved production hashes still match Batch1.

Exact current native item UUIDs and copper coordinates are recorded in **`phase4-7-layer-validation-recovery-exact-copper.csv`** and the matching build JSON. Full native-save diff and result summary are saved alongside them.

## Electrical assessment and retained alternative

Reused the [completed electrical assessment](phase4-7-layer-validation-checkpoint-2026-10-11.md) only after proving geometry equivalence; no repeated broad layout analysis or new routing search was needed. The BATTERY segment does **not** simply duplicate In2 copper: approximately80%of its copper overlaps, with approximately0.193mm²distinct In2 added and0.578mm²distinct F.Cu removed. Useful separate outer-layer parallel conductance/heat spreading is removed, redistributing current into retained vias/In2. Current shares, via plating, actual stackup and operating temperatures remain unmeasured; native DRC is not ampacity/thermal qualification.

The28.652mm PROG route still has about0.160mm minimum F.Cu BTST2 edge gap, about1.12mm close parallel exposure, and projected exposure to B.Cu BTST2/SW2 with intervening In1 ground locally interrupted by via clearances. Per the previously checked TI BQ25798 Rev.C sequence, PROG is sampled at POR before normal converter startup; steady-state coupling is not proof of a POR error. Startup-noise immunity remains unmeasured. Full numeric geometry and ground-coverage evidence from the equivalent candidate remain applicable.

The separately validated **14.198947mm F.Cu/B.Cu PROG** alternative remains available for review, with two Ø0.50/0.30mm through-vias(67.6,65.08)/(64.78,70.01) and unchanged R5/NT1 return. It was **not rebuilt or rerouted during this controlled recovery**; prior saved native DRC/readback and its limitations are retained. It reduces length but retains the common escape and crosses under BATTERY copper without an adjacent B.Cu ground plane. Neither candidate is represented as hardware-qualified.

**STOP for owner review of the concrete scratch result.** No production changes, general routing, C23 relocation, fabrication, purchasing, firmware, commit or push. No need to restore IPC for this offline checkpoint.
