# Nano-Fit connector selection for owner review

2026-10-11. Status: **OWNER APPROVED for bounded CAD replacement only.**
Owner explicitly approved every header/housing pair, numbered pin assignment and two 1053002100 terminals per harness below, with proposed 20 AWG wire. This is not fabrication, purchasing or harness qualification approval. CAD replacement is pending the manufacturer-footprint/tooling blocker in [replacement preflight](nanofit-replacement-preflight.md); production CAD remains unchanged. J4/J6 remain JST-XH. J8 remains DNP in F0. No general routing is authorized.

## Recommended set

All parts are Molex Nano-Fit 2.50 mm, single-row, right-angle THT headers with tin mating contacts. Each assembled cable uses two female tin terminals **1053002100**, 20–22 AWG; propose **20 AWG stranded copper UL1061** for every power harness, including the short J3-to-XT30 cable. Exact wire construction/MPN and finished harness qualification remain open.

| Ref / function | PCB header, qty 1 | Mating housing, qty 1 per harness | Mechanical identity | Proposed numbered pin assignment | Population |
|---|---|---|---|---|---|
| J1 adapter | **1053131102** | **1053071202** | 2 positions, black / key A | 1 PGND; 2 adapter positive (existing Net-(J1-Pin_2)) | All variants |
| J2 VSYS | **1053131103** | **1053071203** | 3 positions, black / key A | 1 PGND; 2 NC; 3 SYS | All variants |
| J3 battery | **1053132102** | **1053072202** | 2 positions, natural / key B | 1 PGND; 2 BATTERY | All variants; short cable to XT30, no PCB XT30 |
| J8 optional 5 V | **1053132103** | **1053072203** | 3 positions, natural / key B | 1 PGND; 2 NC; 3 F5_5V_OUT | F5 only; DNP in F0 |

Terminal count: six in the three mandatory harnesses; eight with F5. The middle PCB contact remains physically present on each 3-position header but has no net or copper connection; its mating housing cavity has **no crimp terminal or wire**. Positive and negative conductors each carry the full load. No contacts are paralleled.

Pin assignments above are owner approved, not current CAD. Exported Phase3.7 netlist has J1/J2/J3 ground on pin1 and positive on pin2; J8 currently has positive on pin1 and ground on pin2. J2 and J8 therefore require an explicit symbol/pin-net update as well as footprint changes, followed by fresh ERC/netlist/parity checks. Manufacturer numbered mating views govern harness assembly; do not infer pin numbering from a front/back photograph.

## Mismating and alternatives

Molex's [Nano-Fit FAQ](https://www.content.molex.com/dxresources/93f0/93f0a0be-dcf0-4354-95a0-5a7c41e2d59e.pdf), slide6, explicitly describes color-dependent mechanical keying: black and natural do not cross-mate. [Header drawing SD-105313-100](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/105/105313/1053131104_sd.pdf), Rev J1, 2025-06-26, sheets2–4, identifies key A/B and the 2/3-position variants. Thus this proposal combines two actual keys with two shrouded circuit counts, rather than relying on labels or paint.

Expected normal full-mating matrix is diagonal: J1 cable to J1; J2 to J2; J3 to J3; J8 to J8. Opposite-color pairs have incompatible keys; same-color J1/J2 and J3/J8 differ in shroud length/circuit count. The outer-position power assignment on 3-position parts adds electrical protection against partial/offset 2-position insertion: a 2-position connector has 2.50mm conductor spacing, while the 3-position harness has 5.00mm spacing. Neither can complete both power conductors through an offset insertion into the other. This is a geometric analysis, **not a measured sample abuse/forced-insertion test**. Verify all twelve wrong pairings unpowered with samples, including partial insertion and latch behavior, before using assembled cables.

Four identical 2-position headers fail interchange prevention. Black/natural alone gives only two identities. Four different counts (2/3/4/5) are possible but consume more edge width and offer no need to parallel pins. Dual-row 4-position parts and larger single-row alternatives were considered; the selected 2/3 arrangement minimizes disturbance. Gold plating is not a key and must not be mated to these tin parts. BMI is a separate mating system and unnecessary here.

## Current assessment and limits

Calculations use current V4_REQUIREMENTS R03–R06: 90% downstream conversion efficiency, 1.5W shared auxiliary reserve, loaded pack minimum 6.4V/12.8V. These are planning assumptions, not measured efficiency or an exact worst-case guarantee.

