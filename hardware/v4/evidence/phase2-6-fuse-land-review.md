# F1 manufacturer land comparison

2026-10-10; 5 A Littelfuse 0451005.MRL preserved, BOM **PROPOSED**.
[Manufacturer 451/453 GD.12/01/25 p.4](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1)
gives body 6.10 +/-0.20 x 2.69 +/-0.25 mm and recommended pad layout:
outer span 6.86 mm (0.270 inch), pad 1.96 x 3.15 mm (0.077 x 0.124 inch),
inner gap 2.95 mm (0.116 inch). Rounded metric figures differ by 0.01 mm when
summed. Use the internally consistent inch dimensions: pad 1.9558 x 3.1496 mm,
outer span 6.858 mm, gap 2.9464 mm, centres +/-2.4511 mm, pitch 4.9022 mm.

Original assumed lands: 2.20 x 2.20 mm, centres +/-2.25 mm. Corrected through
Konnect create_footprint; body nominal preserved, courtyard regenerated from
pad/body envelope with 0.25 mm clearance. No real PCB footprint was placed or
updated. Existing project table and footprint name preserved.

Current PDF text was accessible through web retrieval; direct manufacturer
downloads returned HTTP 403. A [historical manufacturer PDF mirrored by
Fuse-Tech](https://www.fuse-tech.com/uploads/pdf/littelfuse0451.pdf), copyright
2009, p.4/printed p.60, was downloaded solely to inspect drawing orientation.
Its land dimensions agree with the current manufacturer text. Do not transfer
its older electrical/solder-profile specifications into the current design.
Cache SHA256 e4f66814c90d70b283a5962080711f26554d974373a550958bda772dfdaf1bf9.
The cached PDF/page PNG are ignored; this record retains provenance.

## Nonpolar physical map and verification

Top/component view; two interchangeable metal end caps, no functional polarity
or manufacturer electrical pin-one direction. Project numbering is explicit:

| Physical cap | Symbol | Footprint pad / local centre | Circuit role |
| --- | --- | --- | --- |
| Left end | Device:Fuse F1.1 passive | 1 / (-2.4511, 0) mm | VIN1, downstream fused input |
| Right end | Device:Fuse F1.2 passive | 2 / (+2.4511, 0) mm | ADAPTER_RAW, J1.2 |

Two physical caps, two symbol pins, two electrical pads; no exposed/duplicate or
mechanical pads. A swap of this nonpolar fuse's caps does not change function.
Query-back with include_pads/include_graphics is saved in
phase2-6-fuse-readback.json. Disposable placement at (30,30) mm under
../.validation/phase2-6/fuse-check was performed through Konnect's closed-file
fallback, not live IPC. SVG and detail PNG were inspected: two broad rectangular
lands, separate copper, body/courtyard and arbitrary pad-one marker agree with
the nonpolar map. The instance pad-query tool returned 'F1 not found' despite
the rendered footprint and DRC reporting F1; error saved in
phase2-6-fuse-instance.json. The component-list tool required IPC. A targeted
read-only instance-file inspection independently confirmed both local pad
coordinates/sizes and placement; this limitation is not concealed as a live
readback pass.

Disposable DRC: one error **invalid_outline**, one warning **extra_footprint**;
the fixture intentionally has no board outline and its blank schematic has no
F1. Full report phase2-6-fuse-drc.json. No pad/courtyard/silkscreen violation
was reported. This is **not a clean real-board DRC or schematic/PCB parity**.
There is still no real V4 PCB. Real-board DRC/parity remain mandatory later.

Package/land comparison is complete for the provisional schematic library;
manufactured fit, solder process, fuse temperature, interrupt/fault current,
cable/BMS coordination and hot-plug I2t remain prototype/release gates.
