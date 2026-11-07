# Legacy routing geometry review — scratch proposals; STOP

2026-10-17. The owner accepted Phase4.9 and authorized read-only assessment and
isolated scratch proposals only. Production remains **901 tracks /265 vias /
154 footprints /473 pads**, SHA256
`a3ba56068026a6942c4ca22d7e0eee8f5f2320afc4defefabbbcee3861b29a78`.

## Quick start for owner review

1. Review the three ranked candidates below and their focused illustrations.
2. Use the linked comparison JSON for every original/proposed UUID, coordinate,
   layer, width, nearest object and clearance location. These are actual native
   scratch objects, not merely planned geometry.
3. Authorize a separately bounded production milestone only for specifically
   selected candidates. **No production replacement is authorized or performed.**

| Rank | Proposed scope | Measured change | Decision |
|---|---|---|---|
| 1 | R35 USB3V3 bleeder, v2; A branch within B supply region | 7→3 objects; copper-edge gap 0.158210→0.264178mm; no change to U4/C40 supply or ground | Recommended for separate owner review |
| 2 | R12–C26 snubber, v3; C protected input region | 7.078992→6.644354mm; gap to C22.1 PMID 0.147590→0.259377mm; width stays0.8mm | Recommended for separate owner review, with the input-transient qualification limitation below |
| 3 | SYS north horizontal trunk; C power region | 3→1 collinear objects; exactly the same physical copper union, 8.25mm/1.2mm | Recommended as a representation-only cleanup |
| — | SYS southeast oblique section, 45° study | 10.191322→10.493503mm; strip resistance scenario +2.965% | **Reject; keep original** |

All three selected candidates also pass a **combined** joint copper/hole/
reservation/edge check against the accepted baseline with exactly12 originals
excluded and7 new tracks included. A hypothetical combined board would have
896 tracks/265 vias. It was not installed. Each native scratch separately starts
from the exact accepted901/265 baseline.

## Read-only assessment of accepted copper

[Complete per-net audit, flagged objects and UUIDs](legacy-geometry-proposals-2026-10-17/audit.json)
covers all901 ordinary tracks and265 vias. Strict integer-nanometre angle screening
flags235 non-0/45/90° segments,118 segments shorter than0.2mm, and13 repeated
same-net/layer centerline groups, including different-width/reversed overlaps.
These are quality flags, **not235 electrical defects**. Exact pad endpoints,
short bypasses, current spreading and branching often justify irregular geometry.
Overlapping tracks do not create a second copper thickness or double ampacity.

| Class | Regions and observed flags | Disposition |
|---|---|---|
| A | R35 10k bleeder branch: seven objects including a0.02mm return over an existing wider C40 stub, a0.01mm pad-internal return and several bends. Low-speed CHG/UART/status routing is inventoried too. | Use only the bounded R35 proposal; no wholesale signal reroute. |
| B | USB3V3 supply:26 tracks/16 angle flags/10 microlegs. PROG:23/16/12 with2 vias. CE_BIAS:25/14/9; CE_N:20/10/5; TS:17/7/4 with2 vias; ILIM_HIZ:3/2/1. REGN:45/32/17 with2 vias. | No automatic straightening. Separate a resistor branch from bypass/current paths. Local REGN bypass portions are protected under C despite the broader net's B audit label. Preserve accepted PROG, control defaults, analog sense and decoupling. |
| C | SYS:54 tracks/20 angle flags/8 microlegs/7 vias; VIN1:23/3/0/8. R12/C26 input damping, PMID/VBUS/BATTERY/BATP, SW1/SW2/BTST, IC1/L1 loops, U3 switching/feedback, PGND/domain isolation. | Keep switching/commutation, sense and high-current paths. SYS's0.2mm **net-wide** minimum is a small branch, not evidence that the power trunk is0.2mm. Only the exact collinear SYS merge changes the selected power representation. |

Repeated centerlines occur on PGND, MCU3V3, USB_VBUS, USB3V3, VBUS, BATP,
BATTERY, MAIN_3V3 and MUX_PR1; all identities remain in the audit. They are not
blanket removal authority. Similarly, via count alone does not establish an
unnecessary layer transition: high-current parallel vias and protected SW paths
remain unchanged. No demonstrably unnecessary power-layer change was proposed.

## 1. R35 bleeder v2

