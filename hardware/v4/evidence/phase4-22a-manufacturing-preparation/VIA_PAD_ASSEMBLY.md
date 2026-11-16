# Actual via / solderable-pad screen — prototype assembly concern

2026-10-18. Accepted Phase4.21 PCB hash `4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737`. **Actual open via-in-pad cases exist. Free ink plugging must not be treated as a remedy for these cases.** No PCB/order-process change was made, and no solder failure was measured.

## Evidence and scope

[Final object screen](actual-object-screen-final.json) uses accepted native pad polygons, per-layer via copper/drills and IPC pad-mask layer membership. Retained setup has zero pad-to-mask expansion, front/back via tenting and no pad/footprint mask override or custom mask artwork. Thus solderable pad openings are the accepted copper polygons at1:1. This identifies holes exposed by **pad mask openings even when global via tenting is requested**. It does not guarantee the manufactured mask, individual tent integrity, ink plugging or CAM processing; unexposed-by-pad vias are not declared hermetically sealed.

Of324vias, **256 unique vias** have annulus edges within0.35mm of solderable pad openings; **144** have bore overlap with an opening; **118** have their centers inside an opening. There are319via/pad/side pairs; counts overlap and are not added. DNP and test-pad openings are included because they still exist physically. All bore-overlap pairs found are same-net; no different-net short is demonstrated.

The0.35mm screen is explicitly **via annulus edge to pad mask-opening edge**. Bore-edge distance is separately recorded, since vendor wording does not fully define the distance convention. Hole-overlap/center-in-pad cases are unambiguous. Negative distance denotes geometric overlap, not depth. Full UUIDs, refs/pins, positions, sides, bores and both distances are in the JSON, not summarized away.

| Power/service component | Unique near vias / centers inside opening / bores overlapping | Practical implication |
|---|---:|---|
| IC1 |6 /0 /0|Nearby package/switch-array escapes; ink-plugging eligibility must be checked, but no bore opening in IC1 pads found |
| L1 |24 /24 /24|Twelve0.30mm switch vias in each solderable terminal; actual solder-wicking/volume risk during reflow/hot-air |
| Q1 |5 /4 /4|Four0.40mm vias in exposed drain pad9; hidden joint/voiding and solder-volume concern |
| Q2 |5 /4 /4|Four0.40mm vias in exposed drain pad9; same concern |
| Q10 |0 /0 /0|No via within this screen of its pads; smaller-land prototype deviation remains independently accepted |
| U3 / U7 |1/0/0 and2/0/0|Near openings; no bore exposure found at their own pads |
| U4 |6 /4 /4|Four vias exposed in solderable pads/tab; reflow solder-volume concern |
| U5 |4 /2 /3|Small-pad via exposure; control solder quantity and inspect joints |
| U8 |2 /0 /1|Partial bore overlap with a pad opening; no filled/capped assumption |
| C60 / C64 / C65 |1/1/1, 3/0/1, 2/0/1|F5 input/output capacitor soldering can drain into an open bore |
| U1 |22 /8 /11|Module land/ground-pad openings; hidden-joint assembly inspection needed |

Q1 pad9 center-via positions(mm): (43.6,69.4), (44.3,69.4), (43.6,70.1), (44.3,70.1). Q2: (44.0,64.3), (44.7,64.3), (44.0,65.0), (44.7,65.0). These are existing accepted geometry, not new defects or proposed edits. Other capacitor/logic-pad cases remain in the complete result.

## Process interpretation and owner decision

JLCPCB's [Via Covering guide](https://jlcpcb.com/help/article/pcb-via-covering), updated2026-09-09 and checked2026-10-18, describes **Plugged as soldermask ink**, separately from epoxy-filled/copper-capped processes. It excludes holes in pads and vias within0.35mm of pad openings from ink plugging. Tenting may be incomplete near openings. Consequently the owner's currently displayed free Plugged option cannot be assumed to seal the cases above. This is not a quotation for resin fill or a reason to automatically change that option.

For self-assembly, open barrels can consume solder, alter paste volume and promote voids/starved hidden joints. Backside tenting alone does not create a planar solderable cap. Controlled solder/flux/reflow or hot-air, small-part-first sequencing, unpowered inspection and later temperature/drop checks can form a prototype process; no stencil adjustment, process yield or inaccessible-joint quality has been qualified here. Do not prescribe “add more paste everywhere”: fine-pitch bridges and the accepted smaller AON lands need local control.

**Pending next-phase owner disposition:** retain an explicitly reviewed open-via prototype assembly process, or request a separately assessed fabrication-process option. Confirm which vias JLC would actually ink plug/leave exposed and review finish/CAM accordingly. No automatic epoxy upgrade, drill/routing change or new acceptance threshold. This decision is separate from the already accepted Nano-Fit tolerance and AON exposed-land deviations.

## Actual trace/gap check

The same bounded screen covers all **1170 routed tracks/arcs**, minimum width **0.100mm**, with none below0.100mm. Different-net routed copper versus fixed tracks/vias/pads has no gap below0.100mm beyond the stated numerical allowance; the closest exported polygon result is0.099999484mm, effectively0.100mm within native polygon/numerical precision. This is above JLC's0.09mm capability floor. Pad-pad, via-via, fills and connectivity reuse accepted Phase4.21 native DRC/vendor results; no fresh Gerber CAM or full-board reroute analysis is claimed.

Initial generic artwork classification produced seven apparent gaps against the three intentional NT1/NT2/NT4 copper bridges. Owner-preserved net-tie ownership explains all seven; final screen separately records these bridges instead of calling them a foreign net. No genuine net mismatch was waived. Regression controls still reject a real0.09mm different-net trace gap and unknown copper artwork. [Bounded toolkit module](../../tools/v4kicad/manufacturing_screen.py), [focused tests](../../tools/tests/test_manufacturing_screen.py).
