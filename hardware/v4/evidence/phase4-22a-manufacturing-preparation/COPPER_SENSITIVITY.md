# Bounded copper/current/thermal comparison — REVIEW ONLY

2026-10-18. Calculations, not hardware measurements or fabricated minimum guarantees. Source scalars: accepted [Phase 4.5 charger review](../phase4-5-routing-review.md), [Phase 4.17 engineering](../phase4-17-review/engineering.json) and its [review](../phase4-17-review/REVIEW.md), preserved through Phase 4.18 and accepted Phase 4.21. No path search, whole-board resistance extraction, new current requirement or architecture change.

## Model and bounded interpretation

**Owner selected1oz outer/1oz inner, bare board/self-assembly.** Primary updated case is **30.5µm processed inner** from the owner's live JLC calculator observation (2026-10-18), not35µm guaranteed minimum. Exact stackup ID and copper tolerances/minima remain unestablished; no special impedance service is required.

`Rtrace = ρ L/(w t)`, ρ20 = 1.724×10⁻⁸ Ω·m; `R(T)=R20[1+0.00393(T−20)]`. At imposed125°C copper, R and I²R are **1.41265×** their20°C values. This does not predict copper temperature or permit125°C component operation. Outer copper stays35µm as an explicit unguaranteed assumption. Inner35µm is the old-model reference;30.5µm the selected-construction scenario;17.5/15.2µm are unselected half-ounce comparisons.

For an assumed finished bore d, barrel plating p and nominal board length 1.6 mm: `Rvia = ρ L/[π p(d+p)]`; N equal barrels give R/N. Actual interlayer span can be shorter; using full board length is a conservative barrel-length screen only. Unequal sharing, land/spreading/plane/contact resistance and solder joints are excluded. Published 18 µm average is used only as a sensitivity case; **not a guaranteed lower bound**. The accepted 25 µm assumption is also not an order guarantee.

At the standard1.6mm nominal tolerance's upper finished value1.76mm, barrel resistance/loss terms alone scale1.10×, not whole trace paths. This is a finished-thickness sensitivity, not a proposal to change the approved nominal1.6mm. Actual barrel length and bore tolerance remain manufacturing inputs.

At fixed geometry, inner resistance/heating at the same current increases **2.00×** for 17.5 µm and **2.303×** for 15.2 µm. The published ±20% width case, if represented as uniform −20% width, adds **1.25×** trace resistance; real etch cross-sections and copper minima remain unknown. Do not apply this to whole paths including barrels as if they were traces.

For the selected-construction30.5µm scenario, inner R/heating increases **14.75%** over35µm. Per10mm: SYS/BATTERY3mm gives **1.884mΩ/26.35mW at3.74A**; VIN/VBUS2.2mm gives **2.569mΩ/27.98mW at3.3A**; F5OUT2mm gives **2.826mΩ/11.30mW at2A**; F5SYS1.5mm gives **3.768mΩ/15.07mW at2A**. Same-temperature I²R changes, not actual temperature predictions. The old IPC illustration scales fixed-rise current by **0.905×** and fixed-current rise by **1.255×**:3mm/2.2mm inner examples become **3.89/3.10A** at the illustrative30°C rise. Whole-board spreading still prevents treating these as rated currents.

## SYS, BATTERY and charger sensitivity

Per **10 mm** of the accepted inner widths, not complete end-to-end path extraction:

| Inner path / illustrative current | R20 mΩ: 35 / 17.5 / 15.2 µm | I²R20 mW: 35 / 17.5 / 15.2 µm |
|---|---|---|
| SYS/BATTERY 3.0 mm, 3.74 A screen | 1.642 / 3.284 / 3.781 | 22.97 / 45.93 / 52.88 |
| VIN1/VBUS 2.2 mm, 3.3 A input ceiling | 2.239 / 4.478 / 5.156 | 24.38 / 48.76 / 56.14 |
| F5 OUT 2.0 mm, 2 A | 2.463 / 4.926 / 5.671 | 9.85 / 19.70 / 22.68 |
| F5 SYS branch 1.5 mm, 2 A screen | 3.284 / 6.568 / 7.561 | 13.14 / 26.27 / 30.25 |

The retained planning cases are approximately 3.24 A at 41.5 W/12.8 V, 3.74 A with 0.5 A charging before losses/tolerance, and 1.97 A at 12.61 W/6.4 V for the supported 2S load. These are different operating cases, not summed simultaneous maxima. For 3.24 or 1.97 A, scale this table's SYS/BATTERY voltage by I/3.74 and loss by (I/3.74)². Battery charging/discharging direction changes voltage sign, not I²R.

The charger B.Cu SW paths, 1.2 mm F.Cu local buses and short 0.20 mm package necks retain the same nominal trace resistance in A/B because outer copper is unchanged. Reuse the 5.08 A RMS / 6.59 A peak switching screen, not a claim of continuous trunk current. A representative 1.5 mm ×0.20 mm ×35 µm neck remains about 3.69 mΩ / 95.3 mW at 5.08 A. Actual split-pin sharing differs. Inner PGND spreading resistance and return heating still increase with thinner In1, so unchanged outer traces do not establish unchanged converter temperature.

