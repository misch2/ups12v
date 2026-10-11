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

**Preferred suppliers: TME.eu and LCSC.com.**

This is a small-volume hobby project. PCBs will likely be manufactured by JLCPCB without assembly. Loose components may be ordered from LCSC and, where economically practical, shipped together with the JLCPCB order.

When selecting or replacing components:

1. Prioritize electrical suitability, reliability, correct packaging and manufacturer documentation.
2. Prefer exact MPNs readily available from **TME.eu or LCSC.com** in small quantities.
3. Compare price, minimum order quantity, stock availability and potential shipping costs. Optimize for the total cost of a small prototype order, not just individual component prices.
4. Prefer common, actively manufactured components. Avoid obsolete, NRND, obscure or unnecessarily expensive parts when suitable alternatives exist.
5. Use Konnect's component-catalog tools for LCSC discovery when available. Use TME's website or official API for TME verification when accessible.
6. Never invent product URLs, stock quantities, prices or confirmed availability. Record verification date and source.
7. If neither preferred supplier has a suitable component, consider Mouser, Farnell or DigiKey and document the reason.
8. Verify exact manufacturer MPN, package, footprint and relevant electrical specifications before committing to a final schematic choice.

### V4 BOM review

Maintain **`hardware/v4/V4_BOM_REVIEW.md`** continuously throughout schematic design and PCB development.

For each selected component or group of interchangeable passive components, track:

- KiCad reference designator(s) and functional description.
- Exact manufacturer and MPN.
- Quantity per assembled PCB.
- Package and KiCad footprint.
- TME product URL/code, if available.
- LCSC product URL/code, if available.
- Unit price, currency, minimum order quantity and availability, when verified.
- Verification date and source.
- Alternative compatible components.
- Applicable BOM variants and DNP status.
- Approval status: `PROPOSED`, `VERIFIED`, `APPROVED`, or `REPLACE`.

Update this file whenever components are added, removed, replaced or their values/footprints change. Preserve existing valid procurement information from the KiCad project.

Do not select a component based solely on JLCPCB assembly-library availability, since **manual assembly using separately purchased components** is intended.

Before schematic freeze, identify all unresolved sourcing issues. Before ordering PCBs, review the complete BOM, confirm critical component availability and flag any parts whose footprints may need changing.

Prefer a practical combination of TME and LCSC purchases over forcing all components to come from one supplier.

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
