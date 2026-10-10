# UPS V4 — Project Handover for Codex

## Your role

You are assisting with the design of a new revision of a custom battery-backed UPS, using KiCad 10 and the Konnect MCP integration.

Repository: https://github.com/misch2/ups12v

Work as an experienced electronics design reviewer with knowledge of power electronics, PCB layout, ESP32 hardware design, battery charging, and KiCad.

**Reliability and electrical correctness take priority over board size, cost, and aesthetics.**

Do not assume the existing hardware is perfect simply because it works. Equally, avoid changing proven circuits without a specific reason.

## 1. Project background

This is a hobby project for uninterruptible power supplies using 18650 Li-ion batteries.

Existing deployments include:

- A legacy 4S UPS using BQ25798 with PMID backup switchover for a 12V mini PC (up to approximately 3 A).
- Newer 4S and 2S systems using the VSYS power path.
- Applications including a mini PC, Wi-Fi router, Ethernet switch, ESP32, and Zigbee router.
- Input supplies and load requirements differ between installations, including 5V and 12V sources.
- Monitoring and control via ESP32, MQTT, Home Assistant, OTA, and syslog.

The original PMID backup architecture was found to be relatively fragile, especially during recovery from battery power to the primary adapter. Some firmware issues were identified and fixed separately.

The new design should primarily use **VSYS uninterrupted power**, while retaining the option to use PMID backup with BQ25798.

The goal is one compact, reliable, maintainable PCB that can be assembled in several configurations.

## 2. Existing KiCad projects

Start by examining:

- `hardware/v2-3/bq25798_module/` — main power board, schematic, PCB, and project settings.
- `hardware/v2-3/controller/` — separate ESP32 controller board.
- `hardware/v2-3/bq25798_breakout_board/` — earlier experiments and reference material.
- `software/ups/` — firmware, board configuration, and PlatformIO.
- `README.md` — project history and original design goals.

The existing main power PCB uses four copper layers.

It contains:

- BQ25798 charger.
- External input MOSFETs.
- 2.2 µH inductor.
- Ceramic capacitors.
- POSCAP and low-ESR electrolytic capacitors.
- M3 mounting holes.
- Power and control connectors.

The controller board currently uses a complete ESP32 development module and an external DC/DC module.

Do not modify the old production designs in place.

Create a new development branch and use `hardware/v4/` for the new design once the initial audit is complete.

The old KiCad files may originate from earlier KiCad versions. Preserve them and verify migration to KiCad 10 in a separate copy.

## 3. Non-negotiable V4 requirements

### One PCB, multiple assembly variants

There must be **exactly one physical PCB design**, shared by all configurations.

Variants should differ only in their BOM and component population, for example:

- BQ25792 versus BQ25798.
- 2S versus 4S batteries.
- Different PROG resistor values.
- Optional components marked DNP (Do Not Populate).
- Optional onboard 5V output supply.

Use KiCad's assembly-variant/BOM mechanisms or a clearly documented equivalent workflow.

Do not create separate PCB layouts for the variants.

### Battery charger

Preserve pin/footprint compatibility between BQ25792 and BQ25798, subject to verification against both TI datasheets.

Support:

- 2S Li-ion, approximately 6.4–8.4 V over the intended operating range.
- 4S Li-ion, approximately 12.8–16.8 V over the intended operating range.

Candidate PROG configurations at 750 kHz:

- 2S: 8.2 kΩ.
- 4S: 27 kΩ.

Verify these and all other cell-count-dependent settings against the datasheets.

The input power budget, voltage limits, current limits, charging behavior, and battery protection must be validated for each variant.

### Power outputs

Provide accessible, clearly labeled connections for:

- VSYS — principal uninterrupted, non-fixed-voltage power output.
- PMID — retained for BQ25798 compatibility and optional backup operation.
- GND.
- Optional regulated 5V output.

Do not assume PMID is a regulated battery-backed output when BQ25792 is installed.

PMID backup operation is optional, not the primary UPS architecture.

Do not integrate a fixed 12V output converter into the main PCB merely for one installation.

External converters are acceptable for high-power or variable-voltage loads.

### Integrated ESP32

Replace the complete ESP32 development board with an official Espressif surface-mount RF module.

Preferred candidate: **ESP32-C3-MINI-1**.

Evaluate suitability, availability, native USB programming, GPIO count, power consumption, and PCB antenna requirements.

The design must include:

- Proper 3.3V power supply.
- I²C connectivity to BQ2579x.
- Boot/reset circuitry.
- Convenient USB programming and debugging.
- A fallback UART programming interface or test pads.
- Antenna placement and RF keepout per Espressif reference design.
- Safe GPIO states during power-up and reset.

Retain the existing monitoring capabilities where practical.

### USB-powered standalone programming

**A fully assembled PCB must be programmable using only a USB cable, with no battery and no primary power adapter connected.**

This is an explicit requirement.

Design safe power selection/isolation between:

- The normal VSYS-derived 3.3V supply.
- USB-derived power used for programming and diagnostics.

Prevent reverse current from USB into:

- VSYS.
- PMID.
- The BQ2579x power stage.
- The battery or primary adapter.
- The onboard 5V output.

Also consider back-powering through I²C lines, pull-up resistors, GPIO protection structures, and regulator outputs.

Determine the appropriate implementation using a power mux, ideal-diode arrangement, or other properly specified solution.

USB programming must remain reliable when the charger IC is unpowered or unavailable.

The firmware should handle such conditions gracefully. Do not allow charger communication failures to prevent programming or recovery.

Include proper USB-C CC resistors, ESD protection, and a clearly documented programming procedure.

Verify native USB download/recovery behavior for the selected ESP32 module.

### Integrated regulators

Replace the external 3.3V power module with onboard components.

The 3.3V regulator must accommodate the full expected VSYS range in both 2S and 4S configurations, including relevant charging and transient conditions.

Prefer:

- High efficiency.
- Low quiescent current.
- Sufficient peak current for Wi-Fi operation.
- Adequate input voltage margin.
- Good component availability.

Also evaluate an **optional onboard 5V buck converter**, populated only in configurations that need it.

It should be powered directly from VSYS, independently of the 3.3V regulator.

Determine its suitable current rating and dropout margin, especially for 2S operation at low battery voltage.

Do not select regulators solely by their advertised maximum current. Review efficiency, thermal performance, availability, and reference layouts.

### Mechanical requirements

Design one physically practical PCB including:

- M3 mounting holes.
- Mechanical clearance for screw heads and standoffs.
- Convenient and clearly labeled power connectors.
- Suitable orientation of headers for external connections.
- USB accessibility.
- Testpoints for critical power rails and control signals.
- Reasonable separation of power circuitry and the RF module.

Prefer keyed or otherwise mistake-resistant connectors where practical.

## 4. Critical design-review work

### BQ25792/BQ25798 schematic review

Compare the existing design with current TI datasheets, application circuits, layout guidance, and reference designs.

Check:

- Correct connections and supporting components.
- Battery and input protection.
- External FET specifications and drive connections.
- Charging-current and input-current constraints.
- Startup and recovery behavior.
- PMID versus VSYS behavior.
- Stability and operation across the supported battery configurations.

Distinguish verified problems from potential risks and purely optional improvements.

### Inductor

The existing PCB uses a 2.2 µH inductor.

An existing TME reference appears to identify an Eaton `DR125-2R2-R` part.

Verify the exact installed component, then evaluate:

- Inductance requirements.
- Saturation current.
- RMS current.
- DC resistance.
- Temperature rise.
- Worst-case inductor ripple and peak current.
- Losses at the selected switching frequency.

Consider both 2S and 4S, the complete input voltage range, charging, and worst-case loads.

Do not change a working inductor without a documented reason.

### Capacitors

Review all input, PMID, SYS, BAT, bootstrap, and regulator capacitors.

Pay particular attention to:

- Effective MLCC capacitance under DC bias.
- Temperature characteristics.
- Voltage ratings and derating.
- ESR and ripple current.
- Placement and current loops.
- Requirements for stable converter operation.

The existing design contains POSCAPs on PMID, notably C20 and C22.

Investigate whether these can be **DNP in VSYS-only configurations**.

Retain suitable PCB footprints if needed for BQ25798 PMID backup mode.

Also investigate whether the additional low-ESR electrolytics on PMID are necessary, or can be reduced/replaced.

Removing expensive components is desirable only when electrical performance and reliability remain acceptable.

### PCB layout and thermal design

Do a thorough review against TI recommendations.

Focus on:

- High-current and high-frequency switching loops.
- SW1/SW2 copper geometry.
- Inductor and capacitor placement.
- PGND/GND handling.
- Thermal pads and via arrays.
- Copper planes and return-current paths.
- MOSFET placement.
- Current bottlenecks and narrow necks.
- RF interference with the ESP32.
- Thermal management at maximum continuous power.

The existing design has multiple ground vias, but do not assume their number or position is optimal.

### DRC and netclasses

Review the existing `.kicad_pro` rules.

Known areas worth investigating:

- Global minimum track width currently configured as 0 mm.
- Global minimum clearance approximately 0.05 mm.
- A broad POWER netclass that groups high-current nets together with SW and BTST signals.
- Multiple trace widths, from narrow signals to 1.5mm power tracks.

Design appropriate constraints based on electrical requirements and the intended PCB manufacturer's actual capabilities.

Separate functional classes where useful:

- High-current power.
- Switching nodes.
- Sensitive analog signals.
- I²C / digital signals.
- Ground and thermal connections.

Do not treat a track-width setting as proof of sufficient current capacity.

Review stackup, copper thickness, temperature rise, via current capacity, and the real geometry of power paths.

## 5. Component procurement and BOM

Preferred supplier: **TME.eu**.

Many existing schematic components have TME product URLs in the custom `Source` property. Other properties include `Bought`, `Parameters`, and `LCSC Part`.

Preserve and reuse existing procurement information when correct.

For proposed new or replacement components, provide:

- Manufacturer and exact part number.
- Electrical specifications relevant to the design.
- Package and KiCad footprint.
- Preferred TME product URL, where available.
- Alternative supplier or equivalent part if necessary.
- Reason for the selection.
- Which assembly variants use the part.

Do not invent supplier links, availability, prices, or technical specifications.

Prefer readily available components with documented electrical characteristics over obscure modules or poorly specified parts.

## 6. External USB-C PD output

The user owns SW3518-based USB-C PD Source modules.

These may be used externally, powered from a VSYS header.

Do not integrate a USB-C PD Source controller into V4 at this stage.

The connected device may use an external USB-C PD trigger acting as a Sink.

Document the relevant electrical constraints:

- SW3518 is buck-only.
- Available output voltages depend on actual VSYS.
- A 4S battery at 3.2V/cell nominally provides 12.8 V before load-related voltage drops.
- A 2S battery at 3.2V/cell nominally provides 6.4 V before load-related voltage drops.
- Regulation headroom and module input-voltage limits must be verified.

For fixed 5V critical loads, the optional onboard regulator may be preferable to an external USB-PD module.

## 7. Tools and workflow

Environment:

- KiCad 10.
- Codex.
- Konnect MCP: https://github.com/mixelpixx/Konnect
- Git/GitHub.
- KiCad CLI (`kicad-cli`).

Use Konnect where it provides reliable analysis or editing capabilities.

Verify the MCP connection and available tools rather than assuming all operations are supported.

For critical design modifications:

1. Inspect the current schematic/PCB state.
2. Explain the intended change and its technical justification.
3. Apply a small, coherent group of modifications.
4. Re-run relevant ERC/DRC checks.
5. Inspect the generated netlist/layout and confirm no unintended changes.
6. Review the Git diff before committing.

Do not consider passing ERC/DRC sufficient proof of electrical or thermal correctness.

Use current TI and Espressif datasheets as primary engineering references.

Record datasheet revision, section, and link for important decisions.

Preserve stable reference designators where possible to simplify comparison with older revisions.

Do not silently change established firmware behavior or hardware interfaces.

Use Git commits at meaningful milestones. Never overwrite the known-working V2/V3 layouts.

## 8. Proposed work phases

### Phase 0 — Existing design audit

Read the existing KiCad project, firmware configuration, BOM fields, and relevant documentation.

Establish baseline ERC/DRC results.

Produce an evidence-based engineering review identifying:

- Confirmed problems.
- Potential risks.
- Unverified assumptions.
- Opportunities to reduce cost and board size.
- Components requiring replacement.
- Areas already consistent with manufacturer recommendations.

### Phase 1 — Architecture and BOM decisions

Define:

- Supported configurations.
- Population/DNP matrix.
- Common versus variant-specific components.
- Power architecture.
- USB-only programming power architecture.
- Proposed ESP32 module.
- Onboard regulator candidates.
- External connector and testpoint requirements.

### Phase 2 — New schematic

Create the unified V4 schematic from the audited circuits.

Integrate the ESP32, regulators, USB programming, isolation, and power-output headers.

Keep all configuration variants within one schematic.

Validate every variant against its expected component population.

### Phase 3 — Mechanical placement and PCB design

Choose the board outline and connector positions.

Lay out the high-current circuitry according to TI recommendations.

Place the ESP32 and its RF keepout.

Route power, analog, and digital signals with appropriate constraints.

### Phase 4 — Verification and manufacturing preparation

Run ERC, DRC, and manufacturing checks.

Review component footprints and availability.

Generate BOM variants, Gerbers, drill files, assembly drawings, and a prototype test plan.

Test planning must cover:

- Normal input operation.
- Backup operation and repeated power interruptions.
- 2S and 4S variants.
- Charging and maximum load.
- Brownouts and low-battery conditions.
- USB-only programming.
- USB plus adapter and/or battery connected.
- Reverse-current protection.
- Thermals and power efficiency.
- Wi-Fi operation near switching power circuits.

## 9. Your immediate task — start here

**Start with Phase 0 only. Do not modify KiCad schematics or PCB layouts yet.**

Inspect the existing files and produce a structured review covering:

1. The current power architecture and exact BQ25798 connections.
2. Components with their actual manufacturer part numbers and TME links, where recorded.
3. Inductor suitability and worst-case operating conditions.
4. Capacitor selection, DC bias, and potential POSCAP removal.
5. PCB layout weaknesses, current paths, grounding, and thermal considerations.
6. Existing ERC/DRC configuration and any actual violations.
7. Compatibility requirements for BQ25792 and BQ25798.
8. Suggested architecture for USB-only ESP32-C3 programming.
9. Proposed 3.3V and optional 5V regulator requirements.
10. A prioritized action plan for V4.

Write the result to `hardware/v4/V4_AUDIT.md` on a new development branch, without changing the existing hardware files.

Use a findings table with severity, affected component/net, evidence, recommended change, and confidence level.

Clearly distinguish verified findings from hypotheses. If an operation cannot be completed with available tools, document the limitation rather than claiming it was checked.

Include a preliminary BOM-variant matrix and a list of decisions that remain open.

**Stop after Phase 0 and present the findings for review before making electrical design changes.**

