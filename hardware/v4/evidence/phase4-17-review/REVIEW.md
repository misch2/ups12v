# Phase4.17 — F5 scratch placement and complete routing

2026-10-17. **Complete isolated CAD candidate; STOP before production migration.**
All41 accepted F5 opens are closed. Native DRC0physical/0unconnected/0parity;
ERC0errors. All473pads and every original connection are retained. This is
layout evidence and calculation, not measured5V/2A, thermal or reverse-blocking
qualification, manufacturing approval, or a production modification.

## Quick start for owner review

1. Inspect [U7/L3](images/buck-FCu.png), [U8/Q10](images/blocker-FCu.png),
   [actual PGND](images/returns-In1Cu.png) and [power trunks](images/power-In2Cu.png).
2. The complete, closed scratch project is
   [ups12v_v4.kicad_pro](../phase4-17-final-candidate-v2/ups12v_v4.kicad_pro);
   its [PCB](../phase4-17-final-candidate-v2/ups12v_v4.kicad_pcb) SHA256 is
   `8221929563ed10653f84933549a6fdf99d69071364c12e83860a22f55326b9e6`.
   Open this exact scratch project only if interactive inspection is desired.
3. Review the calculations/limitations below and the
   [bounded future migration proposal](MIGRATION_PROPOSAL.md).
   No manual routing action remains. Production migration requires separate approval.

## Authority and actual circuit

The source is the exact accepted Phase4.16 production PCB
`bce08349485b0f8d53060fcc9ef1a3911eaabf0408de16b288d0655e30754899`,
bound by its existing manifest. Elevated host process inspection found no KiCad
editors before work. The fresh [entry snapshot](../phase4-17-entry-native/snapshot.json)
and [fresh schematic XML](../phase4-17-entry-native/netlist.xml) establish the actual
geometry and connectivity. Native KiCad10.0.7 APIs acted exclusively on fresh,
unlocked, baseline-derived scratch copies in monitored workers. Konnect tool
availability was checked; no live editor/IPC operation was needed or attempted.

U7=TPS62933DRLR, RT pin1 intentionally NC; EN2=/F5_EN, VIN3=SYS,
GND4=PGND, SW5=/F5_SW, BST6=/F5_BST, SS7=/F5_SS, FB8=/F5_FB.
L3=Coilcraft XAL5050-682MEC6.8uH. C60/C61=10uF50V inputs;
C69=100nF50V VIN bypass; C62=100nF bootstrap; C63=33nF SS;
C64/C65=22uF35V RAW outputs; C66=100nF RAW bypass. R60/R61=53k/10k0.1%;
R62/R63=100k/38.3k1%. Values, exact MPNs, footprint definitions and assembly
properties are unchanged; existing procurement/BOM records remain authoritative.

U8=LM74700QDBVRQ1: VCAP1=/F5_VCAP, GND2=PGND, EN3=/F5_RAW,
CATHODE4=/F5_5V_OUT, GATE5=/F5_GATE, ANODE6=/F5_RAW. C67=100nF50V
between VCAP and RAW; C68=100nF50V OUT bypass. Q10=AON7528:
source1–3=RAW, gate4=GATE, drain5–9=OUT, including exposed pad9.
**Current J8 pin1=PGND, pin2=NC, pin3=OUT.** This fresh three-position
mapping supersedes the old two-position connector description in Phase3.6.
TP17 remains fixed at(115.5,44.5), connected only to OUT.

The MOSFET body diode is directed RAW→OUT. U8 senses source/drain in the intended
direction and pulls the gate toward source on reverse detection. This establishes
correct schematic/layout topology; gate transients, externally energized output
and power-off behavior have not been physically tested. No USB, MCU3V3,
MAIN_3V3 or firmware-controlled path was added to F5.

F0 continues to omit exactly the19 assembly parts U7/U8/Q10/L3/R60–R63/C60–C69/J8.
In F0 the new SYS copper ends at unpopulated F5 pads and the OUT network/TP17
remains unfed. Exported topology still attaches F5 to the base only through SYS
and PGND; no fitted bypass link, new population variant or BOM edit exists.

## Placement and switching loops

Compared with the [accepted before image](images/before-FCu.png),18F5-only
footprints are rigidly moved/rotated; J8 and TP17 remain fixed. All F0 placements,
473pad identities/net assignments and original1053tracks/arcs/294vias are fixed.
Full intended placements and copper are in the immutable candidate
[plan](../phase4-17-final-candidate-v2/plan.json).

