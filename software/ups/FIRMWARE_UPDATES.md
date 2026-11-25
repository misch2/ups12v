# Home Assistant firmware updates

The agreed design uses a standard MQTT Update entity: the UPS checks a public
manifest at boot and periodically, reports installed/latest compatible versions,
and installs only after an explicit request. Home Assistant handles Install/Skip
and remembers skipped versions. No automatic installation is planned.

Implementation is split into three checkpoints:

1. **Release pipeline and manifest: implemented.**
2. **Device HTTPS checker/downloader: implemented.** Checks at boot and every six
   hours; validates TLS, hardware identity, actual inactive-slot capacity, image
   length and SHA-256. The worker downloads independently of the power-service
   loop, preserves NVS, and reserves installation against concurrent updates or
   configuration/reset operations. See [service details](FIRMWARE_UPDATE_SERVICE.md).
3. **HA Update entity and web update controls: not implemented yet.** Both use the
   same update service. Existing telemetry and controls keep their identities.

This does not reinstate the intentionally skipped operating-settings controls.
Existing installations need one bootstrap upload containing the eventual updater;
only subsequent updates can be installed through HA.

## Release workflow

[`.github/workflows/firmware-release.yml`](../../.github/workflows/firmware-release.yml)
runs packaging tests and all three hardware builds on relevant pull requests,
`universal-firmware` branch pushes, manual dispatch, and `fw-*` tag pushes.
Branch/PR/manual runs only produce Actions artifacts. A matching firmware tag
additionally publishes the release and feed.

The normal platform and direct libraries are pinned to the locally observed
versions: pioarduino 55.03.311 / Arduino-ESP32 3.3.11, timer 3.0.1, Syslog 2.0.1,
BQ25798 commit `00c12a2504bbaa6f8b6f56146b027fec43831c98` (1.5.3), PubSubClient
2.8.0 and ArduinoJson 7.4.3. CI uses released PlatformIO 6.2.0; the owner's local
CLI reports 6.2.0.post1. These pins control dependency selection, not a claim of
bit-for-bit build reproducibility. Clean CI builds are not run by the agent.

