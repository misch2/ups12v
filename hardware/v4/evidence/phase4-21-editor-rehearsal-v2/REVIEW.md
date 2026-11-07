# Phase4.21 rehearsal — verifier false positive; preserve stopped scratch

2026-10-18. **Production unchanged; adoption incomplete.**

**Resolved later in the same milestone:** the agent archived and normally closed
its own known scratch through strict live-state and source-preservation guards.
No owner cleanup was required. This context was not reused as a candidate.
Fresh rehearsal-v3 and production adoption subsequently passed in full; see
[final adoption](../phase4-21-production-adoption/ADOPTION.md). The pending-state
notes below are the preserved historical diagnosis, not an outstanding action.

The owner explicitly approved resuming after both historical endpoint failures
and closed all existing KiCad instances. A fresh OS inspection found zero
editors/pipes. Source-identity-v3 then bound the newly launched production editor
PID56728, exact board path and currently observed pipe. Its complete saved/live
preflight PASSED against the accepted Phase4.18 manifest. The clean source editor
was normally closed with guarded lifecycle checks. No production write occurred.

Fresh production-derived owning-editor rehearsal-v2 (PID13084) passed the same
OS PID/document/endpoint guard and saved/live preflight. It executed one native
commit removing exactly the three approved old CC2 UUIDs and creating exactly
the three Phase4.20 target UUIDs. Returned objects matched expected payloads.

## Normal validation false positive, not a CAD/native failure

The post-commit verifier incorrectly called `native_capture` on the whole capture
instead of separately on its sections, unlike the established F5 implementation.
The extra dictionary level prevented the existing normalization of each item's
runtime board-parent link. The three created tracks acquire that link when they
enter the board; CRUD returned objects had omitted it. No geometry or retained
object difference exists. [Exact three differences](post-commit-diagnostic.json).

Export-only diagnosis proves full per-section native equality, preserving every
other payload. Regression tests prove width changes and unexpected child fields
are still rejected; the actual captured three-track geometry is covered by a
second regression. The correction changes verification only. No native
assertion, connection failure or real geometry/connectivity failure occurred
in this rehearsal. [Disposition](validation-disposition.json).

The conservative worker wrapper nevertheless wrote [STOP.json](STOP.json).
This context will not be retried or reused. No refill or save followed the
rejection; the editor contains only the agent's exact three unsaved scratch
replacements. The existing lifecycle helper refuses dirty or stopped targets.
The owner has therefore been asked to close this scratch editor **without
saving**. No programmatic discard, recovery, restart, repeated transaction or
production overwrite was attempted.

After the owner closes it, use another fresh production-derived owning-editor
rehearsal under the corrected immutable implementation. Only its complete
independent geometry/fill/ERC/DRC/parity/connectivity/vendor proof authorizes
the already owner-approved production transaction. Final production verification
is still required. Do not count accepted Phase4.20 evidence as installation.

All four accepted production hashes and approved candidate hash remain unchanged.
Production PCB:
`4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84`.
Owner-fixed nominal thickness1.6mm; stackup, copper weights, barrel plating and
fabrication parameters remain UNSELECTED. No BOM, schematic, footprint, rule,
firmware, manufacturing, purchase, hardware power-up, commit or push changes.
