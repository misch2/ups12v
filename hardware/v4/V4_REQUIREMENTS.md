# V4 requirements — Phase 1 review baseline

2026-10-10 · Based on accepted [Phase 0 audit](V4_AUDIT.md), commit `031cd81`, and its [evidence](evidence/README.md). User direction in Phase 1 supersedes preliminary Phase 0 adapter/load assumptions. **Owner decisions incorporated; Phase 2 authorized in small reviewable stages.** “Shall” is an acceptance requirement; proposed ratings remain prototype qualification targets. This is a personal hobby project: prioritize reliable UPS operation, battery safety and maintainability without adding circuits for hypothetical misuse.

## Scope and document ownership

| Document | Owns |
| --- | --- |
| This document | Electrical envelopes, safety behavior and acceptance criteria |
| [V4_ARCHITECTURE.md](V4_ARCHITECTURE.md) | Alternatives, recommended implementation, trade-offs, verification gates and tool status |
| [V4_VARIANTS.md](V4_VARIANTS.md) | Single-PCB assembly profiles, population groups and configuration identity |
| [V4_AUDIT.md](V4_AUDIT.md) | Historical findings and unchanged baseline evidence |

## R01 — One PCB and preservation

Exactly one V4 schematic/PCB design shall cover BQ25792/BQ25798 and 2S/4S through mutually exclusive IC/PROG population and optional blocks. Preserve V2/V3 production files. V4 shall have principal variable-voltage VSYS/GND terminals, optional labeled PMID test access, optional 5V/GND, battery/NTC and adapter connections. No onboard fixed12V converter, PD Source controller or PD Sink/trigger circuit. Later external PD triggers connect to the adapter terminals within the same electrical limits; programming USB remains separate.

## R02 — Mandatory F01 correction

Connect the local VBUS bank (legacy references C7/C13/C16) to the **actual IC VBUS node**, downstream of the BQ input FETs, and return it to the intended low-inductance power ground. VAC1 sensing shall see the appropriate protected adapter node; preserve the verified single-input VAC2 arrangement unless the reference review justifies a change. Rename/merge misleading nets deliberately, preserving reference mapping. Required evidence: future schematic pin-to-net export showing IC1.2/.3 and the VBUS capacitors on the intended node, net-tie traversal where retained, PCB copper readback, ERC, DRC and parity. A matching but floating capacitor-only net is a failure even with zero unrouted items. [Confirmed baseline](evidence/phase0-main/main-nets.csv).

## R03 — Adapter voltage, protection and derating

Normal operation shall support regulated 5, 9, 12, 15 and **20 V nominal** adapters with ±5% or better tolerance: **4.75–21.0 V at the connector**, including ripple. Lower-power sources are load-limited. 24 V nominal adapters and accidental 25/30 V connections are outside scope; there is no survival test for them.

Use basic input protection, appropriate input/pack fusing and the protected balanced battery BMS. Preserve the BQ-controlled input FET function unless reference analysis justifies a change. **No complex active input OVP/eFuse is required.** Do not add one solely to cover excluded adapters.

Rate all input parts for 21 V continuous plus credible hot-plug/ringing from supported adapters. Determine that waveform with the actual cable/source; add damping or a clamp only where evidence requires it. The former 22 V trip, 23 V protected ceiling and 30 V/100 ms survival stimulus are withdrawn. Use ≥35 V input/PMID capacitors (50 V MLCC where Ceff requires); replace legacy 20 V POSCAPs. At 21 V, a 25 V cap exceeds the retained 80% voltage-use target. Retain AON7528 provisionally, subject to VDS/VGS, SOA and actual transient review. No fictitious protected-node ceiling may justify its rating. Verify fuse, connector, wire, polarity and thermal coordination.