V1/V3 enable link-time optimization and omit C++ exception-unwind support
(`-flto -fno-exceptions`, removing the framework's `-fno-lto -fexceptions`) against
their existing 1280 KiB OTA slots. Return-code error handling remains; see
[measured size results and further options](SIZE_OPTIMIZATION.md). This
does not enlarge installed partitions or waive capacity checks; CI must establish
the resulting final-image fit. Failed matrix jobs upload ELF/map files and native
test logs as separate `diagnostics-<variant>` artifacts for further analysis,
including the actual firmware and partition binaries. Staging errors report image
bytes, each failing slot's capacity and the exact excess. PlatformIO's ELF usage
summary does not include all final image padding; only the final-byte gate
establishes that the downloadable image fits the generated layout.
The device uses a [small GitHub trust store](certs/README.md) instead of the full
SDK CA bundle; hostname and certificate verification remain enabled.

Jobs perform:

1. Validate the calendar version in `include/version.h`; a release tag must equal
   `fw-<FIRMWARE_VERSION>`. The script never rewrites the header.
2. Build each hardware target without device credentials. Run the native behavioral
   suites once using the resolved ArduinoJson headers. Check the **final bytes**
   against every OTA app slot in that build's generated partition table, then stage
   each image with its hardware metadata, source commit, length and SHA-256.
3. Assemble exactly all three variants from the same version/commit. Reject altered,
   missing, unexpected or mismatched artifacts. Upload a five-file release bundle:
   three application binaries, `manifest.json`, and `SHA256SUMS`.
4. Create a draft GitHub Release, upload the complete bundle, then publish it.
   Firmware releases do not change GitHub's repository-wide latest-release label.
5. After release publication, deploy `firmware/stable.json` through GitHub Pages.
   Refuse an older stable version or changed content for the same version. Missing
   feed (HTTP 404) permits initial publication; other fetch failures stop promotion.

Only the publish job has repository-content write permission. Only the Pages job
has Pages/id-token write permissions. The workflow does not upload to any UPS or
read local secrets. Tagged workflows serialize stable-feed publication.

### Self-hosted builds

Branch/tag pushes and manual runs build all three variants on a runner matching
`[self-hosted, linux, x64]`, following the owner's existing runner labels in other
projects. Pull-request builds use `ubuntu-24.04`. Metadata checks, assembly,
release publication and Pages deployment continue on GitHub-hosted runners.

Make the Linux x64 runner available to this repository. Its service account needs
Bash, Git, a native `g++` compiler, network access to GitHub/PlatformIO dependencies
and a writable runner tool cache. Python 3.12 is provided by `setup-python`; use a
supported Linux environment as described in its
[self-hosted setup guide](https://github.com/actions/setup-python/blob/v6/docs/advanced-usage.md#using-setup-python-with-a-self-hosted-runner).
The existing Node 24 actions require Actions Runner 2.327.1 or newer; keep the
runner updated. See [setup-python v6 requirements](https://github.com/actions/setup-python/tree/v6#breaking-changes-in-v6).

Each build installs the pinned PlatformIO CLI into a job-temporary virtual
environment, leaving system Python and other projects' environments alone.
Toolchains/downloads persist under
`$RUNNER_TOOL_CACHE/ups12v-platformio/<variant>` when that directory survives runner
restarts. Per-variant directories avoid simultaneous package-install conflicts.
Application builds and release staging start from the checkout's clean workspace.
One registered runner executes matrix jobs sequentially; additional matching
runners allow concurrent builds. A queued job with no matching runner needs runner
registration/access corrected; it does not automatically fall back to GitHub.

Runner availability and a self-hosted Actions run have not been verified here.

When editing this workflow, run `actionlint .github/workflows/firmware-release.yml`
before pushing. YAML/Bash syntax checks alone do not validate Actions expression
contexts. In particular, the runner cache path is evaluated in a step and exported
through `GITHUB_ENV`; `runner` is not available in the job-level `env` mapping.

If the branch build succeeds, it still creates artifacts only. Publishing the feed
requires a new matching firmware tag containing the corrected workflow; a tag on
an earlier commit does not pick up subsequent fixes.

## One-time repository setup and releasing

Enable **Settings → Pages → Source: GitHub Actions**. Allow `fw-*` tags in the
`github-pages` environment's deployment rules if that environment restricts refs.
This workflow owns the Pages artifact; combine any existing website content before
using it on a repository that already has a Pages site.

Commit the reviewed source, workflow and matching version header before tagging.
For the initial branch-based CI check, commit the workflow change and push
`universal-firmware` (a pushed tag alone does not create that branch):

```text
git push -u origin universal-firmware
```

This explicitly triggers builds without merging the firmware into `main`. The
manual Run workflow button requires the workflow to be present on the default
branch. Pushing an already-published tag again without changing it creates no new
push event; after the branch check succeeds, use a new matching version/tag for
the next release rather than moving an existing tag.

For example, if the committed version is `20261125.3`:

```text
git tag fw-20261125.3
git push origin fw-20261125.3
```

Do not move a published tag or replace its assets; use a new version. If publishing
fails with an incomplete draft, inspect that draft before retrying. If release
publication succeeds but Pages fails, rerun only the failed Pages job; it is
separate so a retry does not recreate/overwrite the published release.

After successful publication, the expected public URLs are:

```text
https://misch2.github.io/ups12v/firmware/stable.json
https://github.com/misch2/ups12v/releases/download/fw-20261125.3/ups_v4_esp32c3.bin
```

These URLs are a deployment contract, not evidence that this session published
anything. Pages base URL is resolved by GitHub, including a configured custom domain.

## Manifest contract (schema 1)

The stable feed is byte-identical to its versioned release `manifest.json`, bounded
to 8192 bytes. Image URLs always name a specific release; only the feed moves.

| Field | Meaning |
| --- | --- |
| `schema` | Integer `1`, update-feed format version. |
| `version` | Calendar `YYYYMMDD.revision`, identical to the compiled version/tag. |
| `source_commit` | Full source commit shared by all builds. |
| `release_url`, `release_summary` | Release page and short description for HA. |
| `variants` | Exactly the three environment IDs from `platformio.ini`. |
| `variants.<id>.hardware` | `version`, `mcu`, `power_path`, matching existing hardware-profile terminology. |
| `variants.<id>.url` | Public HTTPS URL to that variant's versioned application binary. |
| `variants.<id>.size`, `sha256` | Length and digest of the final downloadable bytes. |
| `variants.<id>.build_ota_slots` | Build-layout evidence: slot `name`, `offset`, `size`. Not the device's installed layout. |

These `.bin` assets are application images, not full-flash/partition migration
bundles. CI only establishes fit in the generated layout. The device
service reads its **actual installed inactive partition** before installation.
Legacy layouts may be too small; do not bypass the size gate or silently enlarge
partitions. See [migration requirements](MIGRATION.md).

## Offline checks

The standard-library packaging tool is
[`tools/firmware_release.py`](tools/firmware_release.py). Its commands are `version`,
`stage`, `assemble`, `site`; `--help` describes inputs. Stage/assemble validate local
artifacts and write only the requested output directory. Site fetches the existing
HTTPS feed and prepares files locally; it does not deploy them.

Run the behavioral tests from the repository root:

```text
python -m unittest discover -s software/ups/tests -p "test_*.py" -v
```

Twelve packaging tests plus one trust-root data test pass, using synthetic
images/partition tables and substituted HTTP responses, including actual CLI
invocation. Workflow YAML/job dependencies and PlatformIO dependency resolution
were checked locally. All three firmware builds and final-byte staging now pass
locally; see [current build verification](../../hardware/v4/evidence/firmware-final-size-fix-20261125/RESULT.md).
No device upload, release or Pages deployment was executed by the agent. Original B1
packaging evidence is in
[checkpoint evidence](../../hardware/v4/evidence/firmware-release-step1-20261125/RESULT.md).
