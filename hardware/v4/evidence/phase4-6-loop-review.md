# Phase 4.6 — bounded IC1/L1 switching-loop improvement

2026-10-11. **Checkpoint complete; stop before remaining-board routing. Next milestone: Phoenix J1/J2/J3 → Nano-Fit.** Exact connector/header/harness MPNs remain to select and verify. No connector substitution, manufacturing output, purchasing, firmware build, commit or push occurred.

## Result

The large 12mm L1 remains on F.Cu, 180°, moved from(60,50.5) to(60,52.2), **1.7mm closer to IC1**. This is a modest improvement, not a compact reference-layout equivalent. A trial3.5mm move conflicted with the close bypass/bulk layout and existing vias; it was superseded, not retained. C5/C6 and IC1 stay at their accepted locations. Six final moves only:

| Ref | Before x/y/angle | Final x/y/angle | Purpose |
|---|---|---|---|
| L1 | 60/50.5/180 | 60/52.2/180 | Shorter switched interconnect |
| C12 | 52.5/59.7/90 | 51.2/55/90 | PMID bulk clears the inductor courtyard |
| C15 | 57/59.7/90 | 58.65/60.6/0 | Local same-face PMID bulk beside C6; short direct PGND vias |
| C17 | 62/60/90 | 63.7/60.6/90 | SYS bulk clears L1 and C5 return vias |
| C14 | 64.7/60/90 | 65.8/60.6/90 | Preserve compact same-face SYS bank |
| C11 | 67.4/60/90 | 67.95/60/90 | Clearance to L1/C14 |

All154 references, MPN/value properties, footprint identities, population attributes, custom IC1 pads, RF rule area and96×70mm outline are preserved. C13/C8/C2 trial moves were restored exactly. The schematic is byte-identical to HEAD. BOM components are unchanged; connector replacement decisions are recorded in `V4_BOM_REVIEW.md`.

## Switched copper and current screening

| Measure | Before | Final |
|---|---:|---:|
| SW1 main centreline, same package-side junction to L1 land centre | 17.313mm | **15.441mm (-10.8%)** |
| SW2 main centreline, same junction to L1 land centre | 14.040mm | **11.941mm (-15.0%)** |
| Former SW1 narrow section | 1.2mm | **1.5mm /1.6mm** |
| Main switch runs / land fanout | 2.2mm /3mm | 2.2mm /3mm |
| L1 vias | 12 per land | 12 per land, relocated |
| IC1 switch vias | 6 per switch net | Unchanged |

These lengths are reproducible trace centrelines between defined junctions, **not full physical current-loop perimeters**. They exclude unchanged package pin necks/via-array fanout and the inductor winding. The preceding18–22mm estimate included those escapes. Tiny0.2–0.5mm package/array connections still exist; their spreading/current sharing needs thermal qualification. Do not describe the entire SW net as1.5mm minimum width.

Using the same inherited IPC-2221 screening assumptions (35µm external copper, illustrative30°C rise), 1.2/1.5/1.6/2.2mm screen at **4.426/5.203/5.453/6.869A**. The1.5mm main section now clears the conservative5.08A RMS envelope, with only approximately2.4% numerical margin. This is an engineering screen, **not measured temperature or a new owner acceptance limit**. Actual stackup/plating, ambient, current distribution and package neck heat spreading remain unqualified. The need for an awkward escape remains because existing VBUS/PGND vias constrain the corridor; no extra via deletion or wholesale power-stage redesign was imposed.

Owner natively deleted the preselected24 L1 vias. Konnect created24 replacement switch vias, two C12 return vias and two C15 return vias. Total135 vias vs131. Two retained former C12 return vias were tied into the local B.Cu PGND stitching network, with no new GND/PGND short or dangling warnings. Total242 tracks vs234.

## Actual current-loop assessment

