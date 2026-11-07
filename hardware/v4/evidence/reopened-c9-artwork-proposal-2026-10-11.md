# Reopened checkpoint, revised C9 proposal and safe artwork cleanup

## Completed installation — supersedes proposal status below

2026-10-11 owner approved C9(61.1,69.1)/0° and confirmed PCB Editor closed. Installed the combined native C9/artwork candidate after authoritative hash/process/lock checks. Only the PCB file changed; schematic/project, library links and library files remain unchanged. Failed child-item IPC operation was not reused. After owner reopened via project manager, exact live board confirmed; native IPC refill/save completed. Final DRC262 existing unconnected/0other errors/16library-footprint mismatch warnings/0parity; all6silk-edge warnings removed. ERC0errors/4existing warnings. Live154footprints/473pads/240tracks/134vias/2zones; approved C9 position verified. Full preservation check permits only recalculated zone-fill polygons beyond the already verified candidate. See [installation](approved-recovery-installation.json), [preservation](approved-c9-artwork-final-preservation.json), [DRC](approved-c9-artwork-final-drc.json), [ERC](approved-c9-artwork-final-erc.json), [live snapshot](c9-apply-approved-final-ipc.json).

The standalone reopening attempt had no PCB handler at the configured IPC endpoint; owner reopened through manager. First final synchronization reported AS_BUSY; readback verified no saved change before the subsequent successful synchronization. No blind mutation retry. General routing and hardware operation remain unauthorized; pack/electrical physical qualification remains open. The rest of this report records pre-installation review evidence.

2026-10-11. **Recovery VERIFIED. Production CAD unchanged. C9 proposal not applied.** Existing artwork-only cleanup authorization persists; its verified candidate is ready for a coordinated closed-editor installation.

## Recovery

The owner discarded the interrupted transaction and reopened the project/PCB Editor. Konnect confirms the exact `hardware/v4/ups_v4/ups12v_v4.kicad_pcb`, `ipc_available=true`, `requested_open=true`, one open PCB. [Fresh snapshot](c9-apply-recovery-confirmed-ipc.json) and [comparison](reopened-checkpoint-verification.json) establish identical geometry, connectivity and attributes for **154 footprints, 473 pads, 243 tracks, 135 vias, two zones, four board shapes and five board texts**. C9 remains (54.2,67.5), 0 degrees. PCB, schematic and project hashes match the authoritative entry; the PCB is byte-identical to `c9-apply-entry.kicad_pcb`.

Comparison normalizes runtime board-parent IDs, generated standard-field IDs and four regenerated IC1 custom-pad primitive IDs (eight occurrences across footprint/pad snapshots). No custom geometry or owning pad identity differs. No interrupted artwork persisted. [Saved-checkpoint DRC](reopened-checkpoint-drc.json): **262 unrouted, zero other errors, 17 warnings, zero parity findings**; no live save or refill was needed to prove recovery. This remains an incomplete-board check, not release readiness. The failed `apply_connector_silk_ipc.py` stays disabled and was not executed.

## Revised C9 position for owner approval

**Propose C9 origin (61.1,69.1 mm), rotation 0 degrees**, retaining its 100 nF/50 V value, footprint, pad numbers, nets and population. This replaces the rejected (58.1,69.5)/180-degree target; no other footprint is moved.

| Item | Proposed result |
|---|---|
| C9 pad1 VIN1 | (60.62,69.10), 0.2 mm F.Cu link to existing VIN1 via (59.7,69.4) |
| C9 pad2 PGND | (61.58,69.10), 0.3 mm F.Cu escape to new via (61.9,69.1), diameter0.7/drill0.3 mm |
| Source branch | Short 0.2 mm In2 replacement (59.7,69.4)→(60.5,69.4); retain the source trunk and existing VAC1 escape |
| C9–VAC1 electrical length | **3.733 mm**, previously25.685 mm; approximately85.5% shorter |
| PGND escape | **0.320 mm**, previously2.157 mm |
| Native courtyard separation | No collision; approximately0.200 mm to IC1 and0.370 mm to R9; TP3/C3 clear |
| Conservative copper screen | Minimum approximately0.285 mm against a0.2 mm screening floor; new via checked against copper on all layers |
| Plane/RF | New PGND via lies within the existing filled In1 polygon; no RF-keepout overlap |

