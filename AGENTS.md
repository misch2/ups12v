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

- Keep reusable tools in `tools/` with a short capability description and usage example; retain snapshots and generated reports in `hardware/v4/evidence/`.
- Batch relevant validation after a coherent change. Do not repeat full schematic/netlist/PCB verification after every small step. Use Git history and focused diffs for comparison; metadata-only cleanup needs proportionate checks. Preserve relevant electrical verification and release requirements.
- When the owner requests a comparison against a commit or tag, report a concise list of differences and run ERC/DRC. This is a requested checkpoint, not an automatic action after every edit.

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