| Ref | Approved-profile load calculation / known bound | Selection assessment |
|---|---|---|
| J1 | Normal input target ≤3.0A; possible actual input must stay ≤3.3A including positive limit tolerance and any lower source/assembly limit | 2-position / 20AWG reference 8A; qualify at actual input bound |
| J2 | 4S external12V/3A: 40W at SYS, thus 40/12.8 = 3.125A at connector before path loss; 1.5W onboard reserve does not pass through J2. Optional5V shares total budget. Battery-fed SYS is not automatically limited to the converter's 5A recommendation | 3-position / 20AWG fully-loaded reference 7.75A (interpolated); no claim that converter current is a J2 protection limit |
| J3 | 2S approved5V/2A: (10/0.9+1.5)/6.4 = **1.971A** before battery-path loss. 4S installation: (36/0.9+1.5)/12.8 = **3.242A** before loss. Charge target ≤0.5A; BQ25792 reset may restore2A | 2-position natural retains 8A reference with20AWG. Charge and discharge are opposite directions; do not add their magnitudes as simultaneous cable current |
| J8 | 5V/2A output target; converter input current is not J8 output current | 3-position /20AWG reference7.75A; F0 DNP |

**2S warning relevant to connector selection:** applying the 36W installation load to 2S would require 41.5/6.4 = **6.484A before losses**, already above the charger's6A continuous discharge recommendation. This is not an approved 2S profile. Adding simultaneous independent output maxima is likewise not approved. There is no unconditional connector current bound from the external VSYS connector alone; actual load, pack sag, inrush, fuse/BMS and wiring define it.

