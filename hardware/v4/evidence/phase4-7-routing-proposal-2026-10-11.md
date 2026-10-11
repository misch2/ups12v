# Phase 4.7 — charger auxiliary/control routing proposal

2026-10-11. **Read-only preflight complete; proposal only. STOP for owner approval.** No production CAD mutation, save, refill, DRC rerun, identifier repair/normalization or further live API operation was made during this resumed preflight.

## Authority and evidence

Owner accepted the runtime parent/four IC1 custom-primitive UUID differences and authorized read-only preflight. The approved post-assertion kipy snapshot is the live-captured authority; saved PCB/schematic/project hashes still match it. Analysis uses that capture, the matching native geometry evidence already collected before the stop, exported schematic XML and existing saved-board DRC. No native geometry code was rerun. Full evidence: `phase4-7-affected-connectivity.json`, `phase4-7-geometry.json`, `c9-apply-phase4-7-post-assertion-approved-ipc.json`, `phase4-7-preflight.net.xml`, `phase4-7-preflight-drc.json`. The offline script `phase4_7_review_saved.py` verified saved hashes and exported pad-net assignments and produced `phase4-7-local-layout.png`, inspected for this checkpoint. Plot uses pad bounding boxes and omits fills; it is not a clearance certificate.

Baseline preserved:154 footprints/473 pads/240 tracks/134 vias/2 zones; C9(61.1,69.1),0degrees. Existing saved DRC262unconnected/0other errors/16library warnings/0parity is reused, not represented as a newly run check. No physical measurements or thermal/noise validation were made.

TI references: fitted schematic IC1 remains BQ25798RQMR; accepted BQ25792 architecture/alternative decision is not a part substitution. [BQ25798 SLUSDV2C, June2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf), section5/Table5-1 and section8.4.1/p139: close REGN decoupling with at least two ground vias; BATP/TS away from switching nodes. Existing local BQ25792 SLUSDG1D/April2026 evidence, section11.1/p134, agrees on short REGN/bootstrap paths and BATP separation. These references justify routing priorities, not architectural changes.

## Exact primary nets and remaining connections

Coordinates below are pad centres in mm. DRC counts are existing missing-connection records, not a unique prescribed ratsnest topology. No-copper nets have neither tracks nor vias.

| Net | Exact pads | Current copper / missing records |
|---|---|---|
| REGN | IC1.5(58.1,66); C3.1(56.3,66.45); NT2.2(64.4,68.9); R6.1(71,71.4125); D3.2(78.4,57.5); R8.1(39.0875,75.5) | IC1–C3 complete,2 F.Cu segments;4 remaining records to four isolated bias loads |
| ILIM_HIZ | IC1.17(61.85,67.2); NT2.1(63.4,68.9) | No copper;1 record. Existing NT2 is the intentional connection to REGN; retain it |
| TS | IC1.16(61.85,67.6); R6.2(71,69.5875); R7.2(77,71.5875); J6.2(101.5,38.5) | No copper;3 records |
| BATP | IC1.18(61.875,66.8); C23.1(71.5,66.78); R4.1(74.9,66.2125) | No copper;2 records |
| PROG | IC1.20(61.9,66); R5.1(63.5875,71.2) | No copper;1 record |
| CE_N | IC1.13(60.2,67.9); R9.1(61,72.5125); Q3.3(76.8625,63.25); TP14.1(73.4,72) | No copper;3 records |

The six primary nets account for14 existing missing-connection records. Completing the local subset below intentionally leaves remote branches outstanding.

Necessary supporting connections:

