# UPS V4 handover — stopped during Phase 2 stage 2.2

Updated 2026-10-10. This file is the entry point for resuming without conversation history.

**Stopped at the owner's explicit handover request. Stage2.1/F01 was reviewed and accepted. Root-port cleanup and a first CE implementation are saved in stage2.2; the complete charger/power-stage schematic milestone is NOT complete or accepted. No fabrication/power-up approval. Do not begin PCB routing or ESP32 integration.**

## Repository and Git state

- Repository: `C:/Users/Michal/Git/my/ups12v`.
- Branch: `codex/v4-phase2-power-stage`.
- HEAD at this session's resume: **`fd73fe4cf89fc02d8de28f090762ac8d0bfd75cf`**, `Phase 2b`; previous documentation baseline `5dea83068f5428c3bbce3b4efd9c22399f11d9f5`.
- Earlier audit: `031cd81` (`docs: audit existing UPS design for V4 phase 0`); hardware baseline `9065cace5a7a7f95a39692a55897cd89e01024ea`.
- **No new commit, staging, push or tag was made in this session.** Existing HEAD now contains the Phase1 revisions, CE/parts/Phase2 documents, root `HANDOVER.md` and an ignore change. It still does not contain the Phase2 CAD/evidence; preserve the working tree. A clean checkout of HEAD alone cannot reproduce the CAD.
- Resume working tree had no tracked modifications. This handover, `ups_v4/` (schematic/project/local ignore file), and `evidence/phase2-*` plus `evidence/verify_stage2_checkpoint.py` remained untracked. The earlier [Git status snapshot](evidence/phase2-git-state.txt) is historical, not current.
- Root `HANDOVER.md` is now tracked and unchanged by this session. Preserve local `software/ups/include/secret/`; never sweep secrets into a commit.
- `git status --short -- hardware/v2-3` was empty. No V2/V3 CAD or firmware change was made. No firmware build was needed/run.
- Ignored local artifacts: `ups_v4/.validation/package_check/`, editor `.kicad_prl`/locks, and `evidence/references/` downloads. Do not commit caches, scratch CAD or backups. Exported validation evidence is separate from the ignored scratch source.

## Owner decisions and boundaries

1. Hobby project: reliable UPS operation, battery safety and maintainability take precedence over speculative misuse protection.
2. One physical V4 PCB with explicit BQ25792/BQ25798 and2S/4S population variants. Preserve production V2/V3.
3. Only CAD target: **`hardware/v4/ups_v4/`**. All of `hardware/v2-3/` is a read-only reference. Current root schematic/project: `ups_v4/ups12v_v4.kicad_sch` and `.kicad_pro`.
4. Regulated adapters up to20V nominal with normal tolerance; documents assume±5%=21V. Basic input/polarity protection, adequate component ratings, BMS and appropriate fusing remain required. No complex active input OVP/eFuse and no requirement to survive accidental25/30V adapters.
5. CE default HIGH with normally-off open-drain MCU sink. No external250ms lease/watchdog. Preserve explicit BQ25792 charger-only reset risk.
6. Initial design/qualification exclusively VSYS. BQ25798 compatibility stays required. PMID backup development/qualification is deferred; original concept assumed approximately equal adapter/backup voltages. Optional testpoints/DNP provisions are allowed, not mandatory.
7. Future USB3.3V buck and power mux remain mandatory for USB-only programming with no battery/main adapter, including reverse-current and signal back-power isolation. They are not integrated yet.
8. Complete and present the charger/power-stage schematic for review before ESP32 integration or routing. This request does not authorize automatically crossing that milestone.
9. KiCad10 and Konnect only for CAD mutations; never hand-edit serialized design/library files or library tables. Read `AGENTS.md` and applicable Konnect/schematic/library skills. Verify actual tool callability and query saved results.
10. Before any live PCB modification, create/open the exact V4 PCB and prove full-path-specific IPC access. Never edit an unspecified current board. The owner separately authorized **closed-file disposable footprint checks only** under `ups_v4/.validation/`; this is not permission to bypass the real-board gate.

## Completed saved changes

### Stage2.1 — accepted F01

