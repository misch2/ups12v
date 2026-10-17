# Phase 4.11 — owner scratch review: STOP, source authority unproven

**Historical checkpoint, superseded:** owner confirmed closed editors and current
saved files. See the [completed Phase4.11 review](phase4-11-completed-owner-review-2026-10-17.md)
for the current CONDITIONAL PASS and remaining USB engineering concerns.

2026-10-17. **STOP / incomplete review. No production adoption is authorized.**

## Quick start to resume

Save the scratch PCB and schematic through their owning KiCad editors, or
confirm both editors are closed and the saved files are authoritative. Target:
`hardware/v4/evidence/phase4-10-owner-editable-scratch/ups12v_v4.kicad_pro`.
If unsaved changes exist, preserve and save them through KiCad; do not replace
files externally. Resume with source reconciliation and a fresh isolated review
copy. Do not reuse the native validation directories below.

## Source gate and limits

The exact live PCB path and unsaved PCB/schematic state were not established.
The initial Git status showed PCB/project lock files. A later process/lock query
returned no entries and CIM inspection was denied; that does not prove the editors
were closed or the saved sources were current. See
[source reconciliation](phase4-11-diff/source-reconciliation.json).

Native saved-copy checks were performed before this required gate was fully
proved. This was a sequencing error. Their results are retained as **provisional
saved-file evidence only**, not completion of the requested live-source review.
No further native CAD operation was performed after recognizing the source STOP.
There was no native assertion or IPC failure. The first isolated worker attempt
failed argument validation before CAD loading because the new action had not yet
been registered; its diagnostics are preserved, and a fresh directory was used.

Owner PCB SHA256:
`d05be24dd0f3cb857a806fb94fde87da811f1fb1ee3f2feda89d8278bac003de`.
Owner schematic SHA256:
`d05779687a5da4e663b2168cada5f29127822e14d276721b467298681e3de5b5`.
The final filesystem check confirms all four captured owner CAD/project/rule
hashes and all three production files bound by the accepted manifest are unchanged:
[preservation](phase4-11-diff/final-preservation.json).
Production remains Phase 4.10 PCB SHA256
`6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80`.

## Provisional owner-edit inventory

The exported native UUID comparison is complete at its captured snapshot level;
it is not a complete electrical or serialized-property preservation review.

| Objects | Accepted production | Saved owner | Added | Deleted | Modified existing |
|---|---:|---:|---:|---:|---:|
| Tracks | 944 | 1018 | 125 | 51 | 3 |
| Vias | 283 | 289 | 6 | 0 | 1 |
| Footprints | 154 | 154 | 0 | 0 | 3 |
| Pads | 473 | 473 | 0 | 0 | 10 |

Placement changes (mm; unchanged rotations): C28 `(120,87.4)` to
`(114.074,77.978)`; U2 `(113.8,78.5)` to `(110.744,91.44)`;
R48 `(96,88)` to `(96,91.44)`. R49 and U1 USB pad positions are unchanged.
The In1 PGND zone retains its UUID/net/layer but its exported fill geometry differs.
Full rule/stackup/zone-definition and schematic-property preservation is pending.

Changes outside the four USB data nets include PGND, SYS, MCU3V3, USB_VBUS,
USB3V3, VIN1, MAIN_3V3, `Net-(D1-A)` and `Net-(C26-Pad1)`.
These are review candidates; UUID replacement or routing angle alone is not a
defect. Their current capacity, drill constrictions, clearances, return paths,
protected switching/feedback loops and impact on remaining escape/F5 space have
**not been accepted**. In particular, do not assume the deferred R12–C26v3 plan
was installed merely because this owner edit changes copper on that net.

Exact objects/geometry and placement classification:
[native diff](phase4-11-diff/owner-vs-reference.json),
[classification](phase4-11-diff/owner-modification-classification.json).

## Provisional schematic USB verdict

The fresh saved-schematic netlist preserves both resistor partitions:

- `USB_DP`: J7.A6/B6, U2.1 and R48.2; `/USB_MCU_DP`: R48.1 and U1.27.
- `USB_DN`: J7.A7/B7, U2.2 and R49.2; `/USB_MCU_DN`: R49.1 and U1.26.

