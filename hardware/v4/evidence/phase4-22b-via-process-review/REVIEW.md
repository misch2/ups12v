# UPS V4 — Phase 4.22B proposed epoxy-filled/capped via process

2026-10-18. **Read-only size/exclusion review PASS. Recommend Epoxy Filled & Capped; STOP for owner confirmation.** No manufacturing release or CAM preview was performed.

## Quick start

1. Prefer **Epoxy Filled & Capped** for this self-assembled prototype. Owner-observed displayed order prices: Plugged **USD33.21**, Epoxy Filled & Capped **USD50.59**, difference **USD17.38**. These are owner-reported configurator observations, not a new agent quote or purchase approval.
2. Review the [draft manufacturer notes](MANUFACTURER_NOTES.md) and use **Confirm Production File = Yes** when a later order is authorized. Confirm fill/cap coverage and open component holes in the actual production-file review, before approving production.
3. Keep the accepted PCB unchanged. This review does not authorize Gerbers, upload, ordering, purchasing or CAD edits.

## All 324 actual vias checked

Source: unchanged accepted Phase4.21 production PCB SHA256
`4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737`.
Both accepted native snapshot and IPC manifest agree on every via UUID, circular drill diameter and through-via type. These are design/finished-hole nominal dimensions, not measured manufactured holes or drill-tool compensation sizes.

| Actual via drill | Count | Conservative ≤0.50mm hole-size screen |
|---|---:|---|
| 0.30mm |273|PASS|
| 0.40mm |49|PASS|
| 0.50mm |2|PASS, exactly at the stated limit|
| **Total** |**324**|**Zero holes exceed0.50mm**|

The two0.50mm vias are USB MCU signal vias at **(92.456,91.400) /USB_MCU_DP** and **(92.456,90.200) /USB_MCU_DN**, UUIDs18ba59ba-8e4a-4da0-9ade-99d675fd24fc andf2ebb7a5-bebe-4514-9e3e-8adbed372bcd. Neither intersects a solderable pad opening in the accepted screen. Include both in fill/cap scope and call out the boundary size for CAM confirmation; no resizing is proposed. Via copper diameters up to1.00mm are **not** hole diameters and do not violate the0.50mm hole screen.

JLCPCB's [Via Covering guide](https://jlcpcb.com/help/article/pcb-via-covering), updated2026-09-09 and retrieved2026-10-18, advises holes≤0.50mm and explicitly supports epoxy filling of open and via-in-pad cases excluded from ink plugging. Its [capabilities table](https://jlcpcb.com/capabilities/pcb-capabilities/), checked2026-10-18, separately lists0.15–0.55mm for via-in-pad. This review uses the stricter **0.50mm** without inferring approval above it. “Default for6+layers” does not state a four-layer prohibition; the owner has verified a priced option for the displayed four-layer order. Final offered-process/CAM acceptance is still to be recorded.

## Exposed via-in-pad / nearby openings

Reused the hash-bound Phase4.22A [actual opening screen](../phase4-22a-manufacturing-preparation/actual-object-screen-final.json), rather than rerunning geometry. Across **71 affected references**,144unique via bores overlap pad openings:125are0.30mm and19are0.40mm.118via centers are inside openings;256vias lie within the prior0.35mm annulus-edge screen. Counts overlap and are not added. All bore-overlap pairs are same-net. These openings include DNP/test pads that still exist on the common bare board.

