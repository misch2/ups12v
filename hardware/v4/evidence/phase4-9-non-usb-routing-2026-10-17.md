# Phase4.9 — repaired preflight and independent non-USB routing

2026-10-17. **STOP for owner review.** No subsequent routing candidate is
authorized by this report. USB data remains owner-assisted/deferred.

## Verified result

Production now has **901 tracks /265 vias /154 footprints /473 pads /1 zone**.
DRC: **68 unconnected /0 physical errors /0 parity /16 unchanged warnings**.
ERC: **0 errors /4 unchanged warnings**. Inherited ignored checks are unchanged;
these totals do not establish release readiness.

PCB SHA256:
`a3ba56068026a6942c4ca22d7e0eee8f5f2320afc4defefabbbcee3861b29a78`.
Schematic SHA256:
`990d107296d149775884dc2d2512c2e6102b6191e4818e7fcf5bd9268d48c8f6`.
Project SHA256:
`477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e`.

The accepted entry PCB was `ded2ac1999b672157409b0b6f2bbc636beac4fd54382c8b9548346a0fbcab675`,
604 tracks/179 vias/184 unconnected. All of those routed objects, pads and
footprints remain exact. Only the declared297 tracks/86 vias were added.

Authoritative next saved/live baseline:
[accepted manifest](phase4-9-completion-ipc/accepted-installed-baseline.json).
[Final native routing context](phase4-9-completion-native/routing-context.json),
[production DRC](phase4-9-completion-ipc/production-drc.json),
[production ERC](phase4-9-completion-ipc/production-erc.json),
[full preservation](phase4-9-completion-ipc/full-preservation.json),
[original604/179 preservation](phase4-9-final-original-preservation.json), and
[final read-only live reconciliation](phase4-9-final-reconciliation/preflight.log).
Every batch also preserves full live artwork, fields, models and zone definitions.
Actual native filled contours equal the accepted scratch at each installation;
[final equality](phase4-9-completion-ipc/scratch-fill-equality.json).

## Permanent repair and its demonstrated scope

`tools/v4kicad/plan_validation.py` jointly checks every proposed track/via,
irrespective of producer/order, against the other additions and exported native
board copper, pad polygons/overrides, fixed artwork, physical holes, board edges,
zone restrictions, antenna keepout and explicit F5/USB reservations. It uses
actual widths, per-layer existing via copper and rotated oval drill capsules.
Track-to-copper, copper-to-hole and hole-to-hole constraints are distinct.
Same-net junctions are legal; physical same-net hole spacing is still checked.

PCB/project/rules/context bindings are verified before scratch creation/native
invocation and again in the worker; live IPC also validates before connection.
The current V4 rule profile resolves0.10mm netclass clearance and pad overrides.
Unknown custom rules or differing netclass clearances fail closed, requiring a
future explicit rule-resolution extension. Native refillable PGND is handled by
native antipad generation, DRC and actual fill review, not as immutable copper.

Exact duplicate paths, including reversals/different widths and re-emission of
existing copper, are flagged and rejected before application. Tiny legs are
flagged; export-only cleanup can remove pad-internal redundancy or merge a corner
only after another full joint check. Near-parallel/partially overlapping branches
still need explicit quality inspection; exact duplicate checks alone are not a
topology optimizer.

Expected and actual additions are retained before comparisons after native
creation, save and reload. Net and geometry equality remains strict in integer
nanometres;1nm/net changes fail. No tolerance, free-net exception or guard waiver.
Plane review now tiles the actual geometry domain into windows <=30mm per axis;
the old oversized local request fails before mutation. Native sampling limits
remain enabled. This corrects the domain assumption rather than bypassing it.

**53 offline tests PASS**, including independent reproductions of each of the
three scratch5 PGND-via collisions, mocked prohibition of native invocation for
invalid input, valid different-layer crossings/same-net junctions/PGND stitching,
holes, overrides, reservations, duplicate paths, exact equality, tiled domains,
existing via/PTH reuse and explicit F/In2 search. Previous30 diagnostic tests are
included. Offline tests are distinct from actual native execution.

The unchanged v5 plan SHA remains
`d8ce75bdb4fef153d48e843be9685c421713e64dce7ff35f12c1a39f95a1aacd`;
failed scratch5 remains
`5d9bd5b41137aafbb3adb2637ac45d044c1b270900c8a6a7ebf62b7797c8e34a`.
Neither was edited/replayed. The final all-board offline rejection records the
original physical conflicts as well as subsequently reserved USB corridors:
[regression summary](phase4-9-toolkit-final-regression-summary.json). Its106
findings comprise96 reservation findings and10 physical findings; these are
repeated object/layer findings, not106 independent defects. The three focused
collision negatives do not depend on the USB reservation to reject the plan.