The source was `hardware/v2-3/bq25798_module/bq25798_module.kicad_sch` and matching project, copied and renamed through Konnect to `ups12v_v4`. Added global VBUS label at110.49,57.15mm on the charger side of NT4. Exported VBUS now connects IC1.2/.3/.8, NT4.1 and C7.1/C13.1/C16.1. The previous isolated capacitor net merged with IC input; all other pin partitions were unchanged. NT4 remains the physical input net tie. See [historical stage2.1 record](V4_PHASE2.md), F01 netlist/diff/connectivity/ERC/render evidence.

### Stage2.2a — root-sheet cleanup

Removed seven inherited hierarchical root labels (SDA/SCL/GND/~RST/~INT/PWR_IN/PWR_OUT). Used global signal labels for SDA/SCL/~INT and renamed charge control CE_N. Removed leftover port wire stubs. Refreshed `Device:LED` D2 from the installed library without moving pins. Exported all-pin net partitions match the accepted F01 export exactly; cleanup changed names/port representation, not connectivity. ERC improved from7errors/5warnings after F01 to0errors/2warnings.

### Stage2.2b — CE and VSYS interface

Expanded page A4→A3. Removed the old R9 CE-to-ground branch and #PWR09, reusing R9 as a10kΩ pull-up. Added D3/D4 BAS116H, Q3 PMV16UN, R10=10kΩ gate pull-down, R11=1kΩ request resistor. Actual exported nets:

| Net | Saved pins |
| --- | --- |
| CE_BIAS | D3.1(K), D4.1(K), R9.2 |
| CE_N | IC1.13, R9.1, Q3.3(D) |
| REGN | D3.2(A) added to existing REGN support |
| MAIN_3V3 | D4.2(A), J4.1 |
| CHG_REQ | J4.5, R11.1 |
| /CHG_GATE | R11.2, R10.1, Q3.1(G); slash denotes a sheet-local label in XML |
| GND | Q3.2(S), R10.2 added to inherited GND |
| SYS | J2.2 moved from PMID |

J4 pin mapping now:1 MAIN_3V3 **input from future normal buck**,2 GND,3 I2C_SDA,4 I2C_SCL,5 CHG_REQ,6 ~INT. **Incompatible with old V3 header wiring.** CE no longer connects directly to header pin5. J2 is now variable SYS output electrically; its old `Output12V DC` value is still misleading and must be corrected. J1 similarly retains legacy12V text.

The main-domain buck and controller are absent, so MAIN_3V3 is an interface requirement, not a completed battery-only bias supply. REGN supplies adapter-startup bias. Firmware/GPIO reset behavior and actual sequencing are not proven. [CE review](V4_CE_REVIEW.md) records calculated margins, conditional assumptions and BQ792 reset risk; [part acceptance](V4_STAGE2_PARTS.md) records manufacturer sources and pin-to-pad tables. Q3 deliberately uses the existing `Transistor_FET:2N7002` **drawing only**, with instance PMV16UN value/MPN/datasheet/description; it is not an electrical2N7002 substitution.

## Latest verification and evidence

- Konnect0.13.0 build6bbe3e4f890ba1d37c0e5d5f38ccd03d90958c9e; actual tool discovery/analysis/mutation/export/ERC/render calls succeeded. KiCad CLI10.0.7.
- [Latest ERC](evidence/phase2-2b-ce-erc.json): **0errors,2warnings**. Both are IC1's missing external `mouser (samacsys)` symbol/footprint library registrations. Embedded symbol permits exports, but package/library verification and PCB synchronization remain unresolved. These warnings are disclosed temporary deficiencies, not intentional electrical warnings or a release waiver.
- [Latest XML netlist](evidence/phase2-2b-ce.net.xml), [connectivity assertions/results](evidence/phase2-2b-connectivity.json), [reproduction script](evidence/verify_stage2_checkpoint.py). Assertions passed: root cleanup preserved every pin partition; exact CE/interface/VBUS sets above; J2.2 onSYS, J4.1 removed fromPMID; all unaffected pin partitions match F01.
- Saved schematic SHA256 at verification: `9e24befb0abd0773dc8e0fef906ce1ee626a21169359d601d055aae8a0e5804c`. Re-export/re-run checks after any CAD edit; do not trust stale artifacts.
- [Latest full render](evidence/phase2-2b-ce.png), [CE crop](evidence/phase2-2b-ce-detail.png) inspected. Connectivity is legible, but full visual acceptance is pending: inherited bulk-cap/mounting-hole text overlaps, old title/revision/12V and ground prose remain, and R11 value/reference still need text-layout cleanup. The crop clips left source-label text; use the full render for complete labels.
- [Saved CAD text diff vs read-only V3 reference](evidence/phase2-2b-schematic.diff) includes Konnect reserialization/project rename, port/stub cleanup, LED refresh, A3 page, CE and interface changes. Do not mistake the large serialized diff for equivalent electrical scope. Export partition comparison is the checked electrical evidence. Historical F01 object diff documents the original reordering/metadata noise.
- `git diff --check` passed for tracked working-tree changes. New/untracked CAD is not covered by ordinary `git diff`; use the explicit saved no-index diff and exported assertions.
- New CE package acceptance: queried installed symbols/footprints, placed disposable symbols and footprints via Konnect in the explicitly authorized closed scratch project, read pads back, rendered/inspected key orientation and geometry against manufacturer drawings. [Readback](evidence/phase2-package-readback.json), [schematic render](evidence/phase2-package-sch.png), [board SVG](evidence/phase2-package.svg), [detail render](evidence/phase2-package-detail.png). No routing or real-board work.
- Scratch board fallback reported `source:file`, IPC unreachable, no exact-board sibling lock. This is closed-file validation, **not verified live V4 PCB IPC**.
- CLI registry warnings about HKCU occurred in the sandbox, but exports were produced and parsed successfully. Do not report those warnings as export failures or as hardware validation.
- No matching V4 PCB exists. DRC, schematic/PCB parity, hardware timing, thermal, cell/load and USB partial-power tests have **not** run. ERC success does not establish electrical/thermal correctness.

