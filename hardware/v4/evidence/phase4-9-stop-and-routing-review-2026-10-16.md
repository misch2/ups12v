# Phase4.9 — mandatory geometry-verification STOP; production unchanged

**Follow-up:** the owner accepted this STOP and authorized one diagnostic only.
[Completed scratch5 diagnostic](phase4-9-scratch5-diagnostic-2026-10-16.md)
identifies three wrongly positioned PGND via declarations and their reloaded
signal nets. The unresolved-cause statements below describe the original STOP;
they are superseded by that diagnostic. Routing remains unauthorized to resume.

2026-10-16. The owner accepted Phase4.8B and authorized the complete standard
F0 MCU/USB/control/interface milestone with independent functional batches.
The later owner instruction additionally requested a routing-method/quality
audit. Neither instruction authorizes production relocation, accepted-copper
rerouting, rule changes, F5 routing, software installation, or automatic recovery.

## Outcome and exact stop

**Phase4.9 is INCOMPLETE. No production create/update/delete/refill/save was
attempted.** Production remains 604 tracks / 179 vias / 154 footprints / 473 pads,
SHA256 `ded2ac1999b672157409b0b6f2bbc636beac4fd54382c8b9548346a0fbcab675`.
All source hashes in `phase4-8b-b3-ipc/accepted-installed-baseline.json` were
rechecked after the STOP and match. The unrelated pre-existing
`.codex/config.toml` modification was preserved.

The latest isolated scratch application stopped in `native.verify_added` after
saving and reloading **only the isolated scratch PCB**:

`Added native copper differs from the declared plan; STOP`

See [worker log](phase4-9-usb-scratch5/apply.log),
[request/context](phase4-9-usb-scratch5/context.json), and
[declared candidate](phase4-9-usb-plan-v5.json). This is a new-addition geometry
verification failure; the preceding original-object preservation check passed.
There was **no native assertion, IPC failure, live transaction, or production
preservation failure**. Nevertheless the owner's explicit global STOP for a
preservation failure/unclear verification was applied conservatively: no further
native KiCad or IPC operations, no retry, no editor recovery/restart/close.

The old worker wrote its detailed captures only after a successful comparison.
Consequently the failed run does not identify the mismatched new object or field;
its exact cause remains **unresolved**. Duplicate track candidates found in the
plan also existed in an earlier saved/reloaded candidate, so they do **not** by
themselves explain this new failure. Do not guess that the cause is rounding,
KiCad normalization, duplicate removal or via behavior.

The toolkit now retains expected additions and created/reloaded snapshots before
comparison, emits exact missing/extra/changed additions on failure, and verifies
created geometry before its scratch save. This retains fail-closed equality;
there is no tolerance, geometry substitution or recovery. **30 unit tests pass**,
including same-net physical-hole avoidance, reserved corridors and diagnostic
failure behavior. No native execution of this changed diagnostic path has been
attempted after STOP.

Smallest proposed continuation requiring owner review: authorize one monitored,
read-only, isolated export of the failed scratch board, with explicit hashes and
a fresh output directory, to identify its saved additions and reconcile them with
the immutable plan. Do not retry installation or save production during that
diagnostic step. Establish the exact cause and a tested correction before a new
scratch candidate. The failed scratch is not an accepted production baseline.

## Completed read-only baseline and priority review

- Exact-path Konnect `get_board_info` returned `source=ipc`, four copper layers,
  104 nets. Canonical [IPC preflight](phase4-9-entry-ipc/preflight.json) confirmed
  all saved hashes, document identity and exact full live baseline.
- [Independent isolated snapshot](phase4-9-entry-native/snapshot.json) and native
  zone/artwork audit confirmed the accepted inventory and RF rule area. No source
  save occurred.
- Fresh production entry checks: **184 unconnected / 0 physical errors /
  16 inherited DRC warnings / 0 parity; ERC 0 errors / 4 inherited warnings**.
  [Complete reports](phase4-9-entry-ipc/production-checks.json).
- Fresh schematic export: [netlist](phase4-9-schematic.net). Konnect structural
  short inspection reported zero shorted nets. Production parity checks, rather
  than a heuristic short count, establish saved schematic/PCB agreement.