Normal input profiles target ≤3.0 A; the IC-level continuous ceiling is ≤3.3 A, with lower assembly/source/wire/fuse/thermal limits taking precedence. [BQ25798 Rev. C §6.1/6.3](https://www.ti.com/lit/ds/symlink/bq25798.pdf).

Program input-current limits with positive IC tolerance included: the possible actual current shall not exceed the qualified source, connector or 3.3A ceiling. A nominal 3A register value is not automatically valid for a 3A adapter. Establish an assembly-specific hardware input-current bound where practicable; the inherited ILIM_HIZ-to-REGN tie alone is not a source-matched limit. Hardware/software input limiting and BQ charge-current limiting are distinct functions.

## R04 — Battery, charge startup and failure behavior

Use protected, balanced 4.2 V/cell Li-ion packs with a qualified NTC and pack/wire/fuse ratings. Intended loaded pack ranges: 2S approximately 6.4–8.4 V; 4S approximately 12.8–16.8 V, before detailed sag and temperature characterization. The BQ is not a cell-balancing/BMS replacement.

**All assemblies shall power up with charging disabled by hardware: `/CE` HIGH.** Remove the legacy CE pull-down behavior in V4; never label CE as RESET. Active-low CE disables charging when high; it is not an isolation switch for the battery, input, SYS or PMID. SYS must be able to start the normal MCU supply while CE is high, without depending on an already-running MCU to enable the charger power path.

BQ25792 2S has a **2 A POR charge-current setting**, despite a planned lower host current. RPROG sets cells/frequency, not an arbitrary charge-current cap. Hold CE high during power-up, reset, bootloader, programming, missing MCU, invalid profile, absent/invalid pack or NTC, power-domain failure and charger communication failure. Bias CE from a charger-owned rail valid before charging is possible, with a normally-off open-drain sink, gate pull-down and verified MCU reset behavior. Prove the bias startup timing; a slow VSYS-derived 3V3 pull-up alone is insufficient.

Only allow charging after part/cell/profile identity, pack/NTC validity, source budget, current/voltage limits and readback pass. Initial nominal ICHG target is **0.5 A or less for either pack**, subject to actual cell limits and available power. Keep CE high while programming or resetting registers, changing cell count, and recovering from faults. Leave all hardware temperature protection active.

Use a simple MCU-controlled open-drain pull-down; reset/bootloader/unpowered MCU shall release it. **No external 250 ms watchdog/lease circuit** is selected or required without a specific demonstrated safety need. A stalled MCU that holds the sink on is a residual risk; normal MCU watchdog recovery and firmware fault handling are to be verified, not presented as an independent hardware charge cutoff.

**BQ25792 charger-only reset risk remains:** with CE already low, POR/register reset/internal watchdog expiry can restore 2 A in 2S before host detection. Software-selected 0.5 A is not a hardware ceiling, and a pack BMS need not limit charge to 0.5 A. Record actual cell charge limits and reset behavior; do not qualify a pack for a profile that can exceed its allowed current. Pack choice, lower-current-tolerant operation or an evidence-justified cutoff remains a qualification decision, not a mandatory lease circuit.

Verify CE logic thresholds, startup sequencing, battery-only REGN-off behavior and bias limits for **both ICs** before implementing CE. See [CE review](V4_CE_REVIEW.md) for manufacturer evidence, calculation assumptions and outstanding measurements. Default-off CE must leave SYS available to start the MCU; never pull CE directly to BAT/SYS (up to 16.8/18 V) or to USB-powered MCU3V3.

## R05 — Loads and power budgets

| Profile | Qualification target | Shared budget and restrictions |
| --- | --- | --- |
| 2S / 5V | Optional onboard 5 V, **2 A continuous / 10 W** | No 12V/3A requirement. Allow 1.5 W SYS auxiliary reserve for monitoring and isolation; qualify this reserve by measurement. |
| 4S / VSYS | External regulated 12V/3A installation is a **36 W load target** | At assumed 90% external-converter efficiency needs 40 W at SYS, plus 1.5 W auxiliary reserve. Converter remains external and must tolerate full SYS range. |
| Optional5V with another load | 10 W maximum output target | Counts in the same total battery/input/thermal budget; never add independent output maxima without recalculation |

For planning use conservative **90% per converter stage** and 1.5 W total SYS auxiliary reserve. These are assumptions, not efficiency measurements. Equations:

```text
P_SYS_load = Σ(P_delivered_output / η_downstream) + P_aux
P_charge   = V_pack × I_charge
P_SYS_load + P_charge ≤ η_BQ × V_adapter × I_adapter_allowed
I_pack ≈ P_SYS_load / V_pack       (SYS battery-path drop adds loss)
```

| Source and example load | BQ converted budget | SYS load / remaining charge budget at full pack |
| --- | ---: | --- |
| 5V/3A; 2S 5V/2A load | 13.50 W | 12.61 W / 0.89 W ≈0.10 A at 8.4 V, before extra margin; prioritize load, reduce charging |
| 12V/2A; same 2S load | 21.60 W | 12.61 W / 8.99 W; 0.5 A charge uses 4.2 W, leaving 4.79 W planning margin |
| 12V/3A; 4S external12V/3A | 32.40 W | 41.50 W load exceeds source budget; battery assistance/discharge occurs, so unsuitable for sustained full load |
| 20V/3A; same 4S load | 54.00 W | 41.50 W / 12.50 W; 0.5 A charge uses 8.4 W, leaving 4.10 W planning margin |

Recommended 2S full-load adapter is12V/2A. With a5V/3A adapter, use a planning profile of **5V output≤1.5A and charge≤0.25A**, subject to real efficiency/source tests. At−5% adapter voltage and90% stage assumptions this leaves `4.75×3×0.9 − (7.5/0.9+1.5) − 8.4×0.25 = 0.89W` margin. A5V/2A output from that same5V source has little margin and shall reduce charging to zero as necessary; it is not the guaranteed full-load charging profile. The programming USB port never substitutes for this main5V adapter connection.

The table uses the adapter's full nameplate current as an **upper-bound planning budget**, before current-limit accuracy/headroom. Example with only 2.7A usable: at 19V, the 4S budget becomes 46.17W, leaving 4.67W for charge (about 0.28A at16.8V); a 0.25A target is more credible than guaranteeing0.5A at full load. At4.75V/2.7A, the derated 2S load leaves1.71W for charge; use≤0.1A initially rather than promise0.25A. Minimum usable current, actual efficiency and load tolerance still need qualification. These examples do not prescribe a register value or claim2.7A is a guaranteed IC limit. Adaptive charging may reduce to zero; sustained load capability must be tested at the worst allowed source voltage/current.

At nominal low-pack voltage: 2S target approximately 12.61/6.4 = **1.97 A**; 4S target 41.5/12.8 = **3.24 A**, plus path loss/tolerance. The 4S forward converter must also respect total SYS + charge current, not just watts. At 12.8 V SYS and 0.5 A charge, approximately 3.24+0.5 = 3.74 A before tolerance, below the 5 A IC-level output recommendation; this still needs thermal qualification. Adapters at −5% tolerance and actual efficiency reduce the margins. Charge current shall decrease before starving the critical load. Firmware must report sustained battery supplementation rather than treating adapter presence as proof of adequate power.

## R06 — MCU and regulators

Official ESP32-C3-MINI-1 module; candidate N4X, final suffix procurement/land pattern open. Normal 3V3 from VSYS shall qualify over **6.0–18.0 V** continuous, including low-pack droop reserve and full-charge SYS offset. This is a converter qualification range, not permission to discharge cells below the pack limit. Specify normal 3V3 ≥1 A capability, steady MCU voltage 3.3 V ±5% including mux loss, and remain within 3.0–3.6 V whenever reset is released. Prefer a 30 V input-rated buck class; check actual SYS transient envelope against BQ and regulator limits. SYS/BAT caps ≥25 V subject to specified rail peaks and Ceff; no raw-input transient shall be assumed to pass harmlessly to SYS.

USB branch shall support ≥0.5 A converter output capability with current drawn limited to the source's actual allowance; USB-only mode disables Wi-Fi by default. A higher branch IC rating does not grant higher USB power. Optional5V independent VSYS buck shall regulate 5 V ±5% at 2 A over 6.0–18.0 V, including low-end dropout/load steps. Both USB and optional5V are separate from the normal buck input. Optional5V shall include reverse-current blocking if its connector is externally energized, whether intentionally or during a fault. [Espressif module supply specification](https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html).

## R07 — USB-only programming and complete isolation

Fully assembled board shall enter C3 ROM USB download and flash using only a data-capable USB cable, with no adapter/battery, charger absent or I²C held low. No Wi-Fi, charger initialization, main-rail enable or application software may be required to enter recovery. Reserve native USB GPIO18/19, BOOT/RESET, correct straps and UART fallback. Do not provision eFuses that disable the required recovery paths. Provide separate CC resistors, USB ESD/VBUS protection and documented source-current/inrush behavior; no programming-port connection to BQ BC1.2 D+/D−.

Hardware shall block back-power from MCU/USB into normal3V3, SYS, PMID, BAT, VIN and optional5V, and from normal power into USB VBUS. Review regulator outputs, mux controls/status, I²C pull-ups/buffers, CE, INT, STAT, voltage dividers, enable/PG/control lines, UART and test headers. No ordinary GPIO high-Z assumption substitutes for powered-off isolation. Ground remains common; galvanic isolation is not required.

Prototype acceptance target at 25°C, settled for 1 s, with absent sources: aggregate DC injection into the unpowered main domain **≤10 µA**, each sensitive interface also within its IC's specified powered-off limits. An unpowered rail with a temporary 10 kΩ test load shall remain ≤0.1 V; a floating capacitive rail voltage alone is not a sufficient leakage measurement. Check worst temperature using **maximum**, not typical, component leakage; record dynamic reverse pulses separately and prove they do not wake the charger or energize a load. If candidate devices cannot meet this budget, change hardware or explicitly revise the requirement at review. No zero-leakage assertion is made.

Mixed-source insertion/removal shall not reset the MCU or latch charging on. Firmware diagnostics (future change) shall bound retries and report charger absent independently of Wi-Fi; native ROM recovery remains independent of that firmware requirement. [Espressif reset/USB guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html).

## R08 — Capacitors, thermal, mechanical and verification gates

Keep 2.2 µH / 750 kHz provisionally and mandatory ceramic/REGN/bootstrap/BATP/SDRV support. Initial design and qualification use VSYS exclusively for both charger ICs. PMID testpoints and DNP backup footprints may be retained; do not develop or qualify PMID backup in this phase. The original PMID concept assumed approximately equal adapter and backup output voltages. Keep mandatory forward-mode PMID ceramics; optional bulk DNP requires SYS-mode Ceff/transient evidence. Verify effective capacitance at operating bias/temperature, ripple/ESR, hot-plug and load response. Replace 20 V POSCAPs for the 20 V adapter envelope. Do not infer current capacity from widths or via count.

Start from four layers; confirm fab/copper/plating/stackup, nonzero fabrication floors and separate DC power/SW/bootstrap/analog/digital/USB constraints. Preserve M3 function with screw/standoff keepouts; antenna keepout on every layer, accessible USB, keyed polarity, clear rail labels and power/control testpoints. Exact outline/enclosure/connector ratings remain open.

Before release, pass ERC/DRC/parity with every variant reviewed and all suppressions explained; independently verify F01 and partial-power connectivity. Qualify loss/recovery, charging+load, low pack, BQ792 pack removal/BMS opening, NTC open/short, USB-only/combined sources, reverse current, optional5V DNP/backdrive, RF under load and enclosure thermals. State hardware/BOM/cells/source/load/ambient/cables and measurement limits. No checks or measurements are claimed complete merely because they are specified here.

## Authorized Phase 2 boundary

Use hardware/v4/ups_v4/ as the only V4 CAD target, on a V4 development branch. V2/V3 are read-only references. Start with the charger/power-stage schematic and F01, then present each coherent stage with exported connectivity, ERC and diff evidence. Before any live PCB mutation, Konnect IPC must confirm the exact full path of the V4 PCB; never operate on an unspecified current board. Run DRC/parity when the matching PCB exists and is affected; both ERC and DRC remain release gates. See [Phase 2 progress](V4_PHASE2.md).
