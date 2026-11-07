# Phase 4.8 — complete local U3 scratch proposal; STOP for production review

2026-10-16. **The bounded local U3 layout is physically DRC-clean and electrically reasonable for prototype evaluation under the stated assumptions. No production change is authorized or performed.** U4/U5 Batch B remains unstarted. This is a local routing-feasibility result, not a powered or thermally qualified supply.

## Exact candidate and placement

Start from accepted production SHA256 `8c2f16ff54b803f7c52b2b9084153f2f7c09f88403edd7643f6d7010f1cf5379`,405tracks/145vias/154footprints/473pads. The proposed changes are exactly four native rigid footprint transforms and **68 added tracks /11 added through-vias**. No original copper is removed, moved, widened or relayered.

| Ref | Production center /angle | Original trial | Final proposed center /angle | Reason for trial adjustment |
|---|---|---|---|---|
| L2 |(49,71)/0°|(50,85)/−90°|**(49.65,85)/−90°**|0.35mm left clears actual C33 courtyard; retains0.12mm courtyard gap.|
| C37 |(49,76)/0°|(50.8,79.5)/−90°|**(50.9,79.5)/−90°**|0.10mm right improves U3 courtyard gap from0.03 to0.13mm.|
| C33 |(55,76)/90°|(54,85)/90°|**(54,85)/90°**|Unchanged from trial.|
| C45 |(58,76)/90°|(56.8,85)/90°|**(56.4,85)/90°**|0.40mm left clears fixed TP13 courtyard; positive spacing to C33 also retained.|

U3 remains **(49,79)/0°**. Every other footprint is fixed. The original trial failed two native courtyard checks (L2–C33,C45–TP13); the adjusted four-reference placement passed. Final native DRC also checks copper, holes, courtyards, edge constraints and parity under the existing rules. Existing ignored silk/other checks remain unchanged, not newly waived. The new output copper ends at local TP13; space toward C70/U5 remains for a later separately authorized handoff. No F5 placement/routing change.

- Exact immutable routing/placement input: [proposal plan](phase4-8-u3-proposal-plan.json).
- Native saved/refilled/reloaded [scratch PCB](phase4-8-u3-proposal-scratch/ups12v_v4.kicad_pcb), SHA256 `36687b95ad648042563c7f8700f01b0f3da8fcde15e35da4071fedb273c81de2`.
- Scratch counts: **473tracks/156vias/154footprints/473pads**. Do not replace the open production board with this file.

## Electrical geometry comparison

| Measure | Rejected fixed placement | Proposed complete local stage |
|---|---:|---:|
| SW U3.5→L2 route |9.761mm,F/B,2vias|**3.703mm,F.Cu,0vias**|
| BST U3.6→C37.1 |8.213mm|**1.255mm,F.Cu**|
| Bootstrap SW return U3.5→C37.2 |4.309mm|**1.894mm,F.Cu**|
| Bootstrap projected loop area |6.324mm²|**1.143mm²**|
| Total SW copper area,F.Cu+B.Cu |8.912mm²|**8.295mm²,F.Cu only**|
| Input high-frequency projected loop |Not completed|**3.497mm²**|
| Output loop via C33 /C45 |Not completed|**19.272 /34.552mm²**|

SW length is the declared native trace centerline from U3.5 to the landing point(50,83.345) inside L2.1; no redundant final segment to the pad center is added. L2.1 center is(49.65,83.345). The actual exposed trace stops at the inductor land edge earlier. F.Cu SW area is essentially unchanged (8.295 versus8.301mm²) because the unchanged large inductor land dominates and the new trace is wider; removal of the former B.Cu crossing accounts for most area reduction. Areas use0.01mm raster union of pads/tracks/via lands, not solder-mask openings.

Loop areas are projected centerline polygons using declared routing, representative conductive plane paths and straight internal IC/inductor/capacitor closures. They allow useful geometric comparison but **are not measured inductance, magnetic fields or exact current-density solutions**. The output loops contain filtered inductor current; C33 is the nearer local output capacitor and C45 adds parallel local storage with its own ground vias.

### Input and output current paths

