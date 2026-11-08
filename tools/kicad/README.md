# Reusable KiCad tools

Keep reusable tools in `tools/`; keep input snapshots and generated reports in
`hardware/v4/evidence/`. The scripts below are read-only and use Python's standard
library. Run from the repository root.

| Tool | Purpose | Usage |
| --- | --- | --- |
| `read_annotations.py` | Extract placed schematic symbols and their field values, visibility, positions and typography into JSON. | `python tools/kicad/read_annotations.py input.kicad_sch annotations.json` |
| `verify_equivalence.py` | Compare two KiCad S-expression netlist exports: components, net membership, pin-to-net mapping and library definitions. Exit 0 when equivalent, 1 otherwise; records differences in JSON. | `python tools/kicad/verify_equivalence.py before.net after.net --output comparison.json` |

Netlist comparison includes component metadata, so an intentional Value change
can report a difference even if connectivity is unchanged.

Owner preference (2026-11-08): use checks proportionate to the change and batch
validation after a coherent change. Do not repeat full schematic, netlist and
PCB checks after every small step. Git history provides earlier comparison
points; metadata-only cleanup normally needs a focused diff. Electrical changes
and release checks retain their relevant ERC/DRC and connectivity requirements.

Historical migration scripts under evidence are baseline-specific records,
not general-purpose tools; do not rerun them against the current design.