[Before/after illustration](legacy-geometry-proposals-2026-10-17/r35-v2-comparison.png),
[exact objects and electrical/geometric comparison](legacy-geometry-proposals-2026-10-17/r35-v2-comparison.json),
[explicit replacement plan](legacy-geometry-proposals-2026-10-17/r35-v2-plan.json),
[native validation](legacy-geometry-r35-v2-scratch-2026-10-17/summary.json).

Only the0.3mm USB3V3 bleeder branch is replaced, by a vertical escape from
C40.1 `(109.52,88)` to `(109.52,88.7)`, a45° leg to `(110.32,89.5)` and a
horizontal leg to R35.1 `(111.99,89.5)`. The redundant0.3mm return over the wider
0.5mm C40 pad stub is removed; that wider original stub remains. New objects are
ordinary F.Cu tracks. No vias are created, moved, resized, renetted or removed.

Length increases3.297027→3.501371mm, while bends/objects reduce and the narrowest
selected-track copper-edge gap improves by0.105967mm. The nearest object is
PGND via `7fa9f184-60fc-4cec-81ee-693436003014`; the new facing edge points are
approximately `(110.081066,89.048934)` and `(110.267868,88.862132)`.
Minimum drill-subtracted strip width remains0.3mm, without a drill crossing.
The nearest drill-edge gap improves0.308210→0.414178mm.

At the explicitly assumed35µm copper/20°C, the simple selected-strip resistance
scenario is5.413404→5.748917mΩ. The0.335514mΩ increase is about3.36e-8 of the
retained10kΩ bleeder; at nominal3.3V/10kΩ it adds approximately0.111µV of drop
and0.037nW of dissipation. It does not carry the MCU service load. This is a
calculation, not a measured current or thermal rating. Sampled local USB3V3 union
area changes9.7632→9.8372mm² in the fixed review box, with0.02mm raster cells.

All original U4–C40 supply objects, C35/bulk-cap paths, PGND tracks/vias/pads and
positions are exact-preserved. Thus the LDO/high-frequency bypass forward and
return geometry is retained; the additional length belongs to the bleeder only.
Actual In1 fill contours, drill geometry,0.1mm plane grid and via contact probes
are identical. Selected-path center/edge reference probes find PGND at225/225
original and220/220 proposed points. Sensitive switching/sense copper remains
over31.6mm away. This supports electrical neutrality of this low-current cleanup;
it is not a new LDO stability or USB-load qualification.

The first R35 scratch also passed native checks, but reduced clearance to0.122756mm.
It is rejected in favor of v2; it must not be installed.

## 2. R12–C26 v3, near C22 PMID

[Before/after illustration](legacy-geometry-proposals-2026-10-17/c26-v3-comparison.png),
[exact objects and comparison](legacy-geometry-proposals-2026-10-17/c26-v3-comparison.json),
[explicit replacement plan](legacy-geometry-proposals-2026-10-17/c26-v3-plan.json),
[native validation](legacy-geometry-c26-v3-scratch-2026-10-17/summary.json).

**Net correction:** C26.1 and R12.2 are `Net-(C26-Pad1)`, downstream of R12.
R12.1 is VIN1. The proposal preserves the approved2Ω/2.2µF input snubber; it
does not directly join C26 to VIN1 or PMID. Both original0.8mm F.Cu objects are
explicitly replaced. The new path is R12.2 `(42.4625,49)`→`(42.1625,49)`
inside the same pad→`(38.1625,53)` at45°→C26.1 `(37.475,53)`.

Length decreases0.434638mm (6.14%), with0.8mm width throughout, no new neckdown,
no changed vias and no physical-drill penetration. The initial0.3mm horizontal
leg lies inside R12's original native pad polygon. The nearest other copper
remains C22.1 PMID, UUID `a57f5d1a-b921-4d39-80b8-1225701ff0e9`.
Its minimum gap improves0.147590→0.259377mm, facing approximately
`(39.311593,52.416593)` and `(39.495,52.6)`. Pad-edge distances are conservative
native ERROR_OUTSIDE polygons with an at-most0.0001mm approximation bound;
track/via capsule distances are analytic actual copper edges, not rule values.

The35µm/20°C strip-resistance scenario improves4.358637→4.091024mΩ, a
0.267613mΩ decrease, approximately0.0134% of the2Ω damping resistor. Local
sampled net copper union changes9.3620→9.2900mm² as the path shortens; there is
no width/drill bottleneck. R12/C26 pad geometry, PGND returns, C22, VIN1 feeds,
input FET/sense and all neighboring power routes are preserved. There is no
modified IC1 commutation or bypass object. All In1 fill/antipad contours and drill
geometry remain exact-equal; all431 original/409 proposed center-and-edge path
samples are over PGND. The path is shorter over the same plane and farther from
PMID; nearest enumerated switching/sense-node distance also increases slightly.
These are favorable geometry/resistance/reference proxies, not extracted
inductance, EMI simulation or hot-plug measurements.

