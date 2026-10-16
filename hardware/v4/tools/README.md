# V4 offline KiCad 10 tools

Small project-local Python toolkit extracted from the working Phase4.7 geometry exporter, scratch builder and preservation checks. It supports the V4 four-layer board, straight tracks and through-via route plans. Offline commands never edit production; the explicit bounded IPC adapter edits through the owning live editor. Serialized CAD text is never edited. Shared safety/check CLIs need only standard Python; optional export-only route screening uses NumPy (also required for its tests), and review rendering uses Pillow. Native workers require installed KiCad10 Python/pcbnew; checks require matching kicad-cli.

## Usage (PowerShell, repository root)

Run regression tests first:

```powershell
python -B -m unittest discover -s hardware/v4/tools/tests -v
```

Use an accepted JSON baseline manifest with a `hashes` object mapping source filenames to SHA256. The existing `hardware/v4/evidence/c9-apply-phase4-7-batch1-final-ipc.json` supplies the accepted Batch1 hashes. Any source mismatch is a stop, before native code runs.

Read-only smoke/inventory of a fresh, isolated byte-copy:

```powershell
python -B hardware/v4/tools/kicad_v4.py snapshot `
  --board hardware/v4/ups_v4/ups12v_v4.kicad_pcb `
  --baseline-manifest hardware/v4/evidence/c9-apply-phase4-7-batch1-final-ipc.json `
  --output-dir hardware/v4/evidence/my-new-smoke `
  --native-python 'C:/Program Files/KiCad/10.0/bin/python.exe'
```

Authorized Phase4.7 scratch-only mutation (choose a new nonexistent output directory each run):

```powershell
python -B hardware/v4/tools/kicad_v4.py validate `
  --board hardware/v4/ups_v4/ups12v_v4.kicad_pcb `
  --baseline-manifest hardware/v4/evidence/c9-apply-phase4-7-batch1-final-ipc.json `
  --output-dir hardware/v4/evidence/my-new-candidate `
  --native-python 'C:/Program Files/KiCad/10.0/bin/python.exe' `
  --kicad-cli 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe' `
  --plan hardware/v4/evidence/phase4-7-prog-focused-0.1-0.01-omit-01ab1eb5-layer-model-front-only-plan.json `
  --track-uuid 01ab1eb5-ab75-462d-9e54-2d6eab529481 `
  --from-layer F.Cu --to-layer In2.Cu --erc
```

`validate` checks source hashes, creates a fresh project copy, changes only the requested original track's layer, adds exactly the declared plan, verifies preservation, saves/reloads natively, runs DRC with refill/connectivity/schematic parity, optionally ERC, then verifies final geometry. Footprint movement is disabled except for the explicitly enabled four-reference U3 scratch investigation below. It stops on physical DRC/parity/ERC errors. Remaining unconnected items, warnings and inherited ignored checks are reported, not silently accepted as whole-board cleanliness. Owner review remains mandatory at the authorized checkpoint; tool success is not thermal/noise qualification.

For a separate check on a toolkit-created scratch project:

```powershell
python -B hardware/v4/tools/kicad_v4.py check --scratch-dir hardware/v4/evidence/my-new-smoke `
  --kind erc --kicad-cli 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
```

Existing check reports are not overwritten. Do not open scratch boards in the PCB Editor while these commands run. The toolkit refuses known KiCad lock files; a newly created directory avoids overwriting pre-existing/open boards. It does not claim to detect every externally created editor race without IPC. Windows sandbox restrictions on temporary test directories or native CLI registry access may require the host's normal approval mechanism; do not work around that guard.

## Interfaces and artifacts

- `validate --add-only` omits all original-track/layer arguments and adds only the declared scratch plan. `ipc_install --add-only --allowed-nets ...` extends the established guarded live workflow to whitelisted addition-only batches. Every original object remains exact; counts derive from the explicit baseline and plan. This is the mode for subsequent auxiliary batches, avoiding any replay of the completed PROG/BATTERY change.
- `route_plan` screens bounded F.Cu/B.Cu paths using exported snapshots only. It accounts for all-layer copper at through-vias and conservatively excludes holes near net-tie bridges. No CAD/native API access; optional NumPy dependency. Raster screening is not final clearance evidence; validate every candidate natively, inspect the resulting copper and remove redundant same-net branches before installation. `review` renders exported pads/tracks/vias only and makes no zone-hole/field-solver claim.
- `post_batch check` runs read-only production DRC/parity/ERC with saved-hash guards and monitored CLI workers; never passes external save/refill flags. `post_batch verify` compares exported native snapshots with shared preservation, exact additions, warning multisets and ignored rules, then saves actual remaining DRC entries by net.

