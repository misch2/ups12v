# Phase 4.24 — fixed JLCPCB order configuration (review record)

**Status:** owner-requested configuration record for the independent Gerber review. No cart, upload, fabrication release, order, payment, or vendor submission was made.

| Field | Fixed configuration |
|---|---|
| Fabricator | JLCPCB |
| Board type | Bare PCB only; self-assembly for both F0 and F5 populations |
| Board size | Accepted routed outline, **96 × 70 mm** |
| Copper layers | **4 layers**, in order F.Cu / In1.Cu (PGND) / In2.Cu / B.Cu |
| Finished thickness | Nominal **1.6 mm** |
| Copper weight | **1 oz outer / 1 oz inner** |
| Surface finish | **ENIG** |
| Soldermask | **Green** |
| Legend/silkscreen | **White** |
| Via process | **Epoxy Filled & Capped** on all 324 true through vias; exclude all 41 component PTH and 12 NPTH |
| Electrical test | **Full electrical test** |
| Production-file review | **Confirm Production File = Yes** |

The via process is a design/CAM correspondence requirement, not a blanket hole-diameter rule: the 49 true Ø0.40 mm vias and J7’s 16 Ø0.40 mm plated component contact holes must be resolved by identity, and the J7 holes stay open. Both Ø0.50 mm USB vias at (92.456, 91.400) and (92.456, 90.200) require explicit CAM confirmation.

## Configuration authority

The accepted PCB identity and the four-layer, nominal 1.6 mm, 1 oz outer/1 oz inner, bare-board/self-assembly decisions are carried forward from Phase 4.22A and the active `V4_HANDOVER.md`. ENIG, green mask, white legend, Epoxy Filled & Capped, Full Electrical Test, and Confirm Production File = Yes are the fixed values requested for this Phase 4.24 review. No separate Phase 4.23 manufacturing decision or order record was found in the repository; no conflicting Phase 4.23 value is silently inferred.

The exact JLCPCB stackup code, laminate schedule, copper tolerances, minimum barrel plating, quantity, delivery, price, shipping/tax and stencil choice remain outside this read-only review unless present in the eventual order record. Nominal thickness and copper-weight selections above must not be rewritten from a generic published stackup example.

## Review gate before any production authorization

Select the listed options and retain **Confirm Production File = Yes**. Download and inspect the engineer-generated production file before authorizing production. Confirm the four copper layers, masks, legends, 96 × 70 mm outline, separate PTH/NPTH drills and slots, all 324 epoxy/capped vias, all 41 PTH/12 NPTH open holes, and unchanged solderable pad/mask geometry. Stop for owner review if the production file omits a via, fills a component hole, changes a mask opening, mirrors or alters copper, or cannot establish the two Ø0.50 mm USB-via assignments.

JLCPCB references checked 2026-10-18: [Via Covering](https://jlcpcb.com/help/article/pcb-via-covering), [PCB Manufacturing & Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/), and [How to confirm the production file](https://jlcpcb.com/help/article/how-to-confirm-the-production-file).
