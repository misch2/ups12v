# Engineering rules

- Reliability and electrical correctness take priority over size, cost and appearance. Preserve proven circuits unless evidence justifies a change.
- Preserve production V2/V3 hardware and existing installations. Develop new revisions in their own directory and branch; preserve unrelated edits and local credentials.
- V4 uses exactly one physical PCB with explicit BOM/population variants. Keep detailed specifications and decisions in [hardware/v4](hardware/v4/V4_REQUIREMENTS.md), not here.
- Use KiCad 10 and Konnect as the primary interface for live schematic/PCB changes. When Konnect cannot represent a required operation, check supported native KiCad tools/APIs before treating it as a manual-owner blocker. Never hand-edit serialized KiCad design/library files.
- Justify electrical changes with manufacturer datasheets/reference designs, recording revision, section and assumptions. Distinguish exported evidence, calculations and hardware measurements.
- After each coherent CAD modification, run ERC/DRC as applicable to the affected schematic/PCB, verify connectivity/parity and inspect the diff. Both ERC and DRC are mandatory before design release; passing checks alone does not establish electrical or thermal correctness.
- Validate power changes on matching hardware, recording BOM/revision, cells, source, load, ambient and logs. Build affected firmware environments; documentation-only changes need no firmware build.
- Follow existing code conventions and `.clang-format`. Keep changes focused, credentials local, and generated caches/backups out of commits.
- Respect the authorized phase boundary. Present architecture and electrical changes for review at the specified milestones before proceeding.

### KiCad CAD editing and native APIs

- Native KiCad 10 Python bindings (`pcbnew`) are allowed for focused, authorized changes to **project-local footprint libraries**, including non-circular drills and other geometry unsupported by Konnect. Prefer supported application APIs over ad-hoc text/S-expression patches or approximate substitute geometry.
- Use the installed KiCad version and verify API availability before modifying anything. Save through KiCad APIs, reload the result and compare the intended geometry with the manufacturer's current drawing; explicitly check pad numbers, drill shapes/sizes/positions, copper pads and unrelated geometry.
- Do not use standalone scripts to overwrite a schematic or PCB currently open/locked in KiCad. For live-board changes use Konnect or a coordinated native KiCad workflow; if safe synchronization/replacement is unavailable, stop and request the smallest necessary owner action.
- Preserve project-local library links and existing placed-footprint connectivity. After an authorized footprint replacement, verify schematic/PCB parity, affected routing and copper fills, ERC/DRC and the focused diff. Do not silently broaden the authorized CAD scope.

### Requirements authority and simplicity

- Latest explicit owner decisions govern; reconcile older conflicting requirements before continuing. Do not invent mandatory product requirements, protection thresholds, acceptance gates or failure scenarios without owner approval.
- Distinguish datasheet constraints and demonstrated hazards from optional robustness improvements. Prefer the simplest reliable circuit that meets approved requirements.
- Before adding a supervisor, latch, watchdog, protection IC, large hold-up capacitor or gating stage, document the failure prevented, its probability/relevance and why existing circuitry or firmware is insufficient. Propose optional enhancements for review instead of implementing them automatically.
- Keep sourcing and theoretical corner-case research proportionate to the prototype milestone. Preserve rigorous checks for genuine electrical hazards, battery safety, component limits and prohibited back-power paths.

### Component selection, sourcing and BOM tracking

**Preferred procurement approach for Czech small-volume prototypes: compare Mouser CZ and TME.eu first, and use the lowest qualified *delivered* BOM cost, not the lowest catalog unit prices.** Farnell and DigiKey are additional qualified alternatives. LCSC is an exception, not a default: use it only when a documented landed-cost comparison shows a worthwhile advantage or an essential part is otherwise unavailable, and obtain owner approval for the import-risk trade-off.

This is a small-volume hobby project, typically five bare PCBs from JLCPCB, manually assembled. Fabricated PCB quantity is not necessarily the number of boards to populate immediately. Plan sourcing for the actual intended populated quantity, optional BOM variants, sensible assembly spares and the expected number of prototype revisions.

