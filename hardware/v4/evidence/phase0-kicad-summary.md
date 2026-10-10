# Phase 0 KiCad baseline

Generated 2026-10-10 with KiCad CLI 10.0.7 from the saved KiCad 8.0 projects. The source `.kicad_sch`, `.kicad_pcb`, and `.kicad_pro` files were not edited. The exports in each subdirectory are the raw machine-readable evidence used for review.

## Projects and checks

| Project | Schematic | PCB | ERC | DRC | Unconnected items |
| --- | --- | --- | ---: | ---: | ---: |
| `phase0-main` | `bq25798_module` | `bq25798_module` | 8 (3 errors, 5 warnings) | 39 (warnings) | 0 |
| `phase0-controller` | `controller` | `controller` | 12 (10 errors, 2 warnings) | 9 (2 errors, 7 warnings) | 0 |
| `phase0-breakout` | `bq25798_breakout_board` | `bq25798_breakout_board` | 2 (warnings) | 13 (warnings) | 0 |

The main schematic ERC errors are root-sheet hierarchical labels `PWR_IN`, `I2C_SDA`, and `PWR_OUT` with no parent sheet. It also reports duplicate net names `VIN1/PWR_IN` and `PMID/PWR_OUT`. The main DRC findings are library-copy mismatches (34), one unavailable custom footprint library, and four starved PGND thermal-relief connections. There are no DRC clearance, short, or unrouted-item findings in this run. A second DRC run with `--schematic-parity` reported zero parity issues for the main and controller projects; the breakout reported 143 parity warnings (71 duplicate and 72 extra unreferenced footprints), consistent with that board being an older breakout/reference artifact rather than a synchronized production pair. The controller has the same disconnected root-sheet hierarchy pattern plus two undriven power pins; its DRC has two starved thermal-relief errors and two silkscreen-edge warnings. These results are direct CLI evidence, not an approval.

## Main power connectivity

The exported netlist and IPC-D-356 report show:

- `IC1` is `BQ25798RQMR` with the custom `mouser (samacsys):BQ25798RQMR_smaller_protected_area` footprint.
- `IC1` pins 2, 3, and 8 (`VBUS_1`, `VBUS_2`, `VAC2`) are on `Net-(IC1-VAC2)` and reach only `NT4` pad 1. `NT4` pad 2 is a separate net with Q2 drain pads 5–9. The net tie is therefore the documented physical bridge between the charger input and Q2.
- The schematic `VBUS` net contains only `C7`, `C13`, and `C16`; it has no IC, FET, connector, or net-tie pin. This is a confirmed connectivity concern requiring owner review before re-use of the input bypass network.
- Q1 and Q2 share their source pads on `Net-(D1-A)`; Q1 drain pads 5–9 are `VIN1`, and Q2 drain pads 5–9 are `NT4` pad 2. Both gates are on `Net-(D1-K)`. `ACDRV1` drives that gate network through `R1`; `ACDRV2` is on `GND`.
- `SDRV` is a single net from IC1 pins 24 and 33 to `C8` pad 1; `C8` pad 2 is `PGND`, so the saved design implements a 1 nF SDRV-to-PGND capacitor and no external SDRV-to-BAT connection.
- `PMID` has IC1 pin 29, J2 pin 2, J4 pin 1, C6/C12/C15/C18/C20/C22/C24/C25. `SYS` has IC1 pin 25, TP4, and C5/C11/C14/C17/C19/C21.
- The nearest 100 nF decouplers by IC1 pad centers are C6 on `PMID` and C5 on `SYS`. IPC-D-356 pad-center deltas to the corresponding IC1 pads are approximately 0.67 mm for each; both footprints are on the top side (`S2` in the IPC-D-356 export). Board placement centers are C6 (87.630, 65.405) and C5 (90.170, 65.405), with IC1 at (88.900, 68.580).

## BOM and physical exports

`main-components.csv`, `main.bom.csv`, `main-nets.csv`, `IC1-pin-map.csv`, `main-ipc-d356.txt`, `main-positions.csv`, `main-stats.txt`, and the SVG layer exports are the detailed evidence. The main board is 76.0489 x 55.8580 mm, four copper layers, 1.6 mm stack thickness, 68 through vias, 127 SMD pads, minimum reported track width 0.20 mm, minimum reported clearance 0.10 mm, and minimum drill 0.30 mm. BOM fields record Eaton `DR125-2R2-R` for L1, Alpha & Omega `AON7528` for Q1/Q2, TI `BQ25798RQMR` for IC1, Panasonic `20TQC47MYF` for C20/C22, and Panasonic `EEEFK1E470P` for C24/C25, alongside their recorded TME/Mouser URLs where present.

