# Phase 3.4 pre-LDO CAD baseline

Captured before the owner-authorized USB service buck-to-LDO replacement.

- Source: [ups12v_v4.kicad_sch](../ups_v4/ups12v_v4.kicad_sch), SHA256 `9e35f7545424b1885a91c5742e38fe2b9884143f6b2a36cf0438da44647c83bd`.
- Exact read-only copy: [phase3-4-pre-ldo-baseline.kicad_sch](phase3-4-pre-ldo-baseline.kicad_sch), SHA256 `9e35f7545424b1885a91c5742e38fe2b9884143f6b2a36cf0438da44647c83bd`.
- True KiCad XML: [phase3-4-pre-ldo-baseline.net.xml](phase3-4-pre-ldo-baseline.net.xml), SHA256 `cfa791f4e274198f774f014fa8827bcb50bb865dce13dfdafe4a248d938335ff`.
- Fresh ERC: [phase3-4-pre-ldo-baseline-erc.json](phase3-4-pre-ldo-baseline-erc.json), 0 errors and the same 6 intentional isolated service-label warnings as Phase 3.3.
- Render: [phase3-4-pre-ldo-baseline.png](phase3-4-pre-ldo-baseline.png), generated at 3000 × 2119 px.

The baseline retains U4 `TPS62933DRLR USB 3V3`, L3 `XAL5030-472MEC`, U5 TPS2116 source selection, safe I2C/GPIO isolation, direct MAIN Q8/R50 bias, Q5/Q6/Q7 charger control, and the ESP32-C3 native USB/BOOT/RESET path. No real V4 PCB or hardware claim is made here.
