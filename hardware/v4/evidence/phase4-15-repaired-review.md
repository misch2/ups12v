# Phase4.15 — repaired owner IC1 routing: PASS recommendation

2026-10-17. **PASS for this prototype review; production migration not performed.**
Owner confirms the correction is saved and the editor closed. A new isolated
native review was used; original owner and production files remain hash-bound
and unchanged by the agent. No IPC was needed or retried.

## Verified result

- **IC1.14 I2C_SCL, IC1.21 ~INT and IC1.1 STAT all closed** to their intended
  R21.2, R28.2 and D2.1 islands.
- Native DRC: **41opens, all deferred F5;0physical errors;0parity errors**.
  ERC: **0errors**. Matched isolated warning identities20DRC/11ERC equal the
  accepted reference; no new warnings or ignored-check changes.
- Independent native connectivity:473pads retained,160→157islands; exactly
  one intended merge for each control signal; **no prior pad-island split**.
-95offline toolkit tests PASS. Native assertions: none in the isolated reviews.

## BATTERY correction and electrical review

The only change since the previous review is one0.60mm-wide In2 track between
`(63.1,65.5)` and `(63.1,64.8)`, length0.70mm. The upper via is again connected
on F/In2 and the dangling warning is gone. All original BATTERY via positions,
diameters and drills are unchanged; both primary0.70/0.40mm barrels are available.

The new common0.60mm In2 run is1.690mm long versus the previous main1.565mm;
the former auxiliary0.40/0.70mm branch remains removed to clear moved BTST2.
There is no new smaller drill or narrower main branch. A simple nominal35µm
copper estimate gives1.38mΩ at20°C for the1.690mm common trace, or about50mW
at an illustrative6A. This checks the scale of this local change; it is not a
board current rating or a thermal qualification and excludes barrels/contacts
and process/temperature tolerances. [Geometry, assumptions and calculation](phase4-15-owner-repaired-native/battery-path-geometry.json).

SW1/SW2 tracks/vias and all8native arcs are exactly retained, with no new drill
incursion/clearance error. Bootstrap routing retains0.20mm width: BTST1 changes
1.793→1.874mm; BTST2 changes7.418→6.857mm with the relocated0.30mm drill.
REGN retains its0.20mm trunk with new0.15mm sections; PROG retains minimum0.10mm
and gains0.15mm sections. Native pad connectivity preserves the local bypass,
VIN1, PMID, BATP and intended net-tie functions. Fine-pitch clearance passes DRC.

Local F/In2/B views were inspected. SCL uses four new through-via transitions
to navigate existing routing; STAT is F.Cu with no vias; INT joins the existing
network using one new transition. No electrical reason was found to reopen
these low-speed routes merely to optimize posture or small segment angles.
Source routes and their surrounding changes are captured in the exact diff.

PGND zone definitions are unchanged; its native In1 fill remains one connected
polygon, about6111.20mm² versus6115.60mm² accepted, and no prior PGND pad island
splits. Finite projected fill samples document local antipad/drill interruptions;
they do not establish controlled impedance or a continuous adjacent reference
for B.Cu. No extra high-speed requirement is imposed on these controls.
[Focused electrical evidence](phase4-15-owner-repaired-native/focused-electrical-review.json).

## Complete bounded diff and source authority

Production→owner:247added/221removed/2modified tracks;8added/1removed/3moved
vias; R8 moves `(40,75.5)`→`(40,74.8792)` with its two pads.1053track/arc objects,
294vias,154footprints,473pads. Other surrounding control/supply route changes
are included in the [full physical diff](phase4-15-owner-repaired-native/physical-delta.json),
not silently discarded. SW1/SW2, USB data and deferred F5 routed copper are
unchanged. All pad net assignments/drills, zone definitions and board drawings
are preserved. Source schematic/custom rules are byte-identical to production.
Owner project only adds routing dropdown presets, without constraint changes.

Owner PCB SHA256:
`2ef3030c033f254742736c8da3d74468db133a13905eb55df3716a26335676e5`.
Production PCB remains:
`75060f4b3d0f57e65f2c6e4736f3dc32d42e62e359541671b1ffce63eceb7014`.
[Complete proof](phase4-15-owner-repaired-native/final-review.json),
[native check summary](phase4-15-owner-repaired-native/summary.json),
[pad preservation](phase4-15-owner-repaired-native/pad-preservation.json).

**STOP for owner review and separate migration authorization.**
[Exact native-editor migration proposal](phase4-15-production-proposal/PLAN.md).
No source CAD/production writes, F5/USB redesign, rule/BOM/architecture or
firmware changes, fabrication, purchase, power-up, commit or push occurred.
Existing matching-hardware power/current/thermal qualification remains separate.
