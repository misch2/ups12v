# UPS V4 — Phase 4.10 F0 checkpoint and owner routing handoff

2026-10-17. **Independent F0 completion installed and verified. STOP for owner review before USB/IC1 manual production intervention or F5.**

## Quick start

- Current production PCB: `hardware/v4/ups_v4/ups12v_v4.kicad_pcb`.
- Review [USB routing instructions](phase4-10-usb-owner-guide.md) and [IC1 escape instructions/diagrams](phase4-10-ic1-owner-guide.md).
- The [separate owner-editable scratch](phase4-10-owner-editable-scratch/ups12v_v4.kicad_pro) starts at this checkpoint. It has not been opened or edited automatically. Production is not replaced by this scratch.
- [Exact remaining entries with endpoint descriptions, coordinates and UUIDs](phase4-10-exact-remaining.md):12F0 and41F5,53total.

## Verified production checkpoint

| Item | Entry | Final |
|---|---|---|
| PCB SHA256 | `a3ba56068026a6942c4ca22d7e0eee8f5f2320afc4defefabbbcee3861b29a78` | `6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80` |
| Tracks / vias | 901 /265 | **944 /283** |
| Footprints / pads / zones | 154 /473 /1 | unchanged |
| DRC unconnected | 68 | **53** |
| DRC physical errors / parity | 0 /0 | **0 /0** |
| DRC inherited warnings | 16 | **16, exact multiset unchanged** |
| ERC errors / inherited warnings | 0 /4 | **0 /4, exact multiset unchanged** |
| Toolkit regression tests | 60 | **61 PASS** |

The final [accepted saved/live manifest](phase4-10-independent-ipc/accepted-installed-baseline.json), [production checks](phase4-10-independent-ipc/production-checks.json), [full live/native preservation](phase4-10-independent-ipc/full-preservation.json) and [independent extra proof](phase4-10-production-extra-preservation.json) identify the actual saved board. The schematic, project and rules remain unchanged. Original901tracks/265vias and every original footprint/pad/artwork/model/field/zone definition are retained. Exactly43tracks/18vias were added.

## Installed functional group

The [exact installed addition-only plan v4](phase4-10-independent-plan-v4.json) closes15independent connections:

| Group | Completed work |
|---|---|
| Primary-power PGND,4entries | C20.2, C22.2, C24.2 and C25.2 each receive three short0.80mm F.Cu connections and three0.60/0.30mm vias into the existing In1 PGND plane. |
| VIN1 / BATTERY,3entries | TP15 VIN1 probe; TP16 BATTERY probe; R4.2 BATTERY input to the existing100R BATP sense branch. These are probe/sense feeds, not replacement high-current trunks. |
| PMID,4entries | C12.1→C20.1→C22.1→C24.1→C25.1 bulk branches on F.Cu. Main width1.20mm; C12–C20 uses a short1.00mm corridor alongside the existing C12/C20 ground lands. No new PMID via bottleneck. |
| USB CC,4entries | J7.A5→R13.1 and J7.B5→R14.1 on In2 with short F fanouts; R13.2/R14.2 local PGND connections. All reserved F/B data-access space remains unoccupied by these additions. |

Fourteen new vias are PGND:12for the isolated bulk pads and2for CC pulldowns. The remaining4vias are2BATTERY probe/sense transitions and2CC transitions. Through-vias are ordinary native objects with exact per-layer padstack widths; no graphic substitutes or forced net assignments.

## Electrical and routing quality

[Native production quality](phase4-10-production-quality.json):43newsegments, **0non-45-degree segments,0sub-0.2mm segments,0acute centerline junction candidates**. Joint order-independent preflight checks all additions against one another, native copper/artwork/pads, holes, keepouts and reservations. No duplicates or clearance waivers were accepted. Two uninstalled microlegs were removed and collinear additions merged; original copper was never optimized.

All14newPGND vias have native plane contact at their centers and all four ring sample points. Production fill polygons are **identical** to the accepted scratch fill, and native all-pad connectivity partitions are identical to scratch. Compared with entry,15pad islands merge and none splits. The PGND/GND relationship through NT1 remains exactly inherited; NT2 still connects ILIM_HIZ and REGN, not a second GND tie. Their pads, bridge graphics and surrounding geometry are preserved. No new connection involves USB_VBUS, USB3V3, MAIN_3V3, MCU3V3 or GND; no new power-domain crossing was introduced. These are topology/geometry proofs, not partial-power hardware measurements.

The [drill-aware geometry/reference review](phase4-10-electrical-geometry-review.json) samples the actual native In1 fill at≤0.05mm along each new signal/power trace and at both edges. All3041PMID samples and699VIN1 samples are over PGND copper. BATTERY and CC paths have localized missing samples near their transitions/connector antipads; complete coordinates are retained. Such samples are not a guarantee of impedance, and the connector transition field remains to be reviewed with USB routing. No broad new reference-plane slot or pad-island split is reported.

Bulk connections use wide same-layer copper rather than a single small via. Each return has three parallel barrels;0.60/0.30mm means0.15mm radial annulus, not0.60mm of solid metal. A0.80mm strip crossed by a centered0.30mm drill has only0.50mm residual strip metal before counting the via pad/barrel and adjacent pad copper. Vias and their parallel count were reviewed as conductors, not decorative stitching. No current or thermal rating is inferred from their count.

