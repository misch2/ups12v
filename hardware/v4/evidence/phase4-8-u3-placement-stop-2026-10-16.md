# Phase 4.8 — STOP for bounded U3 placement review

2026-10-16. Phase 4.7 is ACCEPTED. **No production CAD mutation was attempted. Neither Batch A nor Batch B is complete.** This is a scratch feasibility rejection and a minimal placement-change proposal, not a routing completion or hardware qualification.

## Authoritative state and preservation

- Saved production PCB SHA256 remains `8c2f16ff54b803f7c52b2b9084153f2f7c09f88403edd7643f6d7010f1cf5379`.
- 405 tracks /145 vias /154 footprints /473 pads. Fresh isolated native snapshot is exactly equal to the final Phase4.7 native snapshot, including filled-zone exports. Full exact-document live IPC capture matches the accepted final Phase4.7 capture using the existing documented runtime-ID normalization.
- Fresh production checks: DRC239 unconnected /0 physical errors /16 warnings /0 parity; ERC0 errors /4 warnings. Production schematic/project hashes unchanged. All original tracks, vias, footprint/pad geometry, IC1 custom geometry, NT1/NT2, existing zones, RF/mechanics and BOM variants retained.
- 19 canonical toolkit tests PASS. Konnect reports `ipc_available=true`, `requested_open=true` for the exact production path. Initial direct-IPC sandbox connection failed with Permission denied at GetVersion; no document access or write occurred. System-approved host preflight then passed; no native assertion or unstable editor transaction occurred. No recovery/restart/save was attempted.

Evidence: [native entry](phase4-8-entry-native/snapshot.json), [live preflight](phase4-8-entry-ipc-host/preflight.json), [fresh production checks](phase4-8-entry-ipc-host/production-checks.json), [exact preservation and metrics](phase4-8-preservation-and-metrics.json), [fresh schematic export](phase4-8-current.net), [test log](phase4-8-tests.log).

## Current circuit and fixed-placement finding

Current schematic export and native pad/net geometry retain U3 SYS→MAIN_3V3, U4 USB_VBUS→USB3V3 and U5 MAIN/USB→MCU3V3. U5 MODE (pin5) is MAIN_3V3; PR1 retains the R23/R24 MAIN divider; C70/C71 remain the separate input bypasses. No alternate architecture, direct supply bridge or PGND/GND bypass is proposed.

U3 is at(49,79)/0°, L2 at(49,71)/0°, C37 at(49,76)/0°. U3.5 SW=(49.74,79.75); L2.1 SW=(47.345,71). Their **straight-line lower bound is9.072mm** before any clearance detour. The accepted REGN F.Cu route passes below L2 and diagonally between the SW endpoints. Its existing UUIDs and geometry remain exact; it must not be rerouted for this task.

The canonical exported-geometry route screen found a narrow feasibility candidate:

| Connection | Routed length | Layers / widths / vias |
|---|---:|---|
| U3.5→L2.1 SW |9.761mm|F.Cu +1.273mm B.Cu crossing;0.28mm tracks;2 through-vias Ø0.50/0.30mm at(48.85,72.95),(47.95,72.05)|
| U3.5→C37.2 SW |4.309mm|F.Cu,0.28mm; partly shares the SW escape|
| U3.6→C37.1 BST |8.213mm|F.Cu,0.28mm; wraps around the IC's lower and left sides|

The candidate adds24 tracks/2vias solely to an isolated scratch board. It contains redundant shared same-net screening legs, which would need consolidation before any possible installation. The bootstrap branch length sum is12.522mm, excluding the capacitor and internal driver path. This is conductor length, not measured loop inductance or a field-solver result. SW passes through the IC inter-row region and approaches sensitive pin escapes; the long bootstrap path uses space needed by local supply/return escapes.

[Native scratch validation](phase4-8-u3-sw-scratch/summary.json) completed: **0 physical DRC errors /0 parity,236 unconnected**, ERC0 errors. Scratch library-context warnings are20 DRC and11 ERC, versus16/4 on production; their types include missing library/footprint context. These are explicitly not claimed as production warning equivalence or complete acceptance. The saved production hashes remained exact throughout. The rejected candidate was never submitted to live IPC.

This candidate demonstrates that reduced unrouted count and a physical DRC pass do not establish an acceptable switching layout. Its0.28mm copper is only a feasibility screen, **not an approved1A power/thermal sizing result**. No optimized wider fixed-placement route, complete Batch A, or thermal acceptance is claimed. A longer all-front detour has not been disproved; it would not remove the9.072mm endpoint lower bound. The decision to request placement review is engineering judgment under the owner's significant-compromise STOP, not an invented maximum-length datasheet limit.

## Return-current and thermal limits