When selecting or replacing components:

1. Prioritize electrical suitability, safety, reliability, correct package/footprint, manufacturer documentation and practical solderability. Never silently downgrade a safety-critical specification to save money.
2. **At schematic-design time**, check stocked, low-MOQ options from Mouser CZ and TME, including footprint-compatible alternatives where technically acceptable. Prefer common, actively manufactured components with more than one viable distributor/MPN where possible. Do not let a single inexpensive LCSC-listed part needlessly lock in a unique footprint.
3. Assess total **landed cost for the planned build quantity**, not unit price: actual order quantities versus usage, MOQ and price-break waste, spares, shipping, VAT where not already included, customs duty and EU import charges where applicable, broker/courier fees, currency-conversion fees, and separate orders. Count VAT exactly once; distinguish taxes from additional costs. Check shipping/incoterms (DDP versus import-on-delivery) for the *selected checkout method*, not merely the distributor's home page. Mouser is not assumed to ship from within the EU.
4. For imports from outside the EU, **explicitly evaluate per-declaration-line charges** for a diverse electronics BOM, not just the invoice value. Do not assume LCSC and JLCPCB orders can be consolidated or that any courier will waive customs processing.
5. Compare at least a practical **Mouser/TME-first basket** against the proposed alternative basket (e.g., LCSC plus EU supplements), including full prototype PCB manufacturing/delivery where relevant. If exact live cart prices are unavailable, label estimates and uncertainty; never invent availability, import terms or prices.
6. Before freezing footprint-dependent choices, identify expensive or hard-to-source items and propose electrically qualified alternative MPNs/footprints for owner approval. Do this before layout and PCB fabrication, when corrections are still cheap.
7. Record current supplier URL/code, manufacturer MPN, stock, MOQ, verified date, currency, net/gross treatment and any incompatible substitutions. Use available official catalogs/APIs; product listings are not confirmed checkout totals.
8. If no economical qualified option exists, present the trade-off and request owner direction instead of proceeding silently. Distinguish a genuine component-safety blocker from a supplier/price preference.

### V4 BOM review and mandatory procurement checkpoints

Maintain **`hardware/v4/V4_BOM_REVIEW.md`** continuously throughout schematic design and PCB development.

For each selected component or group of interchangeable passives, track:

- KiCad reference designator(s), role, exact manufacturer and MPN, value/tolerance/ratings and package/footprint.
- Quantity per populated PCB and quantity for each applicable F0/F5 BOM variant; DNP status.
- Actual planned purchasing quantity including spares/MOQ, unit price/price breaks, source, stock and verification date.
- Mouser CZ and TME links/codes when found, plus relevant Farnell/DigiKey/LCSC offers and qualified alternatives.
- BOM approval status (`PROPOSED`, `VERIFIED`, `APPROVED`, `REPLACE`) and explicitly unresolved sourcing risks.

Update the BOM when components, values, footprints, quantities or purchasing assumptions change. Preserve previously verified information but do not treat old stock/prices as current.

**Two review gates are mandatory for each materially new PCB revision:**

1. **Early schematic/footprint gate:** present a rough but complete cost range for the intended build, including bare PCB manufacturing, shipping and populated-quantity estimates. Identify high-cost parts, foreign-source risks and substitution options; invite owner review **before footprint choices become expensive to change**.
2. **Pre-order gate:** before approving PCB manufacture or parts purchase, present a dated, quantity-specific **landed-cost BOM** with at least Mouser/TME-first versus any proposed non-EU sourcing plan, shipping/incoterms, VAT/customs/fees (or clearly marked uncertainty), grand total in CZK, approximate cost per assembled board **without batteries** and battery/extras separately. Flag any material cost increase from the early estimate and require explicit owner approval of the total budget. Neither an ERC/DRC pass nor an MPN inventory alone satisfies this gate.