The pre-existing matching-hardware input-transient qualification remains open.
Do not infer a guaranteed VAC1 peak, snubber pulse margin or ampacity from these
CAD calculations. If the owner requires measured snubber equivalence before
authorizing any input-copper change, retain the original until that separate
qualified fixture comparison is available; no power-up is authorized here.

The first legal C26 candidate lengthened the affected branch and is superseded.
A shorter two-leg45° candidate was rejected **offline before native mutation**:
only0.047245mm clearance to C22.1. The retained v3 includes the pad-internal
escape that removes that collision without narrowing copper or relaxing rules.

## 3. SYS exact merge; oblique alternative rejected

[Before/after exact merge](legacy-geometry-proposals-2026-10-17/sys-comparison.png),
[exact objects and comparison](legacy-geometry-proposals-2026-10-17/sys-comparison.json),
[replacement plan](legacy-geometry-proposals-2026-10-17/sys-plan.json),
[native validation](legacy-geometry-sys-scratch-2026-10-17/summary.json).

Three contiguous1.2mm F.Cu sections at y60.95, spanning x67.95→70.1→72.8→76.2,
become one1.2mm segment x67.95→76.2. Same endcaps, physical union and all pad/
branch contacts remain. Length is8.25mm; minimum gap to REGN track
`c4fb45c7-4773-4b76-a205-026b1b562fbb` remains0.282749mm. The nominal no-hole
strip scenario remains3.386429mΩ; local native-export sampled copper union
remains20.4788mm². Since physical geometry is identical, current spreading,
parallel routes, voltage drop, thermal area and magnetic geometry are preserved
independently of that simplified resistance model.

**Drills matter:** the1.2mm nominal width is not1.2mm of solid metal everywhere.
Existing SYS Ø0.7/0.4mm through-vias at `(75.5,60.95)` and `(76.2,60.95)` cross
the strip; their companion vias at y61.65 clip its lower edge. All four native
padstacks are0.7mm on each copper layer and stay exact-preserved. The selected
strip's minimum residual metal width is **0.70mm before and after**, subtracting
the central0.4mm drill and0.1mm clipping by the nearby drill. The original0.7mm
parallel branch/annular copper outside the strip and plated barrels provide
additional paths;0.70mm is a conservative strip cross-section, not a global
current-density solution or an ampacity rating. No via is silently treated as
an ordinary track or queried without its copper layer.

In1 fill/antipad topology, physical drills, all four via contacts and the native
0.1mm grid are unchanged. Identical deduplicated center/edge sampling finds
PGND under447/498 points for both representations; the51 missing samples are
inherited clearances/antipads, not new plane breaks. Full contours and exact
copper-union equality are stronger here than a sampling percentage. IC1/L1
and U3 switching/feedback loops are unchanged.

For the southeast section `(77.2,76.2)`→`(72.8,77.1)`→`(67.1,77.15)`, the
[45° alternative and native UUIDs](legacy-geometry-proposals-2026-10-17/sys-oblique-comparison.json)
also pass native DRC/ERC/parity/preservation. Its
[illustration](legacy-geometry-proposals-2026-10-17/sys-oblique-comparison.png)
shows a cleaner angle at the cost of0.302181mm additional conductor. With0.8mm
unchanged width, the simple strip scenario increases6.274942→6.461000mΩ
(2.965%). At an illustrative1A that is0.186057mV and0.186057mW more;
these are scenarios, not an approved load. More local area does not compensate
for a demonstrated series-path penalty. **Reject; preserve the original.**

## Remaining-route obstruction, verification and production boundary

All selected changes remain inside their original local axis-aligned envelopes.
Joint plan validation includes actual widths, pad overrides, copper artwork,
holes, native restrictions and existing RF/F5/USB reservations. The closest
remaining USB-net copper is8.514→8.520mm from R35,51.377→52.447mm from C26,
and28.650mm unchanged from SYS. Distances to enumerated blocked IC1 nets are
31.192→31.211mm,20.253→21.285mm and5.297mm unchanged. F5-node distances are
24.885→24.889mm,50.963mm unchanged and20.277mm unchanged. These concern
exported objects/endpoints and reservations, not a guarantee of future routing
feasibility. The exact SYS union cannot introduce a new obstacle. No selected
change introduces a material obstruction in the reviewed remaining corridors.

