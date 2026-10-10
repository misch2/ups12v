# Phase 3.2 pre-simplification CAD baseline

Captured 2026-10-10 before the owner-approved MCU/power-domain simplification.

## Source identity

- Repository branch: `codex/v4-phase2-power-stage`
- HEAD: `8799b2f1c3a4b3e5018b153e387e5ea08244879b`
- Source: `hardware/v4/ups_v4/ups12v_v4.kicad_sch`
- Source SHA256: `ac7e0d19e90848bf7f04c9c2aef9e4deadbb502559a12af42d7e5e65e83f4e1a`
- Read-only source copy: `phase3-2-pre-simplification-baseline.kicad_sch` (same SHA256)
- Git index was empty; the only pre-existing worktree change at capture was the
  owner's `hardware/v4/V4_REQUIREMENTS.md` edit. No source CAD or project file
  was changed while capturing this baseline.

## Independent exports

- True KiCad XML netlist: `phase3-2-pre-simplification-baseline.net.xml`
- XML SHA256: `7b96301061665e1cc9bfa9efcc660a51ee8014a3e24e45f8395179ea9594c40f`
- Konnect rendered sheet: `phase3-2-pre-simplification-baseline.png`
- Render SHA256: `6fcb78ddf2ee708e9ab2e888076c6f207ed2ea85c63f298dbf9f640dca5984c0`

The XML contains 149 component entries and 109 nets. The rendered sheet is
2400 x 1695 pixels. This is a baseline capture only; it is not an ERC,
connectivity, preservation, footprint or electrical-acceptance result.

## Simplification candidates visible in this baseline

The candidate-only blocks are U8/U9/U12 with D5, Q10, R54/R55 and C42/C52;
U10 with C49/C50/C51; U11 with C41 and R56/R57; and the current U7/R23
MAIN-valid supervisor branch. The exact retained/removal set remains subject
to the owner-reconciled requirements and the subsequent Konnect mutation
readback. The normal and USB TPS62933 supplies, TPS2116 mux, TCA9517
isolation, ESP32-C3 USB/recovery circuitry and Q5/Q6/Q7 default-off charger
gate are retained design anchors for that review.

## Stale evidence explicitly excluded

`phase3-2-erc-clean.json`, `phase3-2-mcu-power-a1.png` and the earlier
`phase3-2-mcu-power.net.xml` describe pre-stop or intermediate CAD and are not
used as current acceptance evidence.
