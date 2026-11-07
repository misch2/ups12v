# AP7361C-33E package and disposable fixture readback

Date: 2026-10-10. This is a library/package acceptance artifact for the proposed USB service LDO. It does not modify the real V4 schematic or authorize PCB placement.

## Source and selected libraries

- Manufacturer / exact MPN: Diodes Incorporated AP7361C-33E-13, fixed 3.3 V, SOT-223 E package.
- Datasheet: [AP7361C DS37274 Rev. 5-2, October 2020](https://www.diodes.com/datasheet/download/AP7361C.pdf), package top view and pin table pp. 1–2. The exact orderable suffix is recorded separately from the library's generic `AP7361C-33E` symbol name.
- Symbol: `Regulator_Linear:AP7361C-33E`.
- Footprint: `Package_TO_SOT_SMD:SOT-223-3_TabPin2`.
- Datasheet and library readbacks were obtained through Konnect. The symbol reports 3 electrical pins; the footprint reports 4 physical pads with duplicate pad number 2 for the exposed GND tab.

## Physical pin map

The datasheet's package drawing is a top view. The footprint coordinates below are local coordinates returned by `get_footprint_info`, with rotation 0° and F.Cu orientation.

| Datasheet lead | Function | Symbol pin / type | Footprint pad | Local position / geometry | Evidence |
|---:|---|---|---:|---|---|
| 1 | IN | 1 / VI / power_in | 1 | (-3.15, -2.30) mm, 2.0 × 1.5 mm | DS37274 Rev. 5-2 pp. 1–2; Konnect readback |
| 2 | GND | 2 / GND / power_in | 2 | (-3.15, 0.00) mm, 2.0 × 1.5 mm | DS37274 Rev. 5-2 pp. 1–2; Konnect readback |
| 2 | Exposed/tab GND | no separate symbol pin | 2 (duplicate physical pad) | (+3.15, 0.00) mm, 2.0 × 3.8 mm | DS37274 Rev. 5-2 pp. 1–2; Konnect readback |
| 3 | OUT | 3 / VO / power_out | 3 | (-3.15, +2.30) mm, 2.0 × 1.5 mm | DS37274 Rev. 5-2 pp. 1–2; Konnect readback |

This reconciles 3 datasheet electrical leads, 3 symbol pins, 4 physical SMD pads, 3 unique pad numbers, one duplicated electrical GND pad, and no mechanical-only pad. The footprint's pin-1 marker is at the upper-left pad in the top-side disposable render.

## Disposable fixture

Konnect created a separate fixture project, placed the exact symbol and footprint, and read both instances back:

- Schematic source: [ap7361c-fixture.kicad_sch](ap7361c-fixture.kicad_sch), SHA256 `e7039fb3d9f98e450982ebac8c9fc898d1c29414480d3915fed3f7121a13205a`.
- PCB source: [ap7361c-fixture.kicad_pcb](ap7361c-fixture.kicad_pcb), SHA256 `20aa0b66a22c892dcf503739c3174924cf20371932f404d5724778cc79d6f229`.
- Symbol render: [ap7361c-fixture-schematic.png](ap7361c-fixture-schematic.png), SHA256 `bdfe8a737c7f71e238a50c845e24ef66ba58f74faa4a114fdb38dee50813f91d`.
- Board render: [ap7361c-fixture-board.png](ap7361c-fixture-board.png), SHA256 `ea8f08395972dc52241df2afd86a1867961ddb3a264b97d40a8674f3c2d1b0fd`.

Visual inspection confirmed the symbol pin labels and the board pin-1 marker, three left-side leads, and right-side duplicate GND tab. The fixture board has no production routing and is disposable evidence only.