| Component | Vias with bore overlap / drill | Exclusion review |
|---|---|---|
| L1 |**24 ×0.30mm**,12per terminal|All qualify by hole size; fill/cap addresses existing open switch-node via barrels at solderable lands|
| Q1 / Q2 |**4 ×0.40mm each**, exposed drain pad9|All qualify; existing smaller exposed-land deviation remains separately accepted, not corrected by capping|
| U1 |11 ×0.30mm, including8centers inside openings|No published open-pad exclusion for epoxy/cap identified; verify module lands/ground array remain solderable|
| U4 |4 ×0.30mm|No size/open-pad exclusion identified; inspect tab/lead caps and mask|
| U5 |3 ×0.30mm, including2centers inside openings|Includes partial bore exposure; inspect small solderable pads carefully|
| F5 U8 |1 ×0.30mm partial bore overlap|Qualifies;0.35mm ink restriction does not transfer to epoxy|
| F5 C60 / C64 / C65 |1 ×0.40mm at each|Qualify; inspect power-capacitor pad surfaces|
| F5 C67 |1 ×0.30mm|Qualifies; preserve the100nF bypass pad|

All19F5 references were covered: U7(2near/0bore overlap), U8(2/1), Q10(0/0), L3(0/0), R60(1/0), R61(1/0), R62(0/0), R63(1/0), C60(1/1), C61(1/0), C62(1/0), C63(2/0), C64(3/1), C65(2/1), C66(1/0), C67(1/1), C68(1/0), C69(2/0), J8(0/0). J8's component PTH holes stay open even though it is DNP inF0. Q10 has no exposed via-in-pad instance within the accepted screen.

Every other exposed-pad reference and UUID is retained in [the complete final review JSON](final/via-fill-review.json), with per-reference drill counts and exclusion lists. **No oversize or published open-pad/proximity exclusion was found for epoxy/cap** in these actual instances. This is a supported process recommendation, not proof of filled-hole quality, cap planarity, solder-joint yield or full board manufacturability.

## Keep component holes open

The separate inventory contains **41component PTH** and **12NPTH**. In particular **J7 has16contact PTH of0.40mm**, the same diameter as49actual vias. A blanket instruction “fill all0.40mm holes” would be wrong. Include the [324via identity/coordinate inventory](final/all-324-vias-review.csv) and [53keep-open holes](final/component-holes-keep-open-review.csv) in the eventual CAM correspondence after authorization; these present files are **review inventories, not production drill files**.

## Manufacturing preview acceptance and remaining limits

Recommend **Confirm Production File = Yes**. The reviewed CAM result must distinguish all324vias from the41PTH/12NPTH, show epoxy fill and copper caps at both via ends as applicable, and retain the intended pad mask openings/finish. Check L1, Q1/Q2, U1, U4, U5, all exposed F5 cases and both0.50mm vias. No open barrel crater, resin-only surface or soldermask plug may replace an intended solderable capped pad. If an ordinary2D preview cannot establish the internal fill/cap assignment, require JLCPCB's explicit CAM/process confirmation before approving production; a colored dot alone is insufficient.

Preserve existing0.10mm tracks/gaps, pad numbers/nets, outline, mask geometry and F0/F5 common-board population. Do not authorize automatic land enlargement, mask closure over solderable pads, copper rerouting or substitution with ink plugging. Finished cap acceptance follows the selected vendor process; no new numerical flatness specification is invented here. Minimum barrel plating and exact layer-copper tolerances remain unconfirmed; epoxy is nonconductive and does not replace the current-carrying plated barrel or validate thermal performance. No controlled-impedance or particular-stackup requirement is added.

Verification: **8focused [tests PASS](focused-tests.log)**, including exact0.50mm acceptance,0.500001mm rejection, PTH/via discrimination, shifted-via/component-drill drift and unknown geometry refusal. Final accepted input digests match the Phase4.22A analysis manifest; [preservation](final/preservation.json) confirms26production CAD/library/BOM files unchanged. [Toolkit implementation](../../tools/v4kicad/via_fill_review.py) uses accepted exports only, with no native/editor operation. The `final/` inventories supersede this checkpoint's initial inventory copies. No fresh ERC/DRC, full-board route analysis or historical suite was warranted. Existing accepted native checks and hardware qualifications remain in force.

**STOP for owner review.** Epoxy Filled & Capped is the recommended preferred process, not a confirmed order/release. No files were sent to JLCPCB; no CAD, BOM, fabrication outputs, purchase, power-up, commit or push.
