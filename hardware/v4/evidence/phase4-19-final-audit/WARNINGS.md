# Phase 4.19 warning disposition

2026-10-18. Accepted Phase4.18 PCB hash `4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84`.
Complete type, description, UUID and position identities are preserved in
[warning-identities.json](warning-identities.json). No rule, severity, exclusion,
library or instance was changed. Production reports remain authoritative:
16 PCB warnings, four ERC warnings, zero errors/parity/opens. The separate
isolated-library 20/11 counts are contextual, not another production defect set.

## Retained PCB warnings

All 16 are `lib_footprint_mismatch`, meaning the placed instance differs from
the currently resolved library copy. None means a demonstrated short or collision.
They are footprint-owned; moving a component cannot reconcile its definition.
The prior Phase4.4 pad comparisons and Nano-Fit native proof, followed by accepted
preservation, are reused. That does not qualify every manufacturer's process or
justify automatically replacing any placed footprint.

| Reference | PCB origin mm | Meaning and release relevance |
| --- | --- | --- |
| J2 | 58,40.38 | Approved project-local Nano-Fit RevJ1 and instance artwork; retain. Finished-hole/locator tolerances remain a fab decision. |
| U4 | 109,83 | SOT-223-3_TabPin2 instance/library difference; prior pad map retained. AP7361C E pin/tab mapping accepted; thermal/service load remains measured qualification. |
| IC1 | 60,66 | Intentional reviewed Texas RQM0029A custom lands, including pads1/9/16/24; retain rather than rebuild. Native mask/paste review found the intended custom apertures. Assembly process remains unqualified. |
| J7 | 117.39,83.975 | Approved GCT USB4085 instance. Native THT and four plated slot geometry retained. Separate DFM-01 CC2 drill clearance issue is not caused by this warning. |
| J4 | 122.5,40 | JST side-entry instance differs from library; prior pad comparison retained. Exact mating housing/wire and height/enclosure need assembly verification. |
| U2 | 115,81.4 | Texas DRT-3 instance; prior pad comparison retained. TPD2EUSB30A is still marked provisional; exact component qualification is a BOM decision. |
| Q1 | 43.9,69.4 | Project-local AON7528 definition. Pin groups/pitch checked; smaller exposed land than current AOS recommendation requires owner/assembly disposition (also Q2/Q10, whether or not warned). |
| U5 | 65,82 | SOT-583-8 instance for TPS2116; prior mapping and local bypass retained. No evidence of mux isolation wiring defect. |
| J6 | 104,38.5 | JST side-entry instance; prior pad comparison retained. NTC/harness qualification remains open. |
| J3 | 73,40.38 | Approved project-local Nano-Fit RevJ1/artwork; same tolerance/harness qualification as J1/J2/J8. |
| U3 | 49,79 | SOT-583-8 instance for normal TPS62933; accepted local geometry retained. Do not refresh to chase a warning. |
| J1 | 43,40.38 | Approved project-local Nano-Fit RevJ1/artwork; retain, subject to fabrication tolerance decision. |
| U7 | 102,59 | SOT-583-8 instance for F5 TPS62933; accepted local geometry retained. Matching-hardware Ceff/current/thermal tests remain. |
| J8 | 89,40.38 | Approved three-position Nano-Fit RevJ1/artwork, F5-only. Preserve actual PGND/NC/OUT pin order and key-B mating set. |
| C22 | 41,57 | Corrected local CASE-D courtyard/artwork retained; optional 20V POSCAP remains DNP. Warning is not permission to fit the legacy candidate. |
| C20 | 47,52.4 | Same local CASE-D/DNP disposition as C22. |

References: [Phase4.4 pad comparison](../phase4-4-pre-routing-review.md),
[Nano-Fit native proof](../nanofit-native-correction.json),
[Phase4.18 preservation](../phase4-18-production-adoption/final-production-proof.json),
[independent part review](INDEPENDENT_REVIEW.md).

## Retained ERC warnings

All four are `isolated_pin_label` on the sole schematic sheet. Fresh Konnect
short/orphan checks find zero, and its single-pin check identifies exactly the
same four one-pin unused MCU nets. There is no unevaluated child sheet here.

| Label | U1 pin | Sheet coordinates mm | Disposition |
| --- | --- | --- | --- |
| MCU_STATUS_LED | 6 / GPIO3 | 438.15,81.28 | Unused labeled GPIO, no attached LED requirement. Acceptable prototype warning. |
| MCU_GPIO1 | 13 / GPIO1 | 438.15,99.06 | Unused labeled GPIO. Acceptable. |
| MCU_GPIO10 | 16 / GPIO10 | 438.15,106.68 | Unused labeled GPIO. Acceptable. |
| MCU_GPIO7 | 21 / GPIO7 | 438.15,119.38 | Unused labeled GPIO. Acceptable. |

Do not wire these merely to clear warnings or infer firmware initialization from ERC.

## Existing ignored checks

| PCB key | Actual significance / audit disposition |
| --- | --- |
| missing_courtyard | Exported native courtyards exist for151/154 footprints. Only NT1/NT2/NT4 lack one; these intentional net ties have no purchased body. All actual courtyards were screened; zero intersections. |
| track_not_centered_on_via | Valid off-center joining can occur within a copper disk. Accepted native pad-islands and physical DRC establish continuity. No extra centering rule is imposed. |
| tuning_profile_track_geometries | Accepted USB geometry is not reopened. Its prior native arc/pair checks and owner qualification are retained. |
| footprint_filters_mismatch | Symbol filter heuristics do not override accepted exact MPN/pad mapping. Actual footprint/MPN qualifications remain listed in the part review. |
| silk_overlap | Disabled clearance check means DRC does not prove reference readability. Native F.SilkS review shows dense overlapping references near IC1/U3/U5/U7 and TP17/J4; optional marking cleanup. |
| silk_over_copper | Disabled mask clipping check; native mask/silk inspected. Do not infer a mask/paste defect from a silk fragment. Final production CAM clipping remains a later release review. |

ERC also ignores `single_global_label`, `four_way_junction`, `pin_to_pin`,
`simulation_model_issue`, `footprint_filter`. These are not new waivers.
The lack of pin-to-pin reporting is not proof of electrical correctness: the
accepted exported topology/CE/power-domain and manufacturer reviews supply the
electrical evidence. SPICE was not used. No new conflicting driver was found;
the latest schematic hash is unchanged. The full settings remain visible in JSON.

**Warning disposition does not waive DFM-01 or any unconfirmed manufacturing
capability. No attempt was made to produce an empty warning report.**