The critical high-di/dt loop must close C43/C32 SYS→U3.3→internal switching devices→U3.4→capacitor PGND. C43.1=(47,81.48),C43.2=(47,80.52); C32.1=(45,82.95),C32.2=(45,81.05). These local parts are preserved. Existing PGND vias nearest U3.4 are approximately13.95mm away; completing the stage would require new local PGND escapes/vias, as already allowed in Batch A. **The rejected SW/BST-only candidate does not complete this return loop.** No connected local ground path or thermal spreading is inferred merely from the visible PGND pad nets.

Output return must close U3.4 through PGND to C33/C45 negative pads, with the inductor/output positive paths kept compact. Both output capacitors currently have PGND pads at y74.525 and MAIN pads at y77.475, at x55 and58. Moving L2 to the pin5 side without reviewing these caps would leave avoidably long output/return geometry.

The two trial SW vias introduce antipads through In1.Cu. The existing exported In1 PGND outer contour remains one contour, but the current toolkit snapshot does **not export full hole topology**; that alone does not prove continuous local return under a proposed route. No actual field/current distribution, loop inductance, copper temperature rise or hardware noise was measured. A complete new candidate must verify local filled-copper paths/holes and PGND via connections before acceptance. Since the fixed-placement switching candidate is rejected, no further ground/thermal additions were made and no whole-stage return-path pass is claimed.

## Manufacturer basis

Reviewed2026-10-16:

- [TI TPS62933 datasheet](https://www.ti.com/lit/ds/symlink/tps62933.pdf), SLUSEA4D, revisedAugust2022, §7 pin functions and §12.1–12.2 pp40–41: minimize input switching loop; place IC, inductor and capacitors together; keep SW short; put bootstrap capacitor beside BST/SW; separate/shield feedback; provide wide VIN/GND copper and vias. These directions support regrouping, without prescribing a universal millimetre limit. The four-layer approved architecture is retained; TI's example two-layer copper does not authorize a stackup change.
- [TI TPS2116 datasheet](https://www.ti.com/lit/ds/symlink/tps2116.pdf), SLVSFG1A, revisedMay2021, §10.1 p17: close bypasses and short wide power/GND connections. Batch B not started.
- [Diodes AP7361C datasheet](https://www.diodes.com/datasheet/download/AP7361C.pdf), DS37274 Rev5-2, October2020, thermal data p6 and application power dissipation p12: dissipation depends on(VIN−VOUT)×IOUT and actual copper/ambient. SOT-223 tab spreading and permissible service load remain to be assessed in Batch B; no1A continuous thermal capability is inferred from the part rating.

## Concrete minimal-change proposal — NOT APPLIED

Authorize a **placement-feasibility checkpoint limited to L2,C37,C33,C45**, preserving U3 and all other positions, every existing copper object, topology/rules/zones and the entire accepted charger routing. Suggested starting trial positions are below. They are **not courtyard/DRC-qualified replacement coordinates** and are not an installation request; full footprint and zone checks must precede a final exact placement proposal.

| Ref | Current center /angle | Proposed scratch trial center /angle | Purpose |
|---|---|---|---|
| L2 |(49,71)/0°|(50,85)/−90°|Bring SW pad1 to(50,83.345), on U3 pin5 side; direct SW endpoint distance becomes3.604mm; keep new switching routing below the retained REGN path.|
| C37 |(49,76)/0°|(50.8,79.5)/−90°|Put BST/SW pads beside U3.6/U3.5 rather than above the sensitive pin bank.|
| C33 |(55,76)/90°|(54,85)/90°|Place the first output capacitor alongside the new inductor output with its PGND return facing the local ground region.|
| C45 |(58,76)/90°|(56.8,85)/90°|Keep the second output capacitor adjacent to C33; preserve TP13 at(59,85) and require courtyard/clearance verification.|

The proposed lower rectangle contains no existing routed-object endpoints in the export screen; this is only an initial screen and not proof that no segment, courtyard, mask, artwork or mechanical boundary crosses it. C32,C43,C39, all feedback/EN parts, U3,U4,U5,TP13 and F5 remain fixed. Proposed C37 and inductor/capacitor courtyards need special checking. If these four moves cannot fit without changing anything else, return a new bounded proposal; do not silently move another component or copper.

After owner authorization, test isolated placement/routing first through supported native APIs and the canonical toolkit, prove local input/output and bootstrap current paths, ground-plane holes/continuity and widths/vias/thermal assumptions, then present the exact verified placement change before production installation. Do not overwrite an open production board from scratch. Batch B remains unstarted pending resolution of this Batch A STOP.

**STOP for owner review.** Production remains the accepted Phase4.7 checkpoint,239 unconnected. No fabrication,purchases,power-up,firmware,commit or push. A fresh session is appropriate for the bounded placement checkpoint after approval.
