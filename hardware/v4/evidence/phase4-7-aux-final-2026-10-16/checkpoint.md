# Phase 4.7 local REGN / CE_N / CE_BIAS — completed production checkpoint

2026-10-16. **Both bounded production batches completed; STOP for owner review.** Continued from the accepted preferred-PROG production checkpoint. No previous routing or BATTERY layer change was repeated.

## Identity, current connectivity and procedure

Exact live document/project confirmed over Konnect IPC (`ipc_available=true`, `requested_open=true`) and independently by the canonical live-IPC adapter. Saved PCB SHA256 was the accepted `3ec08c7872b7d510829d4c3ce759fdacc74c813c6e5d522000940a842ab6c69b`; schematic/project hashes also matched. Full live capture matched that saved checkpoint, normalizing only documented runtime IDs and inactive circle-anchor metadata. Counts:154footprints/473pads/299tracks/141vias. No unexpected live/saved divergence or unsaved design edits found in captured scope.

Current schematic exported as `../phase4-7-aux-entry/current.net.xml`, current native geometry in `../phase4-7-aux-entry-native/snapshot.json`, and fresh production DRC in `../phase4-7-aux-entry/current-drc.json`. Required connections came from these current artifacts, not historical unrouted lists. Existing IC1.5–C3.1 REGN, ILIM_HIZ–NT2.1, PROG, BATP and TS routing were skipped/preserved.

Canonical `hardware/v4/tools/` reused for native geometry, safety monitoring, scratch save/reload, DRC/ERC parsing, add-only IPC installation and preservation. Add-only mode explicitly disallows original-track changes and whitelists the batch's nets. The bounded export-only feasibility screen accounts for copper on all four layers at through-vias, hole clearance and conservative net-tie bridge exclusion. It requires native DRC and is not a clearance authority. No serialized CAD text was edited.

Scratch feasibility was used for the dense NT2/analog corridor. Rejected scratch candidates (inner-power/hole/net-tie collisions) remain as diagnostic evidence; none was installed. Final plans passed scratch refill/save/reload/DRC/parity and exact preservation. Redundant same-net path branches were removed before final validation. No clearance relaxation, net-tie modification, component movement or original power reroute was needed.

Each production batch used one native undo transaction through the owning live editor, verified returned added geometry, pushed the transaction before visible-object/count readback, refilled and saved through that editor. Then fresh **production** DRC/ERC/parity and independent native readback of an isolated saved copy were completed before the next batch. No scratch board replacement or external overwrite of the open board. No native assertion, IPC instability or unexpected production DRC/preservation failure occurred.

## Completed batches

| Batch | Current connections completed | Added geometry | Production DRC / ERC |
|---|---|---|---|
| REGN / NT2 | C3.1/IC1.5 network → NT2.2; NT2.2 → R6.1; R6.1 → D3.2, with shared branches |32tracks,0.20mm;2through-vias Ø0.50/0.30mm at(57.2,66.3)/(72.1,69.4)|248unconnected,0physical errors,16known warnings,0parity;ERC0errors/4known warnings|
| CE_N / CE_BIAS | CE_N:IC1.13/R9.1/TP14.1/Q3.3. CE_BIAS:R9.2/D3.1/D4.1 |45tracks,0.15mm,F.Cu;0vias. D4.1 connected by a short branch; D4.2 MAIN_3V3 untouched|243unconnected,0physical errors,16known warnings,0parity;ERC0errors/4known warnings|

REGN uses the existing 0.20mm local REGN width; its short IC1–C3 decoupling connection and C3 return remain intact. Two through-vias avoid unavailable F.Cu crossings; their per-layer copper sizes/drills were verified natively. Total new REGN copper44.246621mm is a branched network, not a single C3–NT2 path. CE_N adds27.753531mm; CE_BIAS adds40.237845mm. Their lengths reflect preserved placement/copper constraints, not high-speed signalling or timing matching.

No additional local ground return was necessary. Fresh DRC contains no ground/PGND unconnected entry touching C3, Q3, R10, R7, NT1 or NT2. Their existing returns and intentional NT1/NT2 topology remain unchanged; no direct GND↔PGND or ILIM_HIZ↔REGN shortcut was added outside the existing net-ties.

## Actual remaining unconnected entries

Counts below are native DRC entries, not a unique-endpoint count; airwire representative endpoints can change when networks merge.

