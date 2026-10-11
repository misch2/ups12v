# Phase 4.7 scratch layer validation — native assertion STOP

2026-10-11. Owner authorized scratch-only validation of BATTERY track `01ab1eb5-ab75-462d-9e54-2d6eab529481` F.Cu → In2.Cu with the original BATP/PGND/ILIM_HIZ/TS subset and modeled F.Cu PROG. Production modification remains unauthorized.

## Actual result

Installed native KiCad reports 10.0.7; LoadBoard/SaveBoard/PCB_TRACK APIs are present. Saved production PCB, schematic and project SHA256 hashes equal accepted Batch 1 before and after the attempted native read. **No scratch board was created. No CAD mutation, refill, DRC or schematic-parity check ran.** No electrical acceptance claim is made.

The first native assertion occurred while constructing the original-track/via inventory, before the BATTERY SetLayer call or route creation:

```
pcb_track.cpp(387): assert "false" failed in GetWidth():
Warning: PCB_VIA::GetWidth called without a layer argument
```

Trigger: `row(t,b)` called the track-style no-argument `GetWidth()` on a PCB_VIA. This is a helper error, not an observed copper or routing failure. **Stopped immediately; no retry, assertion suppression, process termination, KiCad close/restart/recovery or save.** The launched native Python process (tool session 61831) was left untouched after the assertion; its completion was not checked through further native operations.

## Proposed recovery, awaiting owner approval

Installed `pcbnew.py` exposes the PCB_VIA.GetWidth(layer) overload. Prior scratch builders in this repository use explicit per-layer via widths. Corrected `phase4_7_layer_validation.py` to read via width with an explicit F.Cu argument and record all four copper-layer widths separately. Ordinary tracks retain no-argument GetWidth(). **The correction has not been executed or validated after the assertion.** Owner approval is required before resuming KiCad operations under AGENTS.md.

Konnect open_project reports IPC not configured. Existing read-only native IPC capture also failed with connection refused, including outside-sandbox confirmation; no fresh live-state comparison is available. Saved production preservation is verified by hashes. Do not claim current unsaved live state matches Batch 1.

Native standalone ZONE_FILLER is not planned: older scratch evidence records a crash. After approved recovery, use native CLI complete DRC with refill and schematic parity on scratch only. The layer-change candidate, BATTERY current redistribution, PROG noise exposure and possible shorter route remain unvalidated. The previous 28.65188 mm numerical route is not accepted by this attempt.

Manufacturer reference checked today: TI BQ25798 SLUSDV2C, revised June 2026, §7.3.2 and §7.3.3–7.3.4, https://www.ti.com/lit/ds/symlink/bq25798.pdf. PROG establishes default cell count/frequency at POR; routing acceptance cannot be inferred from DRC. This attempt did not complete the requested geometry/noise assessment.

No production CAD changes, fabrication, purchasing, firmware, commit or push. **STOP for explicit approval to resume native KiCad operations after the assertion.**
