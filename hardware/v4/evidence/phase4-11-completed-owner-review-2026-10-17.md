# Phase 4.11 — completed independent owner-scratch review

2026-10-17. **CONDITIONAL PASS.** Schematic topology, physical connectivity,
ERC/DRC/parity and bounded non-USB geometry checks pass. The USB layout has
unresolved ESD/reference-path concerns and a new USB power-path via; this is not
unconditional acceptance for production synchronization or release.

## Quick start / owner decision

Review the four USB items below before choosing a production migration scope.
The preferred next CAD milestone is a bounded USB layout improvement: put U2
near J7, favor routing over the close In1 reference, and review any necessary
layer transitions together with their return and connector-barrel asymmetry.
Alternatively, explicitly accept the documented prototype limitations. No
arbitrary skew limit, maximum ESD trace length or new qualification requirement
has been invented. No CAD improvement or migration was performed in this review.

The owner explicitly confirmed: **“Editory jsou uzavřené, soubory aktuální”.**
That resolves the earlier source STOP. All four saved source hashes still match
the previously captured files, no source locks remain, and fresh isolated checks
were completed after confirmation. The earlier
[source STOP report](phase4-11-owner-review-2026-10-17.md) is historical.

## Source and preservation

Reviewed source: `phase4-10-owner-editable-scratch/ups12v_v4.kicad_pro`.
Owner PCB SHA256:
`d05be24dd0f3cb857a806fb94fde87da811f1fb1ee3f2feda89d8278bac003de`.
Owner schematic SHA256:
`d05779687a5da4e663b2168cada5f29127822e14d276721b467298681e3de5b5`.

Accepted production remains **944 tracks / 283 vias / 154 footprints / 473 pads**,
PCB SHA256
`6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80`.
No accepted manifest was edited or replaced. The owner sources and all
manifest-bound production files remain unchanged at final verification.
The scratch project and custom rules are byte-identical to accepted production.

Fresh owner checks: [owner native evidence](phase4-11-owner-confirmed-native/summary.json).
Fresh exact-baseline control: [control evidence](phase4-11-accepted-control-native/summary.json).
Both used KiCad **10.0.7**, guarded isolated copies and monitored workers.
DRC refilled/saved only the isolated verification copies. Independent readback
proved all routed objects, pads and placements unchanged by that refill; owner
saved fill polygons exactly equal the freshly refilled polygons, including holes.
Native zone definitions and board drawings are unchanged between production and
owner scratch. Setup, stackup, models and unlisted properties have no changes in
the supplementary structural comparison.

[Source authority](phase4-11-source-confirmed/source-authority.json),
[artwork/fill preservation](phase4-11-source-confirmed/artwork-and-fill-preservation.json),
[final hashes/status](phase4-11-source-confirmed/final-review-status.json).

## Exact edit classification

| Objects | Accepted | Owner | Added | Deleted | Modified retained UUID |
|---|---:|---:|---:|---:|---:|
| Tracks | 944 | 1018 | 125 | 51 | 3 |
| Vias | 283 | 289 | 6 | 0 | 1 |
| Footprints | 154 | 154 | 0 | 0 | 3 |
| Pads, native geometry/net snapshot | 473 | 473 | 0 | 0 | 10 |

Moved footprints, mm, rotations unchanged: C28 `(120,87.4)`→`(114.074,77.978)`;
U2 `(113.8,78.5)`→`(110.744,91.44)`; R48 `(96,88)`→`(96,91.44)`.
The moved PGND via follows C28 to `(115.174,77.978)`, retaining 0.60/0.30 mm
copper/drill. Added vias: four USB data vias **1.00/0.50 mm** on every copper
layer, one USB_VBUS via **1.00/0.50 mm**, and U2 PGND **0.60/0.30 mm**.
All original physical pads/footprints outside the three moves are retained.
The PGND zone definition is unchanged; actual fill responds to the changed copper.

Track additions/deletions/modifications by net:

