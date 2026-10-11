# Phase 4.4 — native changes verified; stop before routing

2026-10-11. Owner reported completion of the native steps. This report supersedes the incomplete PCB state in [the preparation report](phase4-4-pre-routing-review.md). Checks use KiCad **10.0.7**, exact live IPC document `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_pcb`, synchronized saved-board DRC, fresh schematic XML/ERC and read-only CAD inspection for data unavailable through exports. No agent CAD changes except the explicit save performed by synchronized DRC; owner CAD edits preserved. No routing, fill, fabrication, purchase, commit or push.

## Verified native results

- **J7 USB4085-GF-A** is now on the PCB, correct footprint and manufacturer/MPN metadata, at **(117.39,83.975), 90°, F.Cu**. Its 16 PTH signal contacts and four plated shell slots match the checked manufacturer/library pattern. Full A/B/SH-to-net map matches the unchanged schematic; USB_DP/DN, CC1/CC2, VBUS, grounds and SBU no-connects preserved. The four old hole-clearance errors and old SMD/through-hole classification warning are gone. Body mating face at X126, opening centre Y81; forward courtyard extends 0.5 mm beyond the board deliberately. Actual cable/enclosure fit and hand-soldering are not physical measurements.
- **C70 VIN1** at (62.75,84.5), −90° (=270°); **C71 VIN2** at (67.9,82.75), 0°; retained **C36 VOUT** at (67.5,80), 90°. Values/MPNs/footprints and pad nets agree with the schematic. U5 supply-pad centre distances are **2.111 / 1.472 / 1.933 mm**, respectively. No duplicate C72. Remote bulk and ESP32-local C30/C31 remain in place. Placement leaves short supply connections and local PGND access for later routing; no routed loop/impedance or transient performance is claimed.
- **U1_RF_ANTENNA exists in the saved PCB**, exact rectangle **X75.4–88.6 / Y99.2–104.6 mm**, on **F.Cu, In1.Cu, In2.Cu and B.Cu**. Native flags prohibit tracks, vias, pads and copper pours. No existing pad intersects this area; U1 ground/module pads remain outside it. Generic footprint prohibition is deliberately off; the saved project custom rule separately disallows intersecting footprints except U1. Its exact condition and `disallow footprint` constraint match the approved native instructions. DRC accepts the rule file; project `items_not_allowed` severity is **error**, not ignored.
- Native zone-fill exclusion is configured on all four layers. There are **no copper zones**, so no fill experiment was performed or represented as a successful physical test. Continuous PGND outside the RF area remains a routing requirement; no ground moat/cutout was added. The antenna region follows the retained Espressif v2.2 drawing; the recommended 15 mm clearance to external metal/wires/enclosure cannot be measured from this PCB and remains a physical integration check.
- **U1 reference text** is (90.5,98.0), 0°, F.SilkS, and visually readable inside the board. Module placement remains (82,93.6), 180°.
- **J4 PopulationGroup** restored verbatim to `Future MCU and normal 3V3 domain`; **J6 Bought** restored to `at home`. J7 exact MPN/manufacturer fields match. Fresh native sync dry run is **noop**, with no apply needed.

## Verification

| Check | Result |
|---|---|
| Schematic / PCB references | **154 / 154**, exact set agrees |
| Full exported pin-net / value / footprint parity | **443 pin entries pass**, all prior 439 plus four C70/C71 pins; 0 schematic parity findings |
| Physical PCB pads / nets | **463 / 102**; saved/live pad nets and board-space positions agree |
| Original geometry | Every retained footprint's full pad geometry matches HEAD except the intended J7 replacement; includes native IC1 custom primitives |
| Corrected courtyards | Q1/Q2/Q10 and C20/C22 preserved |
| Current library pad geometry | All 14 reviewed instances pass, including replacement J7, new C70/C71 and all 11 remaining warned instances |
| F0 / F5 | One physical PCB; all **19 F5-only references** retained |
| Outline / layers | **96 × 70 mm**, X30–126/Y30–100; four verified copper layers |
| Routed items / copper zones | **0 tracks / 0 vias / 0 copper zones**, one actual native RF rule area |
| Fresh ERC | **0 errors / 4 original isolated-label warnings** |
| Fresh synchronized DRC | **345 unrouted items**, **0 other errors**, **13 warnings**, **0 parity findings** |

The increase from 337 to 345 unrouted connections accompanies the two new capacitors and the distinct physical THT contact lands in J7. No track was removed; none existed. Unrouted items are expected at this phase, but this is **not a clean release DRC**.

Remaining warnings:

- **2 J7 silkscreen-edge warnings**: the library's two front side segments reach X126.12 with the mating face at X126. These are footprint silkscreen graphics, not copper/hole violations or a displaced reference. Trim/omit the clipped silk in a later supported cleanup before fabrication, preserving the mating geometry. No waiver, severity change or CAD alteration was made during verification.
- **11 library mismatch warnings**: U4, IC1, J4, U2, Q1, U3, J6, U5, U7, C20, C22. Full pad geometry, including custom primitives, matches current libraries after placement-angle/closing-vertex normalization and 1 nm tolerance. Remaining differences involve non-pad library/instance content; this does not assert every graphic/model is identical. Keep existing proven geometry and corrected project-local courtyards; no blanket refresh needed to establish electrical parity.

The [new top-view image](phase4-4-native-top.png) was visually inspected for J7, U5 bypass placement and U1 reference. It contains no invented RF overlay; saved native RF flags/geometry are verified structurally. Current hashes and exact readback details are in [verification](phase4-4-native-verification.json). Complete evidence: [live IPC](phase4-4-native-live-readback.json), [editor identity](phase4-4-native-editor.json), [XML](phase4-4-native.net.xml), [ERC](phase4-4-native-erc.json), [DRC](phase4-4-native-drc.json), [noop sync](phase4-4-native-sync-plan.json), [SVG](phase4-4-native-top.svg).

Reproduce the read-only comparisons with `verify_phase4_4_native.py`. It consumes captured live evidence and saved artifacts; it does not recapture IPC or rerun ERC/DRC. No firmware changes/build or hardware qualification.

**Native CAD steps verified; stop at pre-routing review.** The two minor silk warnings remain recorded. **VAC1 hot-plug and BQ25792 2S reset/default charge-current risks remain explicitly OPEN fabrication/power-up gates.** USB-only flashing, source transitions, effective capacitance, electrical/thermal behavior and RF/enclosure performance are not newly verified on hardware. A separately authorized routing milestone should begin in a fresh session.
