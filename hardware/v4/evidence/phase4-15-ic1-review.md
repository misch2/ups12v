# Phase4.15 — IC1 closures verified; BATTERY correction required

**Historical finding, now resolved:** see the [repaired review PASS](phase4-15-repaired-review.md).

2026-10-17. **No production migration recommendation yet.** Owner closed the
saved scratch editor and confirmed manual track/via moves. The independent
native review used a fresh isolated copy and no IPC. No source CAD was changed.

## One actionable issue and smallest practical correction

BATTERY via **`(63.1,64.8)`**, UUID
`2095b89a-f273-40f1-9092-a50a802662af`, is now connected only on F.Cu. Its former
In2 branch was removed. Native DRC reports the new `via_dangling` warning.
The accepted design had two0.70/0.40mm BATTERY vias feeding In2; the current
design relies on the lower via `(63.1,65.5)` for that layer transition.
Pad connectivity survives, but the parallel via/current path was reduced.
This is an actual electrical geometry change, not serialization noise. An
absolute current/temperature limit violation has not been demonstrated.

**Smallest proposed correction:** in the owner's scratch, reconnect the upper
barrel to the lower BATTERY via with **In2.Cu,0.40mm width, `(63.1,64.8)` →
`(63.1,65.5)`**, length0.70mm. The current exported copper/drill joint preflight
accepts this segment without changing other copper. It has NOT been installed
or verified by native DRC; it restores the second barrel's layer connection,
not the entire old parallel In2 branch. Recheck actual BATTERY current geometry
and the rest of routing quality after the correction before adoption.

Do not blindly restore the original0.40/0.70mm In2 branch through `(63.1,66.9)`:
it now collides with BTST2 via `(62.8904,66.8528)`. No copper was removed or
replaced by this review. [Exact correction prechecks](phase4-15-owner-review-native/battery-correction-preapplication.json),
[before/after BATTERY geometry](phase4-15-owner-review-native/battery-local.json).

## Verified checks

- IC1.14 I2C_SCL→R21.2, IC1.21 ~INT→R28.2 and IC1.1 STAT→D2.1 all connected.
- Native DRC **41unconnected,0physical errors,0parity errors**; all opens are
  the deferred F5 nets. ERC **0errors**. Checks refill/save only the isolated copy.
- Native independent connectivity:473/473pads,160→157islands; exactly the three
  intended net merges; **no previous pad connections split**.
- Matched isolated warning counts21DRC/11ERC versus accepted20/11. The sole new
  warning is the BATTERY via above; ignored checks unchanged. These counts
  include scratch library-context warnings; production16/4 is not the comparator.
- Source schematic/custom rules identical to production. The project diff only
  adds0.15mm track and0.50/0.30mm via dropdown presets; constraints/netclasses
  were not changed.

## Focused owner diff and preservation evidence

[Exact native preimages/postimages](phase4-15-owner-review-native/physical-delta.json):
246tracks added,221removed,2modified;8vias added,1removed,3moved; R8 moves from
`(40,75.5)` to `(40,74.8792)`. Total1052track/arc objects,294vias,154footprints.
There are route changes on25nets, including surrounding control/supply routes
and changes beyond the immediate IC1 fanout. Owner confirms the track/via moves;
these changes are retained for review rather than rejected for non-45 geometry.
[Per-net changes](phase4-15-owner-review-native/routed-delta-by-net.json),
[width/length/layer metrics](phase4-15-owner-review-native/changed-net-metrics.json).

SW1/SW2 routed copper/vias are exactly unchanged, hence their switching copper
area is retained. U3 switching/feedback routes and USB data copper also remain
unchanged. BTST2, ACDRV1 and PGND vias moved; bootstrap, REGN, PROG, VIN1, PMID
and BATTERY route changes are explicitly captured, not assumed preserved.
Fine-pitch clearance and net isolation pass native DRC/connectivity. Further
electrical/route-quality sign-off stops at the BATTERY finding.

Zone definitions are unchanged. Refilled In1 PGND retains one native polygon
and no holes; area changes from6115.6044 to6111.2045mm² with the changed routes/
via antipads. Native pad-island preservation finds no lost PGND pad connections.
This is meaningful derived-copper change; no representation-identity requirement
or full PGND current-density/thermal claim is made.
[Physical/fill summary](phase4-15-owner-review-native/focused-physical-summary.json).

## Source authority and STOP

Owner saved PCB SHA256:
`632cb2d1972c3c9f0e670923a65d06b799512b8d4411d6864ef8821b4750d321`.
Production remains accepted SHA256:
`75060f4b3d0f57e65f2c6e4736f3dc32d42e62e359541671b1ffce63eceb7014`.
All source/production bindings rechecked after review. No source save/refill or
production transaction. Previous refused IPC diagnostic remains preserved and
was not retried. No native assertion occurred in the resumed isolated review.

[Machine checkpoint](phase4-15-owner-review-native/phase4-15-checkpoint.json),
[native check summary](phase4-15-owner-review-native/summary.json),
[pad preservation](phase4-15-owner-review-native/pad-preservation.json).

**STOP for owner correction/review.** No further native operations after the
BATTERY finding; no PASS/adoption plan yet. No F5/USB modification, rule waiver,
schematic/BOM/firmware work, fabrication, power-up, commit or push.
