# Phase 4.5 — initial charger power-stage routing, owner review

2026-10-11. The accepted Phase 4.4 board now has an initial routed charger stage. **Stop here for owner review.** This is neither a completed PCB nor fabrication/power-up approval. All CAD changes used Konnect against KiCad 10.0.7 and the exact live board `hardware/v4/ups_v4/ups12v_v4.kicad_pcb`; no serialized CAD was hand-edited. Native owner deletion was required for trial vias because the installed tools cannot move/delete vias. Final DRC includes the rebuilt paths, not those failed trials.

## Result and verification

| Check | Before | Final |
|---|---:|---:|
| Unrouted connections, native DRC | 345 | **262** |
| Other DRC errors | 0 | **0** |
| DRC warnings | 13 | **13 unchanged** |
| Schematic/PCB parity findings | 0 | **0** |
| Schematic ERC | 0 errors / 4 warnings | **0 errors / 4 unchanged warnings** |
| Footprints / copper layers | 154 / 4 | **154 / 4** |
| Tracks / vias / filled PGND zones | 0 / 0 / 0 | **234 / 131 / 1** |

Synchronized DRC saved the live board after a separately completed native refill. All configured categories were reported. The 262 remaining unrouted items are errors in the full-board DRC: this is **not a clean release DRC**. The 13 warnings remain eleven accepted library-instance mismatches and two J7 clipped-silkscreen warnings; no new warnings remain. Fresh native schematic-sync dry run is **noop**, no conflicts, no pad reassignment or footprint changes required. The schematic was unchanged.

Read [final DRC](phase4-5-final-drc.json), [ERC](phase4-5-erc.json), [live inventory, traces and parity](phase4-5-final-native-readback.json), and [preservation/fill verification](phase4-5-checkpoint-verification.json). The latter compares to accepted HEAD `43696f9`: all references, component property values, population attributes and unmoved full pad definitions agree. IC1's complete custom pad definitions, native U1 RF area and 96 × 70 mm outline are unchanged. All F0/F5 footprints and DNP strategy remain. No component/value/MPN/footprint change was made, so the BOM review needs no selection change.

## Applied connectivity and local placement

- J1 → F1 → Q1/Q2 → NT4 → VBUS input bank and charger VBUS power lands are connected. The shared MOSFET source connection, R1/ACDRV1 and D1 gate network are routed. VIN1/VAC1 sense and C9 bypass are connected. Main return uses the PGND plane and J1 ground terminal.
- PMID C6 and SYS C5 100 nF capacitors now sit immediately above IC1 on F.Cu. Their supply escapes are about 1.5 mm and their ground lands have short local links to paired plane vias. Remaining PMID/SYS bulk banks use broad F.Cu buses and paired PGND vias. REGN C3 is connected to IC1 with two local ground vias; C7/VBUS and C4/C10/BATTERY bypasses are connected.
- SW1/SW2 use separate B.Cu paths to L1, each with six 0.5/0.3 mm package-side vias and twelve 0.5/0.3 mm vias at its inductor land. Bootstrap capacitors connect to their respective switch nets; BTST2 uses a short fine-trace B.Cu escape between existing high-current vias. The switch copper stays within the power-stage region.
- BATTERY and SYS connect to J3 and J2 on In2.Cu. The connector PGND PTH lands contact the In1 plane directly. Q3 remains a later converter-stage routing item.
- The R12/C26 series RC shunt remains VIN1 → R12 → C26 → PGND. C26 was rotated to bring its VIN-side land toward R12 and its ground land toward the short plane-via pair. R12, C26 and their values/nets are unchanged. Its branch leaves the fused input before the long MOSFET feed. This routing does **not** demonstrate adequate hot-plug damping.

Only five footprint placements changed: C6 (54.9,62.8) → (58.65,62.8); C5 (63.5,62.4) → (61.35,62.8); C1 (63.6,65) → (64.5,65), retaining 90°; Q3 (77,61.7)/0° → (77.8,63.25)/180° to clear the SYS via bank; C26 at (36,53) rotated 180°. No wholesale placement optimization was performed.

