# One stencil, two variants — exact reference-level covering plan

2026-10-18. Applies to the **original audited GTP**, SHA-bound in the final evidence. The four-pad proposal does not remove variant/DNP apertures.

F0 blocks **53 Gerber object regions on 18 F5-only SMT references** plus 8 regions on the four always-DNP capacitors. Because Q10 drain regions merge, those are 57 actual connected apertures in total. F5 enables all F5 SMT apertures and blocks only the 8 always-DNP capacitor apertures. All 19 F5 references are accounted for; **J8 is through-hole and has zero paste**. The four always-DNP references C20/C22/C24/C25 each have two real apertures; they are not already suppressed.

Other intentionally unfitted PCB features H1–H4, NT1/NT2/NT4, TP5–TP8 and TP13–TP17 have **no GTP apertures**. They need no tape. SMT NC terminals on fitted components (for example U1) remain pasted as component terminations; they are not DNP components. PTH connectors/test loops require their separate hand-soldering process; do not infer paste from their exposed copper/mask. J7 has zero paste, including its shell pads.

Use thin removable tape on the **paste-application side**, adhesive over the openings. Clean/dry the stencil, seat tape flat and verify no edge overlaps an aperture that must stay open. Do not tape the board side or create stacked thickness that prevents a flat print. Place/cut tape before positioning the stencil over the board; do not cut against PCB lands. The existing alignment fixture is retained; actual tape tack, removal residue and squeegee behavior need a first-print check.

The rectangles below are **Xmin/Ymin/Xmax/Ymax in original PCB millimetres, top coordinate view, Y down**, each 0.10 mm outside the outermost paste bounds of that reference. They cover the complete reference, including the space between its pads. They are relative to the aperture layout, not an assumed origin on JLC's 120×120 mm sheet. Rounded display values are to 4 decimals; [exact CSV](final-v2/variant-mask-plan.csv) and [JSON](final-v2/stencil-audit.json) retain full bounds. All 22 rectangles were screened against **every other** aperture, including other currently masked references: zero overlaps; minimum residual clearance 0.450 mm. This supports individually cut patches and leaves room at every active neighbor. A large blanket patch across several references was not geometrically verified.

| Ref | Paste pads / object regions | F0 | F5 | Cover Xmin / Ymin / Xmax / Ymax (mm) | Clearance to other apertures (mm) |
|---|---|---|---|---|---|
| U7 | 1,2,3,4,5,6,7,8 / 8 | BLOCK | OPEN | 100.8250 / 58.0000 / 103.1750 / 60.0000 | 0.550 |
| U8 | 1,2,3,4,5,6 / 6 | BLOCK | OPEN | 115.2000 / 57.1500 / 119.0000 / 59.8500 | 0.925 |
| Q10 | 1,2,3,4,5,6,7,8,9 / 9 | BLOCK | OPEN | 111.6750 / 54.6400 / 114.3250 / 58.3850 | 0.975 |
| L3 | 1,2 / 2 | BLOCK | OPEN | 102.6550 / 61.7500 / 107.3450 / 66.6500 | 1.025 |
| R60 | 1,2 / 2 | BLOCK | OPEN | 104.1750 / 54.4250 / 106.8250 / 55.5750 | 0.950 |
| R61 | 1,2 / 2 | BLOCK | OPEN | 104.1750 / 56.4250 / 106.8250 / 57.5750 | 0.700 |
| R62 | 1,2 / 2 | BLOCK | OPEN | 97.4250 / 53.6750 / 98.5750 / 56.3250 | 0.550 |
| R63 | 1,2 / 2 | BLOCK | OPEN | 97.4250 / 50.5750 / 98.5750 / 53.2250 | 0.550 |
| C60 | 1,2 / 2 | BLOCK | OPEN | 95.0500 / 57.3500 / 97.9500 / 61.6500 | 0.600 |
| C61 | 1,2 / 2 | BLOCK | OPEN | 95.0500 / 62.1500 / 97.9500 / 66.4500 | 0.600 |
| C62 | 1,2 / 2 | BLOCK | OPEN | 103.7250 / 58.1750 / 104.8750 / 60.8250 | 0.650 |
| C63 | 1,2 / 2 | BLOCK | OPEN | 107.1750 / 57.9250 / 109.8250 / 59.0750 | 0.450 |
| C64 | 1,2 / 2 | BLOCK | OPEN | 108.5000 / 61.6000 / 110.5000 / 65.9000 | 1.125 |
| C65 | 1,2 / 2 | BLOCK | OPEN | 112.0000 / 61.6000 / 114.0000 / 65.9000 | 1.455 |
| C66 | 1,2 / 2 | BLOCK | OPEN | 108.6750 / 59.4250 / 111.3250 / 60.5750 | 0.450 |
| C67 | 1,2 / 2 | BLOCK | OPEN | 116.4250 / 60.6750 / 117.5750 / 63.3250 | 0.925 |
| C68 | 1,2 / 2 | BLOCK | OPEN | 111.6750 / 51.9250 / 114.3250 / 53.0750 | 1.665 |
| C69 | 1,2 / 2 | BLOCK | OPEN | 99.2250 / 58.1750 / 100.3750 / 60.8250 | 0.550 |
| J8 | none / 0 | NO PASTE ALREADY | NO PASTE ALREADY | none | n/a |
| C20 | 1,2 / 2 | BLOCK | BLOCK | 45.3950 / 47.9000 / 48.6050 / 56.9000 | 0.750 |
| C22 | 1,2 / 2 | BLOCK | BLOCK | 39.3950 / 52.5000 / 42.6050 / 61.5000 | 1.345 |
| C24 | 1,2 / 2 | BLOCK | BLOCK | 36.1000 / 64.9000 / 37.9000 / 73.5000 | 1.061 |
| C25 | 1,2 / 2 | BLOCK | BLOCK | 37.9000 / 76.7000 / 39.7000 / 85.3000 | 1.121 |