| Net | Added | Deleted | Modified |
|---|---:|---:|---:|
| USB_DP / USB_DN | 19 / 21 | 0 / 0 | 0 / 0 |
| /USB_MCU_DP / /USB_MCU_DN | 13 / 12 | 0 / 0 | 0 / 0 |
| PGND | 2 | 0 | 1 |
| SYS | 6 | 2 | 0 |
| MCU3V3 | 2 | 1 | 0 |
| USB_VBUS | 12 | 16 | 2 |
| USB3V3 | 20 | 19 | 0 |
| VIN1 | 6 | 5 | 0 |
| MAIN_3V3 | 4 | 3 | 0 |
| Net-(D1-A) | 4 | 3 | 0 |
| Net-(C26-Pad1) | 4 | 2 | 0 |

Additional representation changes are explicitly accounted for: two native
`diff_pair_skew` tuning groups; field-UUID refreshes on U2/R48/C33/R14; J1/J2/J3
footprint-filter metadata refresh; J2/J8 no-connect pad metadata and explicit
unit/pin metadata. C33/R14 field text, positions and other geometry are unchanged.
These metadata updates are not component substitutions or circuit changes.
Schematic symbols remain178, no-connect markers24 and physical components154;
labels32→34 and wires295→294. Two collinear wires at `x400.05,y474.98–480.06`
were merged without changing their union. Other schematic differences record
explicit editor/default presentation and cached pin properties; all component
values, exported properties and electrical partitions are unchanged.

[Exact routed diff](phase4-11-diff/owner-vs-reference.json),
[complete property diff](phase4-11-confirmed-comparison-v2/board-properties.json),
[schematic property diff](phase4-11-confirmed-comparison-v2/schematic-properties.json),
[schematic object inventory](phase4-11-source-confirmed/schematic-object-inventory.json).

## Schematic and physical connectivity verdict — PASS

The fresh full XML comparison covers **104 nets and 154 components**: every pin
partition and component property matches production. Only these names changed:

- `Net-(U1-USB_D+_{slash}_GPIO19)`→`/USB_MCU_DP`: R48.1 and U1.27.
- `Net-(U1-USB_D-_{slash}_GPIO18)`→`/USB_MCU_DN`: R49.1 and U1.26.

Connector-side USB_DP is J7.A6/B6, U2.1, R48.2; USB_DN is J7.A7/B7, U2.2,
R49.2. U2.3 is PGND. **Neither series resistor is bypassed** and polarity is
correct. R48/R49 remain default0R with optional22R, unchanged. Native
`BOARD.DpCoupledNet` recognizes both resistor-separated pairs in both directions.

Independent native pad-island traversal covers all **473 pads**:169→160 islands,
**zero previous islands split**. Exactly nine merges occur: USB_DP3, USB_DN3,
each MCU data net1, PGND1. Thus all accepted physical pad connections remain and
the eight USB data links plus U2 ground are closed. No new cross-net path or
copper short was reported. Unchanged circuit topology and retained isolation
components introduce no new designed USB-only back-power path; this is CAD
evidence, not a powered leakage/transient qualification.

[Electrical topology](phase4-11-confirmed-comparison-v2/electrical-topology.json),
[native connectivity](phase4-11-confirmed-comparison-v2/pad-connectivity.json),
[exact merges](phase4-11-source-confirmed/native-closed-connections.json).

## Fresh ERC / DRC / parity — PASS within unfinished routing scope

| Check | Owner | Exact production control in same scratch/library context |
|---|---:|---:|
| Physical DRC errors / parity | 0 / 0 | 0 / 0 |
| Unconnected | 44 | 53 |
| DRC warnings | 20 | 20 |
| ERC errors / warnings | 0 / 11 | 0 / 11 |

Warning identities (type, description, item UUIDs) match exactly. One warning's
coordinates follow the intentional U2 move; its full payload therefore differs.
The original production-context16 DRC /4 ERC warnings remain the accepted
baseline; extra library-context warnings in isolated copies are not new design
regressions. Inherited ignored checks are unchanged; no rule was waived/relaxed.