The exact removal IDs and segment/via geometry are in [proposal geometry](c9-revised-copper.json); [native courtyard evidence](c9-revised-courtyard.json) covers actual polygons, not only bounding boxes. Six superseded track segments and two VIN1 vias are removed; three segments and one PGND via added. Expected candidate counts: **154 footprints /240 tracks /134 vias**. C3/TP3, all connectors, switching loops, source trunk, zone definitions and RF keepout are retained.

A separate [native candidate](revised-c9-candidate.kicad_pcb) was saved and reloaded in a separate process. [Preservation comparison](revised-c9-candidate-preservation.json) proves all153 unrelated footprints, every retained track/via and all other board objects identical; C9 differs only in origin. [Scratch DRC with CLI analysis-only refill](revised-c9-candidate-drc.json) finds **262 unrouted and zero other errors**, including zero courtyard or clearance errors. Six existing silk-edge warnings remain. Scratch library resolution differs from the real project directory, producing19 library-related warnings; this is not claimed to be production library/parity acceptance. Production parity remains the separately checked zero findings. Final live ERC/DRC/parity and refill are required after an approved change.

The [native SVG inspection crop](revised-c9-candidate-inspection.png) was visually checked: C9 fits below IC1 and above R9 without disturbing C3/TP3. Dense reference lettering remains; final C9 label legibility should be addressed within its approved placement change, not treated as a copper collision. No measured noise reduction, transient safety or power-up qualification is claimed.

## Approved artwork: verified candidate, safe installation still pending

[Artwork-only candidate](recovery-artwork-candidate.kicad_pcb) was prepared through KiCad10.0.7 `pcbnew` on the offline entry backup. J1/J2/J3/J8 body rectangles become three-sided F.SilkS outlines ending atY30.35; J7's two outer side lines end atX125.65 and its off-board front stroke is removed. Pin1/polarity marks, text, F.Fab, courtyards, models, all pads/drills/nets and copper remain unchanged.

[Native save/reload and complete preservation check](recovery-artwork-candidate-verification.json) establishes that every source object outside the selected five footprints' F.SilkS graphics is identical. The [native renders](recovery-artwork-candidate-inspection.png) and [J7 detail](recovery-artwork-candidate-j7-inspection.png) were visually checked; outlines remain recognizable and polarity markers are preserved. [Scratch DRC](recovery-artwork-candidate-drc.json): **all six silk-edge warnings removed,262 unrouted,zero other errors**. Twenty library-related scratch warnings remain; some result from candidate-directory lookup and some from intentional placed-instance artwork differences. Library refresh must not silently restore the old artwork. No rule relaxation, warning suppression, connector movement or library pad change was used.

The guarded Konnect library-refresh **dry run only** refused J1/J2/J3/J8 due to unsupported `thermal_bridge_angle`, and J7 due to unsupported `Datasheet/unlocked`; no apply occurred. The previously failed native child UpdateItems/DeleteItems transaction is not a safe alternative and was not reused.

**Safe next step:** owner closes the PCB Editor after preserving any unrelated work, then confirms it is closed. Repository AGENTS.md explicitly says: “Do not use standalone scripts to overwrite a schematic or PCB currently open/locked in KiCad.” After closure, recheck endpoint/locks and authoritative hashes, preserve the entry backup, and install only the verified artwork candidate using a coordinated native closed-board workflow. Do not delete locks or overwrite an open board. Reopen the exact production PCB, verify live/readback persistence, unchanged electrical geometry and parity, and run final ERC/DRC. Existing artwork approval is sufficient; no new scope approval is requested. Revised C9 remains separate and requires explicit position approval.

Implementation diagnostics: standalone `pcbnew.ZONE_FILLER` crashed on the **scratch C9 copy** before save; it was removed from the proposal helper and replaced with CLI analysis-only refill. Reload verification uses a separate native process to avoid an observed same-process SWIG wrapper issue. Neither diagnostic involved a live-board mutation or altered the authoritative PCB. Scratch DRC uses exact copied project/rule settings; early default-settings reports were superseded by the linked final checks.

No general routing, fabrication, purchasing, power-up, firmware build, commit or push. VAC1/BQ25792 architecture decisions remain CLOSED; pack and matching-hardware qualification and safe bring-up remain OPEN.
