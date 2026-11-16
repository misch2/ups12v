# V4 shared BQ25792/BQ25798 package map

2026-10-10. This is the package and symbol reconciliation record for the
charger stage. It does not approve PCB synchronization or fabrication.

## Manufacturer basis

Both intended orderable variants use TI's RQM VQFN-HR package, nominally
4 mm x 4 mm with 29 logical pins.  The TI package-outline drawing also calls
out a 33X terminal/land pattern: four corner pin positions are split into two
solderable land features each.  Those four duplicate land features are not
additional logical pins.

- [BQ25798 SLUSDV2C, Rev. C, June 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf), §5, Figure 5-1 and Table 5-1, pp. 4-5.
- [TI RQM0029A package drawing 4225253/A, November 2019](https://www.ti.com/lit/ml/mpqf573/mpqf573.pdf), package outline and land-pattern pages.  The outline and board-layout views call out `33X` terminal/land dimensions while the package remains RQM0029A.
- [BQ25792 SLUSDG1C, Rev. C, August 2022](https://www.ti.com/lit/gpn/BQ25792), §7, Figure 7-1 and Table 7-1, pp. 5-6.
- TI's BQ25792 product data identifies `BQ25792RQMR` as VQFN-HR RQM, 29 pins; the BQ25798 data identifies the same RQM 29-pin package. The TI E2E BQ25792 discussion describes BQ25798 as the improved, pin-to-pin successor, but the complete symbol/footprint equivalence is still an engineering check for this design.

The previous schematic instance was an embedded legacy SamacSys/Mouser symbol
with 33 electrical pin representations and an unavailable custom footprint
library entry. Its four extra representations are the split corner lands
described below. It is retained here as migration evidence only. The live
`IC1` instance now uses the official `Battery_Management:BQ25798` 29-logical-
pin symbol and the standard footprint below; its fields record the TI source,
shared-variant status and split-land reconciliation.

## Logical pin and split-land map

The following map is read from the TI top-view pin tables. The two VBUS lands,
two BAT lands and single GND land are separate logical pins even when they
share an electrical function. Pins 1, 9, 16 and 24 each use two split corner
land features in the 33X pattern. The drawing is a top view; pin numbers
follow TI's package key and counter-clockwise numbering.

| Physical land | Function | Existing logical pin | Standard footprint land | Evidence |
|---:|---|---:|---:|---|
| 1 | STAT | 1 | 1 + split land 30 | BQ25798 Table 5-1; RQM0029A drawing |
| 2 | VBUS | 2 | 2 | BQ25798 Table 5-1 |
| 3 | VBUS | 3 | 3 | BQ25798 Table 5-1 |
| 4 | BTST1 | 4 | 4 | BQ25798 Table 5-1 |
| 5 | REGN | 5 | 5 | BQ25798 Table 5-1 |
| 6 | D+ | 6 | 6 | BQ25798 Table 5-1 |
| 7 | D- | 7 | 7 | BQ25798 Table 5-1 |
| 8 | VAC2 | 8 | 8 | BQ25798 Table 5-1 |
| 9 | VAC1 | 9 | 9 + split land 31 | BQ25798 Table 5-1; RQM0029A drawing |
| 10 | ACDRV2 | 10 | 10 | BQ25798 Table 5-1 |
| 11 | ACDRV1 | 11 | 11 | BQ25798 Table 5-1 |
| 12 | QON | 12 | 12 | BQ25798 Table 5-1 |
| 13 | CE | 13 | 13 | BQ25798 Table 5-1 |
| 14 | SCL | 14 | 14 | BQ25798 Table 5-1 |
| 15 | SDA | 15 | 15 | BQ25798 Table 5-1 |
| 16 | TS | 16 | 16 + split land 32 | BQ25798 Table 5-1; RQM0029A drawing |
| 17 | ILIM_HIZ | 17 | 17 | BQ25798 Table 5-1 |
| 18 | BATP | 18 | 18 | BQ25798 Table 5-1 |
| 19 | BTST2 | 19 | 19 | BQ25798 Table 5-1 |
| 20 | PROG | 20 | 20 | BQ25798 Table 5-1 |
| 21 | INT | 21 | 21 | BQ25798 Table 5-1 |
| 22 | BAT | 22 | 22 | BQ25798 Table 5-1 |
| 23 | BAT | 23 | 23 | BQ25798 Table 5-1 |
| 24 | SDRV | 24 | 24 + split land 33 | BQ25798 Table 5-1; RQM0029A drawing |
| 25 | SYS | 25 | 25 | BQ25798 Table 5-1 |
| 26 | SW2 | 26 | 26 | BQ25798 Table 5-1 |
| 27 | GND | 27 | 27 | BQ25798 Table 5-1; §8.4.1 |
| 28 | SW1 | 28 | 28 | BQ25798 Table 5-1 |
| 29 | PMID | 29 | 29 | BQ25798 Table 5-1 |

The standard installed KiCad footprint candidate is
`Package_DFN_QFN:Texas_RQM0029A_VQFN-29_4x4mm_P0.4mm`. Its pad geometry and
pin-1 orientation were queried through Konnect. It has 29 numbered pads; its
custom corner pads 1, 9, 16 and 24 encode the same split-corner copper
geometry as the four duplicate land features. The SamacSys footprint queries
returned 33 pads, with the four extra pads at the corresponding corners. This
is a pad-geometry reconciliation, not permission to assign four additional
electrical nets. The live-instance replacement and schematic pin-partition
check are complete. PCB parity and release checks remain separate work.

## Legacy embedded duplicate representations

The previous embedded symbol added four representations beyond the 29 logical
pins. They were connected in the saved netlist to the corresponding logical
function and match the four split corner land features in the TI drawing:

| Embedded pin | Duplicate of logical pin | Net in current export | Treatment |
|---:|---:|---|---|
| 30 `STAT_2` | 1 `STAT` | `STAT` | Split corner land for logical pin 1; same net as pin 1. |
| 31 `VAC1_2` | 9 `VAC1` | `VIN1` | Split corner land for logical pin 9; same net as pin 9. |
| 32 `TS_2` | 16 `TS` | `TS` | Split corner land for logical pin 16; same net as pin 16. |
| 33 `SDRV_2` | 24 `SDRV` | `SDRV` | Split corner land for logical pin 24; same net as pin 24. |

The source/geometry reconciliation is supported by the TI `33X` drawing, by
query-back of both installed footprints, and by the live official-footprint
query. The duplicate pin labels were removed from the schematic rather than
mapped to four extra electrical nets. Fresh XML and ERC evidence is recorded
in `evidence/phase2-3-power-final.net.xml`,
`evidence/phase2-3-power-erc.json`, and
`evidence/phase2-3-power-verification.json`.

## Procurement comparison (pre-freeze)

| Candidate | Package / source | Procurement evidence | Decision |
|---|---|---|---|
| BQ25798RQMR | TI RQM VQFN-HR; official 29-pad KiCad footprint with split-corner pads | TI product page and orderable data identify RQM, 29 pins; exact TME listing not found during this pass (**UNVERIFIED**) | Primary V4 variant; official symbol/footprint replacement and schematic partition proof complete |
| BQ25792RQMR | TI RQM VQFN-HR; same 29 logical pin table family | TI BQ25792 Rev. C source is recorded above; exact TME listing not found during this pass (**UNVERIFIED**) | Alternate population variant; pin/register equivalence still requires the variant review |
| SamacSys/Mouser BQ25798RQMR | 33-pad legacy footprint and 33-representation symbol | Installed local library query only; supplier availability and source revision are not treated as procurement proof | Retain only as migration evidence; not a freeze candidate |

The current IC1 instance therefore has an accepted schematic symbol/footprint
mapping, while procurement verification and the BQ25792 variant equivalence
review remain open. No stock, price or purchase claim is made here.

## Ground and bypass consequence

TI BQ25798 Rev. C §8.4.1, pp. 139-140, calls for the 0.1 uF and bulk PMID/SYS
capacitor returns to use low-impedance paths back to IC GND, and for REGN to
return through the internal ground plane to the IC GND pin. The schematic keeps
PGND and GND as separate named returns with one `NT1` tie adjacent to IC1 pin
27. The PCB must preserve the single local tie and high-current loop geometry;
the schematic does not authorize a board-wide ground moat.

## Input fuse and hot-plug provision

F1 is now the explicit positive adapter path: J1 pin 2 -> F1 pin 2 -> F1
pin 1/VIN1 -> the polarity and reverse-input FET stage. The prototype
candidate is Littelfuse `0451005.MRL` (5 A, 125 Vdc; nominal cold resistance
12.5 mOhm; nominal melting integral 5.566 A2s). The 451/453 manufacturer
datasheet (revision GD.12/01/25, p. 3) gives the 25% continuous derating
baseline; this leaves 3.75 A before temperature derating and is preferable to
the 4 A candidate for the normal adapter-input target of at most 3 A. Final
selection still requires measured temperature, cable, hot-plug, polarity-FET
SOA and fuse-coordination evidence on the matching prototype. TME and LCSC
identities are recorded in `V4_PROCUREMENT_RESUME.md`; current stock remains
UNVERIFIED.

The installed-library search did not find a suitable 2410 fuse footprint. A project-local
`ups_v4:Littelfuse_451_2410` footprint was created through Konnect after a
disposable `.validation/fuse_acceptance` project was queried and rendered in
`evidence/fuse-2410-acceptance.png`. The provisional prototype geometry is two
2.20 x 2.20 mm SMD pads at +/-2.25 mm (4.50 mm pitch), with a 6.10 x 2.69 mm
body and 7.20 x 2.70 mm courtyard. These pad dimensions remain an engineering
assumption pending confirmation against the manufacturer package drawing; the
disposable map is evidence of the CAD workflow only and is not physical
footprint acceptance or fabrication approval.

TI BQ25798 Rev. C Figure 8-1, p. 130, shows a VIN hot-plug damping provision
of 2 ohm in series with a 2.2 uF shunt to ground for hot-plug conditions above
15 V. The schematic records this as pending because an exact >=35 V resistor
and capacitor pair has not yet passed procurement review; no unqualified bulk
or damping part was silently populated.

Status: official shared symbol/footprint acceptance and the 29-pin electrical
partition proof are complete. BQ25792/BQ25798 register equivalence, PCB
parity, procurement, and hardware measurements remain open.

## Historical phase 2.3 candidate qualification — 2026-10-10

Phase 2.3 source SHA256 (superseded by phase 2.4 evidence below):
`2938c56c36c49f4124be519d3b6abe003781b3fd3ac0175aa5b8d36854d156de`.
Use `evidence/phase2-3-review.net.xml`, `phase2-3-review-erc.json` and
`phase2-3-review-verification.json` for current electrical evidence rather
than the intermediate exports named above. Fresh ERC is 0 errors / 0 warnings;
every pin partition matches the explicitly intended changes.

The official IC1 mapping is a completed logical-pin migration check. Its
query-based geometry comparison does not establish manufactured PCB parity or
full variant acceptance. The new F1 footprint is **PROPOSED**, not physically
accepted: its disposable readback and render prove the geometry created by
Konnect, but the manufacturer recommended land-pattern comparison is still
missing. The hot-plug branch is only a note, not an implemented circuit.

The accessible BQ25792 document recovered this session is SLUSDG1D, April
2026; source and provenance are in `V4_PROCUREMENT_RESUME.md`. Older Rev. C
citations above describe the earlier analysis, not a new Rev. D comparison.
The exact 29-pin and 2S/4S default comparison against that recovered revision
remains an explicit schematic-completion item. Do not claim broad register
equivalence or full power-stage milestone completion from this document.

## Actual-revision PROG/POR review — phase 2.4, 2026-10-10

Compared BQ25792 **SLUSDG1D, April 2026**, section 8.3.2 Tables 8-1/8-2
p.27, against BQ25798 **SLUSDV2C, June 2026**, section 7.3.2 Tables 7-1/7-2
p.25. Sources: [TI public BQ25792 support attachment](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/SLUSDG1_3D00_4_3D00_TI-PDF_3D00_en_2D00_us-_2800_2_2900_.pdf)
(confidential marking retained; do not rehost), and
[TI BQ25798 datasheet](https://www.ti.com/lit/ds/symlink/bq25798.pdf).

| Assembly | PROG / frequency | POR VSYSMIN / VREG | POR ICHG |
| --- | --- | --- | --- |
| S792-2 | 8.2k 1% / 750 kHz | 7 V / 8.4 V | **2 A** |
| S798-2 | 8.2k 1% / 750 kHz | 7 V / 8.4 V | 1 A |
| S792-4 | 27k 1% / 750 kHz | 12 V / 16.8 V | 1 A |
| S798-4 | 27k 1% / 750 kHz | 12 V / 16.8 V | 1 A |

Both revisions give the same PROG selections and VREG ranges (2S 5-9.99 V,
4S 14-18.8 V). Necessary configuration addresses correspond: CELL REG0A[7:6],
ICHG REG03/04, VREG REG01/02, VSYSMIN REG00[5:0]. This is a bounded comparison,
not broad register equivalence. CE is active LOW on logical pin 13 and requires
EN_CHG=1; it must not float. Preserve the charger-only-reset risk and normally-off
sink policy; the host must release CE before reconfiguration/on detected fault.

Actual-revision full pin-table comparison/package acceptance remains unfinished;
do not infer it from this PROG/POR check. Earlier official footprint/logical-pin
migration work is preserved, not repeated or promoted to PCB parity.

Current phase 2.4 saved schematic SHA256:
`50842c1c756ed6ebc92b33b9db64ebeb787d378d7b2a22b5386166551052fbea`.
`phase2-4-metadata.net.xml`, `phase2-4-metadata-erc.json` and
`phase2-4-metadata-verification.json` supersede phase 2.3 as current electrical
evidence. ERC 0 errors/0 warnings, all explicit expected partitions pass.

## Phase 2.6 essential variant acceptance — 2026-10-10

This supersedes the earlier unfinished **essential** pin/variant comparison,
not the historical evidence or outstanding physical qualification. Owner
authorizes provisional prototype schematic completion without exhaustive
register equivalence or pre-prototype measurements.

Compared all 29 logical pin functions in SLUSDG1D section 6, Figure 6-1/Table
6-1 pp.5-7 against SLUSDV2C section 5, Figure 5-1/Table 5-1 pp.4-5. Every
number/function agrees with the existing 29-row map above, including separate
VBUS 2/3, BAT 22/23, GND 27 and corner functions 1/9/16/24. Both are RQM
4 x 4 mm VQFN-HR. Reuse the prior TI RQM0029A 4225253/A physical drawing and
split-corner acceptance; no new package or footprint is introduced. Fresh
Konnect symbol/29-pad readbacks are phase2-6-charger-symbol.json and
phase2-6-charger-footprint.json. The top-view pin sequence, pin-one key and
corner geometry remain as previously inspected in phase2-package evidence.
This supports the single-PCB population strategy, not manufactured parity.

The phase 2.4 PROG/POR table remains authoritative: fixed 8.2k/27k 1%, 750 kHz;
792 2S defaults to 2 A, the other listed profiles to 1 A. No current-ceiling or
external expiry circuit was added. Charging still needs CE LOW and EN_CHG=1.
The host must release CHG_REQ/CE before changing CELL/configuration, after a
detected charger reset/watchdog/fault, and until configuration/readback succeeds.
An unnoticed charger-only reset with Q3 held on remains the approved hardware
limitation; this schematic does not make a firmware 0.5 A setting fail-safe.

Bounded firmware-critical differences, from the exact revisions above:

| Register | BQ25792 Rev.D | BQ25798 Rev.C | Required future firmware handling |
| --- | --- | --- | --- |
| 48h[5:3] PN | 001b (section 8.5.1.57 p.126) | 011b (section 7.5.1.57 p.128) | Identify PN separately from DEV_REV[2:0]; select device profile, reject unknown IDs. |
| 0Fh[0] | Reserved (8.5.1.12 pp.68-69) | EN_BACKUP, reset 0 (7.5.1.12 pp.70-71) | Preserve reserved bits on 792; leave backup disabled on 798 for VSYS scope. |
| 15h | Reserved, reset 00h (8.5.1.18 p.78) | MPPT control, reset AAh, EN_MPPT[0]=0 (7.5.1.18 p.80) | No 798 register dump/profile writes to 792; MPPT stays disabled for regulated adapters. |
| 16h[0] | Reserved (8.5.1.19 p.79) | BKUP_ACFET1_ON (7.5.1.19 p.81) | No backup recovery command in initial VSYS firmware; preserve reserved bits. |

Common VSYS controls checked: 00h VSYSMIN; 01/02h VREG; 03/04h ICHG;
0Ah[7:6] CELL; 0Fh[5] EN_CHG; 10h watchdog; 12h[6] EN_OTG reset 0.
Use device-specific masks/readback and explicit firmware configuration, not
raw whole-register images. OTG/MPPT/backup remain off in this phase. Full
register-by-register equivalence is neither claimed nor required for this
provisional schematic. No firmware implementation or build was performed.

F1 land comparison/correction is now documented in
`evidence/phase2-6-fuse-land-review.md`; 5 A remains PROPOSED. R12/C26 are
implemented PROPOSED shunt parts; see `V4_HOTPLUG_REVIEW.md`. These supersede
the older statements that only a damping note exists or fuse lands are unknown.