Basis refreshed from [TI BQ25798 SLUSDV2C, revised June2026, §8.4.1–8.4.2 and Figures8-20/8-21](https://www.ti.com/lit/ds/symlink/bq25798.pdf), checked2026-10-11. TI prioritizes same-face PMID/SYS0.1µF bypass and nearby bulk, then multiple switch vias and compact internal/bottom-layer routing; switch-node copper should not be enlarged indiscriminately because of parasitic capacitance and field coupling.

The buck-side fast commutation loop is **PMID bypass → IC1 power switches → IC1 PGND → bypass return**. C6 remains directly above IC1, with its original short PMID escape and paired ground vias. C15 is now local to C6; two vias at(60.1,60.2)/(60.1,60.9) connect its ground land directly to In1. Its nearest pad-centre-to-plane-via distance is approximately0.301mm, vs approximately1.15mm to the old bank via. The new return-via position is roughly3.4mm in XY from IC1 PGND pin27, vs approximately7.36mm for the nearest old C15 return via. These are geometric distances, not simulated return impedance or actual current trajectories.

The boost-side fast loop is **IC1 power switches → SYS bypass → PGND return**. C5 and its original paired return vias remain tight to IC1. The SYS bulk bank was adjusted around those return vias instead of pushing the critical0.1µF bypass away. The unchanged local C5/C6 loops therefore remain the primary high-frequency reference. REGN/C3 and VBUS/C7 local bypasses remain at their accepted locations; their wider fanout scope is unchanged.

The inductor transfer path still crosses the package switch-via arrays, the B.Cu switched conductors and L1 winding. Its switched-voltage copper is shorter, but **B.Cu still has power distribution on adjacent In2, not a continuous adjacent ground layer**. No second ground plane, PGND moat or oversized switch pour was added. In1 remains one connected PGND fill; the new local C15 return improves the bulk return without routing power through NT1. A plane continuity check cannot prove high-frequency impedance, overshoot, ringing or EMI. Final TS/BATP/PROG/I2C routes must stay away from this region. Further major shortening would require another placement strategy or inductor/mechanical decision; that was not silently implemented.

## RF fill visibility

Fresh native refill and exported filled In1 confirm that copper ends around **Y=98.9995mm along the whole lower edge**. RF keepout beginsY=99.2, board edgeY=100; thus the antenna strip is already within the approximately1mm full-width copper setback. There is no local notch to see. The native keepout is still X75.4–88.6/Y99.2–104.6, on all four copper layers. A26,400-point screen of its board-intersecting In1 strip finds zero filled points. Inspect the final manufacturing layers again after all routing; this is geometric/RF-exclusion evidence, not antenna performance measurement.

## Validation and remaining limits

- Native refill completed, followed by save and synchronized saved-file DRC: **262 unrouted /0 other errors /13 identical warnings /0 schematic parity**. Per-net unrouted counts match the baseline. Four nearest-item airwire edges changed as copper geometry changed (PMID optional C20/C22/C24, SYS C61, deferred REGN NT2); exact airwire-tree identity is not a connectivity invariant.
- ERC **0 errors /4 unchanged warnings**. Live schematic-sync dry run **noop**, zero conflicts and zero pad reassignment. Live readback proves all six final placements; live/saved track UUID sets match.
- Preservation/filled-plane verification passes. Native PGND fill remains one connected polygon; RF rule, outline, IC1 custom pads and all pad nets are unchanged. Images of top/bottom copper and filled plane were visually inspected.
- Placement score80 still reports the existing J7 courtyard projection beyond the board edge; native DRC still reports the same two J7 silk-edge warnings and eleven library-instance mismatches. Neither is resolved by this checkpoint.
- **VAC1 hot-plug adequacy and BQ25792 2S reset/default-current risks remain OPEN fabrication/power-up blockers.** No hardware, thermal, switching-waveform or EMC qualification is claimed.

Evidence: [verification](phase4-6-checkpoint-verification.json), [final DRC](phase4-6-final-drc.json), [ERC](phase4-6-final-erc.json), [live readback and routing](phase4-6-work-state.json), [top](phase4-6-top-detail.png), [bottom](phase4-6-bottom-detail.png), [In1](phase4-6-in1-detail.png), [RF edge detail](phase4-6-rf-filled-detail.png). Native SVGs and read-only verification/render helpers accompany them. Trial DRCs are historical, not final state. Do not reapply the original via-deletion manifest.

Recommend a fresh session for the next bounded milestone: select and verify exact Nano-Fit header/housing/contact/wire combinations for J1/J2/J3, update schematic and PCB through Konnect, BOM and checks, then review before routing the rest.