## Unresolved work — do not treat as done

1. **Ground topology still unchanged:** old GND/PGND joined atNT1; GND includes REGN capacitor, control header, CE sink and quiet analog returns. Rework is not implemented. Do not automatically perpetuate a digital/power plane split. Prefer continuous system reference and controlled high-current loops. TI's [BQ25798 grounding answer](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1377275/bq25798evm-is-it-critical-that-a-net-tie-be-used-between-agnd-and-pgnd) explicitly supports separating quiet returns at pin27; consult EVM and both datasheets before deciding whether to retain a **local** AGND tie for PROG/TS/NTC. This does not justify an arbitrary board-wide moat. BQ25798 SLUSDV2C §8.4.1 requires close PMID/SYS bypass, low-impedance ground returns and short REGN return with ground vias. Exact local net membership/join location still needs review and exported proof.
2. **Input/PMID capacitors still legacy25V/20V populations.** Researched Murata GRM32ER71H106KA12L10µF50V1210 for C12/C15/C18(PMID) and C13/C16(VBUS), plus GRM155R71H104KE14D100nF50V0402 for C6/C7/C9. Verified supplier/manufacturer identities and1210 geometry; **not applied to the main schematic**. Old C20/C2220V POSCAPs remain connected and unsuitable for21V. C24/C25 backup bulk also remains; remove or correctly DNP/qualify, without developing PMID backup. Nominal capacitance does not prove Ceff at21V/temp/aging. See part acceptance for source links. No stock/price claims or purchase authorization.
3. **Charger shared physical map/library:** IC1 inherited custom33-pin symbol contains extra physical-land representations30STAT/31VAC1/32TS/33SDRV beyond the numbered29-pin interface. Do not replace it with a29-pin library symbol without explicit manufacturer split-land/pad reconciliation. External library absent; BQ25792/BQ25798 shared footprint/register/cell defaults remain to be verified. BQ792 TI PDF download had failed previously; indexed TI RevC sections supported CE review, but full package comparison remains pending.
4. **Basic input fuse/polarity/hot-plug design unfinished.** Existing Q1/Q2 AON7528 input pair retained provisionally, NT4/F01 corrected. Verify21V envelope, gate clamp, FET SOA and supported-adapter hot-plug; no activeOVP/eFuse needed. TI BQ25792 single-input application Figure10-2 recommends input damping for hot-plug>15V. Resolve normal adapter transient behavior and fuse/cable/BMS coordination without hypothetical25/30V misuse circuitry.
5. **CE qualification:** verify future main buck ramps, REGN/CE/SYS sequencing, cold diode VF, leakage at actual CE bias, gate discharge, absent battery, brownout/reset, no unintended charge pulse and no USB injection. Select a non-strapping GPIO with documented reset behavior later; no MCU is integrated now. Q3 exact reel suffix/TME listing and R10/R11 exact procurement identities remain open. Retain valid existing Source/Bought fields, but do not treat them as a fresh purchase/stock verification.
6. **Residual BQ257922S charger-only reset:** if MCU keeps Q3 on, charger reset/watchdog may restore2A while host intended0.5A. No external250ms expiry exists. Actual detection/recovery interval and selected cell/BMS current tolerance must be qualified. Firmware must release CE before reconfiguration and on fault detection;0.5A host setting is not a hardware ceiling.
7. **Presentation:** correct legacy rail/value/title/revision/ground annotations and text collisions; add short CE/ground/VSYS population notes. Run fresh export/ERC/render and inspect diff after each coherent modification.
8. **Real-board IPC still unproven:** see below. No real PCB work permitted until exact path check succeeds; no ESP32 integration until power-stage review.

