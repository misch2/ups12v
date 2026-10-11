# C9 / VIN1 / VAC1 focused layout review — proposal awaiting approval

2026-10-11. Owner approved the completed safety architecture decision checkpoint. VAC1 and BQ25792 architecture decisions are CLOSED; physical qualification and safe bring-up gates remain OPEN. This milestone authorizes inspection and proposals only. No CAD geometry has been applied and general routing remains stopped.

## Finding and recommendation

**Meaningful local layout issue: C9 is physically near IC1 but electrically remote from VAC1.** Its 100 nF / 50 V value and approved architecture are unchanged. Recommend moving and rotating only C9, then replacing its local signal/ground escapes. Preserve the accepted switching loops, all other component placements, Nano-Fit connectors and continuous In1 PGND plane. This is a decoupling improvement, not proof that VAC1 transients are safe.

## Actual connectivity and geometry

IC1 is currently BQ25798RQMR; the accepted BQ25792 alternative decision is not a fitted-part substitution. KiCad 10.0.7/Konnect confirmed the exact open board `hardware/v4/ups_v4/ups12v_v4.kicad_pcb`. Independent native IPC corroborated all 243 track positions/widths/nets, 135 via positions/nets and 473 pad positions/nets against the saved native KiCad API capture. There are 154 footprints.

J1.2 feeds F1 and VIN1. VIN1 has the existing R12/C26 shunt branch near F1, and a 2.2 mm In2 feed from (40.0489,44) down to (40.0489,69.7), then toward Q1. The sensing branch leaves this supply through (39,69.7) and follows the 0.2 mm In2 trunk at Y74. This remains a sense branch, not the charger's high-current switching path.

| Path | Actual layout |
|---|---|
| C9.1 → VAC1/IC1.9 | C9.1 (53.72,67.5), F.Cu left to (51.6,67.5), down to the via at (51.6,68.5), In2 to (51.6,74), across the trunk to (60.5,74), up to (60.5,69.4), left to (58.6,69.4), through a via to F.Cu, then via (58.4,68.8)/(58.4,68.05) to IC1.9 (58.6,67.85). **25.685 mm planar centreline**, excluding via-barrel length; direct pad-centre separation is 4.893 mm. A second VIN1 via is at (59.7,69.4). |
| C9.2 → PGND | C9.2 (54.68,67.5), down to (54.68,68), diagonally to C3's PGND land/via (56.3,68.35): **2.157 mm** before the first plane via. A paired via at (56.95,68.35) and stitching via at (57.5,68.9) continue the PGND connection. |
| Local IC ground | IC1.10 is PGND at (59,67.9), with its via at (59,68.6). IC1.27 and accepted bypass-return geometry remain unchanged. |

Both saved fill and live filled-polygon samples show PGND copper below the proposed C9 ground, the existing local ground via, the IC ground via and the Y74 trunk. The saved PGND fill is one polygon. This establishes the available reference connection; it is not an extracted return impedance or measured current-density result.

The long 0.2 mm cap-to-pin excursion and two layer transitions add avoidable series inductance. Its return also shares a short top-layer segment with C3/REGN decoupling before reaching the plane. C9 therefore cannot be treated as an ideal capacitor directly at VAC1 at high frequency.

**Switching-noise assessment:** the long Y74 sense run does not overlap or run closely parallel to the accepted SW1/SW2 trunks. The switching fanout remains under/above IC1 and north toward L1. In1 provides a ground reference between top-layer C9/sense copper and deeper switch routing; In2 and B.Cu do not have an intervening ground layer. Thus unnecessary exposure and common-return inductance are credible concerns, but this review establishes no actual noise amplitude, malfunction or strong direct SW-to-sense coupling. Avoid making that stronger claim. No field solver or hardware measurement was performed.

## Manufacturer comparison

