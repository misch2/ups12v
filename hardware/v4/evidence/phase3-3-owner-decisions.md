# Phase 3.3 simplification authority — 2026-10-10

Source: explicit owner instruction in this task. These are approved product decisions, not manufacturer constraints or measured behavior.

| Decision | Current normative home | Consequence |
| --- | --- | --- |
| USB only for initial programming/debug/recovery; internal port allowed; routine OTA | R07/R08, A07 | No exterior USB access or continuous deployed USB requirement |
| USB-only native ROM flash without adapter/battery/application | R07, A07 | Retain independent service supply, native USB, BOOT/RESET and safe isolation |
| Occasional MCU source-transition restart accepted | R06/R07, A06/A07 | Remove reset-free criterion and circuitry justified solely by it |
| Main VSYS independent of MCU reset under supported supply/load | R04/R07, A01/A06 | Keep autonomous BQ power path; verify later on matching hardware |
| Explicit firmware charge enable after charger/profile validation | R04/R07, A04 | Retain hardware-default-disabled CE and domain-safe drive |
| No 250 ms timeout, latch, D flip-flop or fresh-edge authorization | R04/R07, A04 | Remove candidate authorization/state-retention circuits |
| Up to 20 V nominal (+5%) adapter scope | R03, A02 | Withdraw active 22 V OVP/23 V ceiling and accidental 30 V survival scenarios |
| VAC1 supported-adapter hot-plug concern remains unresolved | R03, handover | Fabrication/power-up remains blocked; no safe transient claim |
| BQ25792 2S reset/default-2 A risk remains | R04, CE review | Explicit residual risk; no claim that firmware 0.5 A is a hardware ceiling |
| Simplest reliable circuit; optional complexity needs review | AGENTS.md | No newly invented requirements/thresholds/gates; genuine limits remain binding |

The owner's pre-existing R07 edit also changes the former aggregate 10 uA bound to a prototype measurement target while retaining prohibition of unsafe back-power and component-limit violations. It was present at task entry and is preserved.

Old Phase 3.2 snapshots, calculations and reports describe historical candidates. Their reset-free/fresh-authorization instructions are superseded. Source copies and past exports remain evidence of what existed, not acceptance of the simplified CAD.

Scope ends at the simplified MCU/power-domain schematic review. No real PCB, fabrication or hardware power-up work is authorized. Future tests are distinguished in V4_HANDOVER.md from schematic/export verification.
