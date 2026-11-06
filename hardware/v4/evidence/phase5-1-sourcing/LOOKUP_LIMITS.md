# Phase5.1 lookup provenance and limits

All observations retrieved2026-10-19; supplier provider-cache age is a separate
field. Page stock is unreserved and may change. Phase5.0 dated observations remain
retained unless explicitly replaced by phase5_1_observations.json. No account,
cart, RFQ transmission, purchase or checkout was used for any lookup.

Fresh primary-page observations: IC1 C2876593,U8 candidate C2653623,TDK candidates
C342620/C2167399,AO3400A C20917. R5 DigiKey pages were retrievable but cached:
27k5days,8.2klastweek,13.7k2months. Their stock is historical page stock, not
confirmed current;10-piece cut-tape price tiers/MOQ1 are dated indicative terms.

TDK catalog product/status/nominal geometry and ordering FAQs were retrievable.
Exact catalog-to-TJ00E controlled-spec equivalence was not established. TDK graph
did not load; characteristic-sheet web fetch timed out and the direct download
returned403. Official LTspice bias-model ZIP downloaded but is encrypted; no
reverse engineering, execution or numeric result inferred from that file.

Murata SimSurfing current part list loaded and confirmed the22uF25V0805 family
in production. Graph/export interactions then became unresponsive. Instead,
manufacturer-authored12/2020 EC sheet hosted at TI was downloaded and rendered.
Yageo9March2023 exact spec sheet was obtained from its distributor mirror.
These are typical manufacturer data with dates explicit, not newly measured data.
The default downloader initially received403; a normal browser User-Agent allowed
the public Murata/Yageo/AOS documents. Sources are linked in compatibility review.

AOS Rev3.1July2023 and package PO-00001N downloaded from manufacturer website,
rendered and visually inspected. Poppler reported missing Symbol display font
on the main MOSFET sheet; pinout and numeric package drawings remained legible.
No package dimensions or pinout were inferred from garbled extraction alone.

Coilcraft exact manufacturer product pages retrievable; Europe no-minimum-order
policy verified. Exact stock/arrival/shipping quote was not available from these
pages. Czech Farnell cut-tape pages unavailable; Irish L3 page4months cached;
Farnell full-reel MOQ400 is not a substitute quote for5pieces. No broker listings
are used as verified exact supply. No new Mouser delivery claim was established.

TME Czech and DigiKey Czech delivery-policy pages verified. LCSC's current EU
notice is recorded as supplier policy information, not a legal determination.
Actual freight/category duties/VAT/clearance/FX and final arrival dates remain
unknown and require shipment-specific quotes. JLCPCB's already-ordered shipment
is not available for assumed combined component shipping.