- [TI BQ25798 SLUSDV2C, June 2026, §8.4.1–8.4.2, pp.139–140](https://www.ti.com/lit/ds/symlink/bq25798.pdf): prioritize local PMID/SYS bypass loops, short low-impedance connections and plane returns; limit switch copper and keep sensitive routing away from switch nodes. These priorities support preserving the accepted switching-loop checkpoint. They do not prescribe a numeric VAC1 trace-length limit.
- TI BQ25792 SLUSDG1D, April 2026, §11.1–11.2, pp.134–135: the existing manufacturer PDF/text under `references/bq25792-safety-review.*` recommends short bypass/ground connections and compact loops. Its strongest same-layer requirements address SYS/PMID/VBUS power bypasses, not explicitly C9/VAC1. No additional mandatory VAC1 gate is inferred from those requirements.
- [TI family checklist V1p0, p.2, VAC1 row](https://e2echina.ti.com/cfs-file/__key/communityserver-discussions-components-files/24/BQ25790_5F00_BQ25792_5F00_BQ25672_5F00_V1p0_5F00_Schematic-Checklist.pdf): identifies the optional 100 nF VAC1 sense filter capacitor; it specifies no numeric VAC1 layout limit. This distinguishes C9's role from the critical PMID/SYS switching bypass capacitors.
- [TI SLUAAL8, May 2023, §3 / Fig.3-1, p.4](https://www.ti.com/lit/an/sluaal8/sluaal8.pdf): depicts a local 0.1 µF capacitor and a separate damped RC branch; discusses connector-side versus IC-side placement when PCB feed/return traces are long. Keep approved R12/C26 2 Ω + 2.2 µF unchanged. Shortening C9's local connection does not qualify the complete hot-plug network or establish that relocating the snubber is necessary.

Sources were checked on 2026-10-11; the BQ25792 current base URL failed in the browser, so its exact revision/sections were read from the already stored TI PDF/text, not substituted with the search index's older Rev C. The recommendation is an engineering application of TI's low-inductance layout principles, not a claimed TI violation of a stated maximum length.

## Smallest proposed local CAD correction — NOT APPLIED

All coordinates are board-space millimetres. Target geometry is concrete for approval; final native clearance/DRC readback remains necessary after application.

1. Move **C9 only** from (54.2,67.5), 0° to **(58.1,69.5), 180°** on F.Cu. New pad1/VIN1 centre (58.58,69.5); pad2/PGND centre (57.62,69.5). Keep the same footprint, value, MPN, pads and population properties.
2. Retain IC1.9's first escape to (58.4,68.8); replace the final segment with a direct 0.2 mm F.Cu segment to C9.1. **VAC1–C9 centreline ≈1.756 mm**, about 93% shorter. Keep the pin escape width; this is a sense connection.
3. Retain the source-side trunk and the existing VIN1 via (59.7,69.4). Feed C9.1 from that via on F.Cu, and shorten the In2 local connection to (59.7,69.4) → (60.5,69.4). Remove the now-redundant VIN1 via at (58.6,69.4), which otherwise conflicts with the proposed capacitor pad, and its superseded top connection.
4. Remove only C9's old left-hand VIN1 spur, the via at (51.6,68.5), and its vertical In2 spur down to Y74. Preserve the Y74 trunk and all source/high-current copper. Two VIN1 vias are removed in total; no new vias are needed.
5. Replace C9's old two-segment PGND escape with a 0.3 mm local connection: (57.62,69.5) → (57.5,69.38) → existing PGND via (57.5,68.9). **Ground-to-via centreline ≈0.650 mm**, about 70% shorter. Preserve C3's PGND land, paired vias and stitching, plus IC1.10's return. Do not split or reshape the plane.

The new C9 courtyard translates to X57.19–59.01/Y69.04–69.96. It fits north of TP3 at (58,71.5); no test-point move is proposed. A conservative geometric screen of proposed top copper against existing tracks, vias and pad bounding boxes finds a nearest foreign-copper gap of approximately **0.282 mm**, to the IC1.10 PGND via. This is a feasibility screen only, not DRC, soldermask review or EM simulation. Exact package/courtyard and native rules must be verified when applying the approved correction. UUID-specific removed segments and replacement endpoints are recorded in `c9-review-proposal.json`.

Scope expressly excludes IC1, L1, C5/C6, all accepted bulk-capacitor placements, SW1/SW2 traces/vias, Nano-Fit copper/mechanics, R12/C26, PGND topology, BOM, architecture and remaining routing. If native checks require changes outside this list, stop and present the conflict rather than broadening scope.

## Connector silkscreen warnings — artwork-only correction feasible

Fresh saved-board DRC reports **six silk-edge warnings**: four Nano-Fit body rectangles (J1/J2/J3/J8) and two J7 side lines. These belong to footprint artwork; they are not evidence that the connector bodies or board edge should move.

- J1/J2/J3/J8 rectangles extend to Y29.89 across the Y30 board edge. Preserve the bottom/rear outline and polarity/pin-1 markers; convert each body rectangle into an open three-sided silk outline, with its side ends clipped at **Y30.35**. Remove the off-board front stroke. This gives nominal 0.29 mm edge-to-ink clearance with the existing 0.12 mm stroke. Keep full body geometry on F.Fab and keep courtyards/mechanical models unchanged.
- J7's two warned lines end at X126.12 beyond the right edge X126; its off-board connecting front stroke also needs removal. Retain the on-board portions and truncate at **X125.65**, nominal 0.29 mm edge-to-ink clearance. Preserve shell lands, holes, copper, fabrication outline and courtyard. Treat all three outer strokes coherently, even though DRC lists only two crossings.

The 0.35 mm centreline inset is a proposed artwork target, not a new fabrication requirement. Verify against configured rules with DRC after approval; retain readable polarity/connector identification. Do not waive warnings, relax rules or shift connectors to silence them. Konnect currently labels these footprint primitives `editable=false`; use a supported native live/coordinated KiCad artwork workflow if its typed editor cannot handle them. Never overwrite the open board offline or refresh footprints in a way that restores old pad mappings/locator geometry. A local-library silk variant may be needed to preserve artwork through future refresh; that is an implementation detail to resolve inside the approved artwork scope.

## Verification and boundaries

Fresh ERC: **0 errors / 4 unchanged isolated-label warnings**; schematic short query: **0**. Fresh saved-board DRC: **262 expected unconnected items / 0 other errors / 17 warnings / 0 parity findings**. Warnings are six silk-edge and eleven library mismatches. The proposed correction has not been applied or DRC-tested. This is not release readiness.

Native hashes prove the PCB, schematic and project configuration stayed unchanged during inspection. Full evidence: `c9-review-geometry.json`, `c9-review-konnect-live.json`, `c9-review-live-parity.json`, `c9-review-proposal.json`, `c9-review-stackup.json`, `c9-review-drc.json`, `c9-review-erc.json`. Saved cropped copper view `c9-review-crop.png` was visually inspected; it is inspection evidence, not a proposed routed-board export.

**Approval requested:** bounded C9 move/local reroute described above, and separately the artwork-only connector silk cleanup. After approval: apply one coherent local change at a time, verify live/saved persistence and connectivity, refill the existing PGND plane without topology changes, run ERC/DRC/parity and inspect the focused diff. Stop at that checkpoint. No general routing, fabrication, purchasing, power-up, firmware changes/build, commit or push. Physical qualification and safe bring-up remain OPEN.