Do not select components based solely on JLCPCB assembly-library availability; hand assembly is intended. Do not purchase parts, order fabrication or authorize a sourcing exception merely because an engineering milestone is otherwise complete.

### Context efficiency and milestone execution

Keep Codex sessions focused and minimize unnecessary context consumption.

- Read `AGENTS.md` and `hardware/v4/V4_HANDOVER.md` first. Load other project documents only when relevant to the current task.
- Do not repeatedly read full requirements, architecture, audit, BOM or handover documents unless they have changed or the task specifically requires their complete contents.
- Prefer targeted file searches and line ranges over reading entire large files.
- Keep full netlists, ERC/DRC reports, CAD exports, datasheets and diagnostic JSON in repository evidence files. Return concise summaries, relevant violations and file references to the conversation.
- Avoid dumping complete XML, JSON, KiCad S-expressions, or large command outputs into the context when a targeted query or script can extract the required facts.
- Reuse existing verified evidence instead of repeating expensive analyses without a specific reason.
- Work on one small, well-defined milestone at a time.
- Before starting a substantially different task, finish the current checkpoint, update `V4_HANDOVER.md` and recommend a fresh session.
- If context compaction occurs, check the current task state and handover before proceeding. Do not repeat completed CAD changes or verification work unnecessarily.

Never reduce the quality of electrical verification merely to save tokens. Store complete evidence on disk while keeping conversational output concise.

### Reusable tools and proportionate checks

- Do not add tests that inspect source text, assert implementation spelling or statement order, or extract function bodies from source into generated test harnesses. The owner explicitly rejected this kind of source-code test. Use proportionate behavioral tests of production modules where useful; do not recreate the removed source-check tooling.
- Keep reusable V4 tools in `hardware/v4/tools/` with a short capability description and usage example; retain snapshots and generated reports in `hardware/v4/evidence/`.
- Batch relevant validation after a coherent change. Do not repeat full schematic/netlist/PCB verification after every small step. Use Git history and focused diffs for comparison; metadata-only cleanup needs proportionate checks. Preserve relevant electrical verification and release requirements.
- When the owner requests a comparison against a commit or tag, report a concise list of differences and run ERC/DRC. This is a requested checkpoint, not an automatic action after every edit.

### Firmware register telemetry (updated 2026-11-11)

- `software/ups/src/UPS.ino` enumerates the BQ25798 library's static setting definitions through `SETTINGS_COUNT` and `getSetting(i)`; the chip supplies register values, not the list of settings.
- `publishHAConfigurations()` derives retained MQTT discovery from setting names, types and units. BOOL settings become binary sensors (excluding read-cleared flags); ENUM settings get enum and numeric sensors, plus a binary entity for range 0-1; other numeric settings become sensors. Discovery is republished after MQTT reconnect.
- `software/ups/include/telemetry_policy.h` explicitly selects register telemetry: core measurements/states refresh after 60 seconds; useful configuration/limiting/fault values publish only initially, after discovery/reconnect/recovery and on change. MPPT/VOC, interrupt masks/flags and other excluded registers have no discovery/state publications; old excluded discovery is removed. Selected enum numeric/binary views keep their existing IDs/topics.
- Defining `DEBUG_BQ25798_SETTINGS` exposes all library settings, including sampled read-cleared flags. Additional debug entities publish on change only; the core refresh policy is unchanged. Without the flag, the production allowlist applies and debug-only discovery is removed. Debug telemetry does not change charger configuration; flag samples are not guaranteed interrupt event history.
- Owner's Grafana series remain production-visible and periodic, including DIS_ACDRV, EN_ACDRV1, TS_ADC and VINDPM_STAT. The three names esp_internal_chip_temperature, internal_chip_temperature and ts_zone_numeric are owner-confirmed Grafana templates/older definitions, not current firmware sensors. See the firmware README for the coverage boundary.
- While the charger is ready, `trackChanges()` processes values every 5 seconds. Payload changes are compared with the last successful send, with retries after failure; the former 10% previous-sample threshold is removed. There is no time jitter. Only periodic entities use HA `force_update` and 300-second expiry; change-only states do not expire. States are retained for HA restart. Battery percent publishes whole-percent payloads and suggests zero decimal places. Discovery topics are `homeassistant/<component>/<device>/<config_key>/config`; state topics are `bq25798ups/<device>/state/<state_key>`.
- ENUM sensors use `_enum` for discovery keys, unique IDs and state topic keys, with `device_class: enum` and deduplicated `options` from `Setting::strings_vector`; omit `state_class` and units. Former retained `text` discovery is deleted on republication. Numeric and binary representations remain separate.
- Register discovery uses BQ25798 v1.5.1 `getHomeAssistantInfo(i)` for category, icon and applicable device/state classes; null metadata is omitted. Enum label sensors retain `device_class: enum`; their numeric/binary views retain generic device classes. Binary sensors omit state class/units and unsupported legacy `status`/`control` classes. Units still come from `Setting::unit`, with `degC` normalized to `°C`. Additional manually defined sensors set their own metadata.

