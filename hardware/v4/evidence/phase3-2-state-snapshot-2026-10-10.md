# Phase 3.2 stopped-state snapshot — 2026-10-10

Work stopped at the owner's request. The CAD worker was interrupted. This is
an incomplete schematic milestone, not an accepted electrical review or freeze.
Do not resume CAD changes without first reading this snapshot and AGENTS.md.

## Exact repository state

- Branch: `codex/v4-phase2-power-stage`.
- HEAD: `1c2d99984cf8ccd92de2aee343e6068634003ed7` (accepted Phase 3.1 baseline).
- Current schematic: `hardware/v4/ups_v4/ups12v_v4.kicad_sch`.
- SHA256: `ac7e0d19e90848bf7f04c9c2aef9e4deadbb502559a12af42d7e5e65e83f4e1a`.
- Schematic modification time: 2026-10-10 19:49:42 UTC.
- Changes are uncommitted, with both staged and unstaged changes. Preserve the
  owner's index; do not reset, blindly stage, or discard files.
- No commit, push, tag, firmware build, real PCB layout, fabrication or power-up.

## Implemented CAD content, pending final verification

- Separate TPS62933 bucks: SYS -> MAIN_3V3 and USB_VBUS -> USB3V3.
- TPS2116 normal-priority mux; MAIN-valid supervision with TPS389033.
- Original non-A TCA9517: A/MAIN charger side, B/MCU side, 4.7 kOhm pull-ups
  on both sides. Q8/Q9 isolate its internally pulled-up EN from MAIN.
- Transistor charge gating, disconnected external CHG_REQ enable branch,
  GPIO0 charge arm, and transistor-isolated INT.
- Additional TPS389033 plus SN74LVC1G74 charge-authorization latch for fresh
  authorization after MAIN loss. A live-arm transistor was also added so a
  retained latch cannot bypass a low/high-impedance MCU GPIO.
- TPS22975 post-mux slew-controlled switch, 47 nF CT candidate, 22 uF pre-rail
  capacitor and fitted 470 uF MCU hold-up candidate.
- Latest visible CAD values include TPS389001 adjustable MCU reset supervisor,
  SN74LVC1G17 clear conditioning, 32.2 kOhm 0.1% buck feedback upper resistors,
  47 kOhm USB EN lower resistor, and XAL5030 4.7 uH inductor candidates.
  These final additions have NOT received the parent's final connectivity,
  pin-map, tolerance, sequencing or render review.
- ESP32-C3-MINI-1-N4X project-local footprint; 61 physical pads, 53 unique
  numbers, nine pad-49 segments and 5.4 mm central array checked. Final exact
  geometric deviations, including central chamfer, still need reconciliation.
- Native USB GPIO18/19, fitted 0 Ohm series links with optional 22 Ohm values,
  rail-less TPD2EUSB30A shunt and corrected Texas_DRT-3 footprint.

## Evidence freshness — do not mistake old passes for current acceptance

| Artifact | Modification UTC | State at stop |
| --- | --- | --- |
| Schematic | 19:49:42 | Current saved CAD hash above |
| `phase3-2-mcu-power.net.xml` | 19:51:14 | Export newer than CAD; final content not independently verified |
| `phase3-2-erc-clean.json` | 19:49:02 | STALE relative to latest CAD; reports 0 errors / 6 warnings for an earlier state |
| `phase3-2-mcu-power-a1.png` | 19:30:10 | STALE; predates latch, slew switch and final reset changes |

Earlier independent preservation passed all 77 Phase 3.1 references and 256
connected pins, with declared USB series-link splits, R11.2 service no-connect,
N4X selection and U2 footprint correction. That result predates the latest CAD
and must be rerun. The worker's Phase 2.6 preservation check must also be rerun.
No PCB exists, so no current PCB parity or DRC result is claimed.

## Remaining work before the requested review checkpoint

1. Read back final connections and exact pin/package mappings for all new parts.
   Confirm MAIN loss clears authorization, static-high arm cannot re-enable on
   MAIN return, live GPIO low/high-Z disables charging, and MCU reset/startup
   reliably clears the latch. Check Schmitt conditioning of slow clear edges.
2. Recalculate both buck operating ranges, EN thresholds (including EN pull-up
   currents and resistor tolerance), feedback error/leakage, mux and load-switch
   maximum resistance, and remaining 1 A trace/drop budget. Reconcile the new
   32.2 kOhm values with documentation and BOM.
3. Verify the adjustable MCU reset threshold/divider and startup sequence. The
   rejected TPS389030 variant trips at 2.89 V, not 3.0 V. TPS389001 with a
   proposed 16.7 kOhm / 10 kOhm 0.1% divider targets about 3.0705 V falling and
   3.0892 V rising; confirm actual CAD values and all tolerances/leakage.
4. Reconcile controlled USB inrush with fitted hold-up capacitance and reset-free
   transitions. TPS22975 rise-time equations are for VBIAS=5 V and steady rails
   before ON, whereas this candidate uses the approximately 3.3 V pre-rail.
   At 47 nF, the nominal equation gives 20.236 ms/V and approximately 53.4 ms
   for a 10-90% 3.3 V ramp at the specified bias condition. No guaranteed ramp
   or reset-free result is established. Legacy 100 mA USB cold-start remains
   a qualification gate; a 3 A regulator does not authorize that USB draw.
5. Confirm L2/L3 exact candidate XAL5030-472MEC and matching land pattern, with
   current/saturation/DCR/temperature limits; remove stale generic 1210/10 uH
   BOM claims. Ordinary passive sourcing need not be purchase-ready.
6. Finish TCA9517 and all cross-domain maximum leakage accounting. EN's
   internal MCU-side pull-up is isolated, but aggregate <=10 uA R07 acceptance
   and partial-power transients are NOT proven. Do not substitute typical
   leakage or GPIO high-Z assumptions for this requirement.
7. Run fresh ERC, XML export, both preservation verifiers, footprint checks and
   render. Inspect the new blocks and resolve overlapping values/stale notes.
   Six earlier isolated-label warnings were intentionally deferred UART_RX,
   UART_TX, MCU_STATUS_LED, MCU_GPIO7, MCU_GPIO1 and MCU_GPIO10.
8. Reconcile the checkpoint report, BOM and handover to the final verified hash.
   They currently contain intermediate values/claims. An extra unlinked N4X
   footprint exists at `hardware/v4/ups_v4.pretty/`; the active footprint is
   under `hardware/v4/ups_v4/ups_v4.pretty/`. The duplicate is staged and was
   not deleted; Konnect footprint-file deletion was unavailable.

## Gates preserved

R07 reset-free source transitions and <=10 uA aggregate main-domain injection
remain requirements, not waived requirements. No hardware validation was done.
The unresolved VAC1 hot-plug transient remains a fabrication/power-up gate.
Stop before real PCB layout, routing, fabrication or powering hardware.
