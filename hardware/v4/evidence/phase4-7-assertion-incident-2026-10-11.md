# Phase 4.7 read-only preflight — assertion incident, operations stopped

2026-10-11. Owner ordered an immediate stop after repeated KiCad assertions and used Cancel to suppress further dialogs. No KiCad/Konnect operation is authorized until owner review. Do not save, refill, revert, restart, close, or automatically recover the PCB.

## Identified trigger

The initial `phase4_7_preflight.py` used this sequence while iterating `pcbnew.LoadBoard(...)` tracks:

```python
row = dict(..., width=pcbnew.ToMM(t.GetWidth()))
if isinstance(t, pcbnew.PCB_VIA):
    ...
```

`GetTracks()` includes vias. The width query ran before the type distinction and invoked `PCB_VIA::GetWidth` without a copper layer. Shell output explicitly recorded `pcb_track.cpp(387): assert "false" failed in GetWidth(): Warning: PCB_VIA::GetWidth called without a layer argument`. This is direct evidence of a caller API error, not evidence of a damaged via or board. Repeated dialogs are consistent with repeating this query for successive vias; the board has 134 vias. No stack trace proves that every owner-observed dialog came from this process.

This call used native KiCad 10.0.7 Python bindings on a separately loaded saved-board object, not a live IPC mutation. Native pcbnew loads KiCad's GUI-capable runtime, so a nominally read-only call can still trigger assertion dialogs. The mistake was continuing diagnostic operations after the assertion instead of immediately stopping and investigating.

Before the owner's stop, the script was corrected to branch first and call `t.GetWidth(pcbnew.F_Cu)` for vias, leaving parameterless `GetWidth()` only on non-via tracks. Two corrected saved-board captures completed and produced `phase4-7-geometry.json`; this does not authorize resuming or establish the current editor state after Cancel. Do not rerun these scripts during the stop.

## Other operations already issued

- Konnect health and exact-path board metadata reads; IC1 pad geometry and netclass queries.
- Native kipy snapshot using `get_footprints/get_pads/get_tracks/get_vias/get_zones/get_shapes/get_text`; protobuf serialization only, no `PCB_VIA.GetWidth()` invocation in that script.
- Saved-file DRC with `sync_live_board=false`, `refill_zones=false`; no save/refill. Report: 262 unconnected, 16 library-mismatch warnings, zero other errors/parity findings.
- Schematic netlist exports. The first export produced KiCad netlist syntax despite the `.xml` filename; it was replaced by explicit CLI `kicadxml` export. The final XML was parsed successfully. No schematic save or redesign.
- Diagnostic plot attempts failed at missing matplotlib imports; no plot or CAD output was generated.
- Initial bundled KiCad Python IPC attempt failed at missing CPython 3.11 CFFI dependency; default Python IPC attempt failed with socket permission denial. The subsequent approved elevated read-only snapshot succeeded. No fallback write was attempted.

## Existing evidence checked after STOP using ordinary file reads only

`c9-apply-phase4-7-ipc.json` exactly matches `c9-apply-approved-final-ipc.json` for footprints, pads, tracks, vias, zones, shapes and texts. Counts remain 154 footprints / 473 pads / 240 tracks / 134 vias / 2 zones; C9 remains (61.1,69.1),0 degrees. The snapshot was acquired after the initial assertion and before the owner's stop.

Current saved PCB, schematic and project SHA256 hashes match that snapshot. `phase4-7-geometry.json` records KiCad 10.0.7 and successful saved/live pad, track and via comparison. These observations support preservation at the captured checkpoint; they do not prove the post-Cancel live editor state. A read-only OS process query after STOP returned none of the explicitly queried process names; that is not proof of editor closure or IPC availability and is not used to infer either.

## Safe workaround and proposed verification — requires owner approval

1. Use IPC protobuf padstack geometry for via dimensions: read the selected copper layer's `size` and drill `diameter`; do not call native `PCB_VIA.GetWidth()` at all. If a future offline native operation needs a diameter, require a specific enabled copper layer before calling `GetWidth(layer)`. Do not assume one diameter applies to every layer of a nonuniform padstack.
2. Recheck the live board with the already-used kipy read-only snapshot path, binding both PCB filename and exact project directory. Request only document identity and existing item protos. No native `pcbnew.LoadBoard`, width getter, DRC, zone refill, editor save or mutation in this verification.
3. Compare returned footprints/pads/tracks/vias/zones/shapes/texts with the authoritative completed C9/artwork snapshot. Separately compare saved PCB/schematic/project hashes. Report every difference and stop if IPC is busy/unavailable, document binding fails, or equality fails; do not retry-loop or automatically recover.
4. If an item-proto query itself triggers an assertion, stop immediately. Existing file evidence remains usable as saved-state evidence only. Owner review decides any recovery action.

This avoids the demonstrated width-query trigger; it cannot guarantee that an already asserted editor has no unrelated latent problem. No further KiCad operations have been made after the owner's stop. The routing preflight remains incomplete and no routing proposal is approved or installed.
