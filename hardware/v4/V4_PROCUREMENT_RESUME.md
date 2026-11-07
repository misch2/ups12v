# V4 procurement observations at resume

Checked 2026-10-10. This supplements [component acceptance](V4_STAGE2_PARTS.md)
under the repository procurement rules. The final supplier policy now prefers
both TME and LCSC; the continuously maintained inventory is [V4_BOM_REVIEW.md](V4_BOM_REVIEW.md).
This file retains the dated TME-first research observations from earlier in
the session. It is not a BOM
freeze or purchase approval. The web reader returned cached TME pages; their
inventory is **UNVERIFIED for 2026-10-10**. Positive cached inventory does not
establish stock today. Prices are intentionally omitted.

## Forward ceramic candidates

Requirement: at least 35 V rating for 21 V continuous input/PMID, adequate
effective capacitance at operating bias, temperature, tolerance and aging;
manufacturer geometry accepted before a footprint change. The already reviewed
50 V X7R ceramic is an electrical prototype candidate, not a guaranteed supply
choice or a demonstrated effective-capacitance budget.

| Manufacturer / exact MPN | TME product code and verified catalog URL | Candidate comparison | Availability observation and limitation |
| --- | --- | --- | --- |
| Murata GRM32ER71H106KA12L | [GRM32ER71H106KA12L](https://www.tme.eu/en/details/grm32er71h106ka12l/mlcc-smd-capacitors/murata/) | Previously accepted 10 uF, 50 V, X7R, 10%, 1210; accepted physical map in part record. | Page retrieved 2026-10-10, marked crawled four days earlier, displayed zero stock and hardly available; current stock UNVERIFIED. Do not freeze as a routinely stocked choice without rechecking or comparing alternatives. |
| TDK C3225X7R1H106M250AC | [C3225X7R1H106MAC](https://www.tme.eu/en/details/c3225x7r1h106mac/mlcc-smd-capacitors/tdk/c3225x7r1h106m250ac/) | Catalog candidate: 10 uF, 50 V, X7R, 20%, 1210. Looser tolerance; manufacturer DC-bias/aging data and physical map not accepted here. No CAD substitution is authorized by this table alone. | Page retrieved 2026-10-10, marked crawled last month, displayed 20 pieces and minimum quantity/multiplicity 1; current stock UNVERIFIED. Other regional cached pages returned different quantities. |

The existing Murata candidate has a manufacturer reference-sheet revision and
disposable package evidence recorded in `V4_STAGE2_PARTS.md`. The TDK candidate
has only been discovered at the preferred supplier; its manufacturer reference
sheet, effective-capacitance budget and package acceptance must be completed
before selecting it. A positive cached stock count does not justify changing a
previously accepted electrical part.

## Other accepted parts

| Manufacturer / exact MPN | TME product code and verified catalog URL | Observation |
| --- | --- | --- |
| Murata GRM155R71H104KE14D | [GRM155R71H104KE14D](https://www.tme.eu/en/details/grm155r71h104ke14d/mlcc-smd-capacitors/murata/) | Cached catalog confirms 100 nF, 50 V, X7R, 10%, 0402. Retrieved 2026-10-10, crawl marked last month; positive inventory displayed, current availability UNVERIFIED. |
| Nexperia BAS116H,115 | [BAS116H.115](https://www.tme.eu/en/details/bas116h.115/smd-universal-diodes/nexperia/bas116h-115/) | Exact catalog identity verified again on 2026-10-10; source marked crawled three weeks earlier. Current availability UNVERIFIED. Manufacturer/package acceptance remains in the part record. |

## BQ25792 sourcing and manufacturer document recovery

On 2026-10-10, [TI support](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1638147/bq25792evm-bq25792-datasheet-and-question)
was accessible and states BQ25792 moved from catalog to custom, rather than EOL.
Preserve the owner's BQ25792 population requirement; do not infer small-quantity
availability from compatibility. An exact usable supply remains UNVERIFIED.

The same public TI reply links an accessible [BQ25792 manufacturer PDF](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/SLUSDG1_3D00_4_3D00_TI-PDF_3D00_en_2D00_us-_2800_2_2900_.pdf).
Its actual cover reads SLUSDG1D, April 2026, rather than the older revision
named in the handover. It carries a confidentiality marking despite being
publicly attached by TI. Keep a source link rather than rehosting the PDF.
Use its actual revision/sections when citing new checks; do not relabel earlier
Rev. C checks retroactively. Table 8-2 p. 27 confirms the documented 2 A 2S
POR charge-current risk remains. Broad register compatibility is not implied.

## Input fuse candidate comparison

Manufacturer basis: Littelfuse [451/453 series datasheet](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1),
revision printed `GD. 12/01/25`, pp. 1-4. Both candidates use the same
two-ended nonpolar 2410 body. Physical package/pad acceptance must precede CAD
footprint assignment. Their 125 V DC rating covers the adapter voltage; the
2-5 A rows specify 300 A interrupting at 32 V DC. That is a fuse rating, not a
claim about the available fault current in this UPS.

| Exact Littelfuse MPN / TME code | Verified catalog URL | Electrical comparison | Procurement |
| --- | --- | --- | --- |
| 0451004.MRL | [TME 4 A](https://www.tme.eu/en/details/0451004.mrl/smd-fuses-2410-ultra-fast/littelfuse/) | 4 A; 16 mOhm nominal cold resistance; 3.152 A2s nominal melting integral. Manufacturer 25% continuous derating permits 3 A before additional temperature derating, leaving no hot-enclosure margin at 3 A. | Retrieved 2026-10-10; crawl marked yesterday. Current availability UNVERIFIED. |
| 0451005.MRL | [TME 5 A](https://www.tme.eu/en/details/0451005.mrl/smd-fuses-2410-ultra-fast/littelfuse/) | 5 A; 12.5 mOhm nominal cold resistance; 5.566 A2s nominal melting integral. Continuous baseline 3.75 A before temperature derating; preferable prototype candidate for normal input at most 3 A. | Retrieved 2026-10-10; crawl marked yesterday. Current availability UNVERIFIED. |

These are design calculations, not measured fuse performance. Apply
`I_cont <= 0.75 * I_fuse * temperature_factor` using the manufacturer's curve
at the actual fuse temperature. Coordinate the resulting rating and opening
curve with the selected connector/cable/PCB copper and fault current. An
adapter that folds back below the fuse opening current need not blow the fuse;
neither the fuse nor a 3 A source nameplate establishes a 3 A charger current
limit. Pack fusing remains a separate protected-pack/harness requirement.

## Supported-adapter hot-plug basis

TI [BQ25798 SLUSDV2C](https://www.ti.com/lit/ds/symlink/bq25798.pdf), Rev. C,
June 2026, Figure 8-1 p. 130, shows a shunt branch comprising 2 Ohm in series
with 2.2 uF and recommends it for adapter hot-plug above 15 V. It is damping,
not active OVP. For an ideal 21 V step, the nominal capacitor energy is
`0.5 * 2.2uF * 21V^2 = 0.485mJ`, initial branch current `10.5A` and time
constant `4.4us`. Actual cable inductance, effective capacitance, pulse resistor
capability, ringing and repetitive plug events still need verification; these
calculations alone do not qualify a resistor or guarantee a clamped voltage.

The retained [AON7528 manufacturer datasheet](https://www.aosmd.com/res/data_sheets/AON7528.pdf),
Rev. 1.0 October 2023, p. 1, gives 30 V VDS and +/-20 V VGS absolute limits.
Preserving its existing gate clamp does not prove VDS margin or SOA on the
supported-adapter waveform. Record those measurements before power-stage
qualification; no excluded 25/30 V adapter protection has been added.

Before schematic freeze, identify every unresolved sourcing issue in the BOM
review. Before PCB ordering, refresh critical-part availability at TME or LCSC,
record the date/practical quantities and flag alternatives requiring footprint
changes. If neither preferred supplier has a suitable part, compare Mouser,
Farnell and DigiKey and explain any selected alternative. Keep historical
`Source`/`Bought` fields distinct from new availability evidence.