The bounded **positive native integration actually passed** creation/readback,
save/reload equality, DRC/parity/ERC and original preservation:
[integration plan](phase4-9-repair-integration-plan.json),
[native summary](phase4-9-repair-integration/summary.json).
Only after that PASS were the following production batches applied.

## Installed coherent batches

| Batch | Added tracks/vias | Production tracks/vias | Unconnected |
|---|---:|---:|---:|
| Accepted entry | — |604/179|184|
| MCU local/ground/reset/BOOT/UART |66/30|670/209|132|
| Charger-host/control/J4 branches |129/25|799/234|98|
| MCU3V3 and MAIN_3V3 distribution |80/21|879/255|74|
| MCU bus/CHG_AND/charger SDA/MAIN closure |22/10|901/265|68|

Each passed joint offline checks, isolated native scratch creation/save/reload,
native refill/DRC/parity/ERC, quality review, exact live entry reconciliation,
bounded live IPC create/returned/visible-object checks, owning-editor refill/save,
independent native saved readback and production checks/preservation.

Exact installed plans and corresponding scratch directories:

- [MCU plan](phase4-9-mcu-plan-final.json), `phase4-9-mcu-final-scratch`;
  [MCU production proof](phase4-9-mcu-host-ipc/full-preservation.json).
- [Control plan](phase4-9-control-clean-plan.json), `phase4-9-control-scratch`;
  [control production proof](phase4-9-control-ipc/full-preservation.json).
- [Power plan](phase4-9-power-quality-clean-plan.json), `phase4-9-power-clean-scratch`;
  [power production proof](phase4-9-power-ipc/full-preservation.json).
- [Completion plan](phase4-9-completion-final-plan.json), `phase4-9-completion-scratch`;
  [completion production proof](phase4-9-completion-ipc/full-preservation.json).

U1 C30/C31 bypass supply/returns, reset/BOOT/straps and UART TP5/TP6/TP7 support
are connected. MCU3V3 and MAIN_3V3 have no remaining DRC unconnected entries.
MCU supply includes a dedicated0.6mm C36-to-C31 feed; routine distribution is
0.5mm. U6 local supply/decoupling, MCU SDA/SCL/INT side and Q5–Q9 associated
low-speed control are connected. CHG_AND and J4 standard F0 signal/power branches
are connected. Charger SDA reaches IC1; charger SCL/INT and STAT remain blocked.
The D2 anode/resistor branch is connected. `MCU_STATUS_LED` is a one-pad net in
the existing schematic; no LED circuit was invented.

The final MCU SCL/SDA trunks use2/3 ordinary In2 segments,8.32/10.42mm and2vias
each. MCU_INT uses2segments/14.73mm and1new via, reusing an existing target via.
This avoids the earlier outer-layer3–4via winding alternatives. Charger SDA uses
2vias/20.40mm at0.13mm on both its IC1 escape and In2 trunk. This low-current
digital branch passes the unchanged0.10mm clearance rules; bus timing/capacitance
is not qualified. No rule was relaxed. The last MAIN connection uses one new
via on its existing new branch and a simple0.5mm In2 trunk outside F5 space.

## Routing quality and ground reference

Routes are proposed by custom bounded A* and explicit short trunks, then created
as standard native `PCB_TRACK/PCB_VIA` (scratch) and SDK `Track/Via` (production).
Konnect establishes live project/context; its routing tools and KiCad interactive
router did not generate these installed paths. No serialized CAD edits or graphic
substitutes. Native inventories exclude ratsnest/selection/highlight graphics.

Power candidate near-duplicate branches and a same-path0.5/0.6mm pair were removed
before application:91 candidate tracks became80, with the same74 connections
remaining. Final power/completion quality has no duplicates, microlegs or acute
centerline candidates. Three control angle candidates occur inside existing pad
junctions, documented in [control review](phase4-9-control-quality-review.json).
The single retained0.141mm BOOT45-degree chamfer avoids adjacent NC pads; proposed
merges violated their clearance, so shortening it was not justified.

Some J4 I2C branches are65–76mm while preserving accepted power and F5/USB space.
They are low-speed control routes; no bus rise-time/capacitance or EMI performance
is claimed. Short non-H/V/45 segments are exact-pad/via alignment transitions,
not evidence that the interactive router was used. Quality artifacts:
[MCU](phase4-9-mcu-final-quality.json), [power](phase4-9-power-clean-quality.json),
[completion](phase4-9-completion-quality.json).

Final read-only native sampling captured all33new PGND vias. All centers contact
PGND;32have all4 ring samples in fill. At(78.48,86.5), the east0.4mm sample is
outside fill near another-net via; the other3are in copper, and a6.72mm sampled
conductive path (physical drills removed) reaches module ground. No additional
PGND disconnection appeared. [Final probes/path](phase4-9-final-reference-probes.json)
and the four `phase4-9-final-reference-*` exports retain this evidence.

