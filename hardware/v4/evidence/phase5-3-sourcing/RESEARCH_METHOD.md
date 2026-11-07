# Phase5.3 evidence and validation boundary

2026-10-19. Public manufacturer/distributor research only, plus one read-only
Coilcraft browser lookup. No supplier messages, RFQs, cart, order or reservation.
Konnect catalog search was attempted for exact L3/C32: the local database was
unavailable, so no catalog availability claims are based on it and no database
download or CAD operation was performed.

research-01..27.json contain full web-tool responses as JSON string values;
decode the string to read the original response, cache ages and failed fetches.
Search-result stock from substitutes was never used as stock of a retained MPN.
Reviewed new fields are in sourcing/phase5_3_observations.json. Other lines retain
preceding dated observations and are not represented as newly refreshed stock.

TDK-C1-update-2023.pdf is the downloaded manufacturer-authored document from
Future Electronics' archive. Pages1/12 were rendered with bundled pypdfium2 and
visually inspected: author/date and exact catalog-to-TDK mapping verified.
TDK-page1.png and TDK-page12.png are read-only evidence, not CAD renders.
The C32 TDK characterization PDF was readable through the web tool, but direct
local download returned403; no local numerical graph extraction is claimed.
The retained Yageo curve/network analysis and Murata/FET reviews were reused.
coilcraft-live-check.txt records selected UK/EUR M/E/C configuration, quantity5,
visible price and missing stock signal. No AddToCart action occurred.

Entry sourcing and two active project-document snapshots were taken before
mutation. All196 accepted protected CAD/library/manufacturing hashes matched
at entry and final verification. The unrelated .codex/config.toml hash matches
entry. Historical Phase4.22A population files are read-only inputs. Authoritative
and actual assembly counts remain separately auditable in the active CSV.

Reproduction, from repository root:

1. `python -B hardware/v4/sourcing/build_purchasing_bom.py --n-f0 0 --n-f5 5`
2. `python -B hardware/v4/sourcing/write_sourcing_reports.py`
3. `python -B hardware/v4/evidence/phase5-3-sourcing/verify_phase5_3.py`

The independent checker covers all154references, source/assembly overrides,
six five-board splits, groups, R5 and IC1, exact owner promotions, proposal
exclusion, MOQ/spare/excess/cost arithmetic, supplier-checklist parity, unchanged
harness, protected hashes and unrelated config. It does not assert capacitor
minimum guarantees, hardware qualification, supplier allocation or full quotes.
Firmware builds and ERC/DRC were not repeated because this checkpoint changes
only documentary purchasing data and reporting code, with CAD hashes unchanged.

**STOP for owner review before purchases.**
