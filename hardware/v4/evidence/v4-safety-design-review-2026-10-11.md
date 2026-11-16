# UPS V4 safety-design decision checkpoint

2026-10-11. **Architecture decisions CLOSED by explicit owner decision; physical qualification OPEN.** Retain R12/C26 and the existing default-off CE control. No active OVP/eFuse, independent 0.5 A limiter, supervisor or external charge watchdog is selected. This checkpoint authorizes documentation only, not routing, fabrication, purchasing or power-up.

## Authority and evidence

The latest owner update supersedes contradictory historical requirements: retain 2 ohm/2.2 uF damping; use **2S1P with two 18650 cells**, or **4S1P with four**, never assume 2S2P. The owner accepts BQ25792's possible 2 A charging default subject to qualification of the cells, complete pack, BMS and wiring, including tolerances and temperature. Normal firmware ICHG remains nominally 0.5 A or lower according to source/pack conditions. This is not a hardware 0.5 A ceiling.

Reviewed AGENTS, current handover, requirements/architecture/variants/BOM, V4_CE_REVIEW, phase3-5 CE truth table, phase3-vac1-review and phase2-6-hotplug-envelope. Historical calculations and source observations are reused with their stated limitations. Fresh native KiCad 10.0.7 **saved-board read**, [geometry evidence](safety-review-native-read.json), and [fresh schematic netlist](safety-review-current.net.xml) establish the actual connections. Konnect confirmed the exact V4 board open over IPC; this does not turn the saved-board geometry into a live export. All **445 pin/net mappings** match the Nano-Fit checkpoint. [Verification](safety-review-verification.json) confirms unchanged schematic/PCB/checkpoint-netlist hashes; 154 footprints, 243 tracks, 135 vias. No CAD mutation or new ERC/DRC run; retain the checkpoint's existing incomplete-board checks and limitations.

## A. VAC1 hot-plug

