# V4 Phase 2 — stage 2.1 review checkpoint

> Historical stage2.1 record below. Owner accepted F01 and authorized the next schematic checkpoint. Current work stopped during stage2.2 at the owner's handover request; read [V4_HANDOVER.md](V4_HANDOVER.md) first. CE/root-port work is saved, but the complete charger power-stage review milestone has **not** been reached. Do not resume PCB routing or ESP32 integration.

2026-10-10 · Baseline5dea83068f5428c3bbce3b4efd9c22399f11d9f5 · Branch codex/v4-phase2-power-stage.

## Owner direction incorporated

Phase1 requirements/architecture/variants now use basic input protection for regulated adapters up to20V nominal (21V including tolerance), simple default-high CE/open-drain control without a250ms external lease, the retained USB buck/3V3 mux and isolation, and VSYS-only initial qualification. BQ25798 remains supported; PMID development/qualification and B798 backup assembly plans are deferred. See [CE evidence and remaining checks](V4_CE_REVIEW.md).

## CAD target and change

The only V4 CAD target is [ups_v4](ups_v4/). It contains the initial charger/power-stage schematic and matching project, copied byte-for-byte from the read-only V2/V3 power-board reference, then renamed through Konnect to ups12v_v4. No PCB has been created/copied or modified. Production V2/V3 and firmware are unchanged. The initial staging directory was moved to the owner's required target before the F01 electrical change.

Konnect added one global VBUS label at110.49,57.15mm on the existing IC-side input wire downstream of NT4. This joins the formerly isolated capacitor bank to actual IC VBUS. No new symbol or package mapping was introduced. NT4 remains a physical net tie between Q2 drains and IC VBUS; VAC2 retains its single-input connection to VBUS, VAC1 stays on VIN1. Capacitor returns remain PGND.

## Observed evidence

- Konnect0.13.0 / build6bbe3e4f890ba1d37c0e5d5f38ccd03d90958c9e; KiCad CLI10.0.7. list_toolboxes/get_active_toolsets succeeded (228 tools). Actual pin, label, connectivity, rename, add-label, export, render and ERC calls ran successfully.
- KiCad IPC ping responsive; [raw probe evidence](evidence/phase2-konnect-ipc.json). Exact-path probe requested C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_pcb; requested_open=false with GetOpenDocuments AS_UNHANDLED. **Exact live PCB access is not verified.** No save-current-board or PCB mutation was called. Before any later live edit, successfully query and match that exact full path; never select whichever board happens to be open.
- [Saved XML netlist](evidence/phase2-f01.net.xml) independently proves VBUS contains IC1.2, IC1.3, IC1.8, NT4.1 and C7.1/C13.1/C16.1. [Connectivity summary](evidence/phase2-f01-connectivity.json) records PGND returns and the NT4 traversal. [Net partition comparison](evidence/phase2-f01-net-diff.json) proves those two baseline nets merged and **all other net partitions stayed unchanged**.
- [ERC after F01](evidence/phase2-f01-erc.json): **7 errors /5 warnings**. Errors are all existing hierarchical ports used at the root without a parent. Warnings: two conflicting port/net names, inherited LED library mismatch and missing custom IC symbol/footprint libraries. [Fresh reference-copy ERC](evidence/phase2-reference-erc.json) and [renamed reference ERC](evidence/phase2-renamed-reference-erc.json) each report3 errors/5 warnings; the F01 checkpoint reports four additional root-port diagnostics (~INT, ~RST, I2C_SCL, GND). Do not describe this as an ERC pass or waive those diagnostics. Port cleanup/hierarchy integration remains required; exported connectivity does not show a new unintended electrical net change.
- [Render](evidence/phase2-f01.png) inspected: added VBUS label is visible on the intended wire. Inherited dense bulk-capacitor and mounting-hole text still overlaps; title/revision/output12V labels are legacy draft content. This is not final schematic visual acceptance.
- [Object diff](evidence/phase2-f01-object-diff.json) and [text diff](evidence/phase2-f01-schematic.diff) inspected. Konnect reserialized/reordered source and rewrote project instance names; label autoplace metadata also changed, and default exclude_from_sim=no was removed from eight text objects. The normalized object comparison leaves only the added VBUS label as a substantive change. These are disclosed separately from the intended electrical net merge.

Checks unavailable/not applicable at this checkpoint: PCB copper, DRC and schematic/PCB parity (no matching V4 PCB), CE waveforms, battery/thermal/load measurements, live procurement and full shared-package verification. CLI export emitted sandbox registry warnings but produced a parseable XML netlist. No firmware changes/build.

## Review boundary and next stage

**F01 schematic connectivity is corrected; F01 PCB/release closure is pending.** Stop at this small review checkpoint before further electrical blocks. The copied schematic still has CE pull-down R9, legacy20/25V capacitor populations, PMID load connectors and incomplete V4 main/USB/control circuitry; it is **not approved for fabrication or hardware power-up**.

Next: clean inherited root ports/naming and establish the shared charger physical pin map, implement the reviewed CE pull-up/open-drain sink with verified bias/reset behavior, then select supported-adapter-rated passives and basic fuse/polarity protection. Keep PMID output/bulk provisions DNP/test-only as appropriate. Do not place unverified package-specific parts or develop PMID backup. Each coherent change needs fresh export/ERC/render/diff evidence. PCB integration follows only after exact V4 IPC access is established; DRC/parity and hardware qualification remain mandatory before release.
