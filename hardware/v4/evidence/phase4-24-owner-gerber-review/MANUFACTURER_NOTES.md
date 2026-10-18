# Phase 4.24 — JLCPCB manufacturer remarks (draft, review only)

**Status:** copy-ready draft for the owner-exported Gerber/Excellon package. Do not submit, upload, release, order, or pay from this file.

Please manufacture this four-layer PCB with **Epoxy Filled & Capped** via processing. Use non-conductive epoxy filling followed by copper plating/capping for **all 324 actual through vias**, preserving the supplied copper, pad, soldermask and finish geometry.

Via scope per PCB:

- 273 vias with nominal hole diameter **Ø0.30 mm**;
- 49 vias with nominal hole diameter **Ø0.40 mm**;
- 2 vias with nominal hole diameter **Ø0.50 mm**;
- total: **324 true vias**.

Identify the vias from the supplied design/CAM coordinates and via identity list. Do not infer the via set from hole diameter alone. Apply the normal process/tool compensation without changing these design hole classes. The two boundary-size Ø0.50 mm vias are at board coordinates **(92.456, 91.400)** on `/USB_MCU_DP` and **(92.456, 90.200)** on `/USB_MCU_DN`; please explicitly confirm CAM/process acceptance of both before production. Their nominal outer copper diameter is 1.00 mm; the relevant fill limit is the Ø0.50 mm hole.

For vias intersecting or partially exposing solderable component-pad openings, provide a continuous, planar, solderable copper-capped surface with the same final surface finish as the surrounding exposed pad. Preserve all supplied pad numbers, nets, pad outlines, soldermask openings, polarity markings and copper clearances. Do not cover an intended solderable land with soldermask. Non-pad vias may retain the supplied front/back mask artwork, subject to the selected epoxy/cap process.

**Do not fill, cap, plug, or otherwise close any component hole.** Keep all **41 component PTH** and **12 NPTH** open and correctly plated/non-plated as supplied. In particular, the 16 J7 USB contact holes are Ø0.40 mm plated component holes and must remain open even though 49 true vias share that nominal diameter. Keep these holes and slots open:

| Component hole group | Quantity and nominal size | Required state |
|---|---:|---|
| J1/J2/J3/J8 Nano-Fit contacts | 2/3/2/3 × Ø1.20 mm PTH (10 total) | Open, plated |
| J4 JST contacts | 6 × Ø0.95 mm PTH | Open, plated |
| J6 JST contacts | 2 × Ø1.00 mm PTH | Open, plated |
| TP1/TP3/TP4 loop testpoints | 1 × Ø1.00 mm PTH each (3 total) | Open, plated |
| J7 USB contacts | 16 × Ø0.40 mm PTH | Open, plated |
| J7 USB shell slots | 2 × 0.60 × 1.40 mm and 2 × 0.60 × 2.10 mm plated slots | Open, plated |
| J1/J2/J3/J8 locating holes | 4 round Ø1.60 mm and 4 oval 1.60 × 1.75 mm NPTH | Open, non-plated |
| H1–H4 mounting holes | 4 × Ø3.20 mm NPTH | Open, non-plated |

Priority CAM inspection locations are L1 (24 × Ø0.30 mm pad vias), Q1 and Q2 exposed drain pad 9 (4 × Ø0.40 mm each), U1 module lands/ground array, U4 tab/lead pads, U5 pads, and the F5 U8, C60, C64, C65 and C67 cases. The process applies to every true via, including vias without a component-pad overlap, not only the priority locations.

Please provide the production-file/CAM result for review before production. Confirm that it distinguishes all 324 via fill/cap assignments from all 41 PTH and 12 NPTH keep-open holes, preserves the 96 × 70 mm outline and all four copper layers, and does not mirror, omit, resize, mask-close, reroute, or otherwise alter the supplied design. Contact us before any omitted cap, process substitution, hole/land/mask change, or copper change.

## Authority and source notes

- Accepted production PCB SHA256: `4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737`.
- Phase 4.22A owner-approved configuration and Phase 4.22B via-process review are the current repository decisions. No separate Phase 4.23 manufacturing decision or manufacturer-note file was found; this draft does not invent one.
- JLCPCB [Via Covering](https://jlcpcb.com/help/article/pcb-via-covering), retrieved 2026-10-18 (page updated 2026-09-09), describes epoxy-filled & capped vias, recommends holes no larger than 0.50 mm, and asks customers to identify which vias are to be filled. It also states that epoxy can cover via-in-pad/opening cases that ink plugging cannot.
- JLCPCB [PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/), retrieved 2026-10-18, lists epoxy-filled & capped via-in-pad processing and the published via-in-pad size range. The two Ø0.50 mm vias remain a boundary-size CAM confirmation item; no capability listing is treated as production acceptance.
- JLCPCB [Confirm Production File](https://jlcpcb.com/help/article/how-to-confirm-the-production-file), retrieved 2026-10-18 (page updated 2026-09-09), recommends selecting confirmation, downloading the engineer-generated production files, and reviewing them before proceeding.

JLCPCB process guidance cannot prove physical epoxy filling, copper capping, barrel plating, planarity, or solder-joint quality from the submitted Gerbers. Those properties require the vendor production-file/process confirmation and, where needed, later physical inspection.
