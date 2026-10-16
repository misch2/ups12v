# Phase4.8B — local supply B1/B2/B3 INSTALLED AND VERIFIED; STOP

2026-10-16. Owner accepted Phase4.8A and explicitly authorized bounded production
routing in separately verified B1/B2/B3 batches. All three are complete. No U3
installation was repeated. No footprint, original copper, schematic topology,
component value, footprint library, rule, zone definition or population variant changed.

## Verified production state

| Checkpoint | Tracks / vias | DRC unconnected / physical errors / warnings / parity | ERC errors / warnings |
|---|---|---|---|
| Accepted entry |473 /156|216 /0 /16 /0|0 /4|
| B1 — SYS and MAIN handoffs |510 /160|212 /0 /16 /0|0 /4|
| B2 — USB LDO and C71 handoff |566 /172|194 /0 /16 /0|0 /4|
| B3 — mux, C36 and priority |604 /179|184 /0 /16 /0|0 /4|

All stages retain154footprints/473pads and both live zone definitions (PGND
and RF rule area). Native snapshots count the one copper zone separately from
the RF rule area. **Final PCB SHA256
`ded2ac1999b672157409b0b6f2bbc636beac4fd54382c8b9548346a0fbcab675`.**
Schematic remains`990d107296d149775884dc2d2512c2e6102b6191e4818e7fcf5bd9268d48c8f6`;
project remains`477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e`.

Each batch had native scratch save/reload, refilled DRC/parity and ERC, visual
inspection, exact live preflight, one add-only IPC commit, returned/visible native
geometry readback, owning-editor refill/save, independent saved-board native
readback and fresh production DRC/ERC/parity. Each full preservation check
compares retained artwork, models, fields, pads, routing and zone definitions.
Only expected copper fill changed. Production warning multisets and ignored
checks are unchanged. Scratch20DRC/11ERC library-context warnings are recorded
separately and were not substituted for production16/4 warnings.

## Actual paths and bypasses

- **B1:37tracks/4vias.** Existing SYS through-via(75.5,61.65) feeds C32.1 and
  the already-connected C43/U3 input network. New52.438mm,0.8mm feed uses B.Cu
  and F.Cu with three0.50/0.30mm layer transitions. It avoids changing the
  charger and accepted U3 input/switching copper. MAIN from C45.1 to C70.1 is
  6.970mm/0.6mm/F.Cu; C70.1 to U5.3(VIN1) is2.208mm/0.28mm/F.Cu. C70 has a
  local0.60/0.30mm PGND via and0.575mm/0.4mm escape.
- **B2:56tracks/12vias.** J7 A4/A9/B4/B9 VBUS are joined, including C28,
  and feed U4.1 through11.718mm/0.6mm/F.Cu. Connector local links use0.3mm;
  C27.1 input bypass is2.400mm/0.6mm. U4.3 to C35.1 is2.816mm/0.8mm;
  C40 and R35 are joined on the same output net. C35 to C71 is39.008mm/
  0.6mm/F.Cu, with no new power-path via. Ground lead and tab are connected
  by6.3mm/1.2mm copper; two0.70/0.30mm ground vias at the lead and four at
  the tab connect directly to In1 PGND. C27/C35/C40/R35/C28/C71 each have a
  local0.60/0.30mm ground via. These vias include existing-pad locations;
  unfilled via-in-pad solder wicking must be considered during manual assembly.
- **B3:38tracks/7vias.** C71 to U5.6(VIN2) is1.481mm/0.28mm/F.Cu;
  U5.2 and U5.7(VOUT) are joined by1.520mm/0.28mm/F.Cu, and U5.7 to C36.1
  is1.958mm/0.28mm/F.Cu. U5.5(MODE) connects to VIN1/MAIN through1.621mm/
  0.2mm/F.Cu. R23.1 is MAIN, R23.2/R24.1/U5.4 are MUX_PR1, and R24.2 is
  PGND. Original8k2/4k7 divider values and thresholds are unchanged. Four
  0.50/0.30mm control/divider vias cross the existing SYS obstruction without
  altering it. U5.1/C36.2/R24.2 gain three local0.50/0.30mm PGND vias.

VIN1, VIN2 and VOUT remain three distinct nets with no copper bypass around U5.
MODE tied to VIN1 and PR1's existing MAIN divider preserve autonomous MAIN
priority. ST remains deferred. Current schematic mapping is captured in
[net mapping](phase4-8b-schematic-net-mapping.json).

## Electrical and return evidence; limits

[Export-only electrical review](phase4-8b-electrical-review.json) proves exactly
**131tracks/23vias added**, all original473tracks/156vias retained, and all
footprints/pads unchanged. All16newPGNDvias have native filled-plane center and
four-ring contact. Nine sampled, drill-aware paths are continuous: C70/C71/C36/
R24 to U5, C27/C35/C40 to U4, tab to ground lead, and USB ground to U4.
The0.1mm sampled plane paths are5.628/5.363/3.894/3.366mm for U5 and
5.311/5.953/7.895/6.173/14.388mm respectively for U4/USB. These are bounded
conductive-path evidence, not impedance or noise measurements. Native In1 PGND
remains one fill contour. The **entire accepted U3 native ground sample grid
and via probes at(44,74)–(60,89) are exactly unchanged**, preserving its accepted
FB/Kelvin reference and local switching-return evidence.

