# Phase 5.4 evidence boundary

19 October 2026. Read-only public supplier/manufacturer research; no supplier
messages, RFQs, cart, checkout, order, allocation or reservation. No CAD/native
KiCad, manufacturing, firmware or hardware operations. Branch retained.

- research-01..25.json preserve full web-tool text responses, including provider
  cache ages and failed regional fetches. Decode JSON strings to read the text.
- refresh-P*.json, refresh-R5-2S.json and refresh-H*.json preserve all 66
  electronics and eight exact harness refresh attempts, with input row identities.
  refresh-ledger.json is a parser ledger before manual review, not final authority.
- sourcing/phase5_4_observations.json is the reviewed overlay, including the
  German USD D3/D4 page, conservative conflicting C8 terms, D1 exact cut-tape SKU,
  unusable L3 supply and R32's indexed EU EUR allowance. Public/cached data is not
  promoted to a firm quote. Failed fetches and older caches are retained.
- LIVE_COILCRAFT_CHECK.md records UK/EUR quantity-five observations for both
  exact inductors. Blank stock after setting five prevents an allocation claim.
  The newer DigiKey unavailable page overrides the older indexed stock offer.
- TDK-C32-dc-bias.csv was exported through the exact manufacturer product page's
  CSV button. The interpolation is independently recomputed in C32-interpolation.json.
  The encrypted LTspice model was not used or reverse engineered.
- Konnect's exact catalog lookup was attempted for C74210; the local database
  was unavailable. No download, catalog availability claim or CAD operation followed.

Entry snapshots preserve preceding uncommitted sourcing, BOM and handover work.
protected-before.json captures 196 existing CAD/library/manufacturing hashes;
config-before.sha256 protects the unrelated .codex/config.toml content. Final
verification checks the same files, exact identities, quantities, currency math,
population, alternative separation and optional price tiers. No firmware build,
ERC or DRC is needed for these documentary procurement changes.

The active CSV's quoted_*_native fields are authoritative for native currency.
Legacy *_usd fields intentionally leave R32 blank rather than inventing FX.
The C32 alternative remains separate from the 66-line master and approved basket.