### Live UPS debugging over MQTT (verified 2026-11-10)

- Prefer fetching MQTT telemetry directly from this computer when the owner asks to debug the UPS; do not require copying values into chat. Python and `paho-mqtt` 1.6.1 were available at verification time; recheck tooling and broker reachability as needed.
- Read connection settings from the local `.codex/mqtt-credentials.txt` file (`host`, `port`, `username`, `password`). This file is excluded in `.gitignore`. Never print credentials, put them in command-line arguments, or copy them into documentation, evidence or commits. Read the configured endpoint rather than hard-coding it; preserve TLS verification when TLS is configured.
- UPS4 state subscription: `bq25798ups/esp76-bq25798-ups4/state/#`. MQTT uses `#` for all descendant topics and `+` for one level; `*` is not an MQTT wildcard. Keep subscriptions scoped to the requested device/topics.
- Debugging access is read-only: connect and subscribe without publishing, sending commands or changing UPS settings unless separately authorized. Use a unique client ID to avoid displacing another client.
- For snapshots or bounded traces, record receive timestamps and distinguish retained messages from newly received updates. Allow at least 65 seconds when checking for updates because the default telemetry refresh is 60 seconds. A retained value is not proof of current device health; an accepted subscription with no data is not proof that the UPS is online. Check power, connectivity and the device/topic name before diagnosing a broker fault.
- The connection test on 2026-11-10 received 299 live messages across 286 state topics during a 65-second subscription after the owner powered on UPS4 without a battery. These are historical test results, not current readings or validation of charging/battery operation. Ask for or confirm the actual battery, source and load configuration when interpreting new measurements.
- Collect and analyze during active debugging sessions. For recording between sessions, use a standalone logger and inspect its saved trace later; do not imply continuous agent monitoring. Save requested traces under `hardware/v4/evidence/` and keep chat summaries compact. Serial logs complement MQTT for resets and WiFi/MQTT outages.

### Tool-output discipline

Keep tool outputs extremely compact.

- Do not dump full KiCad schematic files, PCB files, XML netlists, JSON diagnostics, rendered BOMs, or long command outputs into the chat.
- Save full artifacts to files under `hardware/v4/evidence/` and report only concise summaries.
- Never use `Get-Content` on large files unless restricted to a small range or a specific search result.
- Prefer summaries such as counts, hashes, key violations, changed nets, or changed references.
- For Git, prefer `git diff --stat`, focused file diffs, or specific hunks instead of full diffs.
- For ERC/DRC, report totals and only the relevant violations.
- For connectivity checks, report only intended changes and unexpected mismatches.
- Do not enumerate tool inventories (`ALL_TOOLS`, full MCP tool lists, etc.) unless explicitly debugging tool availability.
- Do not render or attach images to the conversation unless visual inspection is essential for the current checkpoint. Prefer a short textual summary plus the saved file path.
- Keep each tool call narrowly scoped. Avoid combining many unrelated checks in one `exec` call.

Preserve full evidence on disk, but keep conversational output minimal.