Remaining: **3 F0** (`I2C_SCL`, `~INT`, `STAT` at IC1), **41 F5**:
PGND12, SYS5, `/F5_RAW`10, `/F5_SW`2, `/F5_FB`2, `/F5_EN`2,
`/F5_5V_OUT`4, and one each `/F5_BST`, `/F5_VCAP`, `/F5_SS`, `/F5_GATE`.
Ratsnest representative endpoints change on three retained connections; native
islands prove no connection was lost. The older54-entry control had an extra
C12 PMID entry and is superseded by this exact53-entry control.

[Full checks delta](phase4-11-source-confirmed/checks-final-delta.json),
[remaining endpoints/groups](phase4-11-diff/checks-comparison.json).
The44 unfinished connections still prevent design release.

## USB path geometry and tuning

All data tracks are0.20mm. Connector D+ has30.369699mm F plus1.702082mm B;
connector D− has32.064040mm F. Both MCU branches have15.063371mm on B,
with5.310801mm D+ /5.455036mm D− on F and two1.00/0.50mm vias each.
Minimum copper-edge pair gap: connector F0.10mm, MCU F0.10mm, MCU B0.20mm.
These minima do not describe uniform coupling through bends/fanouts.

| Trace-centerline segment, barrels excluded | D+ mm | D− mm |
|---|---:|---:|
| J7 A contact to resistor connector pad | 30.369699 | 30.361959 |
| J7 B contact to resistor connector pad | 32.071780 | 32.064040 |
| Resistor MCU pad to U1 | 20.374171 | 20.518407 |

Both resistor-separated sections are included. Planar combined skew is D−
longer by0.136496mm, but **that hides the asymmetric B-contact PTH crossover**.
The saved nominal stackup has0.10/1.24/0.10mm dielectrics and35µm copper;
F/B copper centers are1.545mm apart. With all terminal endpoints explicitly
on F.Cu pad centers, two extra connector PTH traversals add3.09mm to the B-contact
D+ path. The nominal three-dimensional geometric estimates are:

| Path through resistor | D+ mm | D− mm | D+ minus D− mm |
|---|---:|---:|---:|
| A contacts, tracks + barrels | 53.833870 | 53.970366 | −0.136496 |
| B contacts, tracks + barrels | 58.625952 | 55.672447 | +2.953504 |
| A, also including1.02mm resistor pad-center span | 54.853870 | 54.990366 | −0.136496 |
| B, also including1.02mm resistor pad-center span | 59.645952 | 56.692447 | +2.953504 |

These are defined geometric reference-plane estimates, not measured electrical
flight lengths. Mating-contact/internal package geometry and actual resistor
conduction differ from that pad-center proxy. No approved skew limit was supplied;
the2.95mm asymmetry is a routing-quality observation, not an invented failure limit.

The two native tuning groups target USB_DN on F and /USB_MCU_DP on B. Both have
`last_status=too_short`, target_skew0, last gap0.18 and no custom-rule override.
They do not provide a combined resistor-spanning or full connector-barrel timing
guarantee. U2 data lands are on the main paths (degree2, no separate data spur).
The necessary duplicate-contact branches remain; no long dangling signal spur
was found. A0.096mm PGND leg inside U2's pad is harmless pad-internal copper.

All four nets are native `Default`: track0.50, pair width/gap0.20/0.20 and
via1.00/0.50mm are **routing defaults**. Enforced effective copper clearance is
0.10mm (above the board0.05mm floor); board via/drill minima are0.50/0.30mm,
annular minimum0.10mm. No explicit USB skew, impedance or differential-gap
constraint exists in the unchanged custom rules. Actual dimensions pass those
constraints; a0.10mm local gap does not meet the0.20mm recommendation but is not
an enforced-gap violation.

[Planar paths](phase4-11-resumed-analysis/USB-planar-paths-final.json),
[3D paths/assumptions](phase4-11-resumed-analysis/USB-3D-geometric-paths.json),
[nominal stackup](phase4-11-source-confirmed/nominal-stackup.json),
[effective rules](phase4-11-source-confirmed/usb-effective-rules.json).

## USB reference, ESD and coupling — conditions remain