- **GND**, a distinct net: R5.2(65.4125,71.2), R7.1(77,73.4125), NT1.1(67,70.8), J6.1(104,38.5); no tracks/vias,3 records. Connect R5/R7 to NT1.1. NT1.2 is PGND at(68,70.8), already has a plane connection. Never ground R5/R7 directly with PGND vias: that bypasses NT1.
- **BATTERY sense feed**: R4.2(74.9,64.3875) is isolated. Add only its low-current sense branch to the existing BATTERY network at C4/C10; no battery power-trunk change. Keep existing100ohm R4 and47nF C23.
- **PGND**: C23.2(71.5,65.82), Q3.2(78.7375,62.3) and R10.2(78.9125,66) have existing missing return connections. Add short local plane escapes; these are necessary, not optional stitching.
- **CE_BIAS**: D3.1(75.6,57.5), D4.1(81,63.1), R9.2(61,70.6875); no copper,2 records. Preserve the diode-OR topology and R9 pull-up. D4.2 is MAIN_3V3 at(81,60.3); its rail feed remains outstanding and must not silently pull U3/U7 supply routing into this milestone.
- **/CHG_GATE**: Q3.1(78.7375,64.2), R10.1(77.0875,66), Q5.3(86.4375,70.5); no copper. Local Q3–R10 and R10 PGND return belong to default-off control. The Q5 collector branch and its host/supply/base network can remain deferred, with no functional-completion claim.

Already complete and held: ACDRV1(9tracks/2vias), BTST1(2/0), BTST2(6/2), SDRV(3/0); existing DRC has zero missing records for these nets. IC1 D+/D-/QON are intentional unconnected pins, not routing targets. STAT,~INT,I2C_SCL/I2C_SDA and CHG_REQ are incomplete but host/status fanout is outside the recommended local batch.

## Physical constraints and proposed corridors

1. **Hold the decoupling loop.** C3 is4.7uF/25V, linked to IC1.5 by the existing0.2mm F.Cu path (~1.89mm). C3.2 PGND at(56.3,68.35) has the two existing0.5/0.3mm vias at(56.3,68.35)/(56.95,68.35). Leave capacitor, traces and return unchanged. Branch additional REGN bias from this connected net rather than rerouting its loop through the loads.
2. **Keep sensitive routes outside switching copper.** SW1/SW2 occupy F.Cu under IC1 aroundX59.1–60.9,Y64.3–66.9 and substantial B.Cu paths extending north to the inductor. B.Cu also carries SW2 nearX64.3–64.5,Y54.65–65.48. Do not use the package interior/north side as a shortcut. PGND is the existing continuous In1 plane; no signal tracks or splits there. B.Cu is not automatically a quiet reference layer: adjacent In2 contains power routing, so keep B.Cu crossings short and avoid parallel overlap with power trunks.
3. **East/south signal escape.** IC1.17/18/20 are0.2mm-tall F.Cu lands at0.4mm pitch; IC1.13 is0.2mm-wide. TS/IC1.16 is custom copper: retain its captured polygon; its tiny anchor size is not its full copper extent. Use0.2mm escapes as on existing local routing, transition only outside pad/neighbor copper. Proposed0.5/0.3mm through-vias match existing signal vias; positions remain subject to explicit padstack clearance checks. Netclass Default0.5mm trace/1.0mm via is a default, not a suitable automatic fine-pitch escape size. Do not change project netclasses in this milestone.
4. **Local bias/control corridor:** use F.Cu where clear south/east of IC1 and short B.Cu bridges where C9/NT2 or C10/C4 obstruct F.Cu; working area approximatelyX56–82,Y57–74. Cross south of the B.Cu switching region, broadlyY69.7–73, with separate tracks around R5/R9/NT1. Reserve bottom-pin escape space for future SCL/SDA. No straight-line route through C9, its via(61.9,69.1), or the VAC1 spur. No demand to change accepted power copper to make room.
5. **BATP:** escape IC1.18 east, stay outside the switching-via field, then run toward C23.1 and R4.1 nearY66.8–67.8, using a short layer bridge to avoid C10/C4/BATTERY pads and vias. Prefer F.Cu over In1 for most of the sense run; do not share BATP copper with a BATTERY power segment. At R4.2 take a separate sense branch from the existing battery node. Give C23.2 a short PGND via escape. This is a routed sense network with the existing filter, not a newly added circuit.
6. **PROG/ILIM:** fan PROG outward before turning south to R5.1; route R5.2 to NT1.1. Route IC1.17 to NT2.1, then distribute REGN from NT2.2 toward R6/D3. NT2 copper pads are0.5mm square atX63.4/64.4,Y68.9. Do not merge its named nets by bypassing the tie. Keep PROG separate from the REGN supply branch and switching copper.
7. **TS:** connect IC1.16 to R6.2/R7.2 outside C9/NT2, broadlyX63–77,Y69.5–73; R7 return goes to NT1.1. The J6 thermistor branch is a long separate routing decision, not a short local completion. Reserve a TS/GND pair to J6 with a verified corridor around power blocks; the temptingX94–105,Y52–72 path contains L3/U7 and associated parts. Do not assume that path is clear or route through U7 power territory. The all-layer antenna keepout isX75.4–88.6,Y99.2–104.6 and remains untouched.
8. **CE:** connect R9/IC1.13/TP14 south of C9 and across to Q3.3; carry CE_BIAS from R9.2 around the east side to D3.1/D4.1. Keep the branches distinct at R9. For REGN→D3 use an east-side path outside SW/inductor copper, rather than a diagonal through the power stage. Route local Q3 gate–R10 and its return without bypassing Q5 logic.