Verification evidence:

- [Accepted-baseline read-only native snapshot and routing context](legacy-geometry-entry-2026-10-17/context.json).
  Native KiCad10.0.7; exact901/265/154/473 geometry matched the owner hash.
- [Combined preflight and explicitly enumerated change sets](legacy-geometry-proposals-2026-10-17/verification.json).
  Every actual native creation/save/reload/refill passed exact net/nanometre
  equality; native all-pad connectivity partitions match. Independent
  retained-object comparison also covers models/fields/locks/board setup/pad
  settings/artwork/zone definitions. Only declared replaced tracks, serializer
  identity and derived fill blocks are excluded from that read-only comparison.
- Six separate scratches, including superseded/rejected native candidates,
  have0 physical DRC errors,0 parity,68 unconnected and0 ERC errors. Their20 DRC/
  11 ERC warnings exactly match the unchanged
  [scratch control](legacy-geometry-baseline-control-2026-10-17/context.json)
  as type/description multisets. Ignored checks are identical. Extra scratch
  warnings concern unavailable local libraries; they are not production findings.
- [Fresh read-only production DRC/ERC](legacy-geometry-production-checks-2026-10-17/production-checks.json):
  **68 unconnected /0 physical errors /0 parity /16 DRC warnings; ERC0/4**.
- [Final read-only live/saved reconciliation](legacy-geometry-final-reconciliation-2026-10-17/preflight.json)
  PASS; no editor save/refill/transaction. Production/source hashes remain exact.
- Toolkit regression suite: **60 tests PASS**, including negative original-object,
  net/layer/placement/via/field guards, copper-edge clearance, same-net drill
  width and segmentation-independent reference sampling. No native assertion,
  IPC instability, geometry/net mismatch or failed preservation occurred.

Separate production authorization must name the exact candidates/plans and
the accepted baseline, permit the enumerated original-track removals and require
a guarded native IPC delete/create transaction, visible readback, owning-editor
refill/save, independent saved comparison, joint checks and fresh DRC/ERC/parity/
plane verification. Current production installation remains **add-only**; the
new replacement mechanism was implemented and exercised **only on isolated
scratch boards**, with no production replacement entry point. New live UUIDs
would need to be captured and bound to the reviewed geometry, not assumed equal
to the scratch-created UUIDs. Reconcile any changed baseline before such work.

No USB routing, F5 modification, component/rule/schematic/footprint change,
Freerouting installation, fabrication, purchase, power-up, firmware, commit or
push. The68 outstanding connections still prevent release. STOP for owner review;
use a fresh session for any separately authorized production milestone.

## Manufacturer basis and interpretation

Verified2026-10-17. These sources justify preserving short loops/decoupling and
the existing snubber, not a new electrical architecture or product requirement:

- [Diodes AP7361C DS37274 Rev5-2, October2020, p10 Input/Output Capacitor](https://www.diodes.com/datasheet/download/AP7361C.pdf):
  keep bypass connections close to regulator pins. U4/C40 geometry is preserved;
  only the10k bleeder branch changes. Bulk capacitance/stability is not requalified.
- [TI BQ25798 SLUSDV2C, June2026, §8.4.1 p139](https://www.ti.com/lit/gpn/bq25798):
  preserve short high-frequency paths, close ceramics, sufficient power/via
  geometry and separation of sensitive signals from switching nodes.
- [TI-hosted BQ25792 SLUSDG1D, April2026, §11.1 p134](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/SLUSDG1_3D00_4_3D00_TI-PDF_3D00_en_2D00_us-_2800_2_2900_.pdf):
  the public TI attachment retains a confidentiality footer; provenance is also
  documented in the existing safety review. Layout prioritizes local capacitor
  loops and sufficient current-path copper/vias. No protected IC1 loop changes.
- [TI support, input hot-plug/snubber recommendation](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1109251/bq25792-chip-fried-on-evaluation-board-when-connecting-a-battery):
  supports retaining the2Ω/2.2µF damping function; not a guarantee for this board.
  Latest owner requirements and the existing
  [safety decision](v4-safety-design-review-2026-10-11.md) remain authoritative.

All lengths/gaps/UUIDs are exported CAD evidence. Areas/reference grids are
explicit geometric samples; resistances/current/drop/loss examples are stated
calculations. No hardware measurements, extracted parasitics, thermal results
or new operating ratings are claimed.