| Net | Entry | After REGN | Final | Meaning |
|---|---:|---:|---:|---|
| REGN |4|1|**1**|Only deferred R8.1:final report pairs `Track [REGN] on F.Cu,length1.1885mm` with `Pad1 [REGN] of R8`|
| CE_N |3|3|**0**|All approved local pads connected|
| CE_BIAS |2|2|**0**|All approved local pads connected;D4 supply remains deferred|
| ILIM_HIZ |0|0|0|Existing route preserved|
| TS |2|2|2|Unchanged: R7.2↔existing TS track; R7.2↔J6.2. Local R7.2 branch was not in this REGN/CE add-only scope; report it explicitly rather than claiming all TS routing complete|
| GND |1|1|1|Unchanged deferred GND track↔J6.1|
| PGND |86|86|86|Unchanged whole-board PGND entries; none touches the affected local returns listed above|

Full final endpoint descriptions: `remaining-by-net.json`; per-batch descriptions in `../phase4-7-aux-regn-production/remaining-by-net.json` and `../phase4-7-aux-ce-production/remaining-by-net.json`. No routing was performed toward R8, J6, Q5/host-control, remote /CHG_GATE, D4.2 MAIN_3V3, MCU/I2C/INT/U3/U7/F5 or general remaining board nets.

## Preservation and final saved state

**77tracks/2vias added cumulatively; no original routed object changed.** Final154footprints/473pads/**376tracks/143vias**. Shared preservation compares every original track, via with per-layer widths/drill, footprint metadata and pad geometry/nets/drills against the accepted299-track baseline. Exact additions match the union of both validated plans. PROG/BATP/ILIM_HIZ/TS and BATTERY In2 adjustment retained exactly.

Full original live footprint/pad/shape/text objects and zone definitions (including RF rule area) match entry. Only the expected `filledPolygons` cache changed during refill; In1 PGND remains **one filled contour**. C3/C9/C23, net-ties, IC1 custom pads, Nano-Fit connectors, all placement, schematic and project bytes unchanged. Project hash preserves netclasses and DRC settings. Focused native-save diff contains only additions and fill updates, with no footprint/outline/rule-area structural edits. Native snapshots export outer contours rather than complete hole topology; no field-solver/plane-impedance claim is made.

Final saved PCB SHA256:`05fd52862efd2ee0da74f225192fd8e0ee27cfc94545d7d2543fbb8a1237c930`. Schematic SHA256:`990d107296d149775884dc2d2512c2e6102b6191e4818e7fcf5bd9268d48c8f6`;project SHA256:`477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e`. Post-check hashes match `installed-manifest.json`.

Final production warnings are **16 identical library-footprint-mismatch entries**; inherited ignored categories unchanged. Scratch's20library-context warnings are not production results. Fresh production ERC remains0errors/4known warnings. Toolkit regression suite now **19PASS**, including all-layer through-via screening, off-region geometry handling, scope guards and import safety.

## Electrical basis and limits

Manufacturer basis checked2026-10-16: [TI BQ25798 SLUSDV2C, revised June2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf), pin functions/Table5-1, §7.3.4.1, §8.4.1–8.4.2. REGN powers internal gate drivers and charger-related bias/pull-ups; its local bypass remains at IC1. The new paths serve existing approved charger bias/enable networks only; no new load or topology was introduced. Widths follow existing local signal construction, not a high-current power-path sizing claim.

The REGN B.Cu distribution lacks a continuous adjacent ground reference on In2 and passes near existing switching/power copper; In1 shielding is useful where present, but does not prove noise immunity. CE nets stay on F.Cu over the existing In1 reference where filled. Long constrained CE_BIAS/REGN paths and added plane antipads remain prototype coupling considerations; no startup/enable/TS noise or thermal measurement exists. Scope-preserving DRC cleanliness is not hardware qualification.

Previously accepted BATTERY loss of independent F.Cu conductance/outer heat spreading and PROG bootstrap/reference/coupling limits remain exactly as recorded in `../phase4-7-production-installed-final/checkpoint.md`. This batch neither repeats nor removes that layer change. No new mandatory threshold, protection circuit or component was added.

## Evidence and stop

Batch1:`../phase4-7-aux-regn-production/` plus `../phase4-7-aux-regn-native/snapshot.json`;batch2:`../phase4-7-aux-ce-production/` plus `../phase4-7-aux-ce-native/snapshot.json`. Final union:`installed-plan.json`,`native-preservation.json`,`native-save.diff`,`summary.json`,`installed-manifest.json`,copied production reports and `remaining-by-net.json`. Exact plans:`../phase4-7-aux-regn-install-plan.json`,`../phase4-7-aux-ce-install-plan.json`. Scratch checks:`../phase4-7-aux-regn-install-scratch/`,`../phase4-7-aux-ce-install-scratch/`.

**STOP for owner review.** Recommend a fresh session and separate scope approval before any other routing. No fabrication,purchasing,power-up,firmware,Git commit or push.
