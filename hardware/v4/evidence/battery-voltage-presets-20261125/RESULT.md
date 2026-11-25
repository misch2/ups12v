# Battery voltage presets - 2026-11-25

## Decision and scope

The owner authorized reuse of their UPS8 (`ups8_esp80`) Liitokala preset,
informed by the two sources below. Applied its voltage values to Liitokala
UPS4-7; UPS8 already contains them and was left as edited by the owner:

- `battery.approx80PercentCapacity_mV = 3955` (per cell).
- `battery.approx20PercentCapacityUnderMaxLoad_mV = 3300` (per cell).

Existing charging-current requests, battery current ceilings, capacities and
other profile settings were preserved. These are owner-selected approximate
presets, not new hardware measurements or a verified SOC estimator.

GeB UPS1-3 retain their existing 3920 mV/cell APPROX_80 target and default
0/unconfigured warning. The owner requested a similar GeB preset only if suitable
data could be found. No matching voltage-versus-capacity curve was found in the
reviewed GeB documents or targeted searches; no numerical 20% threshold was
invented from capacity, nominal voltage, storage voltage or discharge cutoff.

## Source review

### Panasonic/SANYO NCR18650B

- [Owner-supplied manufacturer datasheet mirror](https://passionelectronique.fr/wp-content/uploads/NCR18650B_datasheet.pdf?pseSrc=pgAlimUsb18650v2).
- Version **13.11 R1**, one page, copyright 2012 SANYO Energy (U.S.A.).
- Saved as `ncr18650b.pdf`; rendered page `ncr18650b.png` inspected visually.
- Bottom-right **Discharge Characteristics (by rate of discharge)** plots
  voltage versus discharged capacity at 25 C, at 0.2C, 0.5C, 1C and 2C,
  after CC/CV charge at 4.2 V, with a 2.50 V discharge cutoff. The bottom-left
  graph illustrates temperature dependence at 1C.
- These graphs provide relevant under-load context, but do not prescribe
  3.300 V as a universal 20% SOC warning. The preset's application to fitted
  Liitokala cells follows the owner's instruction, not independent confirmation
  of their manufacturer, exact discharge curve or actual maximum UPS load.

### Surducan and Bruj, Batteries 2023, 9(4), 214

- [Article](https://www.mdpi.com/2313-0105/9/4/214),
  DOI [10.3390/batteries9040214](https://doi.org/10.3390/batteries9040214),
  published **2023-04-01**. Saved as `batteries-09-00214.pdf`.
- Section **2.1**, page 2: SOC characterization at 21 C, 1C discharge,
  10% steps and 30-minute rest between steps; limits 4.15 V and 2.5 V.
- Section **3.1**, **Table 2**, page 5 (rendered and inspected in
  `paper-table2.png`): 80% SOC OCV = **3.955 V**. At 20% the table gives
  OCV = **3.511 V** and end-of-step loaded voltage = **3.05 V**.
- Consequently, this table supports the provenance of the owner's 3955 mV
  value, but does not directly supply the chosen 3300 mV warning. OCV and
  in-circuit loaded voltage differ. An OCV point also does not prove that a
  CC/CV charging limit achieves exactly that SOC.

### GeB 18650, 3.7 V / 3200 mAh

- [Manufacturer specification via LaskaKit](https://www.laskakit.cz/user/related_files/geb_18650_3-7v_3200mah_-_datasheet.pdf).
- **Revision A**, cover dated **2018-07-04**, revision-history first issue
  **2018-07-30**. Saved as `geb18650-3200mah.pdf`; all nine pages visually
  reviewed in `geb18650-3200mah-overview.png`.
- Section **3**, page 4: capacity test at 0.2C to **2.75 V**, charge voltage
  4.2 V, standard discharge 1C, maximum continuous discharge 1.5C.
- Section **4.1**, page 5: performance tests specify charging/discharging
  procedures and minimum discharge time, not voltage at 20% remaining charge.
- There are no charge/discharge voltage-versus-capacity graphs in this document.
  The 2.75 V endpoint cannot be used as a 20% threshold.
- Also checked the [GeB 3S 3200 mAh pack specification, A0, 2022-10-20](https://www.laskakit.cz/user/related_files/datasheet-geb18650_11-1v3200mah_18650_3s1p.pdf)
  and the [GeB 3000 mAh cell specification, revision A](https://www.laskakit.cz/user/related_files/geb_18650_3_7v_3000mah_-_datasheet.pdf).
  Neither supplied a usable curve for the configured 3200 mAh cells. Different
  capacities or pack-level cutoffs were not treated as equivalent cell SOC data.

## Validation boundary

Focused profile diffs and `git diff --check` reviewed. Shared warning/MQTT
implementation is unchanged by this preset follow-up. No firmware builds or
uploads, charger-register writes, MQTT publications or battery discharge tests
were performed. Actual warning timing and remaining runtime under the owner's
maximum load remain hardware checks.

## Downloaded source SHA256

| File | SHA256 |
| --- | --- |
| `ncr18650b.pdf` | `E18E569AC94FD1E01C6BA96BAE63EE91F81A3549172410A176B5E19D12062825` |
| `batteries-09-00214.pdf` | `A59E64A21BB5B7E836640450369DEC9DC0545F1D53260E10AA70A182F328355C` |
| `geb18650-3200mah.pdf` | `B63C80C60173D93B1C3E2B85005406CA1FF6412FBFE046581D0DB2D48918BBC2` |
