# Recovery verification and revised proposal — NOT APPLIED

2026-10-11. Owner review required before either correction. No production CAD write/save/refill, general routing, fabrication, purchase, power-up, commit or push occurred in this recovery verification. VAC1/BQ25792 architecture remains closed; physical qualification and safe bring-up remain open.

## Recovery evidence

- Exact live document: `C:\Users\Michal\Git\my\ups12v\hardware\v4\ups_v4\ups12v_v4.kicad_pcb`, project `ups12v_v4`, KiCad 10.0.7. Konnect identified this open PCB; native IPC independently asserted name and project path.
- 154 footprints, 473 pads, 243 tracks, 135 vias, two zones. C9 remains (54.2,67.5), 0 degrees.
- PCB/schematic/project SHA-256 hashes match accepted entry. Normalized live comparison has zero geometry/attribute differences. Only runtime board/field identities and four custom-pad primitive identities changed on reopening (eight occurrences including duplicate pad projections); custom geometry and owning pads are unchanged.
- All connector silk artwork remains original, including the seven previously targeted primitives. No partial correction survived.
- PGND zone including existing fill and the four-layer RF rule area are identical. Every track and via matches baseline, preserving switching loops, source trunk, C3 returns and other completed routing.
- Fresh read-only saved-file ERC: zero errors, four existing isolated-label warnings. DRC: 262 unconnected items, zero other errors, 17 warnings (six silk-edge, 11 footprint-library mismatch), zero schematic/PCB parity issues. No unexpected unrouted-count change.
- Final live snapshot is exactly equal to the initial recovered live snapshot. No live mutation occurred during proposal analysis.

Evidence: `c9-apply-recovery-verified-ipc.json`, `c9-apply-recovery-final-ipc.json`, `c9-recovery-comparison.json`, `c9-recovery-drc.json`, `c9-recovery-erc.json`.

## Revised C9 proposal

Move C9 to **(61.1,69.1), rotation 0 degrees**. This supersedes the rejected (58.1,69.5) proposal. Keep its value, footprint, pad geometry and nets.

| Feature | Proposed geometry |
|---|---|
| C9.1 VIN1 | (60.62,69.1) |
| C9.2 PGND | (61.58,69.1) |
| New F.Cu VIN1 trace | C9.1 to existing VIN1 via (59.7,69.4), width 0.20 mm |
| VAC1 escape | Retain existing (59.7,69.4)–(58.6,69.4)–(58.4,68.8)–(58.4,68.05)–IC1.9 route |
| Source branch | Replace obsolete In2 branch with (59.7,69.4)–(60.5,69.4), width 0.20 mm |
| PGND return | C9.2 to **new PGND through via (61.9,69.1)**, trace width 0.30 mm, via copper 0.70 mm/drill 0.30 mm |

C9-to-VAC1 length becomes **3.733 mm** versus 25.685 mm. Ground escape becomes **0.320 mm** versus 2.157 mm to the original first return via. This proposal explicitly requests one new PGND via; it does not reuse the earlier proposal's ground-via connection across intervening copper.

Native KiCad courtyard checks moved C9 only in memory on the accepted backup, checking all other front courtyards including TP3's actual circular polygon. **No collisions.** Closest native polygon separation: IC1 approximately 0.200 mm, R9 approximately 0.370 mm. Conservatively subtracting 0.05 mm for combined courtyard strokes still leaves approximately 0.150/0.320 mm. No courtyard waiver or other footprint movement is proposed.

The copper screen checks both relocated pads, every new segment and the new via against existing cross-net pads, tracks and vias, plus proposed cross-net geometry. Pad bounding boxes are conservative, including native custom-pad bounds. New via checks cover all copper layers; replacement source trace checks cover In2. Minimum screened clearance **0.2845 mm**, above the explicitly used conservative 0.20 mm screen. The new ground-via position is inside the existing filled In1 PGND plane. C9 courtyard/new via do not intersect the RF keepout. No board-level copper graphic shapes are present beyond the checked tracks/pads/vias/zones.

Remove six superseded local tracks and the same two obsolete VIN1 vias, listed exactly in `c9-revised-copper.json`; retain the two existing VAC1 escape segments that the rejected proposal would have removed. Preserve VIN1 source trunk, C3 return network, all switching loops, every connector and existing PGND/RF zone geometry. Expected totals after approval: **154 footprints, 240 tracks, 134 vias** (six tracks removed/three added; two VIN1 vias removed/one PGND via added). Expected unrouted count remains 262 after refill; investigate any difference.

These are full local geometry screens, not an authoritative production-board proposal DRC or hardware qualification. Scratch-board DRC artifacts elsewhere in evidence have different project/library context and must not be presented as production acceptance results. After approval, native save/readback, refill, ERC, synchronized production DRC/parity and exact geometry/connectivity comparison remain mandatory.

Evidence: `c9-revised-courtyard.json`, `c9-revised-copper.json` and their read-only scripts. An additional courtyard-safe left-side candidate was rejected for NT4 copper collisions; it is not proposed.

## Safer silkscreen workflow proposed for approval

Do not retry the disabled live IPC child-geometry transaction. Installed native KiCad 10 APIs expose footprint `Remove`/`Add`, shape endpoint/shape/layer/width setters and native board/library save/load. Propose a **controlled native workflow with the PCB editor closed**, with matching project-local library artwork updates. KiCad manager can remain open; no standalone writer may coexist with the open PCB editor. Capture baseline and confirm the editor has released this board before any eventual write.

- J1/J2/J3/J8: replace each clipping rectangle by three silk segments; side endpoints stop at global Y30.35 mm. Preserve rear and side X positions and stroke width.
- J7: trim the two offending side endpoints to global X125.65 mm and remove the off-board front stroke.
- Preserve pads/nets/UUIDs, oval drills, connector positions, F.Fab, courtyards, references, mating clearances, every non-target graphic and all routing/zones. Update only F.SilkS in the two existing Nano-Fit RevJ1 library files under `hardware/v4/ups_v4/ups_v4.pretty`; preserve their library IDs. Make a project-local copy of the existing USB4085 footprint with matching silk and explicitly change only J7's library ID to that copy, updating its footprint entry in BOM documentation. This library-link change is included in the approval request; no USB physical/electrical geometry changes. Do not use generic library refresh: its lossless representation limitations have already blocked these connectors. Edit the existing placed artwork natively instead, retaining pad identities/connectivity.
- Save natively once, reload independently and compare every non-target source object/attribute. Reopen only the authoritative board, verify exact live identity/readback, refill and run ERC/DRC/parity. Six silk-edge warnings must disappear with no new error or parity issue; compare library warnings by identity rather than assuming their count remains unchanged after artwork divergence.

The current 11 library-mismatch warnings do not include these five connectors. Matching local artwork avoids adding five new mismatch warnings. Verify library/native roundtrips and compare all non-silk library geometry before writing the closed authoritative board. Stop if library parity cannot be maintained without broader footprint replacement.

**STOP for owner approval of the revised C9 geometry (including one new PGND via) and the closed-editor native silk workflow. Neither correction is applied to the authoritative board.**
