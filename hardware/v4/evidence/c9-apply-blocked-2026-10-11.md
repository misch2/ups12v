# Approved C9 / connector silk corrections — blocked checkpoint

2026-10-11. Owner approved both bounded corrections, requiring a local clearance precheck and verification before stopping. **Neither correction is verified complete. The saved PCB, schematic and project configuration remain byte-identical to the fresh entry checkpoint.** No C9 movement, track change or via removal was attempted.

## C9 preflight conflict

Native KiCad 10.0.7 inspection of the unchanged saved board, corroborated by the exact live document, finds courtyard conflicts at the requested C9 target (58.1,69.5), 180°. The earlier review's copper screen did not check these courtyard extents adequately.

- Proposed C9 courtyard centreline bounds: X57.19–59.01/Y69.04–69.96.
- TP3 authored courtyard is circular, centred (58,71.5), nominal radius1.8mm; its stroke-inclusive bounding box is X56.175–59.825/Y69.675–73.325. C9's lower courtyard crosses the circle, not merely its bounding box: at X58, C9 reaches Y69.96, while TP3's courtyard begins at Y69.7.
- C3 courtyard stroke-inclusive bounds are X55.295–57.305/Y65.675–69.125. Its rectangular courtyard intersects C9's left-upper corner. Including C9's stroke only worsens the overlap.
- The inherited conservative copper screen still finds approximately0.282mm nearest foreign-copper gap, but that does not resolve the courtyard conflicts.

Evidence: `c9-apply-preflight.json`, `c9-apply-entry-ipc.json`, `c9-apply-entry.kicad_pcb`. C9 remains at (54.2,67.5)/0°, with all243 tracks and135 vias preserved. The exact approved target cannot be applied with a clean courtyard result. Do not silently waive/change courtyards, shift TP3/C3, change return vias or choose another C9 position. A revised bounded placement/routing proposal is required; no alternative geometry is approved or claimed verified in this checkpoint.

## Interrupted native silkscreen transaction

Konnect's placed-footprint graphic editor supports only single-outline polygons; it reports these rectangle/segment items non-editable. In accordance with AGENTS.md, the supported native KiCad10 IPC APIs were inspected instead of editing serialized CAD or overwriting the open board.

The attempted live transaction created three-sided F.SilkS outlines for J1/J2/J3/J8 using explicit footprint containers and trimmed J7's two side lines; it aimed to remove J7's off-board front stroke. No board save was reached. The first transaction failed a strict response check and was canceled. Readback then showed all pads/tracks/vias/zones/board shapes unchanged; footprint child ordering and generated standard-field UUIDs differed after undo, with geometry intact.

A subsequent attempt exposed a more serious native child-update inconsistency: the J7 line UpdateItems response carried the intended coordinates but an unexpected parent UUID, unlike the requested J7 parent. The diagnostic is preserved in `c9-apply-silk-update-diagnostic.json`. During the failed operation/cancellation KiCad IPC stopped providing stable board access; the native cancellation timed out. Konnect's fresh editor-state result was `stale_target` / `AS_NOT_READY` from the configured endpoint. **The interrupted live or recovery state is uncertain; neither successful application nor successful final rollback is claimed.** No automatic restart, unsafe fallback or offline PCB overwrite was attempted. The mutation script is now explicitly disabled to prevent rerunning this unverified path.

## Confirmed saved checkpoint and checks

Before attempting changes, synchronized DRC saved and verified the exact live board:262unconnected items,0other errors,17warnings,0schematic parity findings. Native entry capture recorded154 footprints/473 pads/243 tracks/135 vias, no locked footprints, and C9 at its original position. The saved board matched the reviewed geometry hash. A final read-only hash check after IPC became unavailable found the saved PCB, schematic and project configuration unchanged from entry. Thus there is no persisted geometry change to verify and no claim that the six silk warnings were eliminated.

Final live save/readback, refill, synchronized post-change DRC, ERC and final parity cannot be completed against the uncertain editor state. Prior review ERC0errors/4warnings is historical evidence, not a new completion check. Fabrication readiness is not claimed. No general routing, architecture change, purchasing, fabrication, power-up, firmware change/build, commit or push.

## Required recovery and next milestone

Continuation after owner reopened KiCad: saved hashes still matched entry, and the live checkpoint retained154 footprints/473 pads/243 tracks/135 vias and original C9 placement. Raw IPC objects naturally changed their board-parent UUID after reopening; raw JSON inequality alone was not evidence of geometry change. A further explicit-container silk attempt failed its child-removal readback before save, and native cancellation again timed out. Owner observed the project-already-open warning and clicked Open Anyway. No duplicate instance was established: the elevated process check saw only one KiCad manager, with no lingering task Python helper; a later process check saw no KiCad/editor process, no socket entry, and the configured IPC endpoint was unreachable. The exact cause of the warning is unresolved. Do not infer concurrency solely from the dialog, do not delete locks, and do not retry the failed native child-edit script. Final saved PCB/schematic/project hashes still match entry. Existing mutation script is disabled again. For normal Konnect operation, owner should open the PCB editor; closing KiCad is only needed for a separately coordinated offline workflow.

Owner action: recover/reopen the saved V4 PCB, discarding this interrupted silkscreen transaction after checking for unrelated editor changes. The authoritative saved entry board is unchanged; `c9-apply-entry.kicad_pcb` is a separate backup. Confirm exact V4 document state before any more mutations. Do not blindly save a partial recovery transaction over the known-good checkpoint.

Then prepare a revised C9 placement that clears the actual TP3/C3 courtyards and copper, and present it for approval. Existing authorization for artwork-only connector cleanup persists, but its implementation needs a supported native workflow with reliable child-parent persistence. No need to reapprove the electrical architecture: VAC1 and BQ25792 decisions remain CLOSED/APPROVED, physical qualification and safe bring-up remain OPEN.

Skill stop requirement: `C:/Users/Michal/.agents/skills/kicad-pcb/SKILL.md`, Prerequisites: “Pause mutation work … ask them to reopen/recover, reconcile, and save the board in KiCad.” Applied because live IPC authority and transaction outcome were lost; the repository also forbids overwriting a board currently open/locked when safe synchronization is unavailable. STOP for owner recovery and review.
