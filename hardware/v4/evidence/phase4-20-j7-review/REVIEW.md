# UPS V4 — Phase 4.20 scratch J7 DFM correction

2026-10-18. **Candidate PASS; STOP for owner review. Production adoption and
manufacturing release are not authorized.** Phase 4.19 remains the accepted
engineering review, with only DFM-01 addressed in this isolated candidate.

## Quick start

1. Review the [before/after illustration](J7-before-after.png) and exact geometry below.
2. Review the five [fabrication decisions](FABRICATION_DECISIONS.md).
3. Decide whether to authorize a subsequent, guarded production adoption of
   these three tracks. This candidate does not authorize a production write,
   stackup/footprint/rule change, manufacturing files, order or power-up.

## Exact proposed geometry

All coordinates are board millimetres; all three tracks remain USB_CC2,
In2.Cu, width **0.180 mm**. The two external endpoints are fixed. Each diagonal
stays on its original 45-degree line; extending the two legs by 0.084853 mm
and shortening the vertical by 0.120 mm gives total length **+0.049706 mm**.
No additional segment, via, footprint move or width change is needed.

| Source UUID | Before start → end | Proposed start → end | New scratch UUID |
| --- | --- | --- | --- |
| `4d552340-51f3-4a54-8e44-32e11454ef13` | (119.050,75.300) → (119.800,76.050) | (119.050,75.300) → (119.860,76.110) | `6b749cde-148c-4782-a324-42b2486548e4` |
| `1814d666-f764-4da0-839c-339e7a06c1ca` | (119.800,76.050) → (119.800,78.665) | (119.860,76.110) → (119.860,78.605) | `4c8fa43c-a929-427d-a375-6b9d0366ee00` |
| `878d8bda-a418-454a-8362-c06c73dcd100` | (119.800,78.665) → (118.740,79.725) | (119.860,78.605) → (118.740,79.725) | `a01da3d3-795d-4da0-9171-01cdf01cb32a` |

At J7 shell pad `a795896d-5791-49b7-91ae-4207a4427483`, the physical
rotated 0.600 × 2.100 mm plated-slot edge remains X119.420. Proposed track
left copper edge is X119.770, hence **0.350 mm** actual nominal clearance
(before 0.290 mm). Margin over JLCPCB's inner-layer PTH requirement is
**0.050 mm**. This is a design geometry measurement, not a manufactured
tolerance guarantee. [JLCPCB applicable rule](https://jlcpcb.com/capabilities/pcb-capabilities/)
was rechecked 2026-10-18; no reliance on KiCad's existing 0.250 mm setting.

The upper diagonal, vertical and lower diagonal have respective shell gaps
0.532774 / 0.350000 / 1.677003 mm. Thus the corners do not undercut the
vertical clearance. Across the three tracks, minimum different-net copper
clearance is **0.161041 mm** (lower leg to J7 USB_VBUS pad), and minimum
different-net physical drill clearance is **0.311041 mm**. Vertical-to-shell
pad copper clearance improves 0.140 → **0.200 mm**. The lower CC2 endpoint
continues to enter its own CC2 plated contact; this intended same-net
connection is not an isolation error. No new microleg or acute corner.

## Validation and preservation

Native KiCad **10.0.7**, supported pcbnew object operations only, through the
existing `kicad_v4.py replace` monitored isolated-worker workflow. A fresh,
read-only production-derived native context preceded the mutation. Source,
accepted manifest, exact old object preimages, plan, output directory and
project/rule hashes were bound. Only the fresh unlocked scratch was saved,
reloaded, refilled and saved by native CLI; no production/live editor write.

| Check | Result |
| --- | --- |
| Focused preflight / native create / save / independent reload / post-refill comparison | PASS; exactly 3 tracks removed and 3 added |
| Native DRC after actual refill, all-track errors and schematic parity enabled | **0 physical errors, 0 opens, 0 parity** |
| Native ERC, copied unchanged sole sheet | **0 errors** |
| Matched isolated warning identities | **20 PCB / 11 ERC**, exactly equal to accepted Phase 4.18 isolated evidence; production's accepted 16/4 remain unchanged |
| All native pad connectivity islands | **473 pads / 116 islands preserved**, CC2 connected; no old connection lost |
| Retained source objects | **1167 tracks/arcs including all 8 arcs, 324 vias, all 154 footprints/pads/artwork/rules/zone definitions preserved**; independent non-fill serialization comparison PASS |
| Actual filled copper | **All In1 PGND contour vertices and holes exactly equal** before/after; one connected polygon; no other layer has a filled zone; local plane and via/return samples equal |
| Independent vendor-specific PTH screen | **1 → 0** track failures; 0 plane failures and 0 hole-pair failures before/after |
| Local all-layer inventory | F.Cu 33 tracks/4 vias/27 pads; In1 4 vias/20 pads plus actual fill; In2 7 tracks/4 vias/20 pads; B.Cu 10 tracks/4 vias/20 pads; 24 local drills |
| Offline toolkit suite | **127 tests PASS**, including new rotated-slot, cross-layer drill/same-net endpoint and actual-fill-hole regression cases |

The export-only supplemental check initially classified an intentional same-net
CC2 pad entry as a clearance failure. Inspection of exported geometry identified
that predicate error; it was corrected and regression-tested without another
CAD mutation. [Diagnostic](analysis-diagnostic.json). No genuine preservation
failure, unexpected native assertion, IPC transaction or recovery occurred.

Full evidence: [geometry/object delta](geometry-screen.json),
[vendor before](vendor-before.json), [vendor after](vendor-after.json),
[native summary](../phase4-20-j7-candidate/summary.json),
[native preservation](../phase4-20-j7-candidate/replace-verify-preservation.json),
[plan](../phase4-20-j7-dfm/candidate-plan.json),
[input hashes](review-input-hashes.json), [final preservation](final-preservation.json).
The illustration is drawn from native geometry exports and shows physical
drills and In2 copper. It is neither Gerber/CAM nor fabricated-board evidence.

## Bound result and STOP

Production PCB SHA256 remains
`4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84`.
Proposed [scratch PCB](../phase4-20-j7-candidate/ups12v_v4.kicad_pcb) SHA256:
`4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737`.

Schematic/project/rules, libraries, production stackup, BOM/procurement and
firmware are unchanged. No extra USB optimization, legacy cleanup, footprint
replacement, manufacturing output, purchase, power-up, commit or push.
Hardware current/thermal/fit qualifications from Phase 4.19 remain open.
Recommend a fresh session after owner review for any separately authorized
production adoption; do not overwrite production with this scratch file.
