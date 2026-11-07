# V4 variants — shared-PCB assembly matrix

## Owner battery/safety decision — 2026-10-11

All 2S profiles use **2S1P: two 18650 cells**. All four-cell profiles use **4S1P: four 18650 cells**, not 2S2P. No charger or F0/F5 combination is removed. S792-2 pack, each series cell, BMS and wiring must qualify for possible sustained2 A default charging including relevant positive regulation tolerance and allowed temperatures; exact pack identities and qualification are OPEN. Nominal firmware charge remains0.5 A or lower; retain existing default-off CE without an added hardware0.5 A limiter, supervisor or watchdog. R12/C26 retention at2 ohm/2.2 uF is approved in all assemblies; transient validation remains OPEN. See [safety report](evidence/v4-safety-design-review-2026-10-11.md). This closes architecture only, not fabrication, routing or power-up gates.

Phase 4.4 update, 2026-10-11: J7 is owner-approved GCT USB4085-GF-A, common
to every F0/F5 plan. C70/C71 are two new fitted common U5 input bypasses,
Murata GRM188R71C105KA12D, 1 µF/16 V X7R 0603, one per input. C36 output
bulk retained; no C72. Native PCB replacement/import and full 443-pin parity
verified. All 19 F5-only footprints remain on the one PCB; no second board or
new assembly variant. See [Phase 4.4 native verification](evidence/phase4-4-native-review.md).

2026-10-10 · [Requirements](V4_REQUIREMENTS.md) · [Architecture and alternatives](V4_ARCHITECTURE.md) · [Accepted audit](V4_AUDIT.md). **Exactly one physical PCB**, one netlist architecture and one board revision. Tables describe intended population, not fabricated/qualified configurations. Owner update: Phase2 authorized; initial design/qualification is VSYS-only. All CAD targets hardware/v4/ups_v4/.

## Base profiles and load/source identity

| Profile ID | IC population | Pack / RPROG (1%) | POR ICHG setting to guard against | Primary output / intended load | Backup / recommended main adapter |
| --- | --- | --- | --- | --- | --- |
| S792-2 | TI BQ25792RQMR | 2S1P, two18650 / 8.2 kΩ | **2 A; accepted subject to pack qualification** | VSYS; 5V loads via optional onboard or external converter | Backup disabled; 12V/2A for 5V/2A target, or 5V/3A derated profile |
| S792-4 | TI BQ25792RQMR | 4S1P, four18650 / 27 kΩ | 1 A | VSYS; higher-voltage/power external converters | Backup disabled; 20V/3A for external 12V/3A target |
| S798-2 | TI BQ25798RQMR | 2S1P, two18650 / 8.2 kΩ | 1 A per current datasheet | VSYS; 5V loads | Backup disabled; source/load profile as S792-2 |
| S798-4 | TI BQ25798RQMR | 4S1P, four18650 / 27 kΩ | 1 A per current datasheet | VSYS; higher-voltage/power external converters | Backup disabled; source/load profile as S792-4 |

All profiles use 750 kHz / 2.2 µH. All default to **charging disabled by hardware**, irrespective of the stored POR ICHG setting. Initial configured nominal charge target ≤0.5 A; source/temperature/cell limits can lower it. The 2S/5V-adapter profile uses output ≤1.5 A and charge ≤0.25 A for planning. Simultaneous 5V/2A output and 0.5A charging is not a requirement for that source. RPROG is fixed by assembly, not a user cell-count jumper.

PMID backup profiles are deferred and are not part of the initial BOM or qualification matrix. Optional PMID testpoints and DNP footprints may remain on the one PCB. The original PMID concept assumed approximately equal adapter/backup output voltages; no15/20V-to12V recovery development is authorized in this phase. “Backup disabled” above means the BQ25798 PMID backup feature; normal battery-backed VSYS remains the core UPS function.

## Population groups on the shared PCB

Legend: **P** populate; **DNP** do not populate; **Q** qualification/tuning provision with explicit assembly record. Legacy references identify audited functions only; future CAD references should remain stable where practical.

| Group / function | S792-2 | S792-4 | S798-2 | S798-4 |
| --- | --- | --- | --- | --- |
| One common charger footprint | BQ25792RQMR | BQ25792RQMR | BQ25798RQMR | BQ25798RQMR |
| RPROG (legacy R5) | 8.2 kΩ | 27 kΩ | 8.2 kΩ | 27 kΩ |
| Basic input/polarity protection/fuse + BQ input FETs | P | P | P | P |
| L1 provisionally Eaton DR125-2R2-R, 750 kHz | P | P | P | P |
| **Corrected VBUS** bypass C7/C13/C16 | P | P | P | P |
| Mandatory PMID ceramics C6/C12/C15/C18 | P | P | P | P |
| SYS/BAT/REGN/bootstrap/BATP/SDRV support | P | P | P | P |
| Dedicated backup bulk (legacy C20/C22 footprints) | DNP* | DNP* | DNP* | DNP* |
| Supplemental PMID bulk tuning pads (legacy C24/C25) | Q: default DNP* | Q: default DNP* | Q: default DNP* | Q: default DNP* |
| Accessible VSYS/GND, adapter, BAT/NTC terminals | P | P | P | P |
| PMID load connector / optional output-fault protection | DNP; testpoint retained | DNP; testpoint retained | DNP; testpoint retained | DNP; testpoint retained |
| Official C3 module + normal3V3 buck + USB3V3 path + mux | P | P | P | P |
| USB-C/CC/ESD/VBUS protection + BOOT/RESET/UART | P | P | P | P |
| Complete signal isolation, CE bias / normally-off open-drain sink | P | P | P | P |
| Pack NTC connector/sensor profile | Qualified 2S pack | Qualified 4S pack | Qualified 2S pack | Qualified 4S pack |
| Assembly identity components / label | S792-2 | S792-4 | S798-2 | S798-4 |
| Optional5V converter group and output blocker | Overlay F0/F5 | Overlay F0/F5 | Overlay F0/F5 | Overlay F0/F5 |