**Manufacturer basis.** [TI SLUAAL8, May 2023, §3/Fig.3-1 p.4](https://www.ti.com/lit/an/sluaal8/sluaal8.pdf) recommends a 2 ohm anti-surge resistor in series with 2.2 uF as a shunt, plus local 0.1 uF. It describes suitability for common adapter cables, with application-specific adjustment possible; this is guidance, not a guaranteed transient bound. [BQ25798 SLUSDV2C, June 2026, §§6.1/6.3,7.3.3,7.3.5](https://www.ti.com/lit/ds/symlink/bq25798.pdf) gives VAC1 −2 to +30 V absolute limits and 24 V maximum recommended VBUS operation. BQ25792 SLUSDG1D §7.1 has the same VAC1 limits. A 30 V stress limit is not a permissible operating target; the VAC1 table grants no positive-duration exception.

**Actual implementation.** J1.2 → F1 → VIN1. VIN1 feeds IC1.9 VAC1, C9 100 nF/50 V, R12 → C26 → PGND, and Q1 drain. Q1/Q2 AON7528 are common-source back-to-back input FETs; Q2 drain reaches VBUS through NT4. C13/C16 (10 uF each) and C7 are at VBUS; C12/C15/C18 and C6 are at PMID, not all directly across VIN1 at cold insertion. R12 carries transient shunt current, not the continuous load. F1 is not a clamp; D1 is a gate clamp. Opening Q1/Q2 cannot isolate VAC1 from VIN1 ringing.

The shunt leaves F1 before the long input feed. R12→C26 copper is approximately 7.08 mm; C26 PGND has nearby vias at (33.9,52.6)/(33.9,53.3). In1 is the checkpoint's continuous PGND reference; power return does not pass through NT1. This supports the intended return topology, not a measured inductance. C9 is physically near IC1 but its VIN1 path goes via (51.6,68.5), the Y74 sense trunk and (60.5,69.4), approximately 26 mm electrically versus 4.9 mm direct pad separation. Thus connector damping and pin decoupling must not be modeled as one ideal zero-impedance node. During a later authorized layout review, favor a short C9–VAC1 connection and local return; no geometry is changed or newly approved here.

R12 remains Vishay CRCW12062R00JNEAHP, 2 ohm 5%, pulse-proof 1206; C26 remains KEMET C1210C225K1RACTU, 2.2 uF/100 V X7R 10%, 1210. [Vishay 20043 Rev17-Mar-2026, pp.1,5–6](https://www.vishay.com/docs/20043/crcwhpe3.pdf) specifies pulse curves separately from its 0.75 W steady rating. [Vishay 28810, 30-Jun-2023, §2.2](https://www.vishay.com/docs/28810/pulseloadhandling.pdf) supplies equal-peak/equal-energy rectangular pulse comparison. The existing exact KEMET curve review found typical 11–13% DC-bias loss at 21 V; the historical 1.226–2.783 uF sensitivity range includes additional assumptions, not guaranteed Cmin. A 100 V nameplate is not proof of damping. Prior ideal-step pulse screening does not qualify all ringing/bounce pulses.

**Bounded analysis.** [Reproducible passive model](safety_hotplug_model.py) and [all 62 cases](safety-hotplug-model.json) separate connector/snubber, VAC1/C9 and switched VBUS nodes. Assumptions: ideal charged 21 V source; cable 0.2/1/3/10 uH with selected 0.05/0.2/0.5 ohm combinations; fixed C26 Ceff 1.226 or 2.2 uF; C9 0.1 uF; assumed feed 50/150 nH, shunt 20 nH, 1 nF connector parasitic; FET-on resistance plus ESR 20 milliohm and 10/20 uF downstream. These are sensitivity points, not extracted parasitics or a supported-cable specification.

| Selected condition | Calculated VAC1 peak | Interpretation |
|---|---:|---|
| FET off, 1 uH/0.2 ohm, C26 1.226 uF, feed150 nH | 22.90 V | Existing damping can be effective |
| FET off, 3 uH/0.2 ohm, same C/PCB assumptions | 25.67 V | Source variation matters |
| FET off, 0.2 uH/0.05 ohm, same assumptions | 32.85 V | Distributed parasitic resonance can defeat lumped-node intuition |
| FET off, 10 uH/0.05 ohm, same assumptions | 30.47 V | Unmeasured high-L/low-R sensitivity, not an established ordinary-cable worst case |
| FET on, all caps initially20 V, source21 V, 28 cases | 21.03–21.81 V | Precharged reinsertion differs materially from cold insertion |
| FET held on with discharged downstream caps, 3 cases | 24.14–34.12 V | Stress sensitivity; not proven to occur with the real driver |
| Abrupt FET enable after VIN/snubber settle21 V, VBUS initially0 | 24.01–33.09 V | Driver slew, body diodes and protection response must be represented/measured |

The passive equations pass numerical energy-balance checks and worst-VAC sampling refinement (<0.02 V difference). They omit nonlinear capacitor bias, adapter control/output-capacitor dynamics, diode clamps, real ACDRV slew/OVP, ground bounce, converter load and time-varying contact bounce. The known typical 5 ms startup detection delay does not characterize every battery-powered reinsertion. Hence calculated over-limit cases identify sensitivities, **not demonstrated board damage or measured voltage peaks**. R12 sampled maxima are 336 W peak and 0.493 mJ energy (different cases); equal-energy widths are retained per case for manufacturer-curve checks. Pulse repetition, hot film temperature and actual waveforms remain unqualified.

**Decision / impact.** Retaining the existing passive topology and values is a defensible **prototype architecture choice**, consistent with TI and now explicitly approved. It does not prove universal immunity for every regulated 21 V source. No component or PCB change is selected at this checkpoint. Neither the old 39.725 V calculation nor this model justifies automatically adding active protection. First address layout impedance and test the retained network; passive tuning would require new evidence and owner review if actual deficiencies appear.

**Remaining tests.** Use a separate damping/input fixture before exposing the charger to an unqualified transient. Reproduce both cold FET-off insertion and controlled turn-on/precharged reinsertion; include short low-resistance and representative longer cables, regulated source tolerance/ripple up to21 V, realistic load and contact bounce. Record source impedance/output capacitance where possible. Probe at J1, VAC1 relative to IC ground, VBUS, Q1/Q2 VDS/VGS and R12 current with short differential/ground connections and sufficient bandwidth. Check positive/negative peaks, ringing, input/PMID limits, FET stress and resistor pulse/repetition/drift. [AON7528 Rev1.0 Oct2023 pp.1–2](https://aosmd.com/pdfs/datasheet/AON7528.pdf) has 30 V VDS and ±20 V VGS; its separate 36 V/100 ns spike rating cannot be transferred to VAC1. Hardware margin must include measurement uncertainty; no new mandatory 27 V threshold is imposed.

## B. BQ25792 2S1P default current

**Exact manufacturer evidence.** Catalog BQ25792 PDF links returned404. TI support publicly supplies [SLUSDG1D, April2026](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/SLUSDG1_3D00_4_3D00_TI-PDF_3D00_en_2D00_us-_2800_2_2900_.pdf); [provenance](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1638147/bq25792evm-bq25792-datasheet-and-question). The PDF bears a confidentiality footer despite this public TI attachment; record its provenance/revision rather than mislabeling it Rev C. TI also reports custom-product status; no assembly support or procurement decision changes here. Relevant tables are retained in [local extract](safety-bq25792-extract.json).

| Event | Datasheet behavior for correctly configured2S |
|---|---|
| True charger POR | §8.3.1–2, Table8-2: reads PROG; ICHG=2 A, VSYSMIN=7 V, VREG=8.4 V |
| Internal watchdog expiry | §8.4.1 and REG03 Table8-16: ICHG resets; REG0F EN_CHG resets to1 |
| Software REG_RST | §8.4.2 and those register tables: restores ICHG/EN_CHG defaults; does not repeat first-POR FET detection |
| CELL setting changed | §8.3.2: ICHG/VSYSMIN/VREG reset to defaults for the new cell count; hold CE HIGH first |
| Host services WD_RST normally | Restarts watchdog timing; this alone is not an ICHG reset |
| Adapter unplug/replug while battery sustains charger bias | Not automatically a true POR; do not equate it with total charger power loss |

REG10 watchdog default is40 s (Table8-26); timeout is a host-communications interval, **not a maximum duration of subsequent2 A charging**. With CE LOW and default EN_CHG=1, charging is allowed when the other normal source/battery/temperature conditions permit. Default-mode charging can continue autonomously. Input limiting, thermal regulation or CV can reduce current but do not promise0.5 A.

**Actual CE / credible scenario.** R9 pulls CE_N to the D3/D4 REGN/MAIN diode-OR bias. Q3 sinks CE, with R10 gate discharge. Q5 sources gate drive from MAIN only when series Q6/Q7 conduct; Q6 is MAIN-biased, Q7 is driven from GPIO0 through R46 with R47 pull-down. R44/R53 restore/limit Q5 base drive. Thus MCU reset/high-impedance releases charging, USB-only cannot supply the enable drive, and MAIN loss releases it; analog sequencing still needs measurement. A charger reset/expiry need not reset the MCU or remove MAIN, so a retained GPIO HIGH can leave Q3 on. A stalled MCU after0.5 A configuration followed by charger watchdog expiry can therefore allow2 A until another condition stops charge. No short firmware response time is assumed.

**Resolution / impact.** Qualify a2S1P pack capable of this sustained default-current condition. Each series cell carries the full charge current; four cells are4S1P, not a current-sharing workaround. §7.5 p.12 lists +8% at2 A boost and +3.5% at2 A buck, VBAT8 V, TJ−40…85°C: corresponding screens are2.16/2.07 A. These table conditions do not establish every operating corner or transient. Prefer comfortable current headroom rather than a pack marked exactly2 A with no tolerance allowance. Keep nominal0.5 A firmware and default-off CE; no independent current-limiting hardware is warranted for an appropriately qualified pack.

Feasibility example only: [Molicel INR-18650-P28A product sheet v1.3 p.1](https://www.molicel.com/wp-content/uploads/INR18650P28A_1.3_Product-Data-Sheet-of-INR-18650-P28A-80093.pdf) specifies2.8 A standard charging and0–60°C charge temperature. This shows a two-18650 solution is practical, but selects neither this cell nor a finished pack. It does not establish full-current allowance at every temperature, pack thermal behavior, default voltage tolerance or BMS/NTC compatibility. No purchasing research or new PCB BOM component selection was performed.

Still record exact pack/cell MPNs and authenticity,2S1P construction, manufacturer current-versus-temperature/voltage conditions, CC/CV voltage tolerance, BMS continuous **charge** rating/temperature sensing/balancing and trip behavior, welds/contacts/wire/fuse ratings and NTC placement. Confirm default8.4 V regulation accuracy and cell imbalance against allowed individual cell voltages; current qualification alone is not full pack qualification. A generic BMS overcurrent trip, PROG resistor, IINDPM or firmware setting is not a hardware charging-current ceiling.

Prototype tests must force POR, watchdog expiry, REG_RST and controlled CELL reconfiguration with CE LOW and HIGH, then measure actual battery current, CE, MAIN, SYS and register recovery. Start with a battery simulator/protected fixture before real cells. Test at allowed pack temperatures/SOC, source/load extremes and pack removal/BMS opening. Verify default-off startup/MCU reset, battery-backed SYS independent of MCU, USB-only ROM recovery and isolation. Do not disable SYS or add series battery resistance as a charging workaround.

## Safety-gate disposition

| Milestone | Status |
|---|---|
| Architecture choice before further routing | **CLOSED**: retained R12/C26 and CE; accepted qualified2S1P/default-current approach. No layout restart is authorized. |
| Detailed layout / electrical qualification | **OPEN**: input/sense/return parasitics, final pulse/Ceff checks, actual pack identities and ratings; preserve Nano-Fit and switching-loop checkpoints. |
| Fabrication release | **NOT AUTHORIZED**: review qualification evidence and unresolved footprint/population risks, complete layout and ERC/DRC/parity plus other existing release checks. The owner did not waive these by closing architecture. |
| First charger/real-pack power-up | **NOT AUTHORIZED**: use separate fixtures to establish safe input/charging stimuli and approve a controlled bring-up plan first. |
| Normal hardware operation | **OPEN**: matching-prototype hot-plug, charging/default-current, temperature and power-path validation required. |

Some physical data can be gathered on fixtures before fabrication; measurements requiring the actual PCB necessarily follow controlled bring-up. No circular requirement to measure a fabricated V4 before it exists is asserted. Retain revision/BOM, exact cells/BMS, source/cable, load, ambient, probe setup and raw logs. Calculations and CAD checks are not measured safety.
