# UPS V4 — Phase 4.13: reconciliation complete, editor rehearsal STOP

2026-10-17. **Production synchronization was not performed.** The full isolated
editor rehearsal failed its post-transaction net-preservation check. No complete
validated candidate or new accepted production checkpoint exists.

## Nejjednodušší postup vlastníka

1. Otevřený **zkušební PCB editor zavřít bez uložení**. Jeho jediný spuštěný
   dokument je `phase4-13-editor-rehearsal/ups12v_v4.kicad_pcb`, nikoli produkce.
   Živá zkušební transakce je nevyhovující; nepřenášet ji do produkce.
2. V KiCad 10 otevřít [izolovaný projekt](../phase4-13-editor-rehearsal/ups12v_v4.kicad_pro),
   jeho schéma a PCB. Uložený PCB je stále přesná původní produkce; pouze v tomto
   izolovaném schématu už jsou přidané `USB_MCU_DP` a `USB_MCU_DN`.
3. V tomto zkušebním PCB použít nativní **F8 / Update PCB from Schematic**.
   Očekávanou elektrickou změnou jsou pouze názvy sítí R48.1↔U1.27 a
   R49.1↔U1.26. Neprovádět náhradu footprintů ani ruční routing. Pokud dialog
   navrhne jiné elektrické změny, zastavit a předat jeho výpis.
4. Zkušební PCB uložit, editory zavřít a potvrdit dokončení. Následuje nezávislé
   ověření této **izolované** změny a nová úplná zkouška migrace v čerstvé kopii.
   Produkci během tohoto postupu neměnit.

Tento postup řeší konkrétní neprokázané přejmenování sítí nativním editorem.
F8 zde dosud nebylo spuštěné; jeho výsledek není předem označen za ověřený.
Nejde o žádost o další optimalizaci USB. Nový pokus nesmí opakovat již změněnou
živou zkušební transakci ani pracovat s ní jako s přijatou baseline.

## Authorization and source authority

The owner's Phase4.13 request accepts the current USB geometry and its documented
prototype limitations. This supersedes the earlier requirement to decide the
Phase4.11/4.12 USB qualifications. No further USB optimization, ESD-ground change,
pair tuning, IC1 escape or F5 routing was attempted.

Production PCB SHA256 remains
`6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80`.
Owner PCB SHA256 remains
`55fe96f32e8e440996924239dd1409f84cb0ffc27cb30c7ea48c7e6c02f610f5`.
All four files in each original project, and the accepted manifest, remain
hash-identical. Project and custom-rule files are identical between the originals.
No locks were present initially. An out-of-sandbox Windows process/CIM check
found no KiCad editor processes before the agent launched its isolated editor.
The previous owner confirmation that saved sources were current remains
consistent with these exact hashes.

The accepted manifest is still
`phase4-10-independent-ipc/accepted-installed-baseline.json`; it was neither
edited nor promoted. The fresh native read-only production snapshot matches
the exact accepted control. The original owner evidence was reused only after
rechecking all its source bindings; no failed intermediate source was used.

## Complete migration inventory

| Native objects | Added | Removed | Modified retained UUID |
|---|---:|---:|---:|
| Straight tracks and native arcs | 134 | 51 | 3 |
| Vias | 6 | 2 | 1 |
| Footprints | 0 | 0 | 3 |
| Pads | 0 | 0 | 10 |

The owner has 1027 track/arc objects, including **eight actual PCB_ARC objects**,
287 vias, 154 footprints and 473 pads. All source-to-target UUID mappings,
complete original/desired native preimages and exact removals are recorded in
[migration-whitelist.json](migration-whitelist.json). No arc was flattened.
The two removed EN/BOOT vias have exact same-geometry/same-net replacements with
new owner UUIDs; these are explicitly mapped rather than duplicated.

Moved footprint centers, mm, unchanged rotations:

| Ref | Production | Approved owner |
|---|---|---|
| C28 | (120.000,87.400) | (114.074,77.978) |
| U2 | (113.800,78.500) | (115.000,81.400) |
| R48 | (96.000,88.000) | (96.000,91.440) |

The functional PCB delta spans USB_DP/DN, both MCU-side USB nets, PGND,
USB_VBUS/USB3V3, SYS, VIN1, MAIN_3V3, MCU3V3, D1-A and C26's pad1 net. U2's
placement, signal fanout and PGND attachment are coupled; R48's placement is
coupled to its resistor-separated USB route; C28 and its PGND via are coupled
to the VBUS reroute and retained U4 input network. They form one complete
mapped migration, not independent additive batches. No historical R35/C26/SYS
proposal was applied on top of owner copper.

All routed geometry on SYS, VIN1, MAIN_3V3, MCU3V3, D1-A, C26 pad1 and USB3V3
is exactly equal to the independently reviewed Phase4.11 owner geometry.
That review's non-USB clearance, cross-section and protected-loop evidence
therefore remains applicable to the exact current original source. Latest
Phase4.12 confirmation also preserves IC1/L1/U3 local In1 grids, all other
native artwork/rules and the restored EN/BOOT connections. These are CAD/export
results and sampled fill comparisons, not hardware or thermal measurements.

The complete structural comparison separates routed/placed changes from
two owner tuning-generator records, refreshed field UUIDs, cached pin/no-connect
and library-filter metadata, presentation defaults and a collinear schematic
wire merge. The proposed minimum migration retains production metadata and
wire segmentation. It requires independent equality of finished native copper,
pad connectivity and schematic partitions before treating omitted owner tuning
records as harmless. That final candidate proof has **not** completed.