- `validate --add-only --allow-u3-placement` is the **scratch-only Phase4.8 exception** for exactly `L2/C37/C33/C45`, supplied as `placements: {ref: [x_mm,y_mm,angle_deg]}` in the plan. It cannot combine with an original track/layer change. U3/local-net whitelists, native rigid pad-transform checks, unchanged unrelated footprints/pads and exact saved/reloaded additions are required. It does not authorize any live production relocation. Start each candidate from the accepted production manifest into a fresh directory; never edit/reuse a previously open scratch board.
- `probe` uses the same explicit source/baseline/fresh-output/native-Python arguments as `snapshot` and exports native API availability/docstrings without saving. `audit --scratch-dir ... --native-python ...` is a read-only monitored audit of an unlocked toolkit-created scratch board, with new `audit.log/native-audit.json` outputs; it exports complete zone outlines/layers/restrictions (including RF rule areas), board artwork and footprint artwork for preservation comparisons. Source/context hashes remain guarded; no CAD save is performed.
- `geometry.inventory_row(item, board, pcbnew)`: UUID/net, track endpoints/width/layer or via position/drill/per-layer copper widths. Via handling precedes PCB_TRACK because PCB_VIA inherits PCB_TRACK. Never call parameterless GetWidth on a via.
- `geometry.pad_row(...)`, `snapshot(...)`: native copper polygons, pad drill dimensions/shape, positions/nets, footprint metadata and filled-zone polygons. UUID-keyed dictionaries reject duplicate identities. Geometry is in mm. The original snapshot retains its outer-contour schema for compatibility. Separate `layout.json/layout-placed.json/layout-final.json` export actual courtyards, board outline and native outline/hole topology. KiCad can encode holes as bridged/fractured outlines with `HoleCount=0`: do not interpret that as absence of antipads. A plan `review_bounds: [x0,y0,x1,y1]` enables bounded0.1mm native `HitTestFilledArea` sampling and direct via/plane probes after reload/refill. It samples fill, not physical drill voids; subtract actual drill dimensions for conductive-path analysis. These are not field-solver models.
- `u3_review` computes declared-route lengths, explicit projected centerline loop areas, raster-union SW copper areas, sampled return paths through actual native plane fill with drill voids removed, FB reference coverage and stated copper-resistance/legacy thermal screens. It reads exports only. `review.render_u3` renders focused F.Cu/In1.Cu/In2.Cu and loop images from those exports; no CAD access.
- `geometry.preservation(before, after, track_change)`: exact original routed objects, footprint/pad metadata and geometry; allows only the declared original layer change and added routed objects. Zone UUIDs/nets/layers remain; refill may change filled contours. `native.verify_added` independently compares every added item to the plan after reload and DRC.
- `safety.prepare_scratch`, `verify_context`: resolve paths, bind accepted saved hashes, refuse existing/production output, verify copied project/schematic/rule sidecars, check locks and source preservation before native saves/checks. Source is read only as bytes; native API loads solely the scratch copy.
- `checks.parse_check`, `run_check`: native JSON DRC/ERC parser and monitored execution. Missing/incompatible report fields fail closed; zero findings is never substituted for unavailable evidence. DRC parity is required and the scratch schematic must exist for meaningful parity.
- `safety.run_monitored`: captures full stdout/stderr, detects assertion/IPC failure text even without a newline, stops only its own child, and raises an actionable STOP. No assertion suppression, editor restart or retry. Inspection/owner recovery follows AGENTS.md.

JSON artifacts use schema version1 at the summary/context level. Route-plan v1 uses `tracks: [[net, layer, width, x1,y1,x2,y2], ...]`, `vias: [[net,x,y,diameter,drill], ...]`, with `failure: null`. Snapshots, UUIDs, reports, logs, declared plan, build summary and preservation results remain in the output directory. Native stdout is summarized; full diagnostic output stays in logs.

## Maintenance

### Bounded live production installation

`v4kicad.ipc_install` is a separate, owner-authorized live IPC adapter for the exact Phase4.7 plan. Offline `validate` remains scratch-only. Use `python -B -m v4kicad.ipc_install` from this tools directory, with explicit `preflight` then `apply`, `--board`, `--baseline-manifest`, `--plan`, fresh `--output-dir` and `--socket`. The accepted IPC manifest must include full item captures plus saved hashes. It refuses baseline/request drift, duplicate actions and unexpected counts. Owner must reconcile unsaved editor state first; preflight normalizes only documented runtime IDs and inactive circle-anchor metadata.

The owning editor alone mutates, refills and saves production. **New objects are staged until push_commit; do not check visible counts before pushing.** Persist the native commit token immediately. Check returned created geometry before push and independently verify visible geometry afterwards. Do not auto-drop/retry/recover on failure. Full logs, push state and hashes support explicit recovery decisions. Run fresh production CLI DRC/ERC/parity without CLI save/refill against an open board; use the existing isolated snapshot and shared preservation for independent saved readback. See `../evidence/phase4-7-production-installed-final/checkpoint.md` for the completed bounded workflow.

Keep electrical decisions/approval boundaries in V4 requirements/checkpoints. Toolkit maintenance belongs here, not in a new independent geometry script. Preserve the exact prior via failure regression, test a mixed inventory with different per-layer widths, hash/path/lock guards, malformed report rejection and worker stop behavior whenever touching those paths. Use `python -B` to avoid bytecode caches. Unit tests simulate assertion text/API misuse; they never trigger a real KiCad assertion. Run a native read-only snapshot after unit tests before using a changed native workflow.

The old `phase4_7_layer_validation.py`, `phase4_7_layer_geometry.py` and `phase4_7_native_width_smoke.py` are compatibility entry points forwarding to this CLI with explicit arguments. Other scripts under evidence are historical checkpoint artifacts; do not import or reuse their independent native implementations for new work. No general framework, production save command or automatic assertion recovery is provided.
