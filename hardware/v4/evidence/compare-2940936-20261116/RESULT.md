# Saved PCB connectivity comparison — 2026-11-16

**PASS: electrical connectivity between pads is unchanged** relative to
`2940936252309a390db0b28d9469ab6ef240ffa0`.

Scope: current saved `hardware/v4/ups_v4/ups12v_v4.kicad_pcb`, including local
uncommitted edits, compared with the exact Git blob from that commit. Direct
file access with native KiCad 10.0.8 `pcbnew` and `kicad-cli`; no live editor
access, board save, zone refill, or production CAD changes.

## Connectivity evidence

- All **473 physical pads** retain their identities and geometry.
- Native connectivity traversal produces the **same 116 physical pad groups**
  in both files. No pad group splits, merges, additions, or removals.
- Declared net membership partitions are identical when net names are ignored.
- Two net renames account for all 12 changed pad-net assignments:
  `/F5_5V_OUT` → `F5_5V_OUT`, `NEN` → `/NEN`.
- Copper-zone definitions, saved fill polygons **including holes**, and copper
  artwork are equal.
- Independent schematic exports confirm the same 154 electrical components,
  104 nets and 445 pin memberships. Their pin partitions are identical; the
  same two net renames account for all pin-to-net name changes. Component
  metadata differs, so full exported-netlist metadata equivalence is false.

## Differences that do not change electrical connectivity

- 23 track objects removed, 26 added, on `MCU3V3`, `I2C_SDA`, and `SYS`.
  Track count changes from 1170 to 1173; via count remains 324.
- All 30 changed retained track/via objects differ only in net names.
- All original 154 footprint placements are unchanged. Seven padless
  KiBuzzard text footprints were added; there are now 161 footprints.
- Thus the board files and track geometry are not identical, despite their
  equivalent electrical connectivity.

## Fresh ERC/DRC

Checks ran on byte-identical isolated copies with each version's own project,
rule and local-library files. Standard installed KiCad libraries were loaded
through an evidence-local configuration. DRC used the saved copper fills;
neither `--refill-zones` nor `--save-board` was used.

| Check | Commit | Current saved files |
|---|---:|---:|
| DRC errors | 0 | 0 |
| Unconnected items | 0 | 0 |
| DRC library-footprint mismatch warnings | 18 | 18 |
| Schematic parity entries | 0 | 55 |
| ERC errors | 0 | 0 |
| ERC warnings | 7 | 7 |

All 55 current parity entries concern the `Purpose` metadata field; none concern
electrical connectivity. DRC and ERC warning identities match the baseline.
ERC warnings comprise four single-pin labels and three unavailable
`easyeda2kicad` symbol-library links (Q1, Q2, Q10) in the isolated environment.
These library-link warnings are not a demonstrated electrical regression.
DRC rule severities are unchanged; the six ignored check categories are
recorded in `checks-summary.json` for both versions.

This verifies saved CAD connectivity; it does not assess unsaved editor state,
manufacturing readiness, electrical performance or physical hardware.

## Identity and artifacts

- Baseline PCB SHA256:
  `52a7edd2b7d3a17bebd1cc64be3e9c5dd308b8664d329d1139932e8825637ac6`
- Current PCB SHA256:
  `ff3431ffb7fa46f3b093aca1c3184d9aae4ff2067b1260423eb88a64bd63b641`
- `manifest.json`: exact commit blob identities, copy hashes and working HEAD.
- `native-comparison.json`: native geometry differences and connectivity verdicts.
- `connectivity-proof.json`: compact before/after net memberships, physical pad
  groups, pad identities and original native-capture hashes.
- `baseline-drc.json`, `current-drc.json`, `baseline-erc.json`,
  `current-erc.json`: full native check reports. The completed run also emitted
  sandbox registry/cache diagnostics; temporary execution logs were removed.
- `schematic-comparison.json`: exported schematic connectivity and metadata
  comparison; temporary netlist exports were removed after verification.
- `warning-comparison.json`: warning identities and parity classification.
- `source-stability.json`: all copied production inputs unchanged at completion.
- `current/`: saved CAD and local-library snapshot of the then-uncommitted
  design. The baseline can be recovered from the named Git commit.

Owner-authorized cleanup on 2026-11-16 removed bulky native captures, temporary
baseline/configuration copies, exported netlists, execution logs and the one-off
audit driver. The original verdict and full ERC/DRC reports are retained;
`connectivity-proof.json` preserves pad topology without repeated artwork dumps.

The existing locally modified handover was preserved; this independent report
records the checkpoint.
