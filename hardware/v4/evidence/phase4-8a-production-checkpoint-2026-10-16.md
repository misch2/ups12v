# Phase4.8A — exact U3 production installation VERIFIED; STOP

2026-10-16. Owner accepted the complete local U3 scratch candidate and approved only its exact production installation. **The four moves and68tracks/11vias are installed, refilled, saved by the owning KiCad editor and independently verified. STOP for owner review.** U4/U5 Batch B and upstream/remote distribution remain deferred.

## New verified production state

| Item | Actual production result |
|---|---|
| PCB SHA256 |`3b218275b9cc85481852fad67e80b0b32ba80fdbd94453e00b441950f8502418`|
| Inventory |**473tracks /156vias /154footprints /473pads**|
| Fresh native DRC |**216unconnected /0physical errors /16known warnings /0parity**|
| Fresh ERC |**0errors /4known warnings**|
| DRC/ERC warning comparison |Both production warning multisets unchanged; ignored DRC checks unchanged|
| Added geometry |Exactly68tracks /11through-vias; geometry/layers/widths/drills equal immutable plan|

The production result is measured from the saved board after IPC refill/save, not copied from scratch counts. [Fresh production DRC/ERC](phase4-8a-install-ipc-host/production-checks.json) have their native reports/logs alongside. The source schematic SHA256 remains`990d107296d149775884dc2d2512c2e6102b6191e4818e7fcf5bd9268d48c8f6`; project SHA256 remains`477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e`. Rules and BOM/population variants are unchanged.

## Exact installed placement and routing

| Ref | Saved native center /angle |
|---|---|
| L2 |(49.65,85.00)/−90°|
| C37 |(50.90,79.50)/−90°|
| C33 |(54.00,85.00)/+90°|
| C45 |(56.40,85.00)/+90°|
| U3 — preserved |(49.00,79.00)/0°|

[Immutable plan](phase4-8-u3-proposal-plan.json) SHA256 remains`dd4b7d7a107e6d4893db032d17910c8783cde8d36dd21ad93146c13b6867be74`. Every saved footprint/pad position, net, drill and native copper polygon matches the accepted candidate. Every original405track/145via object retains UUID, net, layer and geometry. No optimization, replacement or deletion occurred. The independent addition counter proves exact route endpoints, copper widths, layers and via arrangements.

Confirmed from actual production readback: SW3.703mm/F.Cu/0vias;BST1.255mm plus1.894mm SW return. Projected input loop3.497mm²,bootstrap1.143mm²,output C33/C45 loops19.272/34.552mm². Actual SW copper area8.295mm² on F.Cu and0 on B.Cu. These are the same centerline/raster review measures and qualifications as the accepted proposal, not new inductance or noise measurements.

## Transaction and reconciliation evidence

Entry saved hash`8c2f16ff54b803f7c52b2b9084153f2f7c09f88403edd7643f6d7010f1cf5379`, fresh isolated native snapshots and full exact-document live IPC capture matched the accepted405track/145via baseline. Konnect reported the requested production board open with IPC available. No unaccounted live geometry was present.

Canonical adapter preparation used supported IPC footprint objects, preserving local3D models and all child identities. Exact integer orthogonal transforms avoid the installed SDK's1nm graphic truncation; native field/line/rectangle and pad targets were checked before mutation. No serialized CAD text was edited and no scratch PCB was copied over production. The original candidate was not reoptimized or rerouted.

One native commit updated the four original footprint UUIDs and created79new routed objects. Returned footprint/created-object geometry was verified before commit push; actual visible geometry/counts were read back after push. Zones were refilled, non-zone objects rechecked and the board saved by its owning editor. Commit token, push confirmation, created/updated IDs and full before/applied/final captures are retained in [installation evidence](phase4-8a-install-ipc-host/install-context.json). Fresh native workers loaded only isolated byte-copies for independent snapshot/audit. Production CLI DRC/ERC used no external save/refill flags.

The initial sandbox-only read-only IPC attempt stopped at GetVersion with Permission denied before document access. System approval preceded successful host preflight and the separately approved host apply. **No native KiCad assertion, unstable editor transaction, automatic recovery or uncertain save occurred.**

## Preservation and actual return paths

[Full canonical preservation proof](phase4-8a-install-ipc-host/full-preservation.json) confirms:

- All native footprints/pads and moved/unmoved artwork match the accepted candidate; all unrelated footprint artwork and all board drawings remain exact relative to entry.
- Both zone definitions, including PGND and RF keepout/restrictions, remain identical. Existing IC1 custom pad polygons, switching loops, BATTERY layer assignment, REGN and all Phase4.5–4.7 routed copper remain exact. NT1/NT2, Nano-Fit and mounting geometry are preserved.
- Production In1 native fill occupancy grid is **exactly equal** to the accepted candidate's full16×15mm/0.1mm local grid; direct via probes match. The exported fill remains one contour, with actual antipads represented by KiCad's fractured polygon geometry. All9new PGND vias connect into surrounding PGND copper; the2MAIN sense vias have local antipads. No SW vias/plane interruptions were added.
- Native-fill/drill-aware output and quiet-reference paths remain connected. FB center/±0.15mm reference coverage remains597/597 sampled points. No GND↔PGND connection outside NT1 or new MAIN/USB/MCU rail bridge is introduced.
- Production net unconnected counts equal the accepted candidate: SW/BST/FB/EN/SS local nets0;PGND78,SYS6,MAIN15. Total216. Both DRC/ERC warning multisets equal entry production, not scratch-library-context counts.

Independent evidence: [saved native snapshot](phase4-8a-production-native/snapshot.json), [actual layout/fill samples](phase4-8a-production-native/layout.json), [native zone/artwork audit](phase4-8a-production-native/native-audit.json), [exact additions and original-copper preservation](phase4-8a-install-ipc-host/native-preservation.json), [actual production electrical-layout metrics](phase4-8a-production-metrics.json), [remaining connections](phase4-8a-install-ipc-host/remaining-by-net.json), [verified saved/live baseline](phase4-8a-install-ipc-host/accepted-installed-baseline.json).

**25 toolkit tests PASS**, including exact supported IPC preparation against accepted native evidence, preserved3D model payloads/children, immutable plan rejection, scope guards and existing via/assertion-monitor/import regressions. Native returned/visible and independent saved comparisons also passed.

## Remaining boundary and qualification

Upstream SYS→local C32 supply and MAIN→U5/C70/remote loads remain unrouted boundary connections. No U4/U5,F5,Q5/host control,MCU/I2C/INT or unrelated PGND routing was performed. A remaining PGND entry using C32 as representative terminates at remote C25; the local U3 ground cluster is connected.

The accepted prototype limits remain: copper/thermal estimates assume35µm outer copper and approximately1A target; final stackup/plating, U3/inductor temperature, effective capacitance, startup/transients, stability and noise require matching hardware qualification. No hardware power-up, fabrication or procurement occurred. Reuse the accepted [layer/loop images and electrical comparison](phase4-8-u3-scratch-proposal-2026-10-16.md): independent native geometry and actual plane sampling prove production correspondence.

**STOP for owner review of this verified production checkpoint.** No subsequent routing,firmware,commit or push. Recommend a fresh session for the next separately authorized milestone, using the new verified saved/live baseline above.
