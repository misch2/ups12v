# V4 requirements — current owner-approved baseline

2026-10-10 · Based on accepted [Phase 0 audit](V4_AUDIT.md), commit `031cd81`, and its [evidence](evidence/README.md). User direction in Phase 1 supersedes preliminary Phase 0 adapter/load assumptions. **Owner decisions incorporated; Phase 2 authorized in small reviewable stages.** “Shall” is an acceptance requirement; proposed ratings remain prototype qualification targets. This is a personal hobby project: prioritize reliable UPS operation, battery safety and maintainability without adding circuits for hypothetical misuse.

## Scope and document ownership

The owner's 2026-10-10 simplification decisions supersede conflicting historical Phase 3.2 proposals and evidence. USB is service-only; OTA is routine; MCU source-transition restarts are acceptable. No external charge timeout, latch, D flip-flop or fresh-edge authorization is required. Historical evidence records prior states, not current normative requirements.

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

The separate VAC1 hot-plug transient concern remains unresolved and blocks fabrication/power-up: supported 20 V nominal adapters can excite cable/input ringing; VAC1 has a 30 V absolute maximum. The hypothetical 39.725 V model is not a measured or established board peak. See [bounded VAC1 assessment](evidence/phase3-vac1-review.md). Removing excluded-adapter survival requirements does not close this genuine component-limit concern.

Program input-current limits with positive IC tolerance included: the possible actual current shall not exceed the qualified source, connector or 3.3A ceiling. A nominal 3A register value is not automatically valid for a 3A adapter. Establish an assembly-specific hardware input-current bound where practicable; the inherited ILIM_HIZ-to-REGN tie alone is not a source-matched limit. Hardware/software input limiting and BQ charge-current limiting are distinct functions.

## R04 — Battery, charge startup and failure behavior

Use protected, balanced 4.2 V/cell Li-ion packs with a qualified NTC and pack/wire/fuse ratings. Intended loaded pack ranges: 2S approximately 6.4–8.4 V; 4S approximately 12.8–16.8 V, before detailed sag and temperature characterization. The BQ is not a cell-balancing/BMS replacement.

**All assemblies shall power up with charging disabled by hardware: `/CE` HIGH.** Remove the legacy CE pull-down behavior in V4; never label CE as RESET. Active-low CE disables charging when high; it is not an isolation switch for the battery, input, SYS or PMID. SYS must be able to start the normal MCU supply while CE is high, without depending on an already-running MCU to enable the charger power path.

BQ25792 2S has a **2 A POR charge-current setting**, despite a planned lower host current. RPROG sets cells/frequency, not an arbitrary charge-current cap. Hardware shall release the CE sink during MCU power-up/reset, bootloader, programming and missing/unpowered MCU states. Firmware shall release it on detected invalid profile, absent/invalid pack or NTC, power-domain fault or charger communication failure. This does not specify an independent external fault-detection timeout or fresh-edge interlock. Bias CE from a charger-owned rail valid before charging is possible, with a normally-off open-drain sink, gate pull-down and verified MCU reset behavior. Prove the bias startup timing; a slow VSYS-derived 3V3 pull-up alone is insufficient.

Only allow charging after part/cell/profile identity, pack/NTC validity, source budget, current/voltage limits and readback pass. Initial nominal ICHG target is **0.5 A or less for either pack**, subject to actual cell limits and available power. Keep CE high while programming or resetting registers, changing cell count, and recovering from faults. Leave all hardware temperature protection active.

Use a simple MCU-controlled open-drain pull-down; reset/bootloader/unpowered MCU shall release it. **No external 250 ms timeout, charge latch, D flip-flop or fresh-edge authorization mechanism is required.** Firmware explicitly enables charging only after successful charger/profile validation and the checks above. A stalled MCU that holds the sink on is a residual risk; normal MCU watchdog recovery and firmware fault handling are to be verified, not presented as an independent hardware charge cutoff.

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

