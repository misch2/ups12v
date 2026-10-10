# Engineering rules

- Reliability and electrical correctness take priority over size, cost and appearance. Preserve proven circuits unless evidence justifies a change.
- Preserve production V2/V3 hardware and existing installations. Develop new revisions in their own directory and branch; preserve unrelated edits and local credentials.
- V4 uses exactly one physical PCB with explicit BOM/population variants. Keep detailed specifications and decisions in [hardware/v4](hardware/v4/V4_REQUIREMENTS.md), not here.
- Use KiCad 10 and Konnect for CAD changes. Verify tool availability first; never hand-edit KiCad serialized design/library files. Report unavailable operations and uncertain outcomes.
- Justify electrical changes with manufacturer datasheets/reference designs, recording revision, section and assumptions. Distinguish exported evidence, calculations and hardware measurements.
- Prefer TME.eu. Preserve valid procurement fields; record exact MPNs, packages and verified supplier links. Do not invent stock, prices or specifications.
- After each coherent CAD modification, run ERC/DRC as applicable to the affected schematic/PCB, verify connectivity/parity and inspect the diff. Both ERC and DRC are mandatory before design release; passing checks alone does not establish electrical or thermal correctness.
- Validate power changes on matching hardware, recording BOM/revision, cells, source, load, ambient and logs. Build affected firmware environments; documentation-only changes need no firmware build.
- Follow existing code conventions and `.clang-format`. Keep changes focused, credentials local, and generated caches/backups out of commits.
- Respect the authorized phase boundary. Present architecture and electrical changes for review at the specified milestones before proceeding.