## Saved board rules and stackup

The saved main `.kicad_pro` was read as JSON without modification. Its board design settings specify `min_clearance=0.05 mm`, `min_copper_edge_clearance=1.0 mm`, `min_hole_clearance=0.25 mm`, `min_hole_to_hole=0.25 mm`, `min_through_hole_diameter=0.30 mm`, `min_via_diameter=0.50 mm`, and `min_via_annular_width=0.10 mm`. The global `min_track_width` is `0.0` (no global minimum), while the saved width table is 0.25, 0.50, 0.60, 1.00, and 1.50 mm. The exported board geometry actually contains 0.20 mm tracks and 0.10 mm minimum clearance, so these are observed geometry values and should not be confused with the configured rule fields.

The saved netclass table has `Default` clearance 0.10 mm and track width 0.50 mm, and `POWER` clearance 0.10 mm and track width 1.50 mm; the corresponding default via sizes are 1.0/0.5 mm and POWER via sizes 1.5/1.0 mm (diameter/drill). A single broad POWER pattern assigns `VBUS`, `PGND`, `VIN.*`, `BATTERY`, `PMID`, `SYS`, `BTST.*`, `SW.*`, the D1 and NT4 nets, and `BAT1_?` to POWER. `netclass_assignments` is null. This broad grouping mixes high-current, switching, bootstrap, and ground nets; it is a saved configuration fact, not evidence that each route has adequate current capacity.

The IPC-2581 export from an evidence copy reports a four-copper-layer, 1.60 mm stackup with 0.0350 mm copper on F.Cu, In1.Cu, In2.Cu, and B.Cu, 0.10 mm FR4 prepreg between the outer and inner layers, and 1.240 mm FR4 core between the inner layers. The export marks the stackup `PROPOSED`; it records copper conductivity 5.959E7 S/m and FR4 relative permittivity 4.50, but no fabrication plating tolerance. Treat this as saved/exported design evidence rather than a fab-house stackup guarantee.

## Route geometry and DRC thermal returns

The IPC-2581 route export gives the following concrete widths on the main board: `Net-(IC1-VAC2)` is routed at 0.25 mm; `SW1` and `SW2` use 0.60 mm local switch fanout and 1.00/1.50 mm segments toward L1; `PMID` and `SYS` have 1.00/1.50 mm power segments with 0.25 mm local fanout; `VIN1` has 1.50 mm segments with 0.25/0.50 mm local fanout; `Net-(NT4-Pad2)` has 1.50 mm Q2-to-net-tie segments with 0.50/0.25 mm local fanout; and `PGND` has 0.25/0.50 mm routes plus an internal copper zone and many vias. These widths identify narrow local necks and the intended broad segments, but they do not calculate allowable current, temperature rise, loop inductance, or return-current quality. The SVG layer views corroborate dense central IC switching fanout and extensive internal copper/via return structure; they do not by themselves prove thermal or high-frequency adequacy.

The main DRC saved-result report has four `starved_thermal` warnings on PGND pad 2 of: C8 at `@{x=93.952; y=66.294}`, C7 at `@{x=84.836; y=68.552}`, C10 at `@{x=94.234; y=69.657}`, and C9 at `@{x=84.356; y=70.739}`. Each reports one resolved spoke against a minimum of two on the PGND F.Cu zone. The configured severity is warning, and this is evidence of reduced thermal-relief connectivity at those pads, not proof that PGND is electrically open. The controller DRC separately reports two starved-thermal errors; those references were not conflated with the main-board coordinates.

## Editor-state preservation

Earlier CLI operations touched only editor-state `.kicad_prl` files. Their restored Git-normalized contents match the committed HEAD blobs: main `1371c5550ce3b3ecaf12389a5a0c30464ae99541`, controller `7497c11212748bee482964d9027e0cd6db774796`, and breakout `eae5507f35a774da52a416b15966876c3f002e4b`. A final direct byte comparison confirmed equivalence after CRLF/LF normalization, rather than raw byte identity to the LF Git blob. `git diff` is empty for all three. No production `.kicad_sch`, `.kicad_pcb`, or `.kicad_pro` file was changed.

## Tool limitation

Konnect 0.13.0 was reachable and its review toolsets loaded, but the dynamically loaded analysis/verification functions were not callable in this Codex tool session. Therefore the direct CLI ERC/DRC and exported connectivity are the authoritative checks here; Konnect aggregate review, live IPC board reads, and MCP netclass readback remain unevaluated. Saved netclass JSON was inspected separately. KiCad CLI emitted registry-access warnings in the sandbox. Its run touched `.kicad_prl` editor-state files; their Git-normalized content was restored and `git diff` is empty.
