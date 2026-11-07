# PCB reference readability — 2026-11-07

Owner-authorized scope: move/rotate reference labels only. No footprint placement,
footprint definition, copper, connectivity, text size, visibility, layer or text
content changes. The correct production board was confirmed open in KiCad 10.0.7
over IPC before mutation. Konnect has no reference-position editing tool, so
native KiCad IPC `UpdateItems` for `Field` objects was used, as permitted by the
repository's native-workflow rule.

## Result

- 121 of 151 visible F.SilkS references moved and/or rotated. All 154 reference
  fields now have 0° or 90° orientation; three already-hidden net-tie references
  stayed hidden and unchanged.
- J1/J2 moved closer; mounting-hole references moved closer to the physical NPTH
  holes. J6's 180° orientation corrected. SW1, SW2 and C24 preserved exactly.
- All 151 visible references independently checked from the final native export:
  zero reference/reference, reference/physical-envelope or reference/pad overlaps.
  The physical envelopes include pads, F.Fab body shapes and footprint silk
  shapes; they exclude courtyard-only clearances and hidden fabrication text.
  Mounting holes use the NPTH hole, not the screw courtyard. Fixed board silk
  text and board-edge containment were checked too.
- Minimum checked gaps: 0.04 mm to physical envelopes/fixed text, 0.15 mm to pad
  bounding boxes, 0.18 mm between reference glyph bounding boxes. Most labels
  use a larger gap; the tight R52 space uses the 0.04 mm envelope gap without
  reducing its font. These are geometric checks, not a new fabrication rule.
- Exact native before/after comparison: only the planned reference positions and
  angles changed. All 154 footprint placements/definitions, 473 pads, 1170 tracks,
  324 vias, two zones, four board shapes and six board text items preserved.
- Git diff independently contains exactly 121 changed `(at ...)` lines and no
  other PCB edits. Schematic, project and design-rule hashes unchanged.
- Final DRC in the actual project context: **0 errors, 0 unconnected, 0 schematic
  parity differences, the same 18 pre-existing warning identities**. No copper
  refill was needed or performed. ERC was not rerun: schematic hash-identical;
  this task is not a design release. No firmware/hardware validation required.

Saved board SHA256:
`80c8bc9b413de26d61cd1de42df50f0c1ce5ce6036e430e7f900b8de1c105459`.
The board is saved through the owning editor. Manufacturing outputs were not
regenerated, and the previously accepted production baseline is retained as
historical evidence rather than silently updated.

## Evidence and recovery

`verification.json` records final checks; `plan.json`, `before-labels.json` and
`after-labels.json` record positions; project DRC reports retain all findings.
Full native captures, exported snapshots and visual renders remain locally in
this directory and are ignored by Git. `after.png` is the final native polygon
preview, with detail crops. The scripts never overwrite a live PCB file.

An initial whole-footprint IPC update ignored child-field changes. Readback
caught that no change had applied; the native commit was cancelled and exact
rollback verified (`apply-failure.json`). Direct `Field` updates then succeeded
as one editor undo transaction, with exact readback before push/save
(`apply-result.json`). Do not replay this historical apply script: its baseline
assertion intentionally refuses the now-modified board.

`before-drc.json` is an initial context-less exported-snapshot experiment, not
the baseline verdict: it lacks project rules/schematic. Use only
`baseline-project-drc.json` and `final-project-drc.json` for the stated comparison.