[BQ25798 SLUSDV2C](https://www.ti.com/lit/ds/symlink/bq25798.pdf), Rev C June2026 §6.3, and [BQ25792 SLUSDG1C](https://www.ti.com/lit/ds/symlink/bq25792.pdf), Rev C August2022 §8.3, specify6A continuous RMS battery discharge and10A peak for up to1s. These are IC operating constraints, not enforced cable limits. The selected J2/J3 assemblies have reference continuous-current headroom to6A; **10A pulse suitability and fault-clearing energy are not established by an8A rating**. Existing pack/fuse/BMS and load qualification remain necessary; no new protection stage or arbitrary trip threshold is proposed.

[Molex PS-105300-100](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/105/105300/PS-105300-100-001.pdf), Rev J6 2025-09-26 §4.2–4.4:20AWG reference ratings are8A for2-position and7.75A for3-position; the latter is interpolated. Test basis is fully loaded circuits,30°C rise, applicable also to tin. Derating depends on wire, PCB copper, enclosure ambient and nearby heat. These are guidelines, not assembly qualification. §2.3 agency recognition lists4A; do not claim an8A agency-certified assembly.

[Molex AS-105300-100](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationspecificationspdf/105/105300/AS-105300-100-001.pdf), Rev D1 2025-01-22 §4, prohibits current sharing and tin/gold cross-mating. Mate/unmate de-energized. [Tooling ATS-6382756HM](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/638/63827/ATS-6382756HM-001.pdf), Rev C 2023-07-10 pp1–2, includes1053002100 and20AWG UL1061 using638275600. Check the exact wire OD and crimp profile against the ATS; thick generic20AWG silicone wire is not automatically compatible. Inspect crimp dimensions, retention and polarity; qualify temperature/voltage drop with the actual header/housing/contact/wire/XT30 chain, current and transient duration, enclosure ambient and neighboring heat recorded. No hardware measurement was performed.

## Orderable parts and supplier observations

Checked2026-10-11 through browser-retrieved supplier pages. Displayed stock/prices may be cached; **not an inventory reservation or checkout quote**. USD figures exclude shipping/tax unless the supplier says otherwise. Konnect catalog tool was available but returned database-not-found; no cache download was required. Preferred suppliers were searched first; DigiKey fallback fills missing/unstocked preferred-source entries.

| MPN | Verified supplier link/code | Displayed small-order terms / availability |
|---|---|---|
|1053131102|[DigiKey WM16893-ND](https://www.digikey.com/en/products/detail/molex/1053131102/7693174); TME MX-105313-1102 catalog listing|DigiKey26,470; MOQ1; USD1.03. TME indexed listing0/no price; no usable LCSC listing found |
|1053071202|[LCSC C505029](https://www.lcsc.com/product-detail/C505029.html)|12,540; MOQ/multiple5; USD0.2355 at5 |
|1053131103|[DigiKey WM16894-ND](https://www.digikey.com/en/products/detail/molex/1053131103/7693175); [LCSC/JLC identity C561764](https://jlcpcb.com/partdetail/MOLEX-1053131103/C561764)|DigiKey5,659; MOQ1; USD5.16. JLC listing8 atUSD3.1394, but **loose LCSC order availability not confirmed**; assembly availability is not selection authority |
|1053071203|[TME MX-105307-1203](https://www.tme.eu/en/details/mx-105307-1203/raster-signal-connectors-2-50mm/molex/105307-1203/); [DigiKey WM14959-ND](https://www.digikey.com/en/products/detail/molex/1053071203/6131601)|TME657; MOQ/multiple1; USD0.39 at1. DigiKey25,469; MOQ1; USD0.41 |
|1053132102|[LCSC C17189968](https://www.lcsc.com/product-detail/C17189968.html); [TME1053132102-MOL](https://www.tme.eu/en/details/1053132102-mol/raster-signal-connectors-2-50mm/molex/105313-2102/)|LCSC indexed3; MOQ1; USD1.0579. Direct page retrieval failed; stock freshness uncertain. TME0/custom-order/no price |
|1053072202|[LCSC C17689101](https://www.lcsc.com/product-detail/housings-wire-to-board-wire-to-wire_molex-1053072202_C17689101.html)|Indexed585; MOQ/multiple5; USD0.3261 at5. Direct short-URL retrieval failed; stock freshness uncertain |
|1053132103|[DigiKey WM16901-ND](https://www.digikey.com/en/products/detail/molex/1053132103/7693182)|459; MOQ1; USD1.26. No usable TME/LCSC listing found |
|1053072203|[DigiKey WM15016-ND](https://www.digikey.com/en/products/detail/molex/1053072203/6164105)|44,902; MOQ1; USD0.48. No usable TME/LCSC listing found |
|1053002100, two/harness|[LCSC C505323](https://www.lcsc.com/product-detail/C505323.html); [TME MX-105300-2100](https://www.tme.com/us/en-us/details/mx-105300-2100/other-connectors-molex/molex/105300-2100/)|LCSC6,430; MOQ/multiple10; USD0.0636 at10. TME0/MOQ15,000, unsuitable for prototype |

Manufacturer sources: [105313 header series](https://www.molex.com/en-us/products/series-chart/105313), [105307 housings](https://www.molex.com/en-us/products/series-chart/105307), [105300 terminals](https://www.molex.com/en-us/products/series-chart/105300), header drawing above; [natural3-position packaging/mate confirmation](https://www.molex.com/zh-cn/products/part-detail/1053132503) identifies tray1053132103 and housing1053072203. All selected header numbers are listed in SD-105313-100. Tray/reel packaging alternatives preserving geometry/key/plating can be reviewed without changing the connector scheme:1053131503 is Molex's packaging alternative to1053131103, but DigiKey regular MOQ1,800 makes it unattractive here.

For one F5 prototype, DigiKey headers J1/J2/J8 plus J8 housing totalUSD7.93; adding J2 housing there givesUSD8.34 and avoids a separate TME shipment. LCSC J3 header + five each of2-position housings + ten terminals adds approximatelyUSD4.50: total **USD12.84 before shipping/tax**, based on mixed retrieval snapshots. Recheck actual stock and delivered basket cost; alternatively consolidate at DigiKey if extra LCSC shipping exceeds savings. No order or basket was placed.

## CAD scope after approval

Use installed KiCad10 footprints `Connector_Molex:Molex_Nano-Fit_105313-xx02_1x02_P2.50mm_Horizontal` forJ1/J3 and `Connector_Molex:Molex_Nano-Fit_105313-xx03_1x03_P2.50mm_Horizontal` forJ2/J8. Presence verified by filename; pad/hole/locator geometry comparison with RevJ1 is **pending**, not claimed complete. Black/natural use the common manufacturer's land-pattern dimensions for a given count. Header body widths are5.94mm/8.44mm; keep mating housing, latch access, bend radius and strain relief outside the existing top edge. Retain current cable-row order and face all four outward toward the same edge; exact coordinates/orientation require CAD verification.

After approval, use Konnect only: verify exact live board path, replace affected symbols/footprints and local copper, preserve switching-loop checkpoint geometry and unrelated routing, retain J8 F0 DNP. Run affected ERC/DRC, connectivity/parity and focused diff. Do not resume general routing. Baseline CAD SHA256 values are stored in `nanofit-selection-cad-baseline.json`; this selection milestone changes documentation only. No ERC/DRC rerun or firmware build is appropriate for unchanged CAD/firmware.

Full manufacturer PDF downloads were attempted, including an elevated retry after sandbox DNS failure; the remote host closed the connection. No downloaded PDF is claimed. Browser-readable source links/revisions and extracted observations are preserved here.