Corridors are planning regions, not tested polylines or guarantees of clearance. Exact via sites and bends require the normal bounded routing/DRC verification after approval; any obstruction requiring a held power trace or unrelated component to move is a stop-and-review condition.

## Necessary changes versus optional optimizations

**Necessary:** named missing local connections, correct C23/Q3/R10 PGND returns, R4 sense feed, distinct GND return through NT1, preservation of switching-node separation. No placement change is demonstrated necessary; recommend a first routing batch with **zero component moves and zero existing track/via deletions**.

**Optional, not in the recommended batch:** move C23 closer to IC1.18 to shorten the unfiltered BATP pin-to-cap run (currently9.625mm direct pad separation). The narrow east pocket contains BTST2 via(62.5,66.4), BATTERY vias(63.8,66.9)/(64.5,67.6), IC1 courtyard endingX62.45 and C10 courtyard startingX65.02. A speculative placement there is not approved or clearance-proven; no coordinate is prescribed. Moving R5 or R6/R7 could shorten traces, but the current positions permit a corridor-based approach and no demonstrated electrical hazard justifies moving them. Retain existing values, footprints and BOM.

## Recommended approval boundary and risks

Approve **local charger completion only**: REGN branches to NT2/R6/D3; ILIM; local TS divider and GND through NT1; BATP/C23/R4 sense feed and C23 return; PROG and return; full CE_N/CE_BIAS local network; Q3–R10 gate link and their PGND returns. All existing power/decoupling/switching copper and placements held. No architecture changes or added protection.

Explicitly defer REGN→R8/status-LED branch, TS/GND long run to J6, Q5/host gate chain and MAIN_3V3/D4 supply completion, status/interrupt/I2C and all general-board routing. These remain documented missing connections; local routing alone does not make the charger functional or release-ready. If the owner wants the remote branches in Phase4.7, approve them as an additional bounded corridor review before routing them.

Main risks: fine-pitch/custom-pad clearance; via antipads narrowing the PGND plane; coupling to B.Cu switching or In2 battery paths; remote BATP filter placement; accidental bypass of NT1/NT2; incomplete CE supply/control and remote thermistor circuits. No new protection requirement or hardware acceptance threshold is inferred. After an approved routing batch, use assertion-safe live readback, refill/save only within that later authorization, and affected ERC/DRC/parity/diff checks. Both ERC and DRC remain mandatory before release; current checks do not prove signal quality on hardware.

**STOP: no routing or component movement authorized by this report.**