| Pad-center separation | Before | After |
|---|---:|---:|
| U7VIN–C69SYS |10.877mm|1.552mm|
| U7GND–C69PGND |12.209mm|1.552mm|
| U7SW–L3SW |10.040mm|4.491mm|
| U7BST–C62BST |3.040mm|1.646mm|
| U8GATE–Q10gate |2.545mm|2.055mm|

The SW track enters the upper portion of L3's actual elongated pad rather than
running unnecessarily to its center: actual routed U7-to-L3 copper centerline is
**2.780mm**, with a short0.30mm package escape widening to0.60mm. SW remains
entirely on F.Cu, with zero SW vias; its native pad/track union is7.791mm²
(0.01mm raster approximation, including the existing inductor pad).

C69 and U7 form a1.321mm² projected input loop; bootstrap loop1.382mm².
VIN local trace1.602mm, PGND trace1.677mm, BST trace2.085mm.
These are centerline/pad-center projections with straight internal-device
closures, not measured inductance or field simulation. Short0.28–0.30mm escapes
respect the SOT5830.5mm pin pitch; ground broadens to0.45mm and then1mm.
A nearby PGND via at(100.5,60.1) connects the ground escape directly into In1;
three0.70/0.40mm ground vias serve the C60/C69 return, with additional local
returns at C61, C64/C65, C66, C68, U8 and R61/R63.

Feedback resistors are above U7, away from the lower-right SW/inductor area.
The upper divider gets a separate0.30mm RAW pickup from C64 using B.Cu;
the high-impedance FB node stays on F.Cu, with no FB via. SS crosses to B.Cu
through two legal vias to avoid crossing the short bootstrap. No path search,
F0 shove, serpentine or impedance tuning was used. Every0.05mm station at FB
center and±0.14mm lateral offsets has actual In1 PGND beneath it:381/381samples.
See [B.Cu](images/local-BCu.png). This is reference coverage, not a noise measurement.

## Actual PGND, current and thermal layout

Saved/refilled native polygons with holes, physical drills and independent native
pad islands were checked. Explicit0.05mm sampled paths in actual In1 PGND connect
C64/C65, C66, R61 and U8 returns to the local U7 ground region; real drill voids
are subtracted and diagonal corner cutting is prohibited. These paths establish
conductive return feasibility, not current-density distribution. The plane is
broad around the power block; no newly isolated ground pad or net-tie bypass
exists. Actual fill occupancy in four fixed IC1/U3/USB review windows is unchanged
at0.1mm sampling, alongside exact preservation of all old routed geometry and
all old native pad islands. Complete samples/results are in
[engineering.json](engineering.json) and [plane-window.json](plane-window.json).

The SYS source branch taps the retained3mm In2 SYS trunk atx76.2. A9.6mm-long,
1.5mm-wide B.Cu bridge crosses the fixed In2 BATTERY trunk without touching it;
paired0.80/0.40mm vias at each end return to In2. A1.5mm In2 branch reaches the
F5 input bank through another paired transition. See [bridge image](images/bridge-BCu.png).
The RAW high-current path is1.2mm with a0.40mm×0.84mm escape into Q10source1;
source2/3 are bridged with0.35mm copper. U8's direct ANODE pickup is separate
from that load-current escape; gate length2.206mm at0.35mm width. The OUT drain
and exposed pad join a1.2mm top trunk, paired0.80/0.40mm vias and a24.013mm×2mm
In2 trunk to J8. TP17 has a separate measurement branch. The remaining narrow
power segments are short package escapes, not long thin high-current trunks.

Read-only stackup metadata establishes35um copper on all four design layers;
it is still not a fabrication contract. DC calculation uses this35um, copper
resistivity1.724e-8ohm*m at20C and, explicitly as sensitivity assumptions,
1.6mm plated via length/25um plating/equal two-barrel current sharing.

| Calculated branch, excluding contacts/plane spreading |20C,2A|125C copper,2A|
|---|---:|---:|
| New SYS branch to U7VIN |35.32mV|49.89mV|
| C64regulated RAW pickup→Q10→J8 copper, excluding Q10 itself |25.72mV|36.33mV|

