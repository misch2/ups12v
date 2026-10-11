# Phase 4.7 exact preferred routing — production implementation complete

2026-10-11. **Owner-approved batch implemented, saved and verified. STOP for owner review.** No remaining REGN/CE/control routing is authorized by this checkpoint.

## Safe procedure and baseline

After the earlier adapter sequencing STOP, owner confirmed closure without saving and reopening the unchanged production board. Fresh preflight bound the exact live IPC document to `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_pcb` and project directory. PCB/schematic/project hashes exactly matched accepted `c9-apply-phase4-7-batch1-final-ipc.json`; baseline was **252 tracks / 138 vias / 154 footprints**. Runtime parent/custom-primitive UUIDs and inactive custom-anchor metadata on circular geometry were normalized only for cross-session comparison; real dimensions, shapes, connectivity and all other fields were retained.

Canonical toolkit used unchanged geometry/safety/check parsing plus its narrowly bounded `v4kicad.ipc_install` adapter, needed because existing offline commands cannot edit a live document and Konnect remains without a configured socket. **15 regression tests passed**; fresh isolated native read-only baseline snapshot passed. Direct supported KiCad IPC used the owner-supplied socket outside the sandbox. Native action workers were monitored. No assertions, transport instability, automatic recovery or rollback occurred in this final attempt.

Installed via one native KiCad undo transaction. Returned added geometry checked before commit; transaction confirmed before full-board/count readback, as required for staged IPC creations. Commit token/push status recorded. Editor performed native zone refill and saved its own document. **No scratch board was copied over production, no external overwrite and no editor reload/revert.** Independent `pcbnew` readback loaded only a fresh isolated byte-copy of the saved production board; native CLI production checks did not save/refill externally.

## Exact implemented geometry

- Sole original track change: BATTERY UUID `01ab1eb5-ab75-462d-9e54-2d6eab529481`, **F.Cu → In2.Cu**. Original net, 0.60 mm width, endpoints (63.1,65.5) → (63.8,66.9) and existing endpoint vias preserved.
- Exact accepted original-position BATP/PGND/ILIM_HIZ/TS subset from `phase4-7-preferred-final-plan.json` installed.
- PROG **14.198946619657605 mm** (rounded **14.198946620 mm**), 0.10 mm width; F.Cu8.181075410 + B.Cu6.017871209 mm. Two through-vias **Ø0.50/0.30 mm** at **(67.6,65.08)** and **(64.78,70.01)**. Native readback verified widths on all four copper layers and drill geometry.
- Exactly **47 tracks / 3 vias added**, including the subset's PGND via. Final **299 tracks / 141 vias / 154 footprints / 473 pads**.

Shared toolkit preservation passes against accepted baseline: all original routed objects except declared BATTERY layer unchanged; all original footprint metadata, pad copper polygons/nets/drills and via per-layer copper widths/drills unchanged. Added geometry equals the exact accepted plan. **All final track/via geometry also equals accepted scratch**, independent of new UUIDs. This preserves C23, R5, NT1/NT2, C9, Nano-Fit connectors and switching/power copper.

Live full-object before/after checks preserved unrelated footprint/pad/track/via/shape/text/zone definitions. Native refill changed only fill data; In1 PGND remains **one filled contour**. Native-save diff inspected: authorized routed additions/layer relocation and native filled-polygon updates only, including a few remote contour re-tessellation vertices. No footprint, outline or RF rule-area edit. Unchanged project hash preserves netclasses/rule settings; schematic hash unchanged. No rule relaxation.

## Fresh production checks

| Check | Result |
|---|---|
| Production DRC, all track errors + schematic parity | **0 physical errors / 251 unconnected / 16 warnings / 0 parity** |
| Production ERC | **0 errors / 4 known warnings** |
| Baseline DRC comparison | 257 → 251 unconnected; **16 warning type/description entries identical** |
| Native saved readback and preservation | **PASS**, exact plan and all original geometry accounted for |
| Toolkit regression tests | **15 PASS** |

All 16 production DRC warnings are retained `lib_footprint_mismatch` findings, not new shorts/clearance/thermal/via violations. Existing ignored check categories remain configured; unchanged project bytes demonstrate no severity/settings relaxation. The board remains incompletely routed and is not fabrication-ready.

These are **fresh production** ERC/DRC results with the production library context. Earlier scratch results (20 DRC warnings; 11 ERC warnings including seven missing library-context warnings) are historical scratch evidence and are not substituted for production results.

Saved production PCB SHA256: `3ec08c7872b7d510829d4c3ce759fdacc74c813c6e5d522000940a842ab6c69b`. Schematic and project retain accepted Batch1 hashes. `installed-manifest.json` binds the final saved state; readback and post-check hashes match it. Source-baseline backup stays in `accepted-before.kicad_pcb` for review, not installation.

## Electrical limitations retained

The accepted shorter route halves PROG length but adds two through-vias and lacks a continuous immediately adjacent ground reference on B.Cu. Common F.Cu escape exposure near BTST2 remains (~0.160 mm minimum edge gap and ~1.12 mm close parallel exposure in the prior screen). B.Cu avoids long close parallelism with SW2/BTST2 but crosses beneath BATTERY distribution and has local In1 reference openings. Startup/transient noise immunity is not measured. DRC does not prove immunity of the PROG resistance sample.

Moving BATTERY removes an independent outer-layer parallel branch and associated outer-face heat spreading. Much of moved copper overlaps existing In2 copper without doubling thickness; current sharing shifts toward retained vias and inner copper. Prior copper-only screen estimates ~80% overlap, ~0.193 mm² distinct In2 added vs ~0.578 mm² distinct F.Cu removed. Existing 35 µm/20°C resistance estimates are illustrative, not measured current shares/ampacity/thermal qualification. Later matching-hardware validation remains necessary; no power-up authorized here.

Geometry is identical to the previously assessed accepted candidate, so detailed electrical screen/manufacturer assumptions remain in `../phase4-7-preferred-final-checkpoint-2026-10-11.md` and `../phase4-7-layer-validation-checkpoint-2026-10-11.md`. No electrical redesign or new acceptance threshold added.

## Evidence and boundary

This directory: `preflight.json`, `live-before.json`, `commit-id.json`, `commit-pushed.json`, `created-ids.json`, `live-applied.json`, `live-final.json`, `native-preservation.json`, `installed-manifest.json`, `production-drc.json`, `production-erc.json`, their summaries/logs, `warnings-comparison.json`, `production-native-save.diff` and monitored native worker logs. Independent native snapshot: `../phase4-7-production-final-native-readback/snapshot.json`. Baseline native snapshot: `../phase4-7-production-final-smoke/snapshot.json`.

**STOP for owner review.** No remaining REGN/CE/control routing, fabrication, purchasing, power-up, firmware build, Git commit or push. Earlier failed-attempt diagnostics remain preserved and are superseded by this successful final checkpoint.
