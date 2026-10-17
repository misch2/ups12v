# Phase 4.10 — owner-assisted USB routing

2026-10-17. **Preparation complete; STOP for owner review before intervention.**

## Quick start

1. After review, open the separate [owner-editable scratch project](phase4-10-owner-editable-scratch/ups12v_v4.kicad_pro) in KiCad 10. Production remains in `hardware/v4/ups_v4`; check the full editor path before editing.
2. Use Walk Around, keep collision enforcement enabled, and disable Remove redundant tracks. Do not drag accepted copper. Start with the connector crossover and U2 ground; reserve the two main data paths together.
3. Use the native pair router only on `USB_DP` / `USB_DN`. Route the two U1-side nets as coordinated individual tracks under the present names. Do not rename nets or change rules.
4. Save scratch, refill, run DRC with schematic parity and ERC, then return the saved scratch path for independent comparison. Scratch edits do not transfer themselves into production.

This guide is not permission to change production placement, footprints, rules, stackup or existing copper. There are presently **no data tracks** on these four USB nets. Do not replay historical USB candidates.

## Exact physical topology

Coordinates are board-space mm, from current native export and matching live Konnect pad readback. All U2/R48/R49/U1 pads are F.Cu SMD; J7 signal contacts are plated through holes.

| Function | Positive endpoint | Negative endpoint | Net names |
|---|---|---|---|
| Connector A contacts | J7.A6 `(117.39,81.425)` | J7.A7 `(117.39,80.575)` | USB_DP / USB_DN |
| Connector B contacts | J7.B6 `(118.74,80.575)` | J7.B7 `(118.74,81.425)` | USB_DP / USB_DN |
| ESD shunt junction | U2.1 `(114.225,78.85)` | U2.2 `(114.225,78.15)` | USB_DP / USB_DN |
| Resistors, connector side | R48.2 `(96.51,88)` | R49.2 `(96.51,90)` | USB_DP / USB_DN |
| Resistors, MCU side | R48.1 `(95.49,88)` | R49.1 `(95.49,90)` | `Net-(U1-USB_D+_{slash}_GPIO19)` / `Net-(U1-USB_D-_{slash}_GPIO18)` |
| MCU | U1.27 `(76.1,91.2)` | U1.26 `(76.1,90.4)` | Same respective generated nets |

U1.27 is GPIO19 / USB D+, U1.26 GPIO18 / USB D−: [Espressif MINI-1 datasheet v2.2, §3.2 and §5.2.1.5](https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html). R48/R49 are currently 0R with a 22R population option; both divide the connection into different electrical nets. Neither value nor variant changed here.

U2 is a **shunt protector**, not a series device with separate input/output nets. Its intended DRT mapping is 1=D+, 2=D−, 3=ground: [TI SLVSAC2G, June 2021, §5](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf). It remains PROVISIONAL in the existing BOM. Route the main path through/at its signal lands with minimal branch length. U2.3 at `(113.375,78.5)` is PGND and is the sole remaining USB ground disconnection.

### Connector duplicate contacts

Connect A6 to B6 and A7 to B7. Do not connect the two contacts at the same Y coordinate: those are opposite polarities. Their direct diagonal joins cross at `(118.065,81.0)`. They cannot both be drawn as intersecting copper on one layer. First compare a very short local layer crossover with a compact perimeter approach, using the actual PTH copper/drills and connector shell. Do not create long parallel stubs to the duplicate contacts.

## Pair recognition: actually tested on KiCad 10.0.7

The isolated read-only native `BOARD.DpCoupledNet` probe returned:

| Net | Native coupled net |
|---|---|
| USB_DP | USB_DN |
| USB_DN | USB_DP |
| Both generated U1-side names | null |

[Native results](phase4-10-native-usb-probe/native-usb-pair-recognition.json). Thus the connector–U2 and U2–resistor portions share one recognized pair. There is no recognized native pair across the resistors, or on the MCU-side generated nets. A single uninterrupted end-to-end pair-router operation is unavailable under the current schematic names. If true pair routing on the MCU side is wanted, net labeling would require a separately authorized schematic/parity change; none was made.

## Routing order, layers and corridors

