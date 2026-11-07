# Proposed Phase4.19 — final PCB cleanup and prototype pre-fabrication review

2026-10-18. **Proposal only; not executed or authorized by Phase4.18.**

Start from accepted production SHA256
`4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84`.
The board is fully routed with0physical/parity/ERC errors. F5 prototype-level
geometry and its existing electrical/thermal qualifications are accepted; this
proposal does not reopen F5, USB or IC1 routing optimization.

Suggested single bounded milestone:

1. Read-only review of remaining warning identities and currently ignored checks,
   silkscreen/reference readability, connector polarity/rail labels, F0/F5 assembly
   markings, testpoint access, mask/paste openings, courtyards and mechanical fit.
   Distinguish actual fabrication defects from deliberate library differences.
2. Reconcile the final prototype fabrication stackup/copper/plating and supplier
   fabrication limits with the design model; review critical MPN/footprint/BOM,
   connector/harness and population uncertainties. Verify sourcing information if
   needed, without ordering anything. Do not turn prototype thermal qualifications
   into fictitious proven failures or demand repeated copper optimization.
3. Propose an exact small cleanup whitelist only where evidence justifies it.
   Preferred scope is markings/references/documentation; any copper, footprint,
   component, rule/waiver or electrical change requires an explicit owner decision.
   Do not install the deferred legacy cleanup automatically.
4. For subsequently authorized CAD edits, use an isolated candidate and proportional
   preservation checks, then one complete ERC/DRC/parity/connectivity milestone
   review. Deliver a concise unresolved-item list and an owner-reviewed prototype
   fabrication decision, retaining the matching-hardware qualification plan.

No cleanup, CAD modifications, Gerber/drill/assembly/manufacturing export,
fabrication order, purchase or hardware power-up is included in this proposal.
Those actions need separate authorization. Recommend a fresh session after owner
review of the Phase4.18 checkpoint.
