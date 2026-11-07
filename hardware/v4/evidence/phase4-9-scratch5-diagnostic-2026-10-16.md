# Phase4.9 scratch5 — bounded diagnostic complete; STOP

2026-10-16. Owner authorized one investigation and one monitored read-only native
export of the failed saved scratch5 board. This does not resume Phase4.9 routing.

## Exact finding

**The failure is three via net mismatches, not dimensional rounding, duplicate
removal or a faulty equality tolerance.** All 85 declared tracks and all 23 vias
are present. Track endpoints/layers/widths and via positions/drills/copper sizes
match exactly, including integer nanometres. No physical object is missing or
extra. Two duplicated track geometries in the plan are also duplicated in the
native export; they remain a separate routing-quality defect.

First discrepancy **in immutable plan order**: via index13 (the14th via), UUID
`3b82fb3a-9ac3-4736-90a4-730081fd0fb2`, at `(98.5,88.8)` mm. Expected `PGND`,
actual `USB_DP`. The original failing dictionary equality did not capture an
ordered first-error trace; this is the first discrepancy reconstructed from the
plan order, not a claim about dictionary-comparison internals.

| Via plan index (zero based) | Position mm | Expected net | Reloaded native net | Actual UUID |
|---|---|---|---|---|
|13|98.5,88.8|PGND|USB_DP|3b82fb3a-9ac3-4736-90a4-730081fd0fb2|
|14|97.1,90.0|PGND|USB_DN|569746cd-c176-40b8-b08e-65b9a79e2f36|
|15|94.3,90.6|PGND|Net-(U1-USB_D-_{slash}_GPIO18)|87570e37-768a-4390-bfc8-09c6080102bf|

All three are ordinary native `PCB_VIA` objects, type4/THROUGH, F.Cu→B.Cu,
padstack mode0, diameter0.500000mm on each of four copper layers and drill
0.300000mm. Raw coordinates are respectively `[98500000,88800000]`,
`[97100000,90000000]`, `[94300000,90600000]` nm. All per-layer copper sizes are
`[500000,500000]` nm with circular shape0; native drill-shape enum is1.
Neither layer span nor annular-ring settings explain the mismatch.

## Demonstrated root cause and stage qualification

**Plan-generation defect:** `f0_plan.build('usb')` appended fixed PGND return-via
coordinates without screening them against the paired trunks/fanouts already
declared in the same plan. These three PGND copper disks intersect different-net
signal tracks in the immutable plan:

| Via index | Conflicting planned track | Layer | Centreline distance mm | Copper edge gap mm |
|---|---|---|---:|---:|
|13|USB_DP, `(107.7,88.7)→(97.2,88.7)`|B.Cu|0.100000|−0.240000|
|14|USB_DN, `(97.49,90)→(96.51,90)`|F.Cu|0.000000|−0.340000|
|15|MCU USB_D−, `(95.4,90.4)→(75.3,90.4)`|B.Cu|0.200000|−0.140000|

Negative edge gap means actual copper overlap in the **declared geometry**,
not merely a near-clearance issue. This calculation uses the exact native-
confirmed planned endpoints,0.18mm track width and0.50mm via diameter. It is
exported geometric evidence, not a fresh native DRC or a hardware measurement.

The unchanged creation code explicitly looks up each declared net, sets that
net code on the via and records the expected PGND geometry. The failed run then
called native `SaveBoard`, reloaded and performed exact comparison. KiCad10.0.7
source gives a concrete compatible mechanism:

- [SaveBoard/LoadBoard helpers](https://gitlab.com/kicad/code/kicad/-/blob/10.0.7/pcbnew/python/scripting/pcbnew_scripting_helpers.cpp):
  SaveBoard rebuilds connectivity before serialization; LoadBoard also rebuilds it.
- [Connectivity build](https://gitlab.com/kicad/code/kicad/-/blob/10.0.7/pcbnew/connectivity/connectivity_data.cpp):
  rebuilding reaches net propagation through ratsnest recalculation.
- [Propagation](https://gitlab.com/kicad/code/kicad/-/blob/10.0.7/pcbnew/connectivity/connectivity_algo.cpp):
  changeable objects acquire the connected cluster's originating net.
- [Via constructor](https://gitlab.com/kicad/code/kicad/-/blob/10.0.7/pcbnew/pcb_track.cpp):
  newly constructed vias default to `m_isFree=false`; the project creation code
  does not override that state.

**Conclusion:** the observed net reassignment corresponds exactly to the three
different-net overlaps in the generated plan. Connectivity propagation during
the native save/reload path is strongly supported by the version-matched source;
the equality guard correctly rejected it. It is not safe to accept the changed
nets as benign normalization, force a free/fixed-net flag, or add tolerances.

**Evidence limit:** the original scratch5 run did not retain before-save,
after-save or after-reload addition captures. One allowed read-only export cannot
experimentally distinguish the very first reassignment during SaveBoard from
LoadBoard, or independently observe the original in-memory creation state.
The exact differing fields and the unsafe plan geometry are established; the
substage timing is source-supported analysis, not a replay measurement.

## Paths, hashes and single-export accounting

Failed source:
`hardware/v4/evidence/phase4-9-usb-scratch5/ups12v_v4.kicad_pcb`

SHA256 `5d9bd5b41137aafbb3adb2637ac45d044c1b270900c8a6a7ebf62b7797c8e34a`.
It resolves separately from production, is not the same file/hard link, and had
no detected board lock. Its hash and all sidecar hashes were bound before export.

Immutable plan v5:
SHA256 `d8ce75bdb4fef153d48e843be9685c421713e64dce7ff35f12c1a39f95a1aacd`.
The source plan and failed-run copied plan match exactly and were not edited.

Exactly **one** canonical monitored native snapshot worker ran, with
`--route-diagnostics`, KiCad10.0.7. It loaded a fresh byte-identical isolated
copy in `phase4-9-scratch5-diagnostic-native`, exported and exited. No native
save, refill, routing/creation, IPC or editor action was invoked. No assertion,
unexpected IPC failure, retry or recovery occurred. Source scratch, native
byte-copy and production hashes were checked unchanged afterward.

Key evidence, all under `hardware/v4/evidence/`:

- [Preflight/source identity and captured creation source](phase4-9-scratch5-diagnostic/preflight.json).
- [Bound saved-scratch manifest](phase4-9-scratch5-diagnostic/source-manifest.json).
- [Expected inventory, persisted before native export](phase4-9-scratch5-diagnostic/expected-inventory.json).
- [Actual addition inventory, persisted before comparison](phase4-9-scratch5-diagnostic/actual-inventory.json).
- [Complete raw native routed inventory/padstacks](phase4-9-scratch5-diagnostic-native/routed-diagnostics.json).
- [Native snapshot](phase4-9-scratch5-diagnostic-native/snapshot.json) and
  [sole monitored native worker log](phase4-9-scratch5-diagnostic-native/snapshot.log).
- [Exact changed fields, UUIDs, duplicates and overlap calculations](phase4-9-scratch5-diagnostic/object-level-diagnostics.json).
- [Original snapshot preservation](phase4-9-scratch5-diagnostic/original-preservation.json)
  and [raw-unit/padstack/hash checks](phase4-9-scratch5-diagnostic/raw-geometry-and-hash-checks.json).

The independent saved/native inventory is689tracks/202vias; relative to the
accepted production snapshot that is85tracks/23vias. Original track/via/pad/
footprint geometry is preserved in that comparison. **This failed scratch is
not an accepted candidate or a production baseline.**

Production remains SHA256
`ded2ac1999b672157409b0b6f2bbc636beac4fd54382c8b9548346a0fbcab675`,604tracks/
179vias/154footprints/473pads. All accepted production source hashes were
rechecked, including the source rules hash retained in scratch5's original
context. No post-diagnostic DRC/ERC or second native operation was performed.

## Tooling review: tests versus native coverage

The prior30tests were rerun and passed before export. Their scope covers exact
added-object mismatch logging, mixed track/via getters, same-net physical-hole
avoidance, explicit reservations, path/hash/lock guards, report parsing, import
safety and simulated worker failure detection. They do **not** demonstrate
successful native creation/save/reload or an electrically good route.

For this diagnostic only, the canonical snapshot command gained optional raw-
unit/padstack export; stable ordinary snapshots and equality semantics are
unchanged. A fake-native getter regression brought the pre-export suite to31.
That read-only snapshot diagnostic path was then actually executed once. A pure
export comparator now reproduces the exact net mismatch, retains multiplicity
of duplicate tracks and computes declared via/track overlaps. Two additional
tests and expanded import-safety coverage pass: **33tests total**.

The prior native improvement that records expected/created/reloaded additions
and checks equality before scratch save has **not** been exercised in a native
mutation workflow. Its pre-save inventory check alone does not prove geometric
clearance or prevent net propagation; the post-reload gate remains essential.
No verification guard was disabled or broadened.

## Proposed minimal correction — not implemented

1. In a separately authorized **new** candidate, remove or legally reposition
   only these three invalid PGND return-via declarations, preserving the needed
   return function. Do not replay or edit scratch5. New coordinates require
   actual all-layer clearance, drill and filled-PGND-reference validation; none
   are proposed as DRC-qualified here.
2. Screen **all declared additions jointly**, including manually specified
   trunks and stitching, before native application. Later A* obstacles do not
   retrospectively validate an earlier manually added trunk against a new via.
3. Retain exact net/geometry equality through creation/save/reload. A future
   authorized worker can additionally capture the state immediately after
   SaveBoard and before LoadBoard to locate any normalization stage precisely.
   Do not fix this by pinning a colliding via's net or relaxing comparisons.

No correction to the routing producer or candidate was made during this scope.

## Proposed USB routing-quality strategy — not implemented

- Plan connector branches, ESD entry, paired trunks, resistor fanouts, layer
  transitions and return stitching together. Give both polarities compatible
  corridors; do not route one polarity into a barrier for the other.
- Preserve one exact pad/via endpoint representation. Remove genuinely duplicate
  same-net/same-layer segments before application and avoid grid-rounding hooks.
  Flag sub0.2mm legs for review; do not blindly delete a short leg needed to reach
  an exact pad endpoint or invent a new project-wide minimum-length requirement.
- Prefer clean0/45/90-degree paths with few meaningful bends. Inspect acute
  junctions as actual copper/pad geometry, not merely centreline angle counts.
  Reuse existing same-batch branch access and justify each layer transition.
- Reconsider the13.899mm USB_DN duplicated-contact detour and all connector
  stubs against the accepted VBUS barrier. No search so far proves this is
  unavoidable. If acceptable routing needs accepted-copper movement, present
  the smallest separate owner proposal; do not force or silently reroute it.
- Report actual endpoint-to-endpoint lengths for **both USB orientations** and
  each series-resistor-separated leg, not aggregate branched copper. Scratch3's
  ESD-to-MCU trace sums were DP48.136mm/DN49.436mm (1.300mm skew), but that excludes
  the unequal connector branch paths and does not qualify USB signal integrity.
- Check ground return using actual filled-plane/drill geometry at every layer
  transition. B.Cu has In2 between it and In1 PGND; do not assume an adjacent
  continuous reference or90-ohm impedance without the real stackup. Return vias
  must be clear of **every** signal layer, as this failure demonstrates.
- Preserve the antenna rule area and examine the module manufacturer's internal
  crystal/RF placement before routing beneath the module body. Antenna-keepout
  avoidance alone does not qualify sensitive-region exposure.
- KiCad10's [interactive router](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#routing-tracks)
  offers Walk Around, differential routing and skew tuning. A coordinated
  owner-assisted scratch GUI workflow is practical for sensitive USB; it is
  **not yet a demonstrated unattended replacement** for the current custom A*.
  Installed Konnect tools expose direct segments/L-bends/parallel-pair segments;
  no supported structured PNS route-preview/completion controller was established.
  SDK `run_action` alone does not provide safe obstacle-aware path control.
- After separate authorization, compare that supported scratch workflow with
  custom output, keeping accepted copper fixed and verifying the additive native
  diff. Walk Around is preferable to Shove under add-only preservation, but its
  cleanup/optimization effects must still be checked. Keep canonical live
  installation, independent readback, ERC/DRC/parity and preservation gates.

No backend switch, interactive routing, new candidate or Freerouting work was
performed. **STOP for separate authorization before any new candidate.** No
production CAD writes, firmware, commit/push, fabrication, purchases or power-up.