[Centerline reference review](phase4-9-non-usb-reference-review.json) includes
endpoint antipads, so percentages are descriptive. A1.38mm local SCL reference
gap near(104,37.3) has a1.60mm conductive bypass in actual native fill with drill
voids removed. The1.48mm MAIN gap is at the J4 PTH endpoint antipad. These are not
whole-plane splits. [Local gap details](phase4-9-reference-local-gaps.json).
Sampling at0.1mm does not establish high-frequency return inductance or impedance.

## Remaining connectivity and actual blockers

| Remaining group | DRC entries |
|---|---:|
| IC1 SCL /INT /STAT |3|
| USB data, generated resistor-to-MCU legs and CC |10|
| Explicit F5 nets plus F5 SYS branches |29|
| PGND:12F5 +3USB +4earlier primary-power entries |19|
| Earlier VIN1 /BATTERY /PMID |7|
| **Total** |**68**|

[Exact endpoints by net](phase4-9-completion-ipc/remaining-by-net.json).
All relevant MCU/control local PGND returns are connected. The primary-power
PGND entries involve the earlier bulk capacitor group, not omitted U1/U6 returns.

Bounded F/B and F/In2 search at0.13/0.18mm plus a local0.85mm straight-fanout scan
found no acceptable IC1 SCL, INT or STAT escape. Example source escapes collide
with CE_N/VIN1, BATTERY/PROG and VBUS respectively:
[exact objects/clearances](phase4-9-blocked-control-examples.json),
[fanout scan](phase4-9-charger-fanout-sites.json),
[F/In2 results](phase4-9-inner-charger-search.json).
This establishes failure of the bounded alternatives, **not mathematical
impossibility or a mandatory component move**. Owner-assisted native Walk Around
on a fresh copy is the next sensible comparison. Any change to accepted copper,
placement or rules needs separate owner authorization.

## USB handoff and future routine routing

USB_DP/DN, U1 pins27/26 generated resistor legs and dependent data connections
were not routed. Current routed endpoint-to-endpoint USB skew is therefore
**not established**; zero added USB copper must not be called zero skew.
Do not reuse scratch3/v5 or force a custom A* bypass of the VBUS barrier.

Future USB work should select the complete pair topology J7→U2/R48/R49→U1,
including duplicated connector contacts, branches, resistor segments, transitions
and actual endpoint-to-endpoint lengths. Compare paired paths jointly, remove
duplicates/unnecessary legs/bends/vias before native application and inspect
reference continuity at every transition. Match geometry to the accepted stackup;
no width/gap/rule change or90ohm qualification was performed here.

Espressif recommends parallel matched USB paths,90ohm differential impedance,
few transitions with nearby ground returns and continuous reference. Its crystal
guidance also cautions against digital routing underneath the crystal. For this
module, internal crystal/RF clearance still needs an explicit check; avoiding the
antenna keepout alone does not establish it.
[Manufacturer USB/crystal guidance, checked2026-10-17](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html#usb).

KiCad10.0.7 provides Walk Around without moving obstacles, differential routing,
length/skew tuning and Attempt Finish/Selected. Recommended owner-assisted USB
comparison: fresh scratch, Walk Around and native pair tools, followed by the same
preservation/native/DRC/reference checks. Shove can alter accepted copper, so it
is unsuitable under the current boundary. Automatic completion is not proof of
good topology. [KiCad10 manual, checked2026-10-17](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#routing-tracks).

The installed SDK/Konnect audit from2026-10-16 exposed direct trace/L-bend/parallel
pair tools and SDK `run_action`, but no established structured unattended PNS
path-preview/control workflow. Thus a human interactive comparison is practical;
unattended replacement of custom search is not yet demonstrated. The prior
Freerouting probe found no engine; it was not reprobed, installed or enabled.
[Installed capability evidence and limitations](phase4-9-stop-and-routing-review-2026-10-16.md).

## Execution incidents and electrical limits

Initial sandbox IPC apply was denied at GetVersion before document access or any
transaction. Log inspection and explicitly approved host read-only preflight
established healthy exact entry, then installation succeeded. No editor recovery.
A legacy post-check compared47.879999999999995 with47.88 as floats and stopped;
independent exact-nanometre comparison proved all additions identical. The
post-check was corrected to exact native units, retaining1nm/net rejection:
[representation evidence](phase4-9-mcu-representation-diagnostic.json).
No actual native assertion, geometry/net mismatch or preservation failure occurred.

No electrical circuit, BOM, component placement, existing route, schematic, rule,
zone definition or stackup change. No USB/F5 switching routing, software install,
fabrication, purchase, power-up, firmware change/build, commit or push. Supply
transients/voltage drop under RF load, bus timing, RF/EMI, USB programming, thermal
performance and physical power-domain/back-power tests remain unmeasured/open.
Three blocked control links and remaining power/USB/F5 connections prevent a
complete F0 release. **STOP for owner review before further routing.**