Reuse Phase4.8A's explicitly assumed35um outer copper,20°C resistivity,
approximately1A normal-output screen, and unconfirmed1.6mm/20um plated-via
model. Calculated new trace resistances: SYS32.287mohm; MAIN C45→VIN1
9.606mohm; U4→VIN2 USB branch36.362mohm; VOUT7→C36 3.445mohm. A single
0.30mm drill via is approximately1.463mohm under those assumptions. These
exclude existing paths, contacts, mux resistance, solder and temperature rise.
The new SYS feed dissipates32.3mW even at a1A input screen; actual buck input
depends on SYS voltage, efficiency and output. The USB branch drops10.9mV at
the existing provisional0.3A service screen. Short0.28mm pad escapes adjoin
wider copper; these calculations do not grant a3A board rating or establish
actual plating/temperature/current sharing.

Manufacturer references rechecked2026-10-16:
[AP7361C DS37274 Rev5-2,October2020](https://www.diodes.com/datasheet/download/AP7361C.pdf),
pin table and Application Information pp10–11: ceramic input/output bypass
and short wide IN/GND/OUT connections. C27 remains4.7uF; C35 remains22uF,
C40 remains100nF; effective capacitance/DC bias still needs BOM/hardware
qualification. [TPS2116 SLVSFG1A RevA,May2021](https://www.ti.com/lit/gpn/tps2116),
§5,§7.6 and§10.1: actual pin mapping, autonomous VIN1 priority and local wide
supply/bypass paths. Source isolation remains the existing device behavior,
including finite leakage and dynamic thresholds; no ideal zero-leakage claim.

U4's tab and via spreading are useful geometry, **not a measured thermal
resistance**. Retain the earlier minimal-land110°C/W service screen: at assumed
5.25V input/3.234V output,0.3A gives about0.605W and116.6°C junction at50°C
ambient;0.5A continuous gives about160.9°C on that model and is not qualified.
No inference of1A continuous service support follows from the IC rating.
USB port allowance, ROM cold-start/inrush/flash peaks, cable drop, capacitor
effective values, mux transitions and actual LDO temperatures remain unmeasured.
Remote MCU supply and USB signal/CC completion are deferred; this checkpoint
does not claim a functional cold-start/programming test. In particular the
remaining J7-to-R14 PGND airwire belongs to the deferred CC resistor circuit.

## Actual remaining entries

| Net | Remaining DRC entries | Boundary |
|---|---:|---|
| SYS |5|C61/C60/R62/U7/C69 remote optional branch; U3 input is connected|
| MAIN_3V3 |11|Remote R28/R21/R22/U6/C48/D4/Q5/Q8/R44/R50/J4 branches|
| USB_VBUS |0|Complete local source/LDO input network|
| USB3V3 |0|Complete U4 output/C35/C40/R35/C71/U5 VIN2 network|
| MUX_PR1 |0|Complete local divider/PR1 network|
| MCU3V3 |16|Remote loads/probes; U5 VOUT pins and C36 are joined|
| PGND |66|Unrelated/deferred returns, including R14; affected local power returns complete|

Full actual descriptions: [remaining entries](phase4-8b-b3-ipc/remaining-by-net.json).
A net with remote airwires is not a completed board-wide supply.

## Reproducibility and preservation

Immutable installed plans: [B1](phase4-8b-b1-plan.json),
[B2](phase4-8b-b2-plan-v3.json), [B3](phase4-8b-b3-plan.json).
Per-batch IPC/native/check/preservation evidence is in`phase4-8b-b1-ipc`,
`phase4-8b-b2-ipc`, `phase4-8b-b3-ipc` and corresponding`*-native` directories.
Next accepted saved/live baseline:
[final manifest](phase4-8b-b3-ipc/accepted-installed-baseline.json).
Final independent read-only live preflight after documentation/evidence work
also PASS: [saved/live reconciliation](phase4-8b-final-ipc/preflight.json).
It compared every captured live section against that manifest and the exact
saved hashes, without refill, save or mutation.

Canonical toolkit gained export-only planning/review, complete add-only
preservation, explicit endpoint layers and duplicate physical-pad obstacle
coverage. **27regression tests PASS**. Initial KiCad-bundled Python test run
lacked`_cffi_backend`; normal project Python passed. Initial sandbox IPC failed
with Permission denied at GetVersion before document access; explicit command
approval preceded host preflight. No native assertion, unstable IPC, saved/live
mismatch, production DRC/parity regression or automatic editor recovery occurred.
Failed scratch attempts are retained: B1 review bounds exceeded the sampler's
30mm limit after clean DRC; B2 initial route collided with duplicate shield
geometry and same-batch ground returns. Both were corrected on fresh scratch
copies before production. No failing candidate was installed.

**STOP for owner review.** U7/F5, Q5/host control, I2C/INT, general MCU/USB signal
routing, remote MAIN/MCU branches and unrelated PGND completion remain deferred.
No fabrication, purchasing, power-up, firmware changes, commit or push. Start a
fresh session for the next separately authorized milestone.