- Fast input loop: C43.1 SYS→0.5mm F.Cu feed→short0.28mm U3.3 neck→internal devices→U3.4→short0.28mm neck→0.6mm F.Cu PGND→C43.2. VIN path4.870mm; direct PGND return1.624mm. This loop closes on F.Cu and does not require power-via layer changes. The fixed capacitor orientation causes a bend around the pad row, but the resulting small loop and widened feed are reasonable within the approved fixed-U3/C43 boundary. C32 is connected as local bulk input; the proposed upstream SYS port is C32.1.
- SW leaves pin5 through a0.368mm long0.28mm escape, widens through0.5mm to0.8mm, and enters L2 directly. C37 is beside pins5/6; BST and its SW branch are0.28mm. No SW/BST vias or gratuitous SW pour.
- L2.2→C33.1→C45.1 uses1.2mm F.Cu; C45→TP13 uses0.8mm. Both capacitor negatives have independent pairs of0.60/0.30mm PGND vias and0.6mm F.Cu escapes. U3/input return has a pair of0.60/0.30mm PGND vias. No return is forced through a remote charger ground via or through the feedback resistor's ground trace.
- R36/R37 EN divider and C39 SS are physically routed; U3.1 RT remains intentionally floating at the existing500kHz setting. No topology/value change.

### Quiet sensing and actual ground reference

R32's MAIN input is sensed separately from **C33.1**, using two0.50/0.30mm vias and a0.2mm In2.Cu Kelvin trace. It does not share the U5/remote load-distribution voltage drop. The FB node stays on F.Cu above/right of the switching route; R33's ground reaches its own nearby PGND via at(52.6,78.7), rather than sharing the narrow fast switching return escape. Low-current FB/EN/SS traces are0.25mm; no current-capacity argument depends on those traces.

Native `HitTestFilledArea` sampling covers the entire16×15mm local area at0.1mm pitch, plus direct via probes. All9 new PGND vias have connected surrounding In1 fill. The2 MAIN sense vias create local antipads; **no SW via antipads exist**. All597 sampled FB center/±0.15mm reference points are over PGND fill. Actual output and quiet-reference plane paths were found after subtracting real drill voids; no diagonal jump across a missing cell was allowed. Representative annulus-to-annulus paths are6.536mm(C33),8.936mm(C45),5.056mm(FB reference).

The native In1 fill remains one connected exported contour. KiCad represents its antipads in a fractured/bridged outline; `HoleCount=0` does not mean holes are absent. The native occupancy probes and layer image explicitly show those voids. No In1 tracks, zone edits, plane slots or ground moat are introduced. No direct GND↔PGND path is added; established NT1 and NT2 remain exact.

## Plausible prototype capacity and remaining qualification

Copper screen assumes **35µm outer copper**,20°C resistivity1.724e−8Ωm and the already approved approximately1A normal supply target. This is an assumption for review, not a change to the unconfirmed manufacturing stackup. Calculated local VIN-path resistance is5.332mΩ and SW-path resistance2.863mΩ. At1A SW conduction this is approximately2.9mW; even1.1A RMS is approximately3.5mW. The0.28mm neck is short and adjoining wider lands/traces. Legacy IPC-2221 external-trace screening at1A gives about11.2°C for an indefinitely long0.28mm trace,4.3°C for0.5mm,2.0°C for0.8mm and1.0°C for1.2mm. These empirical screens do not predict this board's component temperature or replace IPC-2152/thermal verification.

Illustrative via resistance with1.6mm board,0.30mm drill and20µm barrel plating is approximately1.46mΩ per via; the local power-return pairs provide parallel electrical and thermal paths. Actual plating/stackup and current sharing remain to be confirmed. Existing PGND plane and local via pairs provide spreading, but U3 has no newly invented heatsink or thermal rating. **This is not a3A layout rating.**

For a first-order inductor check at18V→3.3V,1A,450kHz and L=4.7µH−20%, calculated ripple is1.59App, peak1.80A and RMS1.10A. Coilcraft's current XAL5030-472MEC data lists40mΩ maximum DCR,6.7A typical30%-drop saturation current at25°C and4.3A reference RMS current for20°C rise. That supports plausible current margin for this1A prototype; approximately48mW worst-DCR winding conduction loss follows at1.10A RMS. Bias, AC/core loss, temperature derating and actual assembly remain hardware qualifications.

