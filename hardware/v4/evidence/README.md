# Phase 0 evidence

Current safety authority: [2026-10-11 design decision report](v4-safety-design-review-2026-10-11.md). Owner retained R12/C26 and accepted qualified2S1P/default-current charging. Architecture questions are closed; pack and prototype electrical qualification remain open. The Phase0 records below are historical evidence, not current protection-circuit requirements.

Source baseline: `9065cace5a7a7f95a39692a55897cd89e01024ea`, 2026-10-10.
See [V4_AUDIT.md](../V4_AUDIT.md) for interpretation and limitations, and
[phase0-kicad-summary.md](phase0-kicad-summary.md) for detailed check results.

- `phase0-main/`: saved main power-board exports and checks.
- `phase0-controller/`: saved controller exports and checks.
- `phase0-breakout/`: historical reference exports and checks.
- `cli-copy/*/*-drc-parity.json`: separate parity checks from disposable copies.
- IPC-2581 files: saved stackup and routed geometry evidence; not manufacturing outputs approved for ordering.
- `operating-corners.py` / `.csv`: original first-order calculations and assumptions.
- `references/` and copied KiCad inputs under `cli-copy/` are ignored local working artifacts; primary manufacturer links are in the audit.

CLI: `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`, version 10.0.7.
The original projects predate KiCad 10. Re-run checks on **copies containing
the matching schematic, PCB and project settings**, because this CLI session
updated editor-state `.kicad_prl` files. Restored originals match their baseline.
Do not use these exports as a replacement for the original KiCad sources.

Check commands (PowerShell; adjust `$copyDir` and `$outDir` to a disposable
project copy and an evidence directory):

```powershell
$cli = 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
& $cli sch erc --format json --output "$outDir/main.erc.json" "$copyDir/bq25798_module.kicad_sch"
& $cli pcb drc --format json --output "$outDir/main.drc.json" "$copyDir/bq25798_module.kicad_pcb"
& $cli pcb drc --schematic-parity --format json --output "$outDir/main-drc-parity.json" "$copyDir/bq25798_module.kicad_pcb"
& $cli sch export netlist --format kicadxml --output "$outDir/main.net.xml" "$copyDir/bq25798_module.kicad_sch"
python hardware/v4/evidence/operating-corners.py
```

These are reproduction instructions, not a claim that any additional check
ran after the recorded report timestamps. Local CSVs are extracted views of
the exported XML/BOM; IPC-D-356 and IPC-2581 are board exports. Some tools
reported sandbox registry access warnings. Konnect connectivity was checked,
but its dynamic analysis functions were unavailable; CLI results carry the
validation claims. Hardware, firmware build, live procurement and thermal
measurements are outside the completed validation.
