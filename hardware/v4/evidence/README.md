# Retained V4 engineering references

The owner authorized removing obsolete logs, temporary exports and scratch copies
on 2026-11-07. This directory is now a working reference collection rather than
a complete chronological session archive. Older technical reports may retain
historical paths; removed artifacts remain available in Git history. The second
cleanup pass leaves 23 engineering Markdown files here, including this index;
superseded session checkpoints and resolved STOP notes have been removed.

## What remains useful

- Manufacturer documentation and drawings in `references/`, stencil-audit
  `sources/`, and the sourcing evidence directories, including downloaded
  supplier pages, DC-bias curves and models.
- Custom calculation, review, rendering and verification scripts. Reusable
  KiCad tooling and its tests remain in [tools/](../tools/README.md); the local
  downloaded CAM dependencies remain in `phase4-24-owner-gerber-review/deps/`.
- Technical conclusions, electrical decisions and linked illustrations. Start
  with the [safety decision report](v4-safety-design-review-2026-10-11.md).
- Selected snapshots, captures, plans, candidate PCBs and accepted manifests
  used as offline regression fixtures. These are intentional tool inputs,
  not extra production designs or permission to replay historical migrations.
- The accepted Phase4.24W production result, final ERC/DRC, native/paste proofs
  and installed baseline in `phase4-24w-production-native-adoption/`.
- Sourcing inputs and final purchasing/assembly data; start with
  [sourcing/README.md](../sourcing/README.md). Supplier observations remain dated
  snapshots, not current stock or quotations.
- [First-main-power review](FIRST_MAIN_POWER_F5_REVIEW_2026-11-06.md),
  [technical notes](FIRST_MAIN_POWER_F5_TECHNICAL_NOTES_2026-11-06.md), matching
  exports and `phase1-usb-bringup/` records for the current hardware checkpoint.

## What was removed

Repeated IPC/native captures, intermediate ERC/DRC and parity reports, routing
trials, rejected/superseded scratch projects, generated CAM geometry caches,
unneeded renders, old automatic editor backups, Python bytecode, execution logs,
duplicate entry-document snapshots, obsolete checkpoints/STOP notes and old
preservation/execution summaries. The handover and toolkit README now retain
current references and useful operating instructions instead of phase diaries.
Production CAD, local libraries,
manufacturing/order data, source tools and downloaded documentation were retained.

Historical scripts may refer to deleted run outputs or preservation manifests
that intentionally included disposable copies. Restore the matching historical
context from Git if reproducing an old run; do not weaken its hash guards or run
old basket builders over the final purchasing files. Future CAD work requires
a fresh authorized context and fresh checks on the current sources.

First-pass verification: all retained files were hash-checked unchanged before
the documentation update. The offline toolkit suite ran 203 tests both before
and after that pass with identical results: 199 passed; four SDK construction
tests could not read the local `.konnect/native-ipc/kipy` package because of
environment access permissions. No new test failures were introduced.
The second pass removed documentation, unused generated figures and obsolete
execution/environment records. Retained source code, downloaded documents,
regression fixtures, production CAD/libraries and final purchasing data were
hash-checked unchanged; the test suite was not repeated for this pass. No CAD
changes, ERC/DRC rerun, firmware build or hardware validation were performed.