- [Whole-board pad-level review](phase4-9-whole-board-review.json) covers remaining
  F0 nets, endpoints, routing order and explicit reservations. USB first, local
  MCU/reference ground next, control/isolation then distribution/J4. The RF area
  75.4..88.6 by 99.2..104.6 mm is excluded on all copper layers. Planning also
  reserves the F5/U7 region; this creates no CAD objects or rule changes.
- SYS's five actual unconnected entries all terminate in deferred F5 circuitry
  C61/C60/R62/U7/C69. They are not normal F0 supply omissions to route in this phase.
- Preliminary control search found 28 of 32 declared entry-airwire connections;
  four bounded searches failed (~INT to IC1, charger SDA/SCL to IC1 and MCU_INT
  to U1). [Preliminary plan](phase4-9-control-plan.json) is **not native-validated**,
  was not installed, and must be regenerated against a future immediate verified
  baseline. Failed raster searches do not prove an owner relocation is necessary.

## Actual remaining production connections

Production was unchanged; these are the actual entry DRC entries, not planned
reductions. Complete endpoints remain in `phase4-9-entry-ipc/production-drc.json`
and the earlier accepted `phase4-8b-b3-ipc/remaining-by-net.json`.

| Functional group | Actual unconnected entries |
|---|---:|
| USB data, resistor-to-MCU legs and CC | 10 |
| MCU RESET/BOOT/straps/UART and existing status LED circuit | 13 |
| Charger host/I2C/INT/discrete control, including J4 signal branches | 32 |
| MCU3V3 / MAIN_3V3 distribution, including J4 power | 27 (16 / 11) |
| Explicit F5 nets plus F5 SYS branches, deliberately excluded | 29 (24 / 5) |
| PGND, mixed F0/F5/local ground entries | 66 |
| Other existing power: VIN1 / BATTERY / PMID | 7 (1 / 2 / 4) |
| **Total** | **184** |

No completed production nets are claimed. The execution is blocked by the
verification STOP, rather than by an established electrical need to move any
component. Power-domain isolation, supply/ground completion, cold USB ROM
programming and the final live/saved reconciliation remain unfinished.

## Routing mechanism and actual copper objects

The existing canonical workflow uses **custom bounded raster A\* search** over
native exported obstacles, followed by checked line-of-sight chord simplification.
The USB main trunks are explicitly planned paired polylines. Search output is
only candidate geometry; it is not KiCad's interactive router and cannot be
accepted from a pathfinding success alone.

The offline worker constructs native `pcbnew.PCB_TRACK` and `pcbnew.PCB_VIA`
objects and saves only a fresh scratch copy. The production adapter, if later
authorized to resume, constructs `kipy.board_types.Track/Via`, stages them with
`CreateItems`, checks returned geometry, pushes one commit, reads back visible
objects, refills and saves through the owning editor. In this session only its
read-only preflight ran. **Konnect MCP routing tools and KiCad's interactive
router were not used to create these candidate routes.** Konnect was used for
live context, configuration, netlist export and structural inspection.

The earlier scratch3 saved/native readback confirms **70 ordinary tracks and
13 through-vias**, with every original routed object and footprint/pad preserved.
These are real copper objects. Ratsnest airwires and selection/highlight graphics
are absent from this native track/via inventory; visual color alone does not
establish copper. No serialized schematic/PCB/library design was hand-edited,
and no graphical line or filled polygon substitutes for a routed track.

## Read-only candidate quality audit — significant findings

Only scratch3 has a saved/reloaded native candidate export suitable for this
audit; scratch5 failed its new-addition equality gate. Scratch3 passed native
physical DRC/parity and ERC, but final verification stopped on invalid plane
sampling bounds (>30 mm); it is **not an accepted complete candidate**.

[Audit](phase4-9-usb-scratch3-quality.json), derived from native exported copper:

- 70 tracks / 13 vias; **36 non-0/45/90-degree segments**, 21 segments shorter
  than 0.2 mm, and **12 acute centerline-junction candidates**. Angle candidates
  include duplicates and tiny pad-center correction legs and are not twelve
  independently confirmed manufacturing defects.
- Two duplicated connector-end correction legs, on USB_DP and USB_DN, show
  redundant copper generation. These must be removed in a future plan before
  installation, rather than accepted because native DRC permits same-net overlap.