`*` DNP is the intended cost-saving SYS assembly candidate, **conditional on** effective ceramic capacitance and SYS-mode input/load transient tests. If it fails, change the recorded SYS population; do not remove ceramic requirements or assert that “backup-only” means all bulk is irrelevant to forward operation. No backup population is qualified in this phase. Supplemental electrolytics remain tuning parts until evidence establishes the necessary population. No legacy 20V POSCAP is fitted in a 20V-nominal adapter assembly. Keep the same physical footprints/PCB across qualified population choices; confirm replacement package fit before selecting them.

Charger-owned LED/STAT support may be common; MCU STAT crossing is omitted by default. Direct rail-sense dividers to MCU are omitted, using charger ADC instead. CE/I²C/INT/charge-request/PG or reset crossings that are fitted must satisfy the complete domain table; a SYS profile does not omit USB reverse protection or charge gating to save cost.

## Optional5V overlay

Phase3.6 implements the optional converter on the common schematic. See [review](evidence/phase3-6-review.md) and [machine-checked population CSV](evidence/phase3-7-population.csv).

| Physical references | F0 fitted quantity | F5 fitted quantity |
| --- | --- | --- |
| U7,U8,Q10,L3,R60,R61,R62,R63,C60,C61,C62,C63,C64,C65,C66,C67,C68,C69,J8 | 0 for every reference | 1 for every reference (19 total) |
| TP5-TP8,TP13-TP17 | Copper only; no fitted part | Copper only; no fitted part |
| R32/R33,C33/C45 | Common31.6k/10k0.1%10ppm and2x22u35VX5R1206 | Same common population |

F0 must omit J8 as well as the converter/blocker, with no bypass links. TP17 remains isolated copper. F5 connector is J8 pin1=5V_OUT/pin2=PGND; reverse blocker U8/Q10 separates external output from RAW/SYS. F5 is independent of MCU/serviceUSB and attaches to the base only atSYS/PGND. Capacitor Ceff,85degC X5R body rating and layout/thermal qualification apply; no fabricated variant is qualified. Native USB Serial/JTAG and USB-only MCU power are common and primary. Optional fallback UART is only TP5 ESP_TX(GPIO21),TP6 ESP_RX(GPIO20),TP7 GND at2.54mm near an edge, with no fitted header/supply pin. TP8 MCU3V3/TP13 MAIN_3V3 are separate measurement pads elsewhere. TP9-TP12 removed; BOOT/RESET buttons retained. TP14 CE_N is separate passive charger-domain bring-up access. Common copper is not another assembly variant. See current Phase3.7 handover.


| Overlay | Population and use |
| --- | --- |
| F0 | DNP the complete independent 5V block: IC, inductor, feedback/enable parts, input/output capacitors, output reverse blocker and connector. Avoid fitted bypass links or feedback paths that reconnect its output to SYS/USB. Leave accessible labeled pad/test provision as mechanically appropriate. |
| F5 | Populate the complete independent VSYS→5V block, reverse blocker, capacitors and keyed 5V/GND connector. Target 5V ±5%, 2A continuous over qualified 6–18V SYS. All losses/load share the base profile's source/pack budget; do not increase total UPS rating merely because F5 is fitted. |

Orderable assembly name example: `V4.<board-revision>-S792-2-F5-<BOM-revision>`. Four SYS bases×two overlays give eight initial population plans from **one** layout. The service USB supply is common to these plans. The latest owner decision uses U3 normal buck plus U4 service-USB LDO and U5 mux; no separate regulator assembly variant is introduced.

## Procurement baseline and replacement requirements

