# Home Assistant firmware updates

The agreed design uses a standard MQTT Update entity: the UPS checks a public
manifest at boot and periodically, reports installed/latest compatible versions,
and installs only after an explicit request. Home Assistant handles Install/Skip
and remembers skipped versions. No automatic installation is planned.

Implementation is split into three checkpoints:

1. **Release pipeline and manifest: implemented.**
2. **Device HTTPS checker/downloader: not implemented yet.** It will verify TLS,
   hardware identity, actual inactive-slot capacity, length and SHA-256; coordinate
   installation with charger/ARM/override state without blocking power service;
   preserve NVS; and prevent concurrent update/reset operations.
3. **HA Update entity and web update controls: not implemented yet.** Both use the
   same update service. Existing telemetry and controls keep their identities.

This does not reinstate the intentionally skipped operating-settings controls.
Existing installations need one bootstrap upload containing the eventual updater;
only subsequent updates can be installed through HA.

## Release workflow

[`.github/workflows/firmware-release.yml`](../../.github/workflows/firmware-release.yml)
runs packaging tests and all three hardware builds on relevant pull requests,
manual dispatch, and `fw-*` tag pushes. PR/manual runs only produce Actions
artifacts. A matching firmware tag additionally publishes the release and feed.

The normal platform and direct libraries are pinned to the locally observed
versions: pioarduino 55.03.311 / Arduino-ESP32 3.3.11, timer 3.0.1, Syslog 2.0.1,
BQ25798 commit `00c12a2504bbaa6f8b6f56146b027fec43831c98` (1.5.3), PubSubClient
2.8.0 and ArduinoJson 7.4.3. CI uses released PlatformIO 6.2.0; the owner's local
CLI reports 6.2.0.post1. These pins control dependency selection, not a claim of
bit-for-bit build reproducibility. Clean CI builds are not run by the agent.

Jobs perform:

1. Validate the calendar version in `include/version.h`; a release tag must equal
   `fw-<FIRMWARE_VERSION>`. The script never rewrites the header.
2. Build each hardware target without device credentials. Check the **final bytes**
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

## One-time repository setup and releasing

Enable **Settings → Pages → Source: GitHub Actions**. Allow `fw-*` tags in the
`github-pages` environment's deployment rules if that environment restricts refs.
This workflow owns the Pages artifact; combine any existing website content before
using it on a repository that already has a Pages site.

Commit the reviewed source, workflow and matching version header before tagging.
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
bundles. CI only establishes fit in the generated layout. The future device
service must read its **actual installed inactive partition** before installation.
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

Twelve tests pass using synthetic images/partition tables and substituted HTTP
responses, including actual CLI invocation. Workflow YAML/job dependencies and
PlatformIO dependency resolution were checked locally. No firmware build, upload,
GitHub Actions run, release or Pages deployment was executed. See
[checkpoint evidence](../../hardware/v4/evidence/firmware-release-step1-20261125/RESULT.md).