One planned signal via at `(80,46)` intentionally joins TP16 to the retained3.00mm-wide In2 BATTERY strip. Its0.30mm drill changes the local residual strip width from3.00to**2.70mm**; the exact retained track is `48d23bf6-f231-45ea-8193-539508f495bd`. It does not force battery current through the0.30mm probe track. This local remaining width exceeds narrower existing battery route sections; the very short constriction does not become the demonstrated geometric bottleneck. Current sharing, plating and temperature are still unmeasured. The R4 feed remains a low-current sense branch with0.25mm width.

For scale only, the C12–C20 portion uses about3.076mm of1.20mm track and6.486mm of1.00mm track: approximately4.46mΩ at20°C with35µm copper andρ=1.724e−8Ωm. This is a uniform-strip calculation, excluding pads, current spreading, AC behavior and heating. It does not qualify the optional bulk bank or establish a load-current limit. [TI BQ25798 SLUSDV2C, June2026, §8.4.1, p139](https://www.ti.com/lit/gpn/bq25798) calls for preserving short local bypasses and low-impedance bulk paths. Existing IC1/L1 SW1/SW2/BTST, C5/C6 bypass, REGN, PROG and U3 switching/bootstrap/feedback objects remain unchanged. The remote optional bulk routing does not replace those bypasses.

C20/C22/C24/C25 remain **DNP** under the existing BOM review; their legacy voltage ratings remain `REPLACE if fitting`. Routing their pads does not approve component procurement, assembly or the optional PMID backup mode. No BOM component/value/footprint/population change occurred.

## Remaining assessment

| Subsystem | Remaining entries | Treatment |
|---|---:|---|
| USB data | 8 | Native owner-assisted routing, including duplicate contacts and both sides of series resistors |
| USB ESD PGND | 1 | U2.3 short return to PGND; solve with USB geometry |
| Charger controls | 3 | IC1.14 SCL, IC1.21 INT, IC1.1 STAT; blocked, no accepted-copper rework |
| F5 SYS | 5 | Deliberately deferred |
| F5 PGND | 12 | Deliberately deferred |
| F5 other nets | 24 | Deliberately deferred |
| **Total** | **53** | **12F0 /41F5** |

Ordinary F0 routing is complete **apart from owner-assisted USB/ESD and the three IC1 escapes**, as measured by the current pad-level DRC records. This is not a design-release or electrical-qualification statement. The exact endpoint/UUID inventory is linked above.

Native `DpCoupledNet` confirmed USB_DP/DN recognition and no coupled net for either generated U1-side name. The USB guide therefore treats each resistor side separately, identifies the duplicated-contact crossing, continuous-reference concerns and total end-to-end skew. No custom A* USB plan was generated, and no historical USB plan was replayed.

The IC1 review includes nine native-export close-ups, current source/destination nets,548outward and624all-direction candidate fanouts per pin, all-layer copper/drill obstruction measurements and specific smallest obstruction sets observed. None is a validated add-only native route. Minimal obstruction sets touch protected SW1/SW2 or the battery-current fanout, so they are **conditional diagnostics, not approved repairs**. A native Walk Around comparison can still discover a better tangent/multi-corner route; bounded custom searches do not prove impossibility.

## Verification sequence and limitations

Entry exact native snapshot, live Konnect board/pad identity and guarded IPC preflight matched the accepted Phase4.9 manifest. Four versioned plans and three validated scratch variants document refinement; the final v4 alone was installed after native create/save/reload/refill/DRC/ERC/parity, routing-quality and preservation checks. Scratch warnings20DRC/11ERC match the unchanged scratch control exactly; they are library-context differences, not new production findings.

Production installation used the existing monitored add-only native SDK transaction, then **owning-editor refill and save**. Independent saved-board native readback, actual fill equality, ERC/DRC/parity, warning-multiset comparison, complete live and serialized retention, pad connectivity and source hashes passed. Final read-only reconciliation is retained under `phase4-10-final-reconciliation/`.

The initial sandboxed IPC attempt was denied `Permission denied` before connection; its log is retained. The approved outside-sandbox read-only check passed. This was not a KiCad assertion or unstable editor transaction. A new extra serialized comparison initially counted the18intended vias as unexpected because the older scratch-replacement comparison excluded only track UUIDs. Offline diagnosis showed zero changed/missing originals and exactly those18newvias. The comparison now excludes only explicitly enumerated new track/via UUIDs, with a negative retained-via regression test; it then passed. No CAD recovery or replay followed either diagnostic.

No native assertion, uncertain write, actual unexpected net/geometry change or unaccounted regression occurred. No USB data, F5 switching, placement, schematic, BOM, netclass, stackup, keepout, zone-definition, firmware, fabrication, purchase, power-up, commit or push work was performed. Signal integrity, ESD performance, bus timing, inrush, power losses, thermal/RF/EMI and matching-hardware measurements remain unqualified.

Focused authored-code/document whitespace checks pass. A whole staged-evidence check also reports four inherited tab-only lines in each byte-identical schematic copy; the copied CAD was deliberately preserved rather than text-normalized. This is separate from the passing native ERC/DRC/parity and preservation checks. Unrelated staged owner changes were left intact.

The accepted legacy cleanup plans remain deferred and uninstalled: [R35v2, C26v3, exact SYS collinear merge](legacy-routing-geometry-review-2026-10-17.md). The southeast SYS45° alternative remains rejected. The existing **0.70mm SYS residual metal width** remains a later current/thermal review item; it was not changed.
