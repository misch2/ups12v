# Phase 5.4 — additional C32 stock, pending owner approval

Quick start: approve or decline **ten TDK C2012X7R1H225K125AC**, DigiKey
**445-5968-1-ND**, **USD 0.322 each / USD 3.22 goods**, on the existing DigiKey
shipment. Retain the ten approved Yageo pieces. This adds comparison stock,
with zero additional fitted positions and no CAD replacement.

| Attribute | Approved prototype purchase | Additional proposal |
|---|---|---|
| Exact MPN | Yageo CC0805KKX7R9BB225 | TDK C2012X7R1H225K125AC |
| Nominal grade | 2.2 µF ±10%, 50 V, X7R | Same |
| Existing footprint | Capacitor_SMD:C_0805_2012Metric | Same 0805 footprint |
| Body L×W×T | 2.0±0.2 × 1.25±0.2 × 1.25±0.2 mm | Same; maximum thickness 1.45 mm |
| Operating temperature | −55..125°C | Same |
| Typical Ceff at 18 V | About 0.5–0.6 µF, accepted manufacturer curve | About 1.19 µF, interpolation of exact manufacturer CSV |
| Supplier and purchase URL | [LCSC C125847](https://www.lcsc.com/product-detail/C125847.html) | [DigiKey 445-5968-1-ND](https://www.digikey.com/en/products/detail/tdk-corporation/C2012X7R1H225K125AC/2443446) |
| Order / MOQ / multiple | 10 / 5 / 5 | 10 / 1 / 1; ordinary cut tape |
| Unit / extended allowance | USD 0.1274 / USD 1.274; three-day cache | USD 0.322 / USD 3.22; last-week cache |
| Advertised stock | 105,915 | 476,200 |
| Approval | APPROVED FOR PROTOTYPE | PENDING OWNER APPROVAL |

Both parts are rated 50 V and share the same body dimensions. The reason to
compare the TDK part is its better typical biased capacitance: about 2.0–2.4
times the documented Yageo value at 18 V. No guaranteed minimum or hardware
qualification is claimed. This is evidence of an improvement, not an inference
from a higher nominal voltage rating.

The standard 0805 end-terminal body is compatible with the existing 0805 land.
TDK's characterization dimensions give end band B ≥0.20 mm and gap G ≥0.50 mm;
Yageo gives terminal length 0.25–0.75 mm and nominal gap 0.7 mm. The body and
height envelope match. No footprint or pad change is needed to purchase it.

## Manufacturer evidence and calculation

From the [exact TDK product page](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X7R1H225K125AC):
Characteristic Graph → DC Bias Characteristic → Download data as CSV. The
[saved manufacturer CSV](../evidence/phase5-4-sourcing/TDK-C32-dc-bias.csv)
names the exact MPN and was created **19 October 2026 GMT**. The points bracketing
18 V are 16 V → 1.29463 µF and 25 V → 0.827622 µF:

```text
C(18 V) ≈ 1.29463 + (18−16)/(25−16) × (0.827622−1.29463)
        ≈ 1.19085044 µF
```

This is linear interpolation, not an exported point at 18 V. About 54.13% of
nominal capacitance remains. The page describes its graphs as reference data
without a product-characteristic guarantee. No joint tolerance, temperature,
aging or ripple-current bound is inferred.

Nominal and mechanical evidence comes from the manufacturer
[characterization sheet](https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/c2012x7r1h225k125ac.pdf),
one page. Phase 5.3 recorded the 3 January 2016 sheet; Phase 5.4 re-read its
manufacturer PDF text. Direct terminal download was denied, so no local PDF is
claimed. The exported manufacturer CSV is the numeric authority. An encrypted
LTspice model was downloaded but was not run, decoded or used for this result.
Yageo's 9 March 2023 specification, page 1 dimensions and page 3 bias, remains
in evidence/phase5-1-sourcing/Yageo-CC0805KKX7R9BB225.pdf and Yageo-EC-3.png.

Supplier evidence in Phase 5.4 research-08.json contains the fetched exact
DigiKey page, product ID **2443446**. The earlier ID 2444009 was incorrect.
At the ten-piece tier the goods cost is USD 3.22, cheaper than eight at USD 4.24.
Stock is a dated cache observation, not reserved; freight, VAT and FX are extra.
Select cut tape, avoiding paid Digi-Reel service.

The accepted Phase 5.3 actual-network bring-up observations apply to either
prototype choice. No new purchasing qualification gate, electrical requirement,
power-up or design change is introduced. **STOP: additional stock awaits owner approval.**