Official ESP32-C3-MINI-1 module; candidate N4X, final suffix procurement/land pattern open. Normal 3V3 from VSYS shall qualify over **6.0–18.0 V** continuous, including low-pack droop reserve and full-charge SYS offset. This is a converter qualification range, not permission to discharge cells below the pack limit. Specify normal 3V3 ≥1 A capability, steady MCU voltage 3.3 V ±5% including mux loss, within the module's 3.0–3.6 V operating range. Source-transition droop may cause a restart under R07; this is not a requirement for an external supervisor to hold EN low at every instantaneous voltage excursion. Absolute maximum limits still apply. Prefer a 30 V input-rated buck class; check actual SYS transient envelope against BQ and regulator limits. SYS/BAT caps ≥25 V subject to specified rail peaks and Ceff; no raw-input transient shall be assumed to pass harmlessly to SYS.

Use U3 TPS62933 for VSYS → MAIN_3V3 normal operation (3 A IC capability, approximately 1 A MCU supply requirement). Use a simple 3.3 V LDO for U4 USB_VBUS → USB3V3 service power; the second USB buck is superseded. Select a current-rated ≥0.5 A class LDO with dropout and thermal margin for ROM flashing, respecting actual USB allowance. U4 candidate is Diodes AP7361C-33E-13 (1 A class, SOT-223); its IC rating does not guarantee 1 A continuous service operation. USB-only programming/debug/recovery disables Wi-Fi. Qualify actual ROM load, inrush and PCB thermal behavior; do not infer source-current permission from the regulator rating. Optional5V independent VSYS buck shall regulate 5 V ±5% at 2 A over 6.0–18.0 V, including low-end dropout/load steps. Both USB and optional5V are separate from the normal buck input. Optional5V shall include reverse-current blocking if its connector is externally energized, whether intentionally or during a fault. [Espressif module supply specification](https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html).

## R07 — Service USB, power-domain isolation and MCU recovery

### Intended USB use

USB is a **service-only interface**, used for initial firmware programming, debugging and recovery. It is not part of normal UPS operation and does not need to be accessible from outside the enclosure. An internal USB-C connector accessible after opening the enclosure is acceptable.

Routine firmware updates shall use OTA. Native USB Serial/JTAG, BOOT/RESET and fallback UART access shall remain available for recovery.

Owner service clarification (2026-10-10): native ESP32-C3 USB Serial/JTAG is the primary and sufficient interface for programming, serial logging and debugging; USB-C supplies the MCU during USB-only service. Retain existing BOOT/RESET buttons. Optional emergency UART is only ESP_TX(GPIO21), ESP_RX(GPIO20), GND at2.54mm pitch near a board edge, copper footprints with no fitted header. No MCU3V3/MAIN_3V3 supply/sense contact belongs in that group; voltage-measurement pads are separate elsewhere. Do not add a duplicate pogo programming header. Additional signal pads require a concrete bring-up/diagnostic purpose; CE_N may remain a separate passive charger-domain charging-gate probe. UART uses3.3V logic on a powered target, external outputs highZ while off, no adapterVCC or undocumented supply input and no bypass of existing domain isolation. See current handover for references/orientation/keepouts.


The assembled board must support native ESP32-C3 ROM programming using only a data-capable USB cable, with no battery or main adapter connected and without requiring functioning application firmware or charger communication.

USB-only operation does not require Wi-Fi or normal UPS functionality.

### Power-domain isolation

Maintain the normal U3 VSYS-derived buck supply and separate U4 USB-derived 3.3 V LDO programming supply, selected through the retained U5 TPS2116 reverse-blocking mux. Prefer MAIN_3V3 when valid. USB-only ROM flashing must work without adapter or battery; the LDO is not a normal deployed supply. Keep BOOT and RESET service buttons.

USB power must not meaningfully back-power the normal 3.3 V rail, SYS, BAT, VIN, PMID, REGN or optional 5 V output. Normal power must not energize USB VBUS.

Review I2C, GPIO, charger-control signals, ESD structures and regulator/mux paths for unintended back-powering. Preserve powered-off-safe isolation where necessary. Hardware isolation shall not depend solely on firmware-configured GPIO states.

