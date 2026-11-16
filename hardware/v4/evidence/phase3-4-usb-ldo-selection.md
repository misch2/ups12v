# Phase 3.2 follow-up — service USB LDO selection

2026-10-10. Owner explicitly selected normal buck / service LDO / TPS2116 mux. This supersedes the earlier optional LDO comparison; only one practical LDO is selected here. Evidence filenames use `phase3-4` to keep earlier exports immutable; this does not authorize another project phase.

## Selected part and sources

U4: **Diodes Incorporated AP7361C-33E-13**, fixed 3.3 V, SOT-223, one per PCB in all initial profiles, fitted (not DNP), **PROPOSED** for prototype. `E` and `ER` have different physical pin assignments and are not interchangeable on this footprint.

Manufacturer: [AP7361C product page](https://www.diodes.com/part/view/AP7361C), [DS37274 Rev. 5-2, October 2020](https://www.diodes.com/datasheet/download/AP7361C.pdf), checked 2026-10-10. Relevant pp.1–2 (pin/application), 4–6 (limits/electrical/thermal), 11–13 (application/order suffix), 19/21 (package/lands). Published input range 2.2–6 V, 1 A electrical capability; 300 mA dropout maximum 140 mV under the stated test conditions. The 1 A dropout entry is typical, not guaranteed maximum. Minimum ceramic input/output are 1/2.2 uF respectively; typical application uses 4.7 uF each. SOT-223 thetaJA is 110 C/W for minimum recommended lands. Junction absolute limit is 150 C. These are device constraints, not measurements of this project.

| Preferred supplier | Exact identity | Page observation on 2026-10-10 |
| --- | --- | --- |
| [LCSC C500795](https://www.lcsc.com/product-detail/C500795.html) | AP7361C-33E-13, SOT-223 | Indexed page crawled yesterday: 3,168 pieces, minimum/multiple 1; USD 0.8178 at 1+, USD 0.6507 at 10+. Cached observation, current stock/price not guaranteed. |
| [TME AP7361C-33E-13](https://www.tme.eu/cz/details/ap7361c-33e-13/stabilizatory-napeti-neregulovane-ldo/diodes-incorporated/) | Exact manufacturer MPN, SOT-223 | Indexed page crawled last month: zero stock; 1-piece price CZK 9.45 excluding VAT, CZK 11.43 including VAT. Current availability unverified. |

Loose LCSC purchase is practical at quantity one; combine with other parts where shipping permits. Shipping was not quoted, and no total-cost optimum is asserted. TME may become useful if stock returns. No compatible substitute was selected; do not fit AP7361 (NRND predecessor) or `ER` based on similar naming. There is no need for an exhaustive comparison or assembly-library qualification.

## Bounded power and thermal screen

Assumptions for engineering calculations: USB high voltage 5.25 V; conservative output 3.234 V (3.3 V minus 2%, a screening allowance); LDO quiescent current 80 uA; thetaJA 110 C/W; service ambients 25/50 C. Neither ambient nor the following current points is a newly imposed product requirement. Actual ROM/flash current is unmeasured.

`P = (5.25 - 3.234) I + 5.25 × 80e-6`; `Tj = Ta + P × thetaJA`.

| Service load screen | LDO dissipation | Tj at 25 C / 50 C ambient |
| --- | ---: | ---: |
| 100 mA | 0.202 W | 47.2 / 72.2 C |
| 300 mA | 0.605 W | 91.6 / 116.6 C |
| 500 mA | 1.008 W | 135.9 / 160.9 C |

300 mA continuous is a conservative provisional service-load screen, not a measured ROM peak ceiling. It has about 33 C calculated margin to the absolute junction limit at 50 C ambient on the published minimal-land model. A 500 mA transient is within electrical capability, but 500 mA continuous at hot ambient needs better thermal copper; 1 A continuous USB operation is not claimed. For example, 70 C/W effective PCB thermal resistance would give about 120.6 C at 500 mA/50 C; this is a future layout calculation, not achieved performance or a new mandatory acceptance gate. Allocate useful ground-connected tab copper in the later PCB phase and verify actual temperatures/load.

At assumed 4.35 V at U4 input, headroom above 3.366 V output is 0.984 V, comfortably above the specified 300 mA dropout test limit. No guaranteed maximum 1 A dropout or unknown cable drop is inferred. TPS2116 drop must also fit the MCU operating range.

USB input current is approximately output current plus LDO quiescent current and other USB loads: the 1 A regulator rating grants no USB allowance. Respect port/configuration limits; measure ROM cold-start/inrush and flash peaks on the supported source. Wi-Fi stays disabled; there is no battery/adapter dependency. An application cannot repair a ROM power budget, so ROM-only testing remains essential. Preserve mux reverse blocking because the LDO itself is not reverse protection.

No physical PCB, thermal measurement or USB flashing test exists yet. This is a provisional schematic choice with adequate calculated service margin, not hardware qualification. Existing VAC1 and BQ25792 residual risks remain unchanged.