## Copper strategy and dimensions

| Layer | Allocation |
|---|---|
| F.Cu | Charger pad escapes, short decoupling connections, PMID/SYS local buses, fuse/MOSFET lands, RC damping branch |
| In1.Cu | Substantially continuous **PGND** reference plane, solid pad connection; 0.20 mm clearance / 0.25 mm minimum zone width; native RF exclusion preserved |
| In2.Cu | Broad VIN1/VBUS, BATTERY and SYS distribution; a few low-current VIN1 sense connections |
| B.Cu | SW1/SW2 to L1 and local bootstrap/gate escapes; no broad switch-node pours |

The saved plane contains **one connected filled polygon**. Native refill, DRC and visual inspection show uninterrupted PGND around the power-stage via clearances; no split ground moat was introduced. RF-strip samples inside the board find no filled copper in the approved keepout. These checks establish geometric/DC continuity, not measured return impedance or EMI. There is no GND zone. NT1's PGND land has its own plane via; its GND side and the signal-ground network remain for the later control-routing milestone. No significant power return is routed through NT1, and no additional GND/PGND connection was added.

| Path | Actual dimensions |
|---|---|
| J1 to fuse | 2.2 mm F.Cu |
| Fused VIN1 feed / main VBUS distribution | 2.2 mm In2.Cu; short 0.4–0.7 mm transitions into via banks |
| Q2-to-NT4 protected input | 1.2 mm B.Cu, one approximately 2.8 mm long 0.85 mm corridor between existing through vias |
| BATTERY / SYS connector trunks | 3.0 mm In2.Cu |
| PMID / SYS local bulk buses | 1.2 mm F.Cu, local 0.4–0.8 mm links |
| SW1 | 3.0 mm inductor fanout; 2.2 mm main B.Cu run; 1.2 mm local bend/escape, approximately 4.6 mm long; 0.4–0.5 mm via-array links |
| SW2 | 3.0 / 2.2 mm B.Cu; local 0.5 / 0.8 mm transition from the package array |
| Package necks | 0.20 mm at fine IC1 lands, widening as soon as adjacent lands permit; these are short package escapes, not long power traces |
| Power transfer vias | 0.70 mm pad / 0.40 mm drill: four each at BATTERY and SYS distribution banks and MOSFET banks; three at fuse/NT4 transfer points; two at the VBUS pin2/3 escape |
| Switch / small return vias | 0.50 mm pad / 0.30 mm drill; six per IC switch node, twelve per L1 land, paired at bypass grounds |

### Current basis and calculation limits

The [approved requirements](../V4_REQUIREMENTS.md) establish a **3.3 A input ceiling**, the supported 4S load of **41.5 W**, and low loaded-pack planning voltage **12.8 V**. Thus discharge/SYS load is approximately **3.24 A**, or approximately **3.74 A** including 0.5 A charging, before loss/tolerance. The supported 2S profile is approximately **12.61 W / 6.4 V = 1.97 A**. Independent maximum 5 V and external 12 V loads were not added together. Nominal net names were not used as current ratings.

For switching copper, a deliberately broader **5 A average** screen and 2.2 µH / 750 kHz assumptions give a conservative ideal buck/boost ripple bound of `21 V / (4 × 750 kHz × 2.2 µH) ≈ 3.18 A p-p`, approximately **6.59 A peak / 5.08 A RMS**. This is a calculation envelope, not measured ripple; inductor tolerance/saturation and operating modes remain relevant.

