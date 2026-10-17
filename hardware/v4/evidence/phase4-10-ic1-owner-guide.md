# Phase 4.10 — IC1 SCL / INT / STAT escape handoff

2026-10-17. **No IC1 route or accepted-copper replacement installed. STOP for owner review.**

## Quick start

After review, use the separate [owner scratch](phase4-10-owner-editable-scratch/ups12v_v4.kicad_pro), not the open production document. Start at the actual IC1 pad, use native Walk Around with collision enforcement, and inspect F.Cu, B.Cu and In2.Cu together before fixing a via. A pad-sized opening on F.Cu is not a through-via opening. Leave the connection blocked if it requires moving existing copper; record the exact obstructing objects for a new review.

The [USB guide's return procedure](phase4-10-usb-owner-guide.md#returning-manual-work-safely) also applies here. Do not run Shove, remove copper, change footprints/rules or substitute an offline PCB for the open production board.

## Current endpoints and reusable same-net copper

| Signal | Exact IC1 start, mm | Intended destination, mm | Existing same-net transitions |
|---|---|---|---|
| I2C_SCL | IC1.14 `(60.6,67.9)` | R21.2 `(75.51,78)` and its already connected bus | vias `(79.8875,70.6)`, `(79.1875,79.1)`; none beside IC1 |
| ~INT | IC1.21 `(61.9,65.6)` | R28.2 `(69.51,74)` | existing F.Cu branch reaches via `(69.81,74.3)`, with B.Cu bus beyond; distant J4 via `(102.21,40.3)` is not a useful local escape |
| STAT | IC1.1 `(58.1,64.4)` | D2.1 `(42.3625,86.8)` | no existing STAT track/via to reuse beside IC1 |

All named source/destination pads are F.Cu. Native pad exports are authoritative: IC1.1 has an irregular/extended pad envelope about `x57.7999–58.7501,y63.7999–64.5001`; do not substitute the ordinary 0.6×0.2 mm side-pad geometry. IC1.14 is `x60.5–60.7,y67.6–68.2`; IC1.21 is `x61.6–62.2,y65.5–65.7`.

The current saved/native/live identity is production SHA256 `6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80`. All nearby accepted copper is unchanged from Phase4.9. The new independent F0 batch is away from the IC1 fanout.

## Close-ups and measured local obstructions

Each image shows coordinates, actual pads, track widths and drills; the continuous In1 PGND fill is omitted from these local copper diagrams. Copper clearance is0.10 mm; a0.50/0.30 mm through-via must satisfy every layer plus0.25 mm drill clearance and hole-to-hole spacing.

Colour key: SW1 orange, SW2 red, BATTERY brown/red, VBUS ochre, CE_N purple, SDA teal, REGN amber, PROG lilac, PGND pale green. Blue circle marks the exact source-pad coordinate, including when that SMD pad has no copper on the displayed inner/back layer. Other copper is grey.

| Signal | F.Cu | B.Cu | In2.Cu |
|---|---|---|---|
| SCL | [front](phase4-10-ic1-14-FCu.png) | [back](phase4-10-ic1-14-BCu.png) | [inner](phase4-10-ic1-14-In2Cu.png) |
| INT | [front](phase4-10-ic1-21-FCu.png) | [back](phase4-10-ic1-21-BCu.png) | [inner](phase4-10-ic1-21-In2Cu.png) |
| STAT | [front](phase4-10-ic1-1-FCu.png) | [back](phase4-10-ic1-1-BCu.png) | [inner](phase4-10-ic1-1-In2Cu.png) |

**SCL:** inspect the south exit first. CE_N leaves IC1.13 at `(60.2,67.9)` through `(60.3,68.3)→(60.6,68.6)→(60.95,68.6)`. SDA leaves IC1.15 through `(61,68.2)→(61.35,68.55)→(62.15,68.55)`. C9.1 VIN1 at `(60.62,69.1)` and C9.2 PGND at `(61.58,69.1)` close the lower area. At `y68.6`, the0.13 mm SCL route would directly collide with the0.15 mm CE_N horizontal section, rather than merely lacking a grid point. A straight south escape is not acceptable. North/inward through-vias encounter the SW2 network under the IC.

**INT:** east is bounded by BATTERY pins22/23 and their `(63.1,64.8)` / `(63.1,65.5)` power vias, and PROG below. The lower BATTERY via is0.70/0.40 mm. At `x63.1`, its south copper edge reaches `y65.85`; the nearby PROG0.10 mm track lies around `y66.015` with a north edge around65.965. That leaves only about0.115 mm edge gap, less than0.33 mm needed for a0.13 mm signal plus two0.10 mm clearances. A different route around the obstacles is required. Going inward instead reaches SW2, not unused board space.

**STAT:** west is constrained by the VBUS fanout and C2.1; REGN is farther south. The apparent extended-pad/inward via space is obstructed by two1.50 mm SW1 traces on B.Cu. At proposed via `(58.45,64.1)`, the joint validator measures actual copper overlap on B.Cu, not a cosmetic warning. The north route also approaches the PMID fanout and SW1. Do not drill through these paths to obtain an early transition.

Exact negative candidates, copper-edge/hole gaps and blocking UUIDs are in [outward scan](phase4-10-ic1-fanout-scan.json), [all-direction scan](phase4-10-ic1-all-direction-scan.json), and [inward STAT checks](phase4-10-ic1-inward-studies.json). First scan:548 outward0/45-degree dogbones per signal. Second:624 two-leg candidates per signal, in all directions within±1.2 mm, with0.10 mm via-position increments. All use0.13 mm tracks and0.50/0.30 mm through-vias; none passes. This is a bounded search, not an exhaustive geometric proof.

## Native Walk Around comparison

Native interactive routing can select more precise tangent positions, change posture, start from the other end and join the side of existing same-net copper. The custom grid search and these finite dogbones do not reproduce that behavior. There is no demonstrated unattended native PNS backend in this project, and none was enabled. No claim is made that a human cannot route these nets.

Try SCL first, then INT, then STAT on independent fresh scratch comparisons; reserving the most constrained escape before the long trunk avoids another round of dead ends. Compare the reverse order if the first attempt would monopolize a shared corridor. Source-side0.13 mm is a starting comparison based on the existing SDA escape, not a newly imposed fabrication rule. Do not reduce clearance or drill dimensions to force a result. A materially narrower proposal still needs native DRC and manufacturability review.

Once a legal F.Cu fanout reaches a genuinely clear via site, compare In2 and B trunks. In1 stays PGND. In2 offers a reference to In1 across the thick core; B has no guaranteed adjacent PGND plane. For these low-speed signals prioritize short direct routes away from switching copper, rather than turning either layer into a high-speed impedance claim. Reuse remote same-net transitions only if that avoids extra drill sites without a long detour. A via does not avoid an obstacle on another copper layer.

Use `X` for the signal, `/` for posture, and `V` only after checking the all-layer drill envelope. Keep magnetic pad snapping, collision enforcement and Walk Around. Disable automatic redundant-track removal. Do not drag originals while testing. These controls are documented in the [KiCad10 interactive router manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#interactive-router-settings).

## Smallest specific obstruction sets found — conditional rework proposals only

These sets are the fewest existing route objects obstructing the indicated **local** dogbone in the bounded all-direction sample. They do not prove a globally minimal repair, a replacement route for the removed power copper, or a complete connection to the destination. Removing them without reconstructing their electrical function would break the design. They were neither removed nor changed on any native scratch or production board.

[Conditional exported-geometry checks](phase4-10-conditional-local-obstructions.json) confirm that each indicated local escape passes the joint validator when exactly its listed obstructions are absent from an in-memory geometry copy. This establishes the local obstruction set only; no serialized CAD was changed and no replacement power path was constructed.

| Signal / prospective local via | Exact objects that would have to be cleared | Electrical consequence / decision |
|---|---|---|
| SCL `(60.3,67.2)` | SW2 via `34ef7035-7ee6-4bf4-8517-a71adf6b073d` at `(60.35,66.9)`,0.50/0.30; F0.30 track `5e9bf709-65ea-4128-98f0-9f89d3376c6f` and B0.40 track `8bf5e035-e88a-4a69-8afa-132cf4b0ebd6`, both `(60.35,65.7)→(60.35,66.9)` | Alters the protected switching path. Reject as an automatic escape remedy. First compare the south native Walk Around path; a CE_N/SDA fanout rework would need a separately demonstrated complete candidate. |
| INT `(62.6,65.4)` | BATTERY via `e012a565-4061-4615-bf98-9d4d2d4121a8` at `(63.1,65.5)`,0.70/0.40; F0.60 `0ef0aa31-e26a-4870-aabc-e320635f9abd`; F0.20 `7cf7c1f1-c91b-480e-a3d6-ce8852fcf701`; In2 0.40 `18d3b0bc-e5a4-421d-bf82-407726c1d497`; In2 0.60 `01ab1eb5-ab75-462d-9e54-2d6eab529481` | Relocates/rebuilds a parallel battery-current fanout, including the accepted Phase4.7 route. No single low-risk track deletion is established. Requires current-sharing, hole and thermal review before a replacement proposal can be accepted. |
| STAT `(58.2,64.3)` | B.Cu SW1 1.50 mm tracks `0ddad28b-e59e-4c39-9824-0548b73dfcd2`, `(58.65,63.5)→(57.5,62.35)`, and `97c7f73b-0a21-49fb-8598-4d436a77abd9`, `(58.65,65.7)→(58.65,63.5)` | An early via would cut the protected SW1 path. Rerouting that wide switching connection merely to clear STAT is not approved. First compare west/north F.Cu Walk Around; no validated minor VBUS rework is presently available. |

Thus **no acceptable add-only native candidate, or validated small electrical rework, is ready for installation**. The table makes the concrete blockers reviewable; it does not authorize destructive experiments. A true minimal repair remains unresolved until a native owner comparison establishes whether an add-only route exists. The next decision should prefer such a native scratch comparison over authorizing changes to SW1/SW2 or the battery-current path.

REGN/PROG/CE_N/VIN1 are not interchangeable obstacles: REGN has a local bypass and an intentional NT2 connection to ILIM_HIZ; PROG sets the charger hardware profile; CE_N controls the default charging state; VIN1 is the input supply/sense domain. Preserve their functions and routing, including separation from BATTERY and VBUS. [TI BQ25798 SLUSDV2C, June2026, §8.4.1–8.4.2, pp139–140](https://www.ti.com/lit/gpn/bq25798) prioritizes the local bypass and high-current switching geometry. Those loops remain unchanged in the verified checkpoint.