**Q1 — ESD placement.** J7.A6→U2.1 is15.028089mm and A7→U2.2 is15.247562mm.
U2's PGND connection is now correctly connected:0.50mm tracks to a0.60/0.30mm
via, pad-center/via-center distance0.591mm. This short local return is good,
but it does not remove the long connector-side exposed data path. TI recommends
placing the protector near the connector to limit ESD coupling into protected
copper. Recommend revisiting U2 placement before accepting this USB layout.
This is manufacturer-backed risk assessment, not a measured ESD failure.

**Q2 — return/reference transitions.** The main MCU B routes each run15.063mm
above In2, which carries signals/power rather than a continuous ground plane.
The continuous PGND reference is farther away on In1. Actual In1 polygons/holes
and physical drills were sampled at≤0.05mm, center and both track edges:
USB_DP1823/1993, USB_DN1863/1996, MCU_DP1081/1271, MCU_DN1086/1276 stations
have copper. These are observations, not acceptance percentages. Connector gaps
are in the J7 PTH area; all MCU missing stations are within0.701mm of signal-via
centers, consistent with the large antipads. Actual fill is absent at both paired
via midpoints and nearby offset probes. Nearest ground-via centers at the four
MCU signal vias are2.105,2.595,2.711 and3.303mm away. Thus nearby ground exists,
but a close, controlled layer-transfer return has not been established. Prefer
F over close In1, or explicitly review a return strategy for necessary B transfers.
Projected copper on distant In1 alone does not qualify the B transmission line.

USB copper has at least7.70mm edge clearance to the native U1 RF keepout. The
module itself and RF restriction are unchanged. Exact internal physical crystal
position is not established by carrier exports; no crystal/RF immunity claim is
made for routing under the module. Nearest same-layer selected switching/high-
current copper is≥13.19mm away. Protected switching loops and their local PGND
occupancy are retained. No direct new coupling/short into these loops was found;
adjacent-layer effects still require the reference assessment above.

No90-ohm impedance calculation, EMI/ESD compliance, current-density, thermal or
powered USB/back-power measurement was performed or inferred.

[Return/clearance/drill evidence](phase4-11-resumed-analysis/engineering-detail-final.json),
[paired-via void probes](phase4-11-resumed-analysis/actual-plane-between-paired-vias.json),
[ESD on-path/void classification](phase4-11-resumed-analysis/ESD-and-void-classification.json).

## Other owner routes

Metrics below concern the changed/removed track subsets, not the total branched
net. Gaps include actual widths, per-layer via copper and native outside pad
polygons (≤100nm approximation). Joint owner geometry is used after changes.

| Changed net | Length before→after mm | Minimum width mm | Minimum copper gap before→after mm |
|---|---:|---:|---:|
| MAIN_3V3 | 11.298621→8.713036 | 0.60 | 0.423933→0.252817 |
| MCU3V3 | 1.453444→1.491421 | 0.50 | 0.162046→0.162046 |
| C26.1 net | 7.078992→6.644354 | 0.80 | 0.147590→0.601970 |
| D1.A net | 8.007669→7.338525 | 0.30 | 0.344637→0.561349 |
| PGND, C28 move + new U2 branch | 0.620000→1.171051 | 0.40 | 0.480000→0.121699 |
| SYS | 10.283852→10.560660 | 0.80 | 0.127145→0.127145 |
| USB3V3 | 50.188156→51.533171 | 0.30 | 0.125000→0.150000 |
| USB_VBUS | 23.917627→26.027133 | 0.30 | 0.110000→0.175000 |
| VIN1 | 16.488206→16.888348 | 0.30 | 0.150000→0.424387 |

No new width reduction was found. Conservative strip-minus-drill minima remain
MCU3V3 0.20mm, SYS0.40mm, C26 0.80mm, D1.A/USB3V3/VIN1 0.30mm;
MAIN_3V3 improves0.347257→0.362132mm. These exclude helpful pad/parallel copper,
barrel conduction and current spreading. Zero strip width at a USB_VBUS PTH
endpoint occurs before and after and does not mean the complete pad/via copper
is open. Existing separate SYS0.70mm legacy bottleneck remains an unchanged item.

