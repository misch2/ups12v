# VAC1 input transient: bounded assessment, OPEN

> Historical assessment. Owner decision2026-10-11 closes architecture by retaining R12/C26 2 ohm/2.2 uF without additional active OVP/eFuse. Qualification remains OPEN; the calculations below remain unmeasured historical sensitivity evidence. Use the [current safety report and gate disposition](v4-safety-design-review-2026-10-11.md), not historical architecture-open language, for next steps. No routing/fabrication/power-up authorization follows.

2026-10-10. Phase 2.6 owner review is accepted as the provisional charger/power-stage basis. This assessment does not reopen component sourcing or authorize a power-stage change. Scope: reuse the existing 144-case calculation and examine two manufacturer sources; no new global sweep. No measured hardware evidence exists.

## Rating and realistic mechanism

- TI BQ25798 SLUSDV2C, revised June 2026, section 6.1 p.7: VAC1/VAC2 absolute maximum is 30 V relative to GND. Pin 9 is VAC1 (section 5). There is no positive transient-duration exception stated for VAC1. The 30 V figure is a stress limit, not a design target. Source verified 2026-10-10: https://www.ti.com/lit/gpn/bq25798 .
- VAC1 is directly on fused VIN1, ahead of the external input FETs. Opening those FETs or disabling charging does not protect this pin from upstream ringing. Fuse F1 is not a voltage clamp.
- ADI/Linear Technology AN88, March 2001, pp.1–4, demonstrates hot-plug ringing from an already powered ordinary wall adapter and cable, including a 3–10 foot cable example with lumped 1–10 uH lead/filter inductance. Its measurements concern a different 24 V circuit; they establish a realistic mechanism, not this design's peak or a universal cable range. Source verified 2026-10-10: https://www.analog.com/media/en/technical-documentation/application-notes/an88f.pdf .
- A supported 20 V +5% source reaches 21 V before ringing. An ideal lightly damped LC step can approach twice that voltage. A regulated adapter's DC tolerance or current limit alone does not bound the microsecond energy delivered from its charged output capacitor. Device/cable impedance and contact behavior matter.

## What the existing calculation does and does not prove

Existing `phase2-6-hotplug-rlc.json` calculates 39.724908 V with L=10 uH, Rs=0.05 ohm, Cin=10 uF, Cd=1.226046 uF and Rd=1.862 ohm. This combination must NOT be relabelled an ordinary-cable worst case: the combined inductance/resistance is unmeasured and the assumed 10 uF directly visible at VIN1 is not the actual cold-start topology.

Reproducible extraction: `summarize_vac1_review.py` checks VAC1/C9/R12 against the accepted Phase 2.6 XML and extracts the four cases below. `phase3-vac1-review-summary.json` retains complete selected rows, input hashes and VIN1/VBUS pin sets; it is a historical-baseline extraction, not a fresh Phase 3 CAD acceptance report.

The actual VIN1 node has C9 (nominal 0.1 uF) and R12/C26. The large forward ceramics lie beyond the input FETs. TI section 7.3.3, p.26 describes a typical 5 ms delay before ACFET/RBFET detection after valid input. This is relevant to a cold start, but is not a guaranteed isolation interval under every already-powered reinsertion/bounce condition. The single-node model merges VIN1/VBUS and cannot resolve these states.

Selected existing model results at 21 V:

| L (uH) | Rs (ohm) | Cin (uF) | Cd (uF) | Rd (ohm) | VIN peak (V) |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.2 | 0.1 | 2.2 | 2.142 | 21.572 |
| 1 | 0.05 | 0.1 | 1.226046 | 1.862 | 24.424 |
| 10 | 0.05 | 0.1 | 1.226046 | 1.862 | 30.585 |
| 1 | 0.05 | 10 | 2.2 | 2.142 | 35.383 |

These show sensitivity to topology and source impedance. They neither demonstrate a failure with a particular ordinary adapter/cable nor establish immunity. Values are calculated, not exported electrical measurements; Ceff bounds remain assumptions. No new model or measurement is claimed.

**Assessment:** overshoot beyond 30 V during supported-voltage hot plugging is physically credible and cannot be dismissed as requiring an unsupported adapter. The specific 39.725 V result is not established as realistic for this board. Evidence is insufficient to decide whether the present RC is adequate for normal supported use. Status remains OPEN and blocks fabrication and hardware power-up until adequately resolved.

## Simplest mitigation direction, if required

First qualify/tune passive damping at VIN1, ahead of the FETs. Preserve the present RC concept; choose its effective capacitance and resistance against the actual cold-start and already-powered FET states. If a much larger damping capacitance is needed, an appropriately voltage-rated aluminum electrolytic with controlled ESR, or a bulk capacitor with an explicit series damping resistor, is a simple candidate. ADI AN88 pp.3–4 demonstrates these approaches. Its example values are not transferable acceptance values for this board. Added low-ESR capacitance alone can worsen ringing; increasing C26 alone is not automatically sufficient. Do not insert a lossy resistor into the continuous 3 A input path as an unqualified shortcut.

A TVS may supplement damping only if its minimum stand-off at 21 V and maximum clamping voltage at the calculated pulse current/temperature leave real margin below VAC1's 30 V limit. A nominal voltage label alone is insufficient. AN88 p.2 illustrates this selection difficulty. No TVS, active OVP, new MPN or final passive value is selected by this bounded review.

## Evidence required to close

1. Establish representative supported adapter/cable impedance and output-capacitor behavior, including a short low-resistance cable and the longest supported ordinary cable. Record uncertainty rather than treating AN88 values as this product's specification.
2. Model the two VIN1/VBUS nodes and external FET off/on/reinsertion states, including C9/C26 bias-dependent capacitance, tolerances, cable/contact resistance, bounce and stored energy. Bound positive and negative VAC1 excursions, VBUS and FET stresses. A proposed engineering target of <=27 V positive VAC1 peak provides 3 V margin to the 30 V stress limit; it is not a manufacturer requirement or proof of recommended-operation compliance.
3. Before first board power-up, support the final passive choice with sufficient circuit analysis and, where needed, a separate protected damping fixture that does not expose BQ25798 to an unqualified input. Before normal operation approval, capture appropriately probed VIN1/VAC1/VBUS/FET waveforms on matching hardware; check pulse/repetition and thermal stress. Record revision/BOM, cells, adapter/cable, load, ambient and logs. Keep fabrication/power-up blocked if the pre-hardware evidence is insufficient.

No broad sourcing research, new CAD mutation, PCB work or closure of this concern resulted from this assessment.
