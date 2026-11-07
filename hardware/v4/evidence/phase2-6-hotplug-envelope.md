# Phase 2.6 provisional hot-plug design basis

2026-10-10. Owner authorizes a technically sound provisional prototype schematic
using the phase 2.5 candidates, with procurement and physical qualification kept
separate. Adapter model and cable are **not fixed**, as explicitly confirmed by
the owner. No universal hot-plug immunity or guaranteed Cmin is required/claimed.

## Implemented circuit and component suitability

R12 = Vishay CRCW12062R00JNEAHP, 2 ohm 5%, 1206, 0.75 W; C26 = KEMET
C1210C225K1RACTU, 2.2 uF 100 V X7R 10%, 1210. Both remain **PROPOSED**,
quantity one each in all four initial VSYS assemblies. R12.1 joins VIN1 after
F1 and before the input FETs; R12.2/C26.1 is an isolated midpoint; C26.2 joins
PGND. R12 does not carry the adapter's continuous load current. This adapts the
input shunt in [TI SLUSDV2C, June 2026, Fig.8-1 p.130](https://www.ti.com/lit/ds/symlink/bq25798.pdf)
to the fused input ahead of the retained external FET pair. VBUS remains the
separate post-FET node. Layout must keep the shunt loop short at the input.

Reuse phase2-5-source-observations.md and phase2-5-hotplug-screen.json for the
Vishay 20043/28810 pulse evidence and exact KEMET curves. The 21 V ideal-step
236.84 W / 2.981 us / 0.614 mJ screen supports provisional use, not arbitrary
ringing/contact-bounce qualification. Ceff sensitivity spans roughly 1.226 uF
(assumed aging/bias/temp/tolerance margins) to 2.783 uF (reference-condition
positive tolerance/temp corner). Neither endpoint is a guaranteed operating
bound; 100 V rating provides voltage headroom, not damping proof.

Manufacturer package evidence: Vishay 20043 Rev.17-Mar-2026 p.9, 3.1 +/-0.2 x
1.6 +/-0.15 mm body, reflow lands 1.05 x 1.8 mm, 1.50 mm gap. Installed generic
R_1206_3216Metric has 1.125 x 1.75 mm pads, 1.80 mm gap; it is a standard
prototype land, not an exact copy of the Vishay recommendation. KEMET exact
sheet identifies 3.2 +/-0.3 x 2.5 +/-0.2 x 2.0 +/-0.2 mm. [C1002_X7R,
2026-09-01, Table 3 p.12](https://content.kemet.com/datasheets/KEM_C1002_X7R_SMD.pdf)
gives 1210 Level B 1.15 x 2.70 mm lands at +/-1.50 mm. Installed C_1210_3225Metric
uses the same pad size at +/-1.475 mm (0.05 mm smaller pitch). Nonpolar two-pad
maps are interchangeable; no asymmetric lead map exists. These small generic
land differences are retained provisionally; compare copper/paste/courtyard at
PCB library freeze. KEMET specifies reflow for 1210: use a controlled reflow
process for manual assembly, not an assumed wave/iron qualification.

## Dated sourcing feasibility, not an order

- Live DigiKey CZ resistor detail on 2026-10-10: exact MPN, Active (distributor
  status), stock 8219; cut tape 541-2.0UACT-ND, 1+ 7.47 CZK excluding VAT,
  10+ 4.078 CZK each. Link: <https://www.digikey.cz/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2826105>.
- Live DigiKey CZ capacitor: exact MPN, Active (distributor status), stock
  387673; cut tape 399-C1210C225K1RACTUCT-ND, 1+ 23.27 CZK excluding VAT,
  10+ 14.67 CZK each. Link: <https://www.digikey.cz/en/products/detail/kemet/C1210C225K1RACTU/1950689>.
- Supplier delivery page: 600 CZK below 1800 CZK; free delivery at/above that
  threshold. Thus one R+C is 630.74 CZK including stated delivery, **before
  any applicable VAT/other checkout charges**. This is arithmetic, not a quote.
  Ten pairs: parts 187.48 CZK plus stated delivery = 787.48 CZK before those
  charges. Consolidate with a larger order rather than approve a resistor-only
  shipment. <https://www.digikey.cz/en/help-support/delivery-information/delivery-time-and-cost>.
- Preferred LCSC capacitor identity C2168116 and its earlier same-date live
  observation remain in phase 2.5. No exact preferred-supplier resistor listing
  established in the bounded search; that is not proof of absence. DigiKey is
  a justified provisional fallback for pulse-part cut tape. Manufacturer exact
  lifecycle confirmation and total TME/LCSC split-order cost remain open.
- TME browser access was denied by permission review; no alternate access was
  attempted. Current TME price/stock/MOQ remain unverified. Manufacturer family
  documentation is current; distributor Active labels are not manufacturer
  lifecycle commitments. No purchase, supplier communication or reservation.

## Parameterized calculation and prototype gates

[ADI AN88, March 2001, pp.1-3](https://www.analog.com/media/en/technical-documentation/application-notes/an88f.pdf)
explains cable/adapter inductance and parallel RC damping. Its example inductance
is not a guaranteed range for this UPS. Our independently derived linear model
is Vs -> Rs+L -> Cin || (Rd+Cd), no load, initially discharged capacitors:

    diL/dt = (Vs - Rs*iL - VIN)/L
    dVIN/dt = (iL - (VIN-Vd)/Rd)/Cin
    dVd/dt = (VIN-Vd)/(Rd*Cd)

calculate_hotplug_rlc.py uses NumPy eigenmodes, checks KCL/KVL and energy balance,
compares a separate two-state solution against the closed-form RLC peak, and
refines worst voltage/power sampling. Output: phase2-6-hotplug-rlc.json, 144
chosen sensitivity points: L=0.1/1/10 uH; Cin=0.1/1/10/30 uF;
Cd=1.226046/2.2/2.783 uF; Rs=0.05/0.2 ohm; Rd=1.862/2.142 ohm; Vs=21 V.
These are not measured, approved source limits or a global worst-case search.
Cin is hypothetical capacitance visible during FET turn-on; the model does not
replace the actual two-node VIN1/VBUS FET circuit. It omits FET switching, clamp
behavior, capacitor nonlinearity, source control, load and contact bounce.

Maximum sampled VIN is 39.725 V; maximum resistor peak is 482.54 W and maximum
resistor energy is 1.7904 mJ (different corners). Consequently the earlier ideal
step pulse screen does **not** bound cable ringing. This is a test-plan finding,
not a measured disqualifier of either candidate or an approved operating point.
Do not claim the selected branch protects every unspecified adapter/cable.

Before any unrestricted supported-envelope use, record exact prototype revision,
BOM, cells/BMS, adapter, cable, load and ambient. Begin controlled/current-limited
bring-up; capture VIN1, VBUS, VAC1, FET VDS/VGS and resistor current with suitable
bandwidth/probe loops. Check peak/duration/repetition against charger/FET/clamp
ratings and resistor pulse curves, repeated plugging/bounce, resistor temperature
and final resistance drift. Review minimum/maximum effective capacitance and
forward-mode ripple. Revise the passive damping if evidence demands it; no
unnecessary active OVP redesign is authorized. Fuse/cable/BMS fault coordination,
CE sequencing/reset and USB partial-power qualification remain separate gates.

Cached public PDFs remain ignored. New cache SHA256:
KEMET C1002_X7R = d8e6ca6631862e31a19b90b6cfe13f1b20153c2efd6c8e30f1a5d5ba147aa908.
No new hardware measurement or firmware change/build.