Existing C32/C43 input and C33/C45 output values/MPNs are retained. Effective capacitance under bias, ripple heating, loop stability, SYS startup/hot-plug and switching-noise performance remain existing electrical/bring-up qualifications. No sourcing/fabrication/power-up was performed. U3 junction temperature cannot be inferred from trace loss: TI's112.2°C/W JEDEC metric is expressly not an application design value; the60.2°C/W EVM result uses a different2oz reference board.

Manufacturer basis, checked2026-10-16: [TI TPS62933 SLUSEA4D,August2022](https://www.ti.com/lit/ds/symlink/tps62933.pdf),§7,§8.4–8.5 and§12.1–12.2; [Coilcraft XAL50xx Document908-1,revision2026-02-26](https://www.coilcraft.com/getmedia/49bc46c8-4b2c-45b9-9b6c-2eaa235ea698/xal50xx.pdf),electrical table and notes5–6. The proposed short same-layer power/bootstrap loops, separate output sensing and continuous ground reference follow the layout guidance; its example stackup/thermal values are not silently transferred to this board.

## Verification, preservation and interfaces still open

- Native scratch save/reload→CLI refill/save/DRC/parity→independent native reload/geometry verification completed. DRC **216unconnected/0physical errors/0parity**. ERC **0errors**.
- Scratch DRC20warnings and ERC11warnings are exactly the same warning multisets as the prior scratch baseline:14footprint mismatches+6library-context issues for DRC;4known label warnings+6footprint-link+1symbol-library warning for ERC. They are **not production counts**. Production remains239unconnected/0physical errors/16warnings/0parity;ERC0errors/4warnings because its three source hashes remain exact.
- Native rigid-transform verification limits changes to the four approved references and preserves pad numbers/nets/drills/shapes. Exact original405tracks/145vias, all other footprint/pad geometry, both zone definitions including RF keepout, board drawings and every unmoved footprint's artwork are preserved. Moved footprint artwork UUIDs remain; source-to-candidate diff contains no added/removed net-name, variant/DNP, property, netclass or zone-definition lines. Schematic/project/rules are byte-preserved. IC1 custom pads, BATTERY layer, REGN and all Phase4.5–4.7 routed copper remain exact.
- **23 toolkit tests PASS**, including fixed via-API regression, placement scope, rigid geometry, hole topology, actual-fill drill avoidance and import safety. No native assertion or IPC instability occurred; no live write was attempted.
- Local `/SW_NORMAL`, `/BST_NORMAL`, `/MAIN_FB`, `/NORMAL_EN`, `/NORMAL_SS` each have0remaining unconnected entries. PGND86→78,local SYS9→6,MAIN19→15 reflect the bounded connections; no other net counts change.
- **Boundary connections remain:** upstream SYS feed from the completed charger source to the local C32 input cluster; MAIN output handoff to C70/U5 and other remote MAIN branches. These are not routed in this U3-only checkpoint. Remaining PGND entry using C32.2 as representative points to remote C25.2; it does not mean the connected local U3 ground cluster is open. Broader PGND completion,U4/U5,F5 and remote signals remain deferred. A powered complete MCU supply is not claimed.

Evidence: [DRC/ERC/reload summary](phase4-8-u3-proposal-scratch/summary.json), [preservation proof and exact hashes](phase4-8-u3-proposal-preservation.json), [metrics and explicit loop/plane paths](phase4-8-u3-proposal-metrics.json), [remaining net entries](phase4-8-u3-proposal-remaining-by-net.json), [native diff](phase4-8-u3-proposal-native.diff), [tests](phase4-8-u3-final-tests.log).

Focused inspected images: [F.Cu](phase4-8-u3-proposal-F.Cu.png), [In1 PGND /return paths](phase4-8-u3-proposal-In1.Cu.png), [In2 Kelvin sense](phase4-8-u3-proposal-In2.Cu.png), [loop centerline overlays](phase4-8-u3-proposal-loops.png). Images use actual native exported geometry and native fill sampling; no field-solver rendering.

**STOP for separate owner production approval of this exact four-reference/68-track/11-via proposal.** Do not apply it automatically or overwrite the open board. Production is still the accepted Phase4.7 baseline. No U4/U5 Batch B,broader routing,fabrication,purchasing,power-up,firmware,commit or push. Recommend a fresh production-installation session after review.
