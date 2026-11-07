# UPS V4 — Phase 4.22A manufacturing and assembly preparation

2026-10-18. **Preparation complete; manufacturing release INCOMPLETE / not authorized.**

## Quick start

1. Use the owner's approved **four-layer, nominal1.6mm, 1oz outer/1oz inner, bare-board** choices in [the order sheet](ORDER_CONFIGURATION.md). Owner observed **USD16.84 inner-copper surcharge**; total quote and exact stackup ID/minima remain unestablished.2oz is not selected.
2. Review [copper sensitivity](COPPER_SENSITIVITY.md), [F0/F5 population projections](POPULATION_REVIEW.md) and the [assembly/harness outline](ASSEMBLY_OUTLINE.md).
3. Review the actual [via/pad solder-wicking concern](VIA_PAD_ASSEMBLY.md) and remaining [release checklist](RELEASE_CHECKLIST.md) before separately authorizing Gerber generation. Nano-Fit and AON-land prototype deviations are already owner accepted.

## Accepted baseline and outcome

Owner ACCEPTS Phase 4.21 production PCB SHA256
`4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737`.
Four layers, nominal **exactly 1.6 mm**, JLCPCB, one common F0/F5 PCB and all existing geometry/routing are fixed. Older Phase 4.20 alternative-thickness discussion is superseded. No cosmetic routing, legacy cleanup or new architecture is proposed.

- Both compared copper weights have published support for the actual **0.10 mm trace/gap** features. Exact selectable constructions and process guarantees remain pending.
- **1oz outer/1oz inner is owner approved.** Recalculation uses the owner's approximately **30.5µm processed inner** calculator value, not a35µm guaranteed minimum. Exact copper tolerances and minimum barrel plating remain unconfirmed; no controlled impedance or particular stackup is imposed.
- At35µm outer/30.5µm inner/18µm illustrative average-based plating, F5 SYS-branch drop at2A is **38.17mV cold/53.92mV at125°C copper**; output-copper drop is **27.80/39.28mV**. Original35/35/25 model is35.32/49.89 and25.72/36.33mV. These are partial-path sensitivity calculations, not ampacity, delivered-voltage or temperature-rise qualification. Half-ounce remains an unselected comparison.
- Review projections cover **154 references**: F0 **115 fitted / 23 DNP**, F5 **134 fitted / 4 DNP**, each with **16 PCB features** requiring no fitted component. All 19 F5-only components are omitted in F0; C20/C22/C24/C25 stay DNP in both. CSVs retain known identities, footprints, recorded ratings and dated sourcing limitations.
- Nano-Fit standard finished-hole/position/thickness risk and Q1/Q2/Q10 smaller exposed lands are **OWNER ACCEPTED FOR PROTOTYPE USE, 2026-10-18**. No manufacturer-conformity claim or automatic CAD correction. Both variants will be self-assembled.
- New focused exported-object check: all1170tracks/arcs have minimum width0.100mm and compatible routed gaps. Of324vias, **118 centers lie in solderable pad openings**,144bores overlap openings,256vias are within0.35mm by the stated annulus-edge screen. L1 has24open-pad vias; Q1/Q2 each have4in pad9. These are actual assembly/wicking concerns, not new electrical routing defects. Free **Plugged is ink**, excludes these via-in-pad/near-opening cases and is not epoxy-filled/copper-capped. Process/assembly disposition remains open; no automatic upgrade.

## Evidence and verification

Read: AGENTS.md, current handover, Phase 4.19 [engineering audit](../phase4-19-final-audit/REVIEW.md) and independent/sourcing evidence, Phase 4.20 [decisions](../phase4-20-j7-review/FABRICATION_DECISIONS.md), Phase 4.21 [adoption](../phase4-21-production-adoption/ADOPTION.md), accepted manifest and final proof. Reused Phase 4.5 charger and Phase 4.17/4.18 power-path evidence because Phase 4.21 explicitly preserves that geometry. DFM-01 is resolved: J7 PTH-to-CC2 **0.350 mm**. Reuse accepted zero physical DRC/opens/parity/ERC errors and unchanged warning identities; this phase does not claim a fresh native validation.

[Verification](verification.json) reproduces accepted F5 numerical results, checks exact population membership, and confirms **26 production CAD/library/BOM files unchanged**, including all four accepted file hashes. [Before](preservation-before.json) and [after](preservation-after.json) inventories agree. [Final object screen](actual-object-screen-final.json) and **9 passing [focused toolkit tests](focused-tests.log)** cover the new pad/via/trace checks, including genuine-gap and unknown-artwork negative controls. [Analysis input/implementation hashes](analysis-source-manifest.json) bind the evidence. Only offline export analysis and documentation ran, with no native KiCad imports/editor interaction. No historical full suite or firmware build was warranted.

**STOP:** no CAD, saved stackup, rules or authoritative BOM changes; no Gerber/drill/CPL/stencil export, fabrication release, upload, procurement, power-up, commit or push. Next phase records the remaining offered construction/process details, dispositions the actual via-in-pad assembly concern and approved assembly choices. Source/copper selection and the two accepted prototype deviations do not need renewed approval.