The previous aggregate 10 µA leakage limit is retained as a **prototype measurement target**, not an unconditional reason to add further supervisory or gating ICs. Actual back-power must not activate the charger, unintentionally energize the main domain, violate device absolute limits or create an unsafe operating state. Document measured leakage and justify any deviation from the target.

### MCU reset and source transitions

An occasional ESP32-C3 reset or reboot during USB/normal power transitions is **acceptable**.

Do not require guaranteed reset-free switching, large hold-up capacitance, slew-controlled load switches or external reset supervisors solely to prevent such resets.

Use the ESP32-C3 internal brownout detection and an appropriate manufacturer-recommended EN/RESET circuit as the baseline. An external supervisor may be introduced only when a concrete electrical requirement or demonstrated malfunction justifies it.

After power restoration, the MCU must restart reliably and recover normal monitoring functionality.

The main UPS power path and VSYS output must not depend on continuous MCU execution. An MCU reset must not itself interrupt the output while the adapter/battery conditions remain within the UPS's supported operating envelope.

Provide a simple physical ESP32-C3 RESET button, accessible during servicing. An external enclosure-mounted button is not required.

### Charging interaction

Charging must remain hardware-disabled by default. USB-only programming or MCU recovery must not inadvertently enable charging.

Firmware explicitly enables charging only after the required charger, pack, temperature, source and configuration checks have succeeded.

No hardware charge-authorization latch, heartbeat-expiry circuit or additional supervisor is required solely to enforce fresh authorization after every supply transition. Preserve the documented residual risks and qualified battery protections.

### Prototype acceptance

Verify USB-only ROM flashing, BOOT/RESET recovery, both supply paths, autonomous MCU restart, absence of unsafe back-powering and the unaffected main UPS output during MCU resets.

Measure normal-to-USB and USB-to-normal transitions, but do not treat an MCU reset during these transitions as a failure.

Do not infer power-up or fabrication approval merely from ERC or schematic review.

## R08 — Capacitors, thermal, mechanical and verification gates

Keep 2.2 µH / 750 kHz provisionally and mandatory ceramic/REGN/bootstrap/BATP/SDRV support. Initial design and qualification use VSYS exclusively for both charger ICs. PMID testpoints and DNP backup footprints may be retained; do not develop or qualify PMID backup in this phase. The original PMID concept assumed approximately equal adapter and backup output voltages. Keep mandatory forward-mode PMID ceramics; optional bulk DNP requires SYS-mode Ceff/transient evidence. Verify effective capacitance at operating bias/temperature, ripple/ESR, hot-plug and load response. Replace 20 V POSCAPs for the 20 V adapter envelope. Do not infer current capacity from widths or via count.

Start from four layers; confirm fab/copper/plating/stackup, nonzero fabrication floors and separate DC power/SW/bootstrap/analog/digital/USB constraints. Preserve M3 function with screw/standoff keepouts; antenna keepout on every layer, service-accessible USB (inside the enclosure is acceptable), keyed polarity, clear rail labels and power/control testpoints. Exact outline/enclosure/connector ratings remain open.

Before release, pass ERC/DRC/parity with every variant reviewed and all suppressions explained; independently verify F01 and partial-power connectivity. Qualify loss/recovery, charging+load, low pack, BQ792 pack removal/BMS opening, NTC open/short, USB-only/combined sources, reverse current, optional5V DNP/backdrive, RF under load and enclosure thermals. State hardware/BOM/cells/source/load/ambient/cables and measurement limits. No checks or measurements are claimed complete merely because they are specified here.

## Authorized Phase 2 boundary

Use hardware/v4/ups_v4/ as the only V4 CAD target, on a V4 development branch. V2/V3 are read-only references. Start with the charger/power-stage schematic and F01, then present each coherent stage with exported connectivity, ERC and diff evidence. Before any live PCB mutation, Konnect IPC must confirm the exact full path of the V4 PCB; never operate on an unspecified current board. Run DRC/parity when the matching PCB exists and is affected; both ERC and DRC remain release gates. See [Phase 2 progress](V4_PHASE2.md).