Thus neither resistor is bypassed by a same-name schematic net, and polarity is
correct at the inspected endpoints. This is a saved-netlist result, independent
of an ERC pass. Whole-schematic topology/property equivalence and actual native
pair recognition for the renamed nets remain pending; suffix naming alone is
not evidence that the native router recognized the pair.

[Exported partitions and verdict](phase4-11-usb-netlist/partitions.json),
[full exported netlist](phase4-11-usb-netlist/owner-scratch.xml).

## Provisional ERC/DRC/parity

The fresh isolated saved-copy run reported DRC **44 unconnected / 0 physical
errors / 0 parity / 20 warnings**, ERC **0 errors / 11 warnings**.
Remaining connections: **3 F0** (`I2C_SCL`, `~INT`, `STAT` at IC1) and
**41 deferred F5**. No USB/U2 ground disconnection remains in that run.

Warning multisets equal the historical scratch control, whose library context
also has 20 DRC and 11 ERC warnings; do not describe the additional scratch
library warnings as production regressions. Production's accepted result remains
53 unconnected / 16 DRC warnings and 4 ERC warnings.
The historical scratch control has 54 open pairs, including a C12 PMID pair
absent from the accepted 53-entry production checkpoint. Its ten control-only
pairs therefore do **not** establish ten owner closures relative to production;
the accepted count difference is nine. Exact endpoint reconciliation against
the accepted production report must accompany resumed validation.

[Fresh check summaries](phase4-11-owner-review-native-2/summary.json),
[warning/remaining groups](phase4-11-diff/checks-comparison.json),
[historical control delta](phase4-11-diff/checks-control-delta.json).
DRC refilled/saved only its isolated verification copy, never owner originals.

## Provisional USB geometry

Lengths below sum routed trace centerlines. They exclude resistor package
traversal, internal pin/package lengths and vertical via/PTH barrel traversal;
they are not measured complete electrical flight lengths.

| Segment | D+ mm | D− mm |
|---|---:|---:|
| J7 A contact to resistor connector pad | 30.369699 | 30.361959 |
| J7 B contact to resistor connector pad | 32.071780 | 32.064040 |
| Resistor MCU pad to U1 USB pin | 20.374171 | 20.518407 |
| Sum through A contact, excluding resistor/barrels | 50.743870 | 50.880366 |
| Sum through B contact, excluding resistor/barrels | 52.445952 | 52.582447 |

Connector-side skew is D+ longer by 0.007740 mm; MCU-side skew is D− longer
by 0.144235 mm; combined trace-only skew is D− longer by 0.136496 mm.
All four data-net track inventories use 0.20 mm width. MCU sections each have
two signal vias and F/B routing. Connector D+ duplicate-contact path uses F/B
through the connector PTH contacts; the D− inventory uses F.Cu. Minimum reported
connector-pair edge gap is 0.10 mm. This local minimum does not characterize
coupling over the whole path or establish effective configured constraints.

[Exact trace-path evidence](phase4-11-diff/usb-geometry.json).
Pair tuning across resistor-separated sections, stubs, enforced versus suggested
rules, per-layer drills/widths, actual filled In1 return continuity, reference
transitions, ground-via proximity, U2 ESD placement/ground-loop quality, RF/module
clearance, switching coupling and USB power-domain isolation remain **pending**.
The U2 relocation specifically needs a fresh connector-to-ESD routing assessment.
No 90-ohm impedance, EMI, ESD, thermal or hardware compliance is established.

## Decision and next authorized boundary

**STOP**, because source authority is unproven and the engineering review is
incomplete. No production migration proposal is accepted. After source
coordination, finish the pending checks above using fresh isolated copies. If
acceptable, prepare exact schematic and PCB change mappings, distinguish each
placement/copper/net change, and propose a separately authorized guarded editor
installation with complete post-installation verification. A wholesale scratch
overwrite is excluded.

Toolkit support for isolated owner review was added without changing the CAD
originals; **64 focused regression tests pass**. Full geometry, safety and report
helpers remain under `hardware/v4/tools/`. Importing tooling does not load CAD.
No production promotion, automatic repair, original refill/save, rule waiver,
IC1 rework, F5 routing, fabrication, purchase, power-up, firmware, commit or push.
R35v2, R12–C26v3 and SYS cleanup plans remain deferred.