The inherited IPC-2221 illustration (TI TIDA-01232, Eq.7, linked in Phase 4.5) has `I ∝ t^0.725` for fixed width/rise. The 3 mm inner 4.30 A / 2.2 mm inner 3.43 A at an illustrative 30°C rise become approximately **2.60/2.08 A** at 17.5 µm and **2.35/1.87 A** at 15.2 µm. At fixed current its relative-rise factors are **3.13×/3.95×**. These old empirical isolated-trace screens omit plane/component spreading and do not establish a board current rating or a new mandatory temperature limit. Their reduced margin warrants recording the construction and matching-hardware thermal checks; it is not a new routing defect.

## F5 measured-length branch model

Accepted 35 µm trace contributions: SYS input outer **10.2309 mΩ**, inner **6.1886 mΩ**, three transitions of two parallel 0.4 mm bore vias; output outer **6.5315 mΩ**, inner **5.9141 mΩ**, one two-via transition into J8's In2 trunk. J8 PTH terminates the path; no second output via pair is invented. IC1-to-SYS-tap shared distribution, PGND, U7 losses/dropout, Q10/U8, contacts and harness are outside these branch totals.

| Inner / barrel µm; outer 35 µm | SYS tap→U7 at 2 A, mV 20/125°C | RAW pickup→J8 copper at 2 A, mV 20/125°C |
|---|---|---|
| 35 / 25, accepted model | 35.32 / 49.89 | 25.72 / 36.33 |
| 35 / 18, plating sensitivity | 36.34 / 51.34 | 26.06 / 36.81 |
| **30.5 / 25, selected inner scenario** | **37.14 / 52.47** | **27.46 / 38.80** |
| **30.5 / 18, selected inner + average-based barrel sensitivity** | **38.17 / 53.92** | **27.80 / 39.28** |
| 17.5 / 25 | 47.70 / 67.38 | 37.55 / 53.04 |
| 17.5 / 18 | 48.72 / 68.82 | 37.89 / 53.52 |
| 15.2 / 25 | 51.44 / 72.67 | 41.13 / 58.10 |
| 15.2 / 18 | 52.46 / 74.11 | 41.47 / 58.58 |

At 2 A, loss in mW is twice the corresponding drop in mV. For another branch current, drop scales with I and loss with I². SYS branch input current is set by actual conversion power/efficiency/input voltage; a 2 A table is a screen, not the input current at every F5 operating point.

For30.5/18, branch losses are **76.33/107.83mW SYS input** and **55.61/78.55mW output copper** at20/125°C. Holding the old other output budgets fixed gives conditional J8 low **4.77786V**; adding uniform−20% trace width gives approximately **4.76846V**. Neither value bounds unconfirmed minimum copper/plating, shared-source/PGND/contact/harness losses, U7 dropout or temperature. It does not qualify5V/2A continuous operation. Thickness tolerances are not converted to a guaranteed worst case without actual minima.

Holding all other old output budgets unchanged, the accepted conditional J8 low screen 4.78081 V becomes **4.76362 V** at 17.5/18 and **4.75856 V** at 15.2/18. The latter leaves only 8.56 mV above the old 4.75 V comparison, before omitted losses. With a simultaneous uniform −20% trace-width sensitivity it is about **4.7443 V**. None is a guaranteed delivered voltage, a new product threshold, or proof of failure. The old 30 mV PCB allocation stays historical. Hot input-branch drop must also be included in eventual low-SYS dropout tests. Reuse U7 typical FET-conduction-only 0.177–0.276 W at 2 A/18–6 V, plus actual switching/inductor losses; thinner inner copper does not directly rescale semiconductor losses or junction-to-ambient resistance.

## Relevant via arrays

Full nominal 1.6 mm barrels; equivalent R20 in mΩ:

| Finished bore / equal parallel barrels | 25 µm plating | 18 µm illustrative plating |
|---|---:|---:|
| 0.30 mm / 2, bypass/returns | 0.5403 | 0.7670 |
| 0.30 mm / 6, IC1 switch bank | 0.1801 | 0.2557 |
| 0.30 mm / 12, L1 switch bank | 0.0901 | 0.1278 |
| 0.40 mm / 2, VBUS/F5 transition | 0.4132 | 0.5835 |
| 0.40 mm / 3, fuse/NT4 transfer | 0.2755 | 0.3890 |
| 0.40 mm / 4, BATTERY/SYS/MOSFET bank | 0.2066 | 0.2917 |

For a six-via switch bank at 5.08 A RMS, barrel-only dissipation is 4.65/6.60 mW (25/18); a four-via 0.4 mm bank at 3.74 A is 2.89/4.08 mW. One F5 two-via transition at 2 A is 1.65/2.33 mW. These do not include pad necks or prove sharing. If only half the barrels carry appreciable current, equivalent barrel loss doubles and individual active-barrel current doubles. No broken via is presumed; this is a sharing sensitivity. Do not reuse the old via-area ampacity analogy as a validated thermal model.

Machine-readable inputs/results and formulas: [copper-sensitivity.json](copper-sensitivity.json), [generator](prepare_review.py). **A is owner approved**, with30.5µm nominal processed-inner recalculation rather than silently retaining35µm. B remains comparison only. Neither construction establishes thermal performance without matching assembled-hardware data; via minimum remains unconfirmed.