## Konnect / editor operational notes

An open Eeschema locked the V4 schematic; Konnect correctly refused `update_symbols_from_library`. Owner closed Eeschema, allowing file-based schematic edits. A remaining KiCad project manager answered Ping but `GetOpenDocuments` returned `AS_UNHANDLED`; Konnect correctly refused even the disposable PCB edit because IPC was reachable. Owner then closed the project manager too; `check_kicad_ui` reported no process/no listener, and scratch edits safely used the file fallback. Never delete a live editor lock or force a file write around this protection.

Prior exact real-board probe: `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_pcb`, `requested_open:false`, `GetOpenDocuments:AS_UNHANDLED`; [saved probe](evidence/phase2-konnect-ipc.json). Ping alone is insufficient. When real PCB work becomes authorized, create/open that exact board in **PCB Editor**, then use Konnect `open_project(path=full_board_path)` and path-specific read queries. Require exact full-path confirmation and live source; any unhandled/uncertain response remains blocked. Do not launch/open the schematic while file-based mutations are in progress.

Useful Konnect operations: `list_toolboxes`, `get_active_toolsets`; `list_schematic_components`, `get_schematic_pin_locations`, `get_schematic_layout`, `list_schematic_wires`; `batch_*` placement/edit/wiring/deletion; `run_erc`, `render_schematic_png`. Use `inline:false` for PNG output, then view saved image; never print base64 payloads. `update_symbols_from_library` should be dry-run first and refuse moved pins. `save_project` saves the live PCB, not the file-based schematic; never call it blindly.

## Next milestone and resume sequence

1. Read this handover, requirements/architecture/variants, CE review, part acceptance and historical Phase2 record. Inspect current Git status; retain all uncommitted work/unrelated secrets. Confirm branch/HEAD and CAD full path.
2. Verify Konnect callability, KiCad10 CLI and editor locks. Work through Konnect only. Re-export current schematic and run ERC before relying on saved evidence. Reproduce the saved assertions with `python hardware/v4/evidence/verify_stage2_checkpoint.py`; script reads XML exports and writes only a JSON result.
3. Finish the **charger/power-stage schematic**: grounded return topology justified from TI; safe rated forward-mode caps; simple basic input/fusing; shared charger package mapping/library issues; CE calculations/reset/startup documentation and readable annotations. Keep VSYS-only and no MCU/USB integration in this milestone.
4. After each coherent change, export netlist, compare actual pin sets/unchanged partitions, run ERC, render/inspect and review explicit CAD diff. Update assertions when the intended connectivity changes; never weaken them merely to make a failure disappear.
5. **Stop and present the completed charger/power-stage schematic for owner review.** Do not infer approval from acceptance of F01 or from this handover. ESP32/USB integration and PCB work follow only after the agreed review and exact-board IPC gate; DRC/parity and matching hardware qualification remain mandatory before release.

## Local reproduction commands

Run from repository root (PowerShell); these export/check, never mutate CAD source:

```powershell
git rev-parse HEAD
git branch --show-current
git status --short
$v4cli = 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
& $v4cli sch export netlist --format kicadxml --output hardware/v4/evidence/phase2-2b-ce.net.xml hardware/v4/ups_v4/ups12v_v4.kicad_sch
# Re-run Konnect run_erc with output phase2-2b-ce-erc.json first;
# its wrapper/provenance JSON is the schema expected by the script.
python hardware/v4/evidence/verify_stage2_checkpoint.py
git diff --check
```

Commit/push only when requested; if later authorized, explicitly select task files and exclude credentials, scratch CAD and editor artifacts. A future session should update this handover with any new commit and changed validation limits before stopping.
