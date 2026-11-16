# V4 KiCad project

Open `ups12v_v4.kicad_pro` in KiCad 10. The schematic, PCB, project-local
symbols and footprint library belong to this project directory.

All seven project-local footprints are stored in **`ups_v4.pretty/`**.
The project `fp-lib-table` maps both `ups_v4` and the compatibility nickname
`easyeda2kicad` to that same directory. Existing schematic and PCB footprint
IDs therefore continue to work without replacing placed footprints.

The former sibling `hardware/v4/ups_v4.pretty/` held an older ESP32 footprint
without its 3D model and has been removed. The former
`ups_v4_external.pretty/` contents are now in the common library.

The ESP32 model is in `3dmodels/`. Molex models use `KICAD10_3DMODEL_DIR`;
the two imported footprints retain their existing `EASYEDA2KICAD` model
references, which still require that local model collection.

See the [V4 handover](../V4_HANDOVER.md) for current development status and
the [consolidation result](../evidence/library-consolidation-20261116/RESULT.md)
for preservation checks.