## Schematic rehearsal — equivalent exported topology

Konnect added exactly two local labels at `(436.88,134.62)` and
`(436.88,132.08)` in the isolated production-derived schematic. Its exported
XML matches the verified owner **all 104 net partitions and all 154 component
properties**, including the two new names; no net partition was added/deleted.
Only label objects differ structurally from the production schematic.
Source-to-rehearsal label UUIDs may differ, while production identity and all
pre-existing schematic objects remain retained.

The resistor-separated partitions remain the intended ones: connector D+
J7.A6/B6–U2.1–R48.2, MCU D+ R48.1–U1.27; connector D− J7.A7/B7–U2.2–R49.2,
MCU D− R49.1–U1.26. No schematic resistor bypass or polarity change occurred.

See [schematic-equivalence.json](../phase4-13-editor-rehearsal/schematic-equivalence.json)
and [scratch-schematic-delta.json](../phase4-13-editor-rehearsal/scratch-schematic-delta.json).
All34 local labels have explicit source/target UUID maps in
[schematic-label-UUID-mapping.json](../phase4-13-editor-rehearsal/schematic-label-UUID-mapping.json).
Complete native original-source fill polygons with holes are retained in
[source-copper-fill-delta.json](../phase4-13-editor-rehearsal/source-copper-fill-delta.json);
zone definitions are structurally unchanged. These are original-source fill
inventories, not a post-migration candidate refill.

## Supported interface investigation and exact failure

Installed KiCad is 10.0.7. Konnect tools are available, but its configured IPC
socket is absent. The existing project SDK supplies native Track/ArcTrack/Via,
footprint translation, item CRUD, commit/readback, refill and editor save.
The agent launched **only the isolated copy**, PID109024, using the existing
enabled KiCad API. Its actual named pipe is `\\.\pipe\.tmp\kicad\api.sock`,
addressed as `ipc://.tmp/kicad/api.sock`. No KiCad/Konnect settings were changed.

The first read-only preflight identified only C37/L2 footprint-item ordering.
Complete item-payload multisets were independently identical, and all pads,
tracks, vias, zones, drawings and texts matched. A narrowly scoped order-only
normalization, with a geometry-change negative test, allowed preflight to pass.
Both original and reconciled logs remain saved. This was a normal validation
failure, not an assertion or transport failure.

One mapped scratch transaction then returned all requested created/updated UUIDs
and was pushed. The resulting live readback has the intended object counts and
the eight native arcs, but **does not have the intended net assignments**:

| Pad | Requested and returned by UpdateItems | Observed after commit |
|---|---|---|
| R49.1 | `/USB_MCU_DN` | `Net-(U1-USB_D-_{slash}_GPIO18)` |
| U1.27 | `/USB_MCU_DP` | `Net-(U1-USB_D+_{slash}_GPIO19)` |
| U1.26 | `/USB_MCU_DN` | `Net-(U1-USB_D-_{slash}_GPIO18)` |

Additionally **25 D− track/arc objects and two D− vias** read back under the old
MCU D− name. The three individual pad-update responses themselves contain the
requested new names; their response is therefore insufficient as persistence
proof. The point at which KiCad reassigns them is not yet isolated. This report
does not claim a universal KiCad bug or that all supported workflows must fail.

Other differences are default enum/padstack fields on newly constructed items.
They have not been normalized away. Actual saved-board copper/drill, netclass,
fill, pad-island and full candidate checks were consequently not reached.

The [official IPC documentation](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/index.html)
describes the running-editor interface. Installed SDK source and observed
10.0.7 responses are the authority for this specific rehearsal; newer online
development documentation is not proof of installed behavior.

## STOP state and validation limits

The user explicitly requires: “If ... preservation failure occurs, STOP
immediately without automatic retry, recovery, rollback or editor restart.”
The agent stopped the scratch workflow at that check. There was **no native
assertion or IPC transport failure**. No retry of this transaction, rollback,
refill, save, editor restart/close or further KiCad operation followed it.
Only already-captured JSON and original file hashes were inspected afterward.

The rehearsal editor remains open with the unaccepted transaction in memory.
The saved rehearsal PCB is still the exact accepted production byte-copy.
Its schematic contains only the two supported Konnect label additions.
Do not treat either live rehearsal or its old saved PCB as a completed candidate.

Existing original-owner verification remains 44 opens (3 IC1 +41 F5),
0 physical DRC errors, 0 parity findings, ERC0 errors; warnings20/11 in the
matched isolated library context. These are reused verified-source results,
**not post-migration candidate or production validation**. No ERC/DRC/parity or
473-pad candidate PASS is claimed after this failed transaction.

Production PCB, schematic, project, rules, all owner originals and accepted
manifest remain unchanged. No BOM, architecture, stackup, rule, firmware,
fabrication, purchase, hardware power-up, commit or push change occurred.
No IC1/F5 next-phase proposal is issued because production adoption did not pass.

Offline toolkit validation: the85 existing tests and8 focused migration tests
pass. The added STOP-guard test proves rejection before any IPC/context access.
Whitespace validation passes. No firmware build is applicable to this stopped
CAD/tooling checkpoint.

Full observed/prepared payloads, returned items, commit ID, exact net differences
and final preservation hashes are in
[STOP-diagnosis.json](../phase4-13-editor-rehearsal/STOP-diagnosis.json),
[readback-delta.json](../phase4-13-editor-rehearsal/readback-delta.json),
[ipc-apply.log](../phase4-13-editor-rehearsal/ipc-apply.log).
