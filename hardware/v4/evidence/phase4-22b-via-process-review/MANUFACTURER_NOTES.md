# Draft JLCPCB manufacturing notes — NOT SUBMITTED / NOT RELEASED

2026-10-18. For owner review now and eventual order remarks/CAM correspondence only after separate authorization. Recommended selector: **Epoxy Filled & Capped**; **Confirm Production File = Yes**. Bare PCB, four layers, nominal1.6mm,1oz outer/1oz inner; both F0/F5 use the same board. Exact finish and other remaining order fields follow the approved order record, not assumptions in these notes.

## Copy-ready process request

Please use **nonconductive epoxy filling followed by copper plating/capping**, not soldermask-ink plugging, for **all324actual through vias** on this board. Required nominal via hole sizes/counts per PCB:

- **Ø0.30mm:273vias**.
- **Ø0.40mm:49vias**.
- **Ø0.50mm:2vias**.

Fill the via barrels and copper-cap/planarize their ends on both board faces as applicable to the process. At via-in-pad or partially exposed pad locations, provide a continuous solderable copper-capped surface with the same final surface finish as the surrounding exposed component pad. Preserve the supplied component pad geometry and soldermask openings; do not cover intended solderable lands with mask. Non-pad vias remain masked according to the supplied mask artwork. The listed hole sizes are nominal design/finished-hole values; please apply your proper tooling compensation without changing the design hole classes.

**Identify vias by the attached via coordinate/identity list, not by hole size alone.** Do not fill or cap **any of the41component PTH or12NPTH** in the separate keep-open inventory. In particular, **all16J7USB contact holesØ0.40mm must stay open** despite sharing a diameter with actual vias. Keep these other holes open:

| Component holes | Open holes per board |
|---|---|
| J1/J2/J3/J8 Nano-Fit contacts |2/3/2/3 respectively:10total,Ø1.20mmPTH; keep J8open in both F0/F5 bare boards|
| J4 JST contacts |6 ×Ø0.95mmPTH|
| J6 JST contacts |2 ×Ø1.00mmPTH|
| TP1/TP3/TP4 loop testpoints |1 ×Ø1.00mmPTH each|
| J7 USB contacts and shell |16 ×Ø0.40mm contactPTH;2plated slots0.60×1.40mm;2plated slots0.60×2.10mm|
| J1/J2/J3/J8 locating holes |4roundØ1.60mmNPTH and4oval1.60×1.75mmNPTH|
| H1–H4 mounting holes |4 ×Ø3.20mmNPTH|

Priority solderable cap locations: **L1's24Ø0.30mmvias**, **Q1/Q2 exposed drain-pad9 fourØ0.40mmvias each**, U1 module lands/ground array, U4 tab/lead pads, U5 pads, F5U8 and C60/C64/C65/C67, and every other via overlapping a component-pad opening in the review inventory. Fill/cap also applies to the remaining true vias, not just this priority list.

Please explicitly confirm process acceptance of the **twoØ0.50mmvias** at board coordinates(92.456,91.400) and(92.456,90.200). They are true through vias on USB_MCU_DP/DN, not connector holes. Their outer copper diameter is1.00mm; the relevant fill-hole diameter is0.50mm. Use board-coordinate/identity mapping from the design/CAM data if your viewer origin differs; do not infer mirrored coordinates.

Please provide production files/process confirmation for review **before production**. Show/confirm all324via fill/cap assignments,41PTH and12NPTH kept open, and intended solderable caps with unchanged pad/mask geometry. Please contact us before any omitted cap, process substitution, hole/land/mask modification or copper change; do not proceed with an unapproved alteration.

## Owner preview checklist before approving production

- [ ] Order shows Epoxy Filled & Capped and **Confirm Production File = Yes**, not Plugged/ink, tenting-only or uncapped resin fill.
- [ ] Counts273/49/2 match the324true vias; both0.50mm boundary-size vias are explicitly accepted by CAM.
- [ ] L1 pad1and2 each have12capped holes; Q1/Q2 pad9 each has4; U1/U4/U5 and F5 exposed-pad cases are mapped and solderable. Review both board faces, intended mask openings and final finish.
- [ ] All41componentPTH and12NPTH remain open, especially J7's16Ø0.40mmcontacts and four plated shell slots; no locator/mount or testpoint hole filled.
- [ ] No unapproved change to accepted copper/lands/0.10mm features, pad numbering, polarity, layer order, board thickness or outline. Existing AON land and Nano-Fit tolerance prototype decisions remain the owner's accepted deviations.
- [ ] Obtain explicit process confirmation if the preview cannot show fill/cap mapping or distinguish solderable caps from resin/mask. Approve neither production nor payment based only on a generic option label.

Review inventory references: [all324vias](final/all-324-vias-review.csv), [component/connector/locator/mount holes to keep open](final/component-holes-keep-open-review.csv), [complete pad-exposure result](final/via-fill-review.json). These are internal review artifacts, not Gerbers or drill files. No attachment or message has been submitted to JLCPCB in this phase.
