# Nano-Fit replacement preflight — incomplete, production CAD unchanged

2026-10-11. The owner approved the exact selection and pin assignments in [selection](nanofit-connector-selection.md) for CAD only. No further owner approval of that selection is needed. Replacement has **not** been applied. Do not resume general routing, fabricate, purchase, commit or push.

## Verified entry checkpoint

Konnect opened the exact `hardware/v4/ups_v4/ups12v_v4.kicad_pcb` in KiCad 10.0.7 with `ipc_available=true` and `requested_open=true`. Native save completed. Fresh entry ERC: **0 errors, 4 warnings** ([report](nanofit-entry-erc.json)). Fresh synchronized saved-board DRC without zone refill: **262 unrouted errors, 0 other errors, 13 warnings, 0 parity violations** ([report](nanofit-entry-drc.json)). Schematic-sync dry run was `noop`, no diagnostics. Board inventory: **154 footprints, 242 tracks, 135 vias**. These are baseline checks, not verification of an applied replacement.

Exported entry [XML netlist](nanofit-entry.net.xml), [traces](nanofit-entry-traces.json) and [read-only CAD snapshot](nanofit-cad-entry.json) preserve comparison evidence. Scratch-only generic 2/3-pin symbols and installed Nano-Fit footprints were placed and queried through Konnect under the ignored `.konnect/nanofit-validation/` directory. Production schematic, PCB, project and libraries were not modified. Final hash comparison is [unchanged-check](nanofit-production-unchanged.json).

## Manufacturer footprint discrepancy and available-tool limit

Current official Molex drawing **SD-105313-100, Rev J1**, released **2025-06-26**, sheet 1, recommended PCB connector-side view: [Molex drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/105/105313/1053131102_sd.pdf). Browser PDF text identifies 1.20 +/- 0.05 mm electrical holes, 2.50 mm pitch, 7.18 mm locating offset, and locating-hole callouts **1.60 +0.05/-0.00 mm** and **1.75 +0.10/-0.00 mm**. The latter appears to define a slotted locator; exact slot orientation and which end uses it still require visual confirmation from the current figure. Browser screenshot access returned no usable image, and direct PDF retrieval failed. Do not treat inferred slot orientation as verified geometry.

Installed KiCad `Connector_Molex:Molex_Nano-Fit_105313-xx02_1x02_P2.50mm_Horizontal` and corresponding `xx03` footprints have **two round 1.70 mm NPTH locating holes**, at local X=7.18 and Y=0 / 2.50 or 5.00 mm. Their electrical pads are numbered along local +Y, pitch 2.50 mm, with 1.20 mm drills. Body extends toward local +X. The downloaded manufacturer drawing mirrored by Distrelec, **Rev F, 2019-07-31**, matches the old 1.70 mm round locating holes. It does not establish conformity to current Rev J1. See [older PDF](nanofit-header-drawing-distrelec.pdf).

Available Konnect `create_footprint` and `edit_footprint_pad` schemas expose only a scalar circular drill diameter. Pad shape `oval` controls the pad shape and does not establish an oval drill. There is no exposed slotted-drill dimension/orientation parameter. Therefore a corrected current locating-hole pattern cannot be authored and verified through these tools. Do not approximate the slot with overlapping round holes, infer an oversized hole, or hand-edit serialized library/CAD files.

**Continuation requires:** visually confirm the Rev J1 locating pattern, then obtain a verified footprint matching it or add Konnect support for slotted NPTH drills. Retain the approved MPNs and pin assignments. Complete scratch geometry/pin checks before applying production changes. Approval is not the blocker; supported footprint geometry is.

## Remaining bounded work

Replace J1/J2/J3/J8 symbols, fields and footprints; explicitly remap J2/J8 to power pins 1/3 and mark pin 2 NC; retain J8 F0 DNP and all J4/J6 properties. Orient mating faces toward the existing top PCB edge and verify board-edge options, complete mated-envelope clearance, numbering from connector-side and harness mating views, and local copper clearances. Preserve switching-loop routing, ground zone definitions/fill outside intended local changes, RF rule area, outline, and unrelated components. After the real replacement: fresh native refill/save, ERC, DRC, exported-netlist parity and focused before/after diff. Do not present the entry checks as completion checks.

Before hardware assembly, test every wrong-mating combination with physical samples, including partial/offset insertion; qualify actual current/temperature, wire insulation/OD, crimp tooling/quality and strain relief. No contacts paralleled. VAC1 hot-plug and BQ25792 2S charging-current gates remain **OPEN**. No fabrication/purchasing approval is implied.
