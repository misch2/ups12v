# Before Gerber generation — exact decisions and separate blockers

2026-10-18. **No fabrication outputs or release authorized.** Checkboxes record remaining work, not permission to perform subsequent phases now.

## Fixed / already accepted

- [x] Phase4.21 PCB hash4eb7bd2c…a8737 and all current geometry/routing accepted; no cosmetic or legacy cleanup.
- [x] JLCPCB; four layers; nominal **1.6mm**; **1oz outer +1oz inner**. Owner observed **USD16.84 surcharge** in live configurator; no total quote inferred. **2oz not selected.**
- [x] Bare PCB only; self-assemble **both F0 and F5** on the same board.
- [x] Owner accepts standard-process Nano-Fit tolerance risk and existing Q1/Q2/Q10 exposed-land deviation **for prototype use**. Manufacturer compliance is not claimed; no repeated approval needed for those same deviations.
- [x] Actual accepted track/arc objects screen at0.100mm minimum and compatible different-net routed gaps; accepted DRC/vendor evidence retained. J7 clearance0.350mm resolved. No demonstrated need for controlled impedance or a specific named stackup.

## Bare-board release inputs / blockers

- [ ] Record actual offered construction identity **if established**, dielectric/copper schedule and finished-board tolerance under selected1oz/1oz at1.6mm. Do **not** mandate an exact stackup code or controlled impedance without a demonstrated need. Static stackup examples are not selected order codes.
- [ ] Owner reviews **30.5µm processed-inner** calculation and unconfirmed minima. Record outer/inner thickness tolerances/minima and barrel-plating information if vendor supplies it; otherwise retain explicit unconfirmed values and obtain a bounded prototype decision. **18µm average is not a minimum**, 35µm is not guaranteed.
- [ ] Disposition of actual open-via/pad assembly cases and Plugged exclusions: owner chooses how to proceed with self-assembly/vendor process confirmation. Do not infer this decision from accepting AON land area or silently upgrade to epoxy/capping.
- [ ] Record exact offered surface finish, mask color, legend, via covering and drill/slot handling. Preserve PTH/NPTH distinction, global pad openings, RF exclusion and nominal board shape. Confirm no CAM auto-edit of accepted copper/lands. Remaining Nano-Fit tolerance risk is accepted, not silently converted into tighter fabrication guarantees.
- [ ] Resolve or explicitly retain footprint-sensitive selections (especially switches/L1/provisional U2 and any passive requiring a package change). Ordinary availability gaps with unchanged footprints do **not** block bare-board fabrication.
- [ ] Owner authorizes **Gerber/drill generation as a separate next action**, with exact source hashes and these recorded choices. No authorization to order follows from export authorization.

The selected1oz construction and accepted deviations are not reopened. No known copper electrical defect is added by this phase. Outstanding via/process/part choices are recorded honestly; none automatically requires a PCB edit.

## When a later export/release phase is authorized

- [ ] Bind saved production hashes; reuse accepted validation while unchanged, run affected fresh ERC/DRC/parity checks if source/rules change, and complete the applicable final release check. Current metadata has min_track_width0 despite actual0.10mm objects; do not change rules without authorization.
- [ ] Generate into a new empty directory and verify four copper layers in order, masks/silk, closed Edge.Cuts and correct PTH/NPTH drills/slots. Inspect actual Gerber/drill and CAM mask/via behavior. No BOM/CPL required for bare-board fabrication.
- [ ] Complete order record: service/material/finish/mask, quantity, single-board/panel choice, marking location, test service, via option, shipping/tax/lead time and final total. Quantity/shipping are ordering inputs, not electrical reasons to block geometry verification.
- [ ] Owner approves the reviewed manufacturing package/order preview and separately authorizes order/payment. No fabricated-data upload or purchase in4.22A.

## Sourcing and assembly blockers (separate from bare-board release)

- [ ] Freeze exact fitted MPNs/ratings for both projected lists and the selected charger/cell profiles. Retain19F5 omissions inF0 and four bulk DNP inboth. U8/L3 and remaining exact order MPNs/harness basket need supply resolution; no invented live price/stock.
- [ ] Complete Nano-Fit/JST contacts/wire/crimp/polarity checks, exact pack/BMS/NTC and mechanical seating/access. Use the external top-view assembly sheet with explicit pin numbers; do not rely on dense silk.
- [ ] Define solder/paste/hot-air/reflow/inspection for QFN, SOT583, AON, L1 and module open-via/hidden joints before assembly. Do not treat free ink plugging as copper-capped via-in-pad.

## Later hardware qualification — separate authorization

- [ ] Record exact PCB/BOM/population, cells/source/load/ambient and raw logs before powered tests.
- [ ] Existing qualifications: charger reset defaults/2A case, VAC1 hot-plug, pack/BMS/NTC, MLCC Ceff/stability/ripple; shared SYS/BATTERY losses and current sharing; F0 converter temperature; F5 dropout/5V2A/thermal/reverse blocking; USB-only service/back-power; connector heating/crimp quality and RF/enclosure performance.

No new mandatory product limits or architecture changes are introduced. No hardware power-up is authorized by this checklist.