| Function | Preliminary choice / required selection | Procurement / footprint evidence and remaining work |
| --- | --- | --- |
| Charger | BQ25792RQMR or BQ25798RQMR, mutually exclusive | TI RQM; common footprint requires complete split-land/mechanical/register comparison. No exact TME stock claim. [TI792](https://www.ti.com/product/BQ25792), [TI798](https://www.ti.com/product/BQ25798) |
| L1 | Eaton DR125-2R2-R, provisional retain | [Recorded TME](https://www.tme.eu/cz/details/dr125-2r2-r/tlumivky/eaton-electronics/), 12×12mm H6 footprint; confirm installed part and 750kHz thermal loss |
| Protected input FETs | AON7528 conditional retain | [Recorded TME](https://www.tme.eu/cz/details/aon7528/tranzistory-s-kanalem-n-smd/alpha-omega-semiconductor/), DFN3.3×3.3; verify21V continuous plus supported-adapter hot-plug waveforms, SOA and gate drive |
| Basic input protection / fusing | Appropriate fuse, polarity protection and existing BQ input FET function; exact MPNs open | No active input OVP/eFuse requirement; coordinate source, wire/contact ratings, normal hot-plug and5V headroom |
| Normal3V3 and optional5V bucks | TPS62933DRLR candidate, separate circuits; USB uses an LDO | [TI orderable part](https://www.ti.com/product/TPS62933/part-details/TPS62933DRLR); installed `Package_TO_SOT_SMD:SOT-583-8`, pad/stencil readback still required. Exact TME link/stock unverified. |
| USB3V3 service LDO | Diodes AP7361C-33E-13, SOT-223, provisional | Common all profiles; Wi-Fi off; see current BOM and LDO selection evidence for sourcing, exact pin map and thermal limits. |
| 3V3 mux | TPS2116DRLR candidate | [TI orderable part](https://www.ti.com/product/TPS2116/part-details/TPS2116DRLR); DRL8, candidate SOT-583-8, mapping/leakage/priority verification required |
| I²C interface | TCA9517DGKR candidate or qualified Ioff bus switch | [TI orderable part](https://www.ti.com/product/TCA9517/part-details/TCA9517DGKR); candidate `Package_SO:VSSOP-8_3x3mm_P0.65mm`; offset/power/leakage/EN verification |
| CE/INT/control translation | Normally-off open-drain CE sink, gate pull-down and charger-owned pull-up; MPNs open | Verify startup/reset, logic limits and leakage for both BQ ICs; no external250ms lease/watchdog |
| RF module | ESP32-C3-MINI-1-N4X candidate | [Espressif module ordering/land pattern](https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html); exact TME offer and module footprint not verified |
| Input/PMID ceramics and bulk | ≥35V input/PMID;50V MLCC if needed; forward-mode Ceff qualification | Exact MPNs/packages open pending bias/ripple/life curves; retain valid Source/Bought fields and record why old 25V/20V parts are replaced |
| SYS/BAT support | ≥25V subject to rail peak, Ceff and cell limits | Preserve functions/refs; correct X5R/X7R/C0G and C3 metadata identified in audit |
| NTC / connectors / protection / output blocker | Qualified exact MPNs open | Separate NTC and connector MPNs; retain recorded Eaton 10k/B3380 candidate only if cell thresholds fit; select keyed contacts/housings, fuse and cables as complete assemblies |

TME.eu is preferred. Manufacturer links are alternative identification/procurement references, not availability promises. Carry forward accurate existing `Source`, `Bought`, `Parameters`, `LCSC Part`; add `Manufacturer`, `MPN`, `AssemblyProfiles`, `PopulationGroup`, `DNPReason`, `VoltageRating`, `CellCount` and BOM revision where relevant. The compact table is a preliminary BOM, not a purchase order. New references, orderable passive values and all package mappings await the later schematic/BOM work.

## Assembly/configuration controls

1. Generate a BOM from the shared design for exactly one base + overlay. Record fitted MPN/value/profile; no hand-edited layout forks. Q parts require explicit P/DNP state in the exported assembly BOM—never an ambiguous “optional” purchasing line.
2. Cross-check charger identity, cell count and RPROG value/frequency with the profile. Use an assembly-ID strap network or read-only identification scheme on safe MCU GPIO/ADC; exact encoding/pins open. It shall not backfeed the main domain in USB-only operation or conflict with boot straps.
3. Future firmware checks physical IC PN/revision and assembled profile before enabling charge. Identity is not a reliable way to autodetect an incorrectly attached pack; use keying/labels, pack qualification and voltage plausibility checks. Never automatically raise CELL from 2S to 4S to accept an unexpected pack.
4. Charging starts disabled; factory/native USB programming does not arm CE. Program/configure the matching profile, verify readback and perform low-current functional checks before loading qualification settings. The firmware will need a separately reviewed C3 target; none was changed here.
5. Validate every fitted and DNP group's connectivity, including missing regulator feedback parts, output blockers, pull-ups and test headers. Include variant-aware ERC/DRC/parity and manual electrical review. One DRC pass does not qualify all BOMs.
6. Record prototypes with board/BOM revision, base/overlay, source, pack/cells, NTC, load, ambient and logs. Only after R08 tests may the variant gain an approved continuous rating or bulk-reduction decision.

## Open decisions and phase boundary

Phase2 is authorized in small stages, beginning with charger/power-stage schematic and F01. Remaining selection/verification: CE bias/reset and charger-only2A risk versus actual cells; BQ792/798 package/register map; input fuse/polarity/transient ratings; exact MCU/identity GPIO and passive MPNs; optional5V reverse blocker; fab/enclosure/connector ratings. PMID backup development/qualification is deferred. See [Phase2 progress](V4_PHASE2.md); no release approval is implied.