The previous30mV output-PCB allocation is met by the nominal20C calculation;
the125C sensitivity exceeds that allocation. Keeping the previously allocated
50mV blocker,20mV ripple and10mV extra regulation gives a conditional low
J8screen of4.78081V, still above4.75V, but with only30.81mV remaining margin.
This does not prove the complete tolerance/thermal envelope. At18um inner copper
the output cold estimate rises to36.89mV; a thinner production stackup needs a
fresh review rather than inheriting the35um result. No design rule was changed.

The old6V/dropout feasibility calculation used20mV input copper loss; this new
branch's hot estimate is about50mV at2A and must be included in subsequent
matching-hardware validation. Its additional30mV is small relative to the earlier
typical dropout headroom, but typical on-time/Rds(on) data remain non-guaranteed.
The shared pre-existing SYS source path and PGND plane losses are outside these
branch estimates; current-sharing/contacts/AC effects and local pad spreading
are not modeled.

U7 input/SW/output components share F.Cu. VIN, SW and ground broaden after their
package escapes; PGND has a nearby via plus input/output via groups into the
unchanged In1 plane. Typical-FET conduction-only loss at2A is about0.178–0.276W
for18–6V input; switching, ripple and temperature increases add to this.
The existing inductor hot-loss and capacitor-Ceff/85C-body limitations remain
from [Phase3.6](../phase3-6-review.md). Q10's large drain pad/top copper spreads
its much smaller blocker dissipation; the prior50mV/2A allowance is0.1W.
No temperature rise,2A ampacity guarantee, hot dropout, load-step, EMI or
reverse-transient qualification follows from these geometry checks.

## Validation and deliverable identity

Final native build/save, CLI refill/save, independent native reload, full473-pad
connectivity, ERC/DRC/parity, exact old-copper/placement and zone/artwork guards:
**PASS for this scratch milestone**. Candidate:154footprints,473pads,
1170tracks/arcs including all8original arcs,324vias;157→116pad islands.
Exactly41same-net merges: SYS5,PGND12,RAW10,OUT4,BST1,EN2,GATE1,SW2,SS1,FB2,VCAP1.
All41F5opens completed; remaining0, F0opens0. No route needs owner assistance.

Scratch DRC20warnings and ERC11warnings have exactly the same warning identities
as the accepted production-derived isolated reference. These library-context
warnings must not be confused with production's accepted16DRC/4ERC warnings.
Ignored-check lists are not new waivers; no rules were relaxed. No unexpected
native assertion, IPC transaction, editor recovery or uncertain write occurred.
The early subprocess module-path error occurred before CAD load and was corrected
using the existing toolkit worker entry point; its scratch was never reused.

Full verification files: [summary](../phase4-17-final-candidate-v2/summary.json),
[preservation](../phase4-17-final-candidate-v2/preservation.json),
[DRC](../phase4-17-final-candidate-v2/drc.json),
[ERC](../phase4-17-final-candidate-v2/erc.json),
[entry/final binding](FINAL_PROOF.json). Full retained-board/footprint properties
also match exactly after the independently bound rigid transforms;32reordered
fp_line entries are normalized only as complete exact payload multisets.
The expanded offline suite **113tests PASS** is recorded in [tests.log](tests.log).
No firmware build is applicable.

## Manufacturer basis

Verified2026-10-17 against official manufacturer documents:

- TI [TPS62933 SLUSEA4D, RevD, August2022](https://www.ti.com/lit/ds/symlink/tps62933.pdf),
  §7pins and §§12.1–12.2, pp40–41: local input loop, bypass, SW/BST, quiet feedback,
  nearby input/output capacitors and ground/thermal spreading. Our four-layer
  design is assessed against those electrical principles; TI's illustrated
  two-layer2oz board is not our qualified thermal construction.
- TI [LM74700-Q1 SNOSD17G, RevG, December2020](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf),
  §5pin map, §§9.3.3/9.4.2.3 gate/reverse behavior and §§12.1–12.2, pp23–24:
  nearby source/gate/drain sensing, low-resistance load copper and a short gate;
  C67 is beside the controller, away from the MOSFET body.
- AOS [AON7528 Rev1.0, October2023](https://www.aosmd.com/res/data_sheets/AON7528.pdf),
  pp1–2: source1–3/gate4/drain5–8 plus exposed drain land, body diode and electrical
  limits. Existing placed-footprint map and connectivity were preserved.

**STOP after Phase4.17 scratch review.** The accepted production PCB, schematic,
project, rules, BOM and variants remain unchanged. No USB/IC1 optimization,
legacy cleanup, firmware, manufacturing, purchase, power-up, commit or push.
