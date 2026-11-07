# Recommended next phase — closed-editor targeted native production adoption

**Proposal only. Owner approval for a separate production phase is required.**
Phase4.24V has no production installation command; its scope guard rejects
production paths. Do not bypass that guard or promote the rejected U rehearsal.
The tested native operation sequence is in
`hardware/v4/tools/v4kicad/stencil_native_proof.py`, `worker('apply', ...)`.

## Owner coordination before a future production phase

The only editor observed at V entry was `pcbnew.exe` PID72064, command line target:

`hardware/v4/evidence/phase4-24u-production-paste-adoption/owning-editor-rehearsal/ups12v_v4.kicad_pcb`

Its PCB and project lock files are inside that rejected project. V issued **no
IPC requests, save, close, termination, recovery or mutation** to this editor.
Its saved PCB remains `96438b3c…d869481b` and must never be adopted.

When preparing the approved production phase, the owner can activate that exact
rejected project window and choose **File → Quit** (Alt+F4). If a save prompt
appears, choose **Discard/Don't Save**, because this project is rejected. Do not
use End Task or recovery. Identify by full path/process, not just the identical
`ups12v_v4` title. This closure is not needed for V's isolated proof. Re-observe
PID/path at the time: the recorded PID may no longer exist or may be reused.

Before any production write, the owner must also normally close the production
PCB/project if open. The future installer must verify process command lines and
target lock files; it must never force-close or automatically recover an editor.
Coordinate a period with no KiCad editors while the offline worker runs. Stop if
an editor or target lock appears, identity becomes ambiguous, or the source changes.

## Exact guarded application sequence

1. Read the current handover and obtain the new phase's production authorization.
   Require production SHA256 `8c68d920e71cea6373f9ee1f767f661d228ebafd6e1a00fadc580e00bc460e87`
   and accepted T/V SHA256 `d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b`.
   Bind source schematic/project/rules/libraries, accepted transaction/GTP, V
   proof and implementation hashes. Preserve an immutable source backup in the
   new evidence directory. A changed source needs fresh reconciliation.
2. Verify the closed-editor/process/lock guards, installed KiCad10.0.7 APIs and
   fresh output context. Run focused regressions and a read-only isolated native
   source snapshot/save proof. Rehearse the targeted method on a new production
   copy and require all V acceptance checks before touching production.
3. In one monitored isolated native worker, load the **actual closed production
   PCB** using `pcbnew.LoadBoard`. Load the accepted T PCB read-only as the graphic
   donor. Index original footprint/pad UUIDs. Preflight the exact four physical
   pads and original layer sets against T's `transaction.json`; check that none
   of its ten added graphic UUIDs already exist.
4. On the original production pad objects call `SetLayerSet` with only F.Paste
   removed: Q1.9 `e4ac9e85-c811-4bc1-8b0f-fb744a86e69b`, Q2.9
   `33d30c90-2a72-4b46-9865-95576d68a151`, Q10.9
   `2afd57c8-68fa-4e00-b83b-d4a8134c24e4`, and U4 large tab2
   `8de1b06f-f0ab-4d16-8a34-c3891d716649`. Retain all other layer membership,
   pad geometry, net assignments, drain fingers5–8 and the small U4 lead2.
5. For each of the exact ten accepted child graphics use
   `Cast_to_PCB_SHAPE(Cast_to_BOARD_ITEM(graphic.Clone()))`, verify its retained
   UUID, `SetParent(original_footprint)`, then `original_footprint.Add(shape)`.
   Keep the accepted native shape, curves, coordinates and Q2 polygon intact.
   Do not replace/deserialize footprints or regenerate windows.
6. Compare in-memory geometry/layout to source. Recheck source hashes and closed
   editor/lock state immediately before saving. Save the mutated original board
   through native `SaveBoard` to its actual production path. **Do not replace it
   with a scratch file.** This targeted paste-only change preserves all existing
   copper fills exactly; the successful V proof did not require a refill.
7. Independently reload the saved production PCB in a new process/copy. Require
   full saved hash equal T/V, exact original unit blocks for all154 footprints
   (including the unchanged Q10 absence), original473pads/324vias/41PTH/12NPTH,
   geometry/connectivity/layout preservation, and a native inverse save equal to
   the original8c68… source. Use the board for inventory before the inverse proof;
   after native `Remove`/save, exit that worker without traversing consumed objects.
8. Run fresh native DRC/ERC/parity and focused top-paste export on an independent
   copy. Require0errors/0opens/0parity, the exact T18 DRC warning identities and
   ignored checks,0ERC errors with the accepted4 warning identities,411 connected
   GTP openings and zero actual geometric delta against T. Check source companion,
   library, BOM and ZIP hashes. Record full before/after production hashes and
   final saved-state manifest; update handover only after all checks pass.

Any unexpected native assertion/IPC failure triggers AGENTS.md's safety STOP;
do not retry, recover or automatically save/close. Any unexpected property/hash/
geometry delta leaves the phase unaccepted; preserve diagnostics and stop rather
than waiving or normalizing it. If verification fails after production save,
report that saved state explicitly; do not perform an automatic rollback.

STOP after the separately approved and verified adoption. The owner then manually
re-exports Gerber to Order under their approval. Do not regenerate the current ZIP,
upload or order as part of the native installation. Stencil intent remains0.10mm,
top only,1:1 as per Paste Layer; no automatic aperture optimization.
