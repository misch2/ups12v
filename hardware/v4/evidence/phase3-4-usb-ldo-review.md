# Phase 3.2 service-LDO follow-up review

Date: 2026-10-10. This is the bounded USB service-supply follow-up to the simplified Phase 3.2 MCU/power-domain schematic. The milestone does not authorize PCB layout, fabrication, power-up or firmware changes.

## Baseline and final source

- Pre-LDO CAD baseline: [phase3-4-pre-ldo-baseline.kicad_sch](phase3-4-pre-ldo-baseline.kicad_sch), SHA256 `9e35f7545424b1885a91c5742e38fe2b9884143f6b2a36cf0438da44647c83bd`.
- Final source: [ups12v_v4.kicad_sch](../ups_v4/ups12v_v4.kicad_sch), SHA256 `9e9843a91ae49ff0df7625c0071d784ef94c42b1d690216c4c363f65051aee48`.
- Final true KiCad XML: [phase3-4-usb-ldo.net.xml](phase3-4-usb-ldo.net.xml), SHA256 `001a0f64c1cf3491499478396431eed7a702f1191c5875ad3845c5d4b7235b82`.

## Intentional electrical changes

The USB-side TPS62933 buck block was replaced with the library symbol `Regulator_Linear:AP7361C-33E` and exact orderable MPN Diodes Incorporated `AP7361C-33E-13`, footprint `Package_TO_SOT_SMD:SOT-223-3_TabPin2`. The exact symbol/package map is independently recorded in [phase3-4-ap7361c-package-readback.md](phase3-4-ap7361c-package-readback.md).

- U4 pin 1 VI is `USB_VBUS`; pin 2 GND is `PGND`; pin 3 VO is `USB3V3`.
- USB input bypass is the connector-side C27/C28 pair: C27 is `4.7u 10V USB LDO IN`, C28 remains `100n 10V USB VBUS`.
- USB output bypass is C35 `22u USB OUT` and repurposed C40 `100n USB LDO OUT`.
- R35 is retained and repurposed as `10k USB3V3 BLEED`, from USB3V3 to PGND. At 3.3 V it draws approximately 0.33 mA. It bounds output charge during unplug/backfeed conditions because the selected LDO has no reverse-current protection; it does not establish a tested reverse-current guarantee.
- Removed buck-only references: `C34 C38 C44 C46 L3 R34 R38 R39`.
- Removed buck-only nets: `BST_USB SW_USB USB_EN USB_FB USB_SS`.
- The path is USB_VBUS → U4 AP7361C-33E-13 → USB3V3 → U5 VIN2. TPS2116 reverse-blocking source selection and the normal U3 TPS62933/main VSYS path remain present.
- U5's serialized parameters now describe the actual built-in priority comparator and 8k2/4k7 MAIN_3V3 PR1 divider; obsolete U7 supervisor wording was removed.
- R50's serialized parameters now describe its direct MAIN_3V3-to-Q6 isolation bias; obsolete supervisor-released MUX_PR1 wording was removed.

## Verification

- [phase3-4-usb-ldo-verification.json](phase3-4-usb-ldo-verification.json): PASS. The check uses the pre-LDO true XML and final true XML, confirms the exact U4 pin map, stale-net removal, C27/C40/R35 changes, and scopes all changed retained pins to the declared replacement.
- [phase3-4-usb-ldo-preservation.json](phase3-4-usb-ldo-preservation.json): PASS against the accepted Phase 3.1 MCU/native-USB XML projection. The only old-reference property changes are the documented C27 value, prior R11 value, and accepted U1/U2 metadata changes.
- [phase3-4-usb-ldo-footprint-readback.json](phase3-4-usb-ldo-footprint-readback.json): PASS for 18 active MCU, USB LDO, mux, isolation, charger-gate, bleeder and divider references. This is an XML footprint identity check; it is not PCB land or copper verification.
- Fresh Konnect connectivity checks are captured in [phase3-4-usb-ldo-connectivity.json](phase3-4-usb-ldo-connectivity.json): 0 orphan items, 0 floating wire endpoints, 0 shorted nets, and 0 unconnected pins for U4/R35/C27/C28/C35/C40/U5. The decoupling audit reports 8/8 power pins covered. The generic connection audit retains four pre-existing I2C pull-up advisories.
- Fresh ERC: [phase3-4-usb-ldo-erc.json](phase3-4-usb-ldo-erc.json), 0 errors and 6 pre-existing isolated-label warnings (`UART_RX`, `UART_TX`, `MCU_STATUS_LED`, `MCU_GPIO1`, `MCU_GPIO7`, `MCU_GPIO10`).
- Updated render: [phase3-4-usb-ldo.png](phase3-4-usb-ldo.png), 3000 × 2119, SHA256 `9697c86d0cc1dfb1ac8bba4f70828faca1bf2f4a95044a87b5957897e994ac6a`. It was visually inspected. Five inherited schematic symbol overlaps remain in unrelated areas; this checkpoint records the render and does not claim full cosmetic readability acceptance.

## Datasheet and prototype limits

Independent parent review also passed: [372 retained pin-net/property checks](phase3-4-independent-review.json) and [33 Phase 2.6 power-stage partitions / 154 connected pins](phase3-4-phase2-6-preservation.json). The BOM was regenerated from this final XML (104 groups). The current Git index was preserved; final documentation updates remain unstaged. Full staged whitespace checking reports three whitespace-only serialized CAD lines, including two in the immutable original baseline; these were not hand-edited.

The selected device evidence cites Diodes DS37274 Rev. 5-2, October 2020. Its published VIN range is 2.2–6 V, minimum input/output capacitance is 1/2.2 µF, and the 1 A value is an electrical capability rather than a project thermal guarantee. The 300 mA dropout maximum is 140 mV under the stated datasheet conditions; the 1 A dropout entry is typical. The datasheet's minimum-land SOT-223 thetaJA is 110 °C/W. The selection screen estimates approximately 116.6 °C junction at 300 mA, 5.25 V input and 50 °C ambient; this is a first-order calculation, not a measurement. Sustained 500 mA service load at hot ambient needs copper and thermal measurement.

USB is service-only with Wi-Fi off. ROM/programming current and USB-port current capability were not measured here, so this schematic does not claim 1 A continuous operation or universal 100 mA ROM-flashing compatibility. The LDO's output discharge, input/output capacitor behavior during USB removal, TPS2116 reverse leakage and any MAIN-to-USB backfeed require prototype measurement. No firmware build or hardware power-up was performed.