1. Resolve the duplicate-contact crossover locally, then J7 to U2. Consider the ESD ground at the same time; do not finish data geometry and leave its return as a long afterthought. U2.3 needs a short, wide PGND connection into the existing In1 plane. A legal via location must be checked on all four layers. No exact ground-via coordinate is approved by this guide. The deliberately broad USB planning reservation blocks the automated return generator here; it does not prove a native local return impossible.
2. Route U2.1/.2 to R48.2/R49.2 as a pair. Inspect F.Cu first: In1 is the actual continuous PGND reference, nominally 0.10 mm below F.Cu. Candidate exploration area is west/southwest from U2 through approximately `x99–113,y79–89` to the resistor lands. This is a search area, not a proven free channel: U4/U5, USB power and accepted control copper remain obstacles.
3. Route R48.1→U1.27 and R49.1→U1.26 together as two single tracks, approaching the module pins from the west where feasible. Compare access outside the module body before accepting any route underneath it. Exact crystal placement inside the module has not been established by these board exports; do not infer RF safety from the absence of a PCB keepout.
4. Avoid the all-layer antenna keepout around `x75.4–88.6,y99.2–104.6`, charger/power switching areas and the future F5 area. Do not use the rejected southeast SYS proposal or modify any accepted copper to create a corridor.

The historical B.Cu reservations remain available as **planning space**: external `x96.4–121,y77–91.8`, under-module `x74.5–96.4,y89.9–91.8`. They are not a qualified transmission line. In2 contains signals and power, not a continuous adjacent PGND plane. Blindly choosing B.Cu because it looks empty would leave an unverified reference. Any B route needs actual fill/return review beneath its full length. In2 routing faces In1 across the nominal 1.24 mm core; it also cannot inherit an F.Cu impedance calculation.

The new CC routes are on In2: CC1 enters J7.A5 through `(113.65,78.535)` from its via `(113.65,75.65)`; CC2 uses the east-side approach near `x119.8` to J7.B5 from via `(116.65,74.15)`. Their F.Cu via lands stay north of the reserved data access. These tracks and their antipads are fixed obstacles for manual work. The existing PGND vias `(115.16,75.5)` and `(118.16,74)` serve the CC pulldowns; U2.3 is not connected to them yet.

### Width, spacing and transitions

Use the existing **Default pair dimensions: 0.20 mm width / 0.20 mm gap** as the initial native geometric comparison. Copper clearance is 0.10 mm; current minimum via/drill are 0.50/0.30 mm with 0.25 mm hole clearance and hole-to-hole spacing. Do not use the ordinary Default single-track width of 0.50 mm accidentally for the MCU-side comparison. These pair dimensions are legal defaults, **not verified 90-ohm geometry**.

Live stackup reports 35 µm copper, nominal FR4 εr4.5, F–In1 dielectric0.10 mm, core1.24 mm and In2–B dielectric0.10 mm, total1.6 mm; impedance control is false. KiCad can return defaults when no explicit fabrication stack is defined. These values are therefore design assumptions, not a fab contract or field-solver result. Confirm the real stack before claiming impedance or selecting final controlled-impedance dimensions. No netclass/stackup change is authorized here.

Keep the main path on one layer when feasible. The connector duplicate crossover may require a local transition, but an exact transition count/location cannot be fixed before the owner comparison. If a pair changes reference layers, provide a nearby legal PGND return path and verify the actual reference copper on both sides. Do not add arbitrary stitching vias as a substitute for reference analysis. Avoid signal-via asymmetry and unused PTH/via stubs where possible.

## Native tools and total skew

KiCad's [10.0 routing and tuning manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#routing-differential-pairs) documents `6` for a recognized pair, `X` for singles, `V` for vias, `/` to change posture, `7` for single-track length, `8` for pair length and `9` for pair skew. Walk Around preserves obstacles; disabling redundant-track removal also avoids automatic loop cleanup. Use the Route menu if local hotkeys differ. Keep the clearance display visible and stop if the router cannot pass legally.

Tune only after the physical topology is complete. Point-to-point tuners stop at branches; the J7 duplicates and ESD junction can therefore defeat a naive whole-net reading. Measure both cable orientations:

`ΔA = length(J7.A6→R48.2) + R48 package path + length(R48.1→U1.27) − corresponding A7/R49/U1.26 path`.

Repeat for B6/B7. Include used vertical via lengths using the actual stack, and distinguish package/pad traversal from trace-only sums. A matched connector-side segment can still leave substantial total skew after the series resistors. Keep corresponding bends, layer transitions and resistor approaches reasonably symmetric; do not add unnecessary meanders merely to obtain a displayed zero. No new numerical skew limit is imposed by this milestone.

## Returning manual work safely

The scratch starts byte-identical to production SHA256 `6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80`, with matching schematic/project/rules. Finish and save scratch in its owning editor; return its path and selected segment/layer choices. Do not overwrite the open production PCB with that file.

The next authorized review must compare original UUIDs and full geometry, extract only intended additions, run the joint copper/hole/clearance check, native refill/save/reload, DRC/ERC/parity, endpoint and reference/skew review, and independent preservation. Native interactive splitting/merging of old tracks counts as an existing-copper change even in Walk Around and requires explicit review. Only then can a guarded live IPC transaction install an approved delta, followed by production readback and a new manifest. An old manifest must not simply have its hash edited to hide manual changes.
