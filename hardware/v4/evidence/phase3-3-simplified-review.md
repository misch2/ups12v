# Phase 3.3 simplified MCU/power-domain schematic review

> HISTORICAL pre-LDO checkpoint. The owner subsequently approved replacing U4 with a service USB LDO; consult current V4_HANDOVER.md for the new schematic hash/evidence. This report continues to document the preserved charge/reset simplification.

Date: 2026-10-10

This checkpoint is the owner-approved simplification of the unfinished Phase 3.2 MCU, USB-service and charge-control area. The source was mutated through Konnect and then exported by KiCad 10.0.7. The saved schematic source is [ups12v_v4.kicad_sch](../ups_v4/ups12v_v4.kicad_sch) with SHA256 `9e35f7545424b1885a91c5742e38fe2b9884143f6b2a36cf0438da44647c83bd`.

## Intentional CAD changes

Removed the 18 superseded references:

`U7 C42 U8 U9 U12 D5 R54 U10 C49 C50 C51 U11 C41 C52 R56 R57 Q10 R55`

These were the external MAIN supervisor, charge-authorization latch/live-arm and Schmitt stages, external MCU reset supervisor, TPS22975 MCU hold-up/load-switch stage, 470 uF hold-up capacitor, and associated timing/bias parts. The normal VSYS-to-3.3 V buck, independent USB service buck, TPS2116 mux, TCA9517 domain isolation, ESP32-C3 native USB/BOOT/RESET/bypass, and default-off Q5/Q6/Q7 charger gate remain.

The TPS2116 priority input now uses the required MAIN-referenced divider. R23 is `8k2 1%` from `MAIN_3V3` to `MUX_PR1`; new R24 is `4k7 1%` from `MUX_PR1` to `PGND`. U5 MODE remains on `MAIN_3V3`, so priority selection does not depend on the mux output. The nominal divider ratio is 4.7/(8.2+4.7) = 0.364; PR1 is approximately 1.20 V at 3.3 V MAIN and the ideal VREF(max)=1.08 V source-valid boundary is approximately 2.96 V. The 1% worst-case ratio puts the 3.0 V boundary at approximately 3.0 V; this is a source-selection qualification for prototype testing, not a new product acceptance threshold.

The divider is used only for the TPS2116 PR1 comparator. Q8's PMV16UN gate and R50's Q6 base bias are now taken directly from `MAIN_3V3`, avoiding an unqualified ~1.2 V MOSFET/NPN drive while preserving main-domain-only isolation. Q8 remains a non-conductive gate connection to the USB-side NEN isolation node.

Charge authorization is now the explicit firmware-controlled `MCU_CHG_ARM` path through R46 into the separately named `MCU_CHG_BASE` net at Q7, with R47 providing the base pull-down. The existing Q5/Q6 MAIN-valid series gate and pull-downs provide hardware-default-disabled behavior and power-domain isolation. No independent timeout, fresh-edge, latch, or external reset guarantee is implemented.

## Fresh verification

Divider/priority basis: [TI TPS2116 SLVSFG1A Rev. A, May 2021](https://www.ti.com/lit/ds/symlink/tps2116.pdf), sections 5, 6.5 and 7.3.1; checked 2026-10-10. MODE tied to VIN1 selects priority operation. With Q8/R50 moved to MAIN, PR1 has no external transistor load: 1% resistor corners and 0.1 uA maximum PR1 leakage put the upper selection boundary at approximately 3.004 V. This is a calculation, not a new mandatory protection threshold or a measured switchover result.

- True KiCad XML: [phase3-3-simplified.net.xml](phase3-3-simplified.net.xml), SHA256 `19bed88efa8ceecdab5784cab4a306727b1f58cc302bc15302d44b765d2efdb6`; 132 component entries.
- Direct Konnect ERC: [phase3-3-simplified-erc.json](phase3-3-simplified-erc.json), 0 errors and 6 intentional isolated service labels (`UART_RX`, `UART_TX`, `MCU_STATUS_LED`, `MCU_GPIO1`, `MCU_GPIO7`, `MCU_GPIO10`).
- Independent baseline comparison: [phase3-3-simplified-verification.json](phase3-3-simplified-verification.json), PASS. It confirms exactly the 18 removals, the single documented R24 addition, the R23 divider value, expected U5/Q7/R46/R47/Q8/R50 net changes, retained key nets, and no unexpected pin changes.
- Additional parent review: [Phase 2.6 preservation](phase3-3-phase2-6-preservation.json) passes all 33 projected partitions (154 pins, service R11.2 exception); [final independent check](phase3-3-final-independent-review.json) confirms all 394 retained exported pins and unchanged retained values/footprints except R23. New R24's installed 0402 library resolves with two pads: [Konnect readback](phase3-3-r24-library-footprint.json).
- Phase 3.1 projection: [phase3-3-simplified-preservation.json](phase3-3-simplified-preservation.json), PASS. MCU/native-USB partitions and required USB service nets are preserved; only the declared USB series splits and R11 service no-connect are excepted.
- Footprint readback: [phase3-3-simplified-footprint-readback.json](phase3-3-simplified-footprint-readback.json), PASS for the exported XML library identities of 17 active MCU, USB, mux, isolation, charger-gate and divider references. This does not establish physical-land geometry acceptance.
- Direct Konnect connectivity checks after rewiring: 0 orphan items, 0 floating wire endpoints, 0 unconnected component pins, and 0 shorted nets.
- Updated rendered schematic: [phase3-3-simplified.png](phase3-3-simplified.png), SHA256 `de8e23886b2880ebbe6f5d94c7517b74b4ee70ea3e0c52a90a9f0da86bf9b566`. Visual inspection confirmed the new divider and direct MAIN gate/bias labels are present. Dense inherited annotations and value/label overlaps remain in several unrelated blocks; this render is inspection evidence, not full cosmetic readability acceptance. The overlap scan reports seven existing geometry overlaps elsewhere in the sheet; none involves R23/R24 and none was introduced by the simplification.
- `git diff --check` passes. There is no V4 PCB at this checkpoint, so DRC and schematic/PCB parity are not applicable.

## Changed behavior and limits

The direct U5 output now drives `MCU3V3`; the removed MCU pre-rail and external reset supervisor no longer provide a separate reset-free hold-up path. MCU restarts during USB/main source transitions remain acceptable, while the TPS2116 output and main UPS power stage remain independent of those resets in the supported supply/load envelope. The USB buck is retained after the [bounded LDO comparison](phase3-3-usb-ldo-comparison.md). A small AP2112 package does not establish 500 mA thermal suitability; no measured ROM current justifies replacement. Neither regulator rating authorizes extra USB draw.

The divider threshold, TPS2116 switchover behavior, USB-only ROM flashing without battery/adapter, charger CE sink leakage, BQ25792 2S default-2 A risk, and main UPS behavior still require prototype measurements under the approved supply/load matrix. No PCB layout, fabrication, or power-up work was started.