- USB_DN uses 41 segments versus USB_DP's 15. The duplicated USB-C contact link
  is **13.899 mm on DN versus 1.623 mm on DP**, around the accepted VBUS barrier
  and through-hole/contact access. This is genuine candidate copper, not ratsnest.
  The bounded search has not established that this is an optimal or necessary
  solution. Do not install it merely to reduce airwires.
- Three external-data vias per polarity and two MCU-side vias per polarity were
  present in scratch3. Some extra changes arise from joining separately planned
  branches instead of reusing existing same-batch trunk access. A redundant-via
  removal opportunity is a candidate, not proven safe without fresh DRC/readback.
- ESD-to-resistor lengths are DP 24.292 / DN 27.643 mm; resistor-to-MCU lengths
  are DP 23.844 / DN 21.793 mm. Combined ESD-to-MCU trace skew is **1.300 mm**,
  excluding equal resistor package lengths. This does not include the unequal
  connector branches and is not a full USB SI qualification. Aggregate branched
  per-net copper lengths must not be mistaken for end-to-end pair skew.
- Main trunks are parallel on B.Cu with short F.Cu order fanouts. Native plane
  sampling for that candidate is unavailable because of the bounds guard. In1
  contains PGND, but In2 lies between it and B.Cu: there is no claimed adjacent
  continuous B.Cu ground plane or verified 90-ohm impedance. Future reference
  checks must include all transitions and actual drill holes.
- A trunk crosses below the module body. The existing RF antenna keepout is
  avoided; clearance from the module's internal crystal/RF region has **not**
  been established from its internal layout. Check that before accepting the
  path. No EMI, thermal, signal-integrity or hardware measurements were made.

The method creates valid KiCad objects, but its current generic path shaping is
not sufficient to call this USB layout production-ready. It optimizes raster
distance/via cost without explicit bend cost, coupled-pair optimization or global
branch topology; chord smoothing can produce irregular angles and tiny endpoint
hooks. Readability and electrical-quality objections are therefore substantiated.

## Installed capabilities and recommended future approach

Read-only inspection of the installed SDK exposes `run_action(action)` but no
structured interactive-router path-planning/preview API. Running a GUI action
would be stateful; none was invoked to probe it. The available Konnect schemas
advertise direct IPC `route_trace`, L-bend `route_pad_to_pad`, and a parallel
segment `route_differential_pair` with explicit coordinates, width and gap. The
schemas do not demonstrate push-and-shove routing, obstacle-aware pair topology,
completion or length/skew tuning. No mutation was performed to test those handlers.

KiCad 10's official manual documents interactive Walk Around/Shove/Highlight
modes, differential routing and length/skew tuning, and Attempt Finish Selected
(Autoroute, Shift+F). See [KiCad 10 PCB Editor](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html).
These GUI capabilities are useful for future routing, but their availability in
KiCad does not establish a currently callable Konnect router-control interface.
The project's USB_DP/USB_DN names follow KiCad's P/N suffix convention; resistor
legs have generated names and need an explicitly checked pair-selection strategy,
without automatically renaming the schematic or changing rules.

Recommend a **future bounded scratch comparison with KiCad's interactive router
in Walk Around mode**, then its differential router/tuner for USB, rather than
treating all generic raster output as finished layout. Shove mode and global
completion can move accepted copper and should not be used on production under
the current add-only scope. Keep the existing hash guards, native-object
readback, owning-editor save, independent ERC/DRC/parity, plane/reference and
preservation checks regardless of which mechanism proposes the new paths.
No automatic method switch or accepted-copper reroute was performed.

Konnect's installed `check_freerouting` returned **engine_found=false,
native_mcp_available=false, available=false**. The connector advertises local
DSN/SES routing/import capabilities, but no usable engine was found. Freerouting
was not enabled, installed or executed. It is not the proposed first remedy for
this sensitive USB/accepted-power-layout checkpoint.

Espressif's current [ESP32-C3 PCB guidelines, USB and module sections](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html)
support parallel/matched routing, minimizing transitions, return stitching,
continuous reference and avoiding sensitive module regions. They are design
guidance, not evidence of this candidate's impedance or hardware performance.

**STOP for owner review.** A fresh production ERC/DRC/live reconciliation was not
run after the stop, because that would resume the prohibited CAD operation.
Entry checks plus unchanged source hashes are the available production evidence.
No fabrication, purchases, power-up, firmware changes, commit or push.
