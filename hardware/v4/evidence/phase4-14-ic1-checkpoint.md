# Phase4.14 — IC1 add-only completion blocked

2026-10-17. **0/3 connections completed; no production CAD modification.**
Owner accepts Phase4.13. Only IC1.14 I2C_SCL, IC1.21 ~INT and IC1.1 STAT
were in scope. No F5 or USB work was performed.

## Quick start — smallest useful owner-assisted comparison

Open the [fresh production-derived scratch project](phase4-14-owner-walkaround/ups12v_v4.kicad_pro)
in KiCad10, keeping the original production document untouched. Use native
Walk Around with collision enforcement, normal rules and existing sizes;
disable automatic redundant-track removal. Do not use Shove, drag existing
copper, update footprints/netlists or alter rules. Inspect F.Cu, B.Cu and In2.Cu
together before selecting any through-via; keep In1 as PGND.

Try SCL south around CE_N/SDA first, INT outward around BATTERY/PROG second,
STAT west/north on F.Cu third. Starting from the existing destination branch
and changing posture can help native routing. Stop if existing copper must
move. Save only this scratch and return its path for independent checks before
any production integration. No automatic route has been installed here.

## Verified entry and preservation

- Production PCB SHA256:
  `75060f4b3d0f57e65f2c6e4736f3dc32d42e62e359541671b1ffce63eceb7014`.
- All four files match the [accepted Phase4.13 manifest](phase4-13-production-adoption/accepted-installed-baseline.json).
- [Fresh isolated native context](phase4-14-entry-native/routing-context.json)
  is bound to that exact PCB and its rules/project hashes.
- [Read-only native live preflight](phase4-14-entry-live/preflight.json) PASS
  via the already proven socket. Konnect supplied only saved-file evidence;
  it was not treated as a live confirmation.
- No production CAD transaction, refill/save, physical geometry or net change.
  Protected IC1/L1 loops, power paths, PGND fill, pad connections, all8arcs,
  USB and F5 reservations therefore retain the accepted checkpoint evidence.
- Accepted validation is reused: DRC44unconnected/0physical/0parity/16warnings;
  ERC0errors/4warnings. No fresh ERC/DRC run is claimed. An unchanged design
  does not need another whole-board representation-identity exercise.

## Focused obstruction confirmation

The [current geometry comparison and three exact rechecks](phase4-14-local-revalidation.json)
use the toolkit's arc-aware physical copper/drill inventory and joint plan
validator. All525 shapes in x54–66/y60–72mm are unchanged from the previous
IC1 study; all electrical rule values also match. Its bounded negative search
can therefore be reused. Each of its three smallest sampled obstruction sets
was checked once against the current native context and again rejected before
any native CAD mutation. These are local obstructions, not a proof that every
possible add-only route is impossible.

| Signal | Exact technical obstacle | Focused next option |
|---|---|---|
| IC1.14 I2C_SCL `(60.6,67.9)` | South: CE_N crosses y68.6 and SDA/C9 constrain the exit. Inward local via `(60.3,67.2)` collides with SW2 via `34ef7035-7ee6-4bf4-8517-a71adf6b073d` and tracks `5e9bf709-65ea-4128-98f0-9f89d3376c6f`, `8bf5e035-e88a-4a69-8afa-132cf4b0ebd6`. | Native south F.Cu Walk Around toward the existing R21.2/U6.2/J4.4 island. If blocked, a separately designed CE_N/SDA fanout replacement is preferable to disturbing SW2; no complete replacement is yet validated. |
| IC1.21 ~INT `(61.9,65.6)` | East: BATTERY via `(63.1,65.5)`,0.70/0.40mm, leaves about0.115mm to the PROG copper edge;0.13mm track plus two0.10mm clearances needs0.33mm. Sampled via `(62.6,65.4)` hits that battery via and four attached F/In2 tracks. | Native F.Cu Walk Around preserving BATTERY/PROG, toward R28.2 `(69.51,74)` and its existing transition `(69.81,74.3)`. No validated one-track remedy is established. |
| IC1.1 STAT `(58.1,64.4)` | West: VBUS/C2 fanout; north: PMID/SW1. Early via `(58.2,64.3)` overlaps B.Cu SW1 tracks `0ddad28b-e59e-4c39-9824-0548b73dfcd2` and `97c7f73b-0a21-49fb-8598-4d436a77abd9`, both1.50mm wide. | Stay on F.Cu west/north until a genuinely all-layer-clear via site is found, then connect D2.1 `(42.3625,86.8)`. Do not cut SW1 to clear a STAT via. |

The [earlier detailed owner guide](phase4-10-ic1-owner-guide.md) retains exact
additional blocker UUIDs, geometry diagrams and negative candidates. Its old
production hash/scratch are historical; use the new manifest/context/scratch
above. No extensive dogbone/grid search was repeated. No safe unattended native
Walk Around backend was established, and no equivalent capability is claimed.

## Checkpoint and phase boundary

[Machine checkpoint](phase4-14-checkpoint.json). Remaining:3IC1 F0 +41F5 =44opens.
AGENTS.md gains the requested concise risk-proportionate principle. Native
assertion, IPC instability, uncertain transaction and real physical/net mismatch
STOP rules remain intact. No such event occurred in this phase.

No production replacement is proposed as ready for approval: the sampled power
obstruction deletions would need complete electrical reconstruction. The owner
scratch comparison is the smallest useful next action. **STOP for owner review;
do not begin F5.** No BOM, architecture, rules, firmware, manufacturing, purchase,
power-up, commit or push changes.