Live stackup readback reports four 35 µm copper layers, 1.6 mm total thickness and approximately 0.1/1.24/0.1 mm dielectrics. That may be a default stackup and **is not a fabricator-confirmed copper/plating specification**. Screening uses 35 µm copper and assumed 25 µm via plating. The IPC-2221 relation reproduced in [TI TIDA-01232, Equation 7](https://www.ti.com/lit/ug/tiducs7/tiducs7.pdf), with a 30 °C illustrative rise, gives about 6.87 A for 2.2 mm outer copper, 3.43 A for 2.2 mm inner copper and 4.30 A for 3 mm inner copper. The 1.2 mm outer section screens at about 4.4 A; the 0.85 mm outer corridor at about 3.4 A. The 5.08 A RMS envelope exceeds the 30 °C screen of the short 1.2 mm SW1 section; thermal spreading must be evaluated. **30 °C is an assumption, not a newly imposed owner acceptance limit.**

Using via barrel area only in that relation gives approximately 1.46 A per 0.3 mm drill and 1.79 A per 0.4 mm drill. This is an area-screening analogy, not a validated via thermal model or proof of equal sharing. Parallel arrays provide the intended cross-section; fabrication plating and actual sharing remain unmeasured.

At 20 °C copper resistivity, a 1.5 mm long 0.20 mm / 35 µm neck is approximately 3.7 mΩ: about 96 mW at 5.08 A or 52 mW at 3.74 A. Actual individual neck lengths/currents differ, and paired VBUS/BAT lands share current. Their heat flows into the IC land, widened copper and vias; long-trace ampacity cannot be assigned directly to them. No absolute temperature qualification is claimed.

## Switching, thermal and remaining constraints

Layout basis: [BQ25798 SLUSDV2C, revised June 2026, §8.4.1–8.4.2](https://www.ti.com/lit/ds/symlink/bq25798.pdf) and [BQ25792 SLUSDG1C, revised August 2022, §12.1](https://www.ti.com/lit/gpn/bq25792). Same-face local PMID/SYS bypass, multiple switch vias and paired decoupling returns follow that guidance. IC1 custom geometry was preserved rather than replaced with a generic exposed-pad footprint.

The retained L1 placement is about 15.5 mm above IC1; routed switch paths are roughly 18–22 mm including their bends and fanout. **Their loop area is not yet an optimized compact reference-layout equivalent.** Bringing L1 substantially closer would collide with the approved bypass banks and requires another localized placement/routing review. Long B.Cu switch paths also do not have an immediately adjacent continuous PGND layer: In2 carries power distribution, while the uninterrupted reference is In1. Switching-node coupling, overshoot, ringing and EMI therefore remain material prototype/layout constraints. Keep TS, BATP/PROG, I2C and RF routes away from this region in later work; they have not been routed across it.

PGND vias provide local return and heat spreading into In1, and broad copper/via banks spread MOSFET and connector-path losses. There is no measured junction/inductor/MOSFET temperature, via current sharing, load transient or switching-waveform evidence. Confirm actual copper/plating, inductor loss/saturation, capacitor effective capacitance and assembly thermal performance against supported profiles. Existing hardware qualification requirements apply; these are not invented extra product requirements.

Remaining IC1 connections include STAT, CE_N, I2C, TS, ILIM_HIZ, BATP, PROG and INT. REGN's C3 loop is routed, but REGN fanout to NT2/R6/R8/D3 remains unrouted. Other deferred work includes U3, U7/F5 detail, MCU/service interfaces, optional DNP bulk/test branches and signal-ground completion. **This board cannot be powered safely as a completed charger solely on the basis of this routing checkpoint.**

**VAC1 hot-plug/R12-C26 electrical adequacy and BQ25792 2S reset/default-2 A risks remain OPEN fabrication/power-up gates.** No hardware measurements, firmware work, manufacturing outputs, purchasing, commit or push occurred.

## Images and reproducibility

[Top routed copper](phase4-5-top.png), [bottom routed copper](phase4-5-bottom.png), [In1 PGND fill](phase4-5-in1.png), [In2 power distribution](phase4-5-in2.png). All use the same top-coordinate orientation, including the bottom-layer plot; they are not assembly mirrors. Native SVG exports were rendered and visually inspected. Dense inherited reference text remains, outside this electrical routing milestone.

Run `verify_phase4_5_checkpoint.py` for read-only preservation/fill checks and `render_phase4_5.cjs` to render existing exported SVGs. Intermediate `phase4-5-*drc.json` reports and recovery manifests are historical diagnostics; **phase4-5-final-drc.json and phase4-5-final-native-readback.json are the current routing evidence. Do not repeat any historical recovery deletion.**