**Q3 — new USB_VBUS series via.** At `(109.22,80.518)` the main0.60mm supply
route changes F↔B through1.00/0.50mm copper/drill. Its two0.25mm annular sides
sum to0.50mm planar metal through the drill center, rather than a solid0.60mm
strip. Barrel plating and both faces carry current; neither a guaranteed ampacity
loss nor unchanged current margin follows from DRC. Explicitly include this
changed power path in prototype acceptance; retain a simpler path if practical.
No new via was added to SYS/VIN1/MAIN_3V3/MCU3V3/USB3V3/D1.A/C26.

SYS's changed branch length increases2.69%; USB3V3 aggregate changed length also
increases. These are small geometric penalties, not demonstrated thermal failures.
MAIN_3V3, D1.A and C26 routes shorten. Do not reject UUID refreshes or bends alone.

SW1/SW2, BTST1/BTST2, REGN, BATP, /SW_NORMAL, /BST_NORMAL, /MAIN_FB and
/NORMAL_SS routed objects/vias are exact before/after matches. IC1/L1/U3 placement
and pads remain unchanged. Actual In1 occupancy matches on0.10mm grids around
IC1(10101 samples), L1(11011), U3(18471), including native voids. This finite
sampling is not a continuous field solution. Changed-copper gaps to remaining
IC1 pads are no smaller in the closest case (SYS0.379243→0.382mm); no new escape
obstruction is demonstrated. Changed non-USB copper remains≥16.185mm from F5
node copper; no F5 routing or IC1 rework was performed.

The owner C26/SYS routes are review candidates, not installation of the historical
approved-for-study plans. R35v2, R12–C26v3 and SYS cleanup proposals remain
separately preserved and **uninstalled in production**.

## Bounded synchronization proposal — separate authorization required

1. Resolve/accept Q1/Q2/Q3 and choose an exact item/net whitelist. Do not migrate
   incidental power/legacy geometry merely because it is present in the scratch.
   Check dependencies: excluding a changed route can invalidate USB clearance.
2. Reconcile exact production/editor identity and accepted hashes. Prepare a
   native isolated candidate from production with explicit added/deleted/modified
   track/via UUIDs, three selected placement changes, two schematic label additions
   and exact net/pad mapping. The harmless wire merge/metadata refresh need not
   become uncontrolled production changes.
3. Use supported Konnect/coordinated native editor operations for the selected
   delta. Existing add-only installation is insufficient for deletions, moves and
   net renames; a separately reviewed bounded transaction is needed. Preserve
   prior object payloads for rollback. Never overwrite production with the whole
   scratch file or hide owner changes by editing a manifest hash.
4. Before accepting a new baseline, independently repeat native save/reload,
   ERC/DRC/parity, full source/property and connectivity comparison, actual fill/
   return/ESD/current-path review, and saved/live reconciliation. Only then issue
   a new accepted manifest. No migration is authorized/performed in Phase4.11.

## Verification notes and primary basis

**78 toolkit tests PASS**, including negative hidden-resistor-bypass, pad-island
split/missing coverage, disjoint collinear distances, actual-plane holes and
connector PTH barrel contribution. All native assertions/IPC failures: **none**.
A supplemental native inspection encountered an ordinary opaque SWIG-pointer
AttributeError; supported `GetNetClassName()` replaced that getter and diagnostics
were retained. This was not an assertion/recovery event. Initial analytic
clearance artifacts falsely intersected disjoint collinear segments; the shared
geometry fix is regression-tested. The authoritative analysis is
[corrected final screen](phase4-11-resumed-analysis/phase411-exported-analysis-final.json)
and `engineering-detail-final.json`; earlier initial/fresh screens are superseded.

Manufacturer basis verified2026-10-17:
[TI TPDxEUSB30/A SLVSAC2G, Rev.G June2021, §5/§10.1–10.2](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf)
supports the DRT pin mapping and connector-proximity ESD assessment.
[Espressif MINI-1/MINI-1U v2.2, May2026, §3.2/§5.2.1.5/§11.2](https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.pdf)
supports pin assignment, USB full-speed12Mbit/s and module-placement context.
These are manufacturer guidance plus exported geometry/calculations; no hardware
measurements were made. No production change, original refill/save, fabrication,
purchasing, power-up, firmware work, commit or push occurred.
