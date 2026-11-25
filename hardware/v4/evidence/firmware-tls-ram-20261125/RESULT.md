# Classic ESP32 TLS allocation follow-up - 2026-11-25

## Device evidence

Owner confirms migration/bridge operation on UPS1–UPS8, HTTPS checks working on
UPS4–UPS8 (ESP32-C3), and failures on UPS1–UPS3 (classic ESP32). The supplied
UPS1/UPS2 logs show ESP_ERR_MBEDTLS_SSL_SETUP_FAILED (0x8017) with
MBEDTLS_ERR_SSL_ALLOC_FAILED (magnitude 32512 / 0x7f00), not a certificate error.
Before setup their internal free heap is 40716 / 43836 bytes; each has a 22516-byte
largest block. This is RAM pressure/fragmentation, separate from bridge flash fit.

## Focused change and lifetime contract

Home Assistant entity metadata now borrows stable character data instead of
owning seven String copies per entity: component, category, device/state class,
unit, name and icon. All production callers use literals or immutable metadata
owned by the global charger/library. Enum options similarly borrow the library's
immutable labels. These pointers must outlive their entity configuration.

Computed configuration/state keys and last-sent values retain String ownership.
The constructor moves those owned keys into place, avoiding an extra copy.
Nullable optional metadata is omitted exactly as before; comparisons use string
contents, including for independent character buffers. Unit normalization returns
the original stable unit pointer or the same literal degree-Celsius string.

TLS configuration, trust roots, stack sizes, charger behavior, telemetry policy,
entity identifiers and topic construction are preserved. No configuration schema
or migration change. No entity or diagnostic was removed to obtain the saving.

## Measured scope

Actual classic ESP32 ELF debug types show EntityBaseConfig shrinking from 148 to
64 bytes, and EntityConfig from 192 to 108 bytes: 84 bytes saved per object.
This excludes additional savings from avoiding long string/enum-label allocations.
An exact live heap gain has not yet been measured on the affected units.

A scoped read-only MQTT inventory received 142 retained discovery definitions
for UPS1. At that population, the object-size difference alone would be 11928
bytes, plus other string/option savings. Retained discovery is not an exact live
allocation census or a device-health check, so this remains an estimate.

## Behavioral verification

Eleven native suites and four Jinja rendering checks pass. A new native MQTT
suite tests seven component cases, omitted optional fields, enum metadata,
availability, identity/topics and retained state caching. Independent character
buffers catch accidental pointer comparisons.

The test links the full before/after production MQTT module against host platform
substitutes and emits actual packets. All 22 discovery/state packets are identical
as parsed JSON/topic/retain records. This is a protocol behavior comparison, not
source extraction or source-spelling assertions. The same test version was used
on both sides. Production builds subsequently use the owner's .12 header.

No firmware upload or on-device validation of this reduction was performed by
the agent. Recovery of classic ESP32 manifest checking remains pending until the
owner loads the updated image. Check /firmware/status or the existing syslog
network/heap diagnostics afterward. Bridge success does not validate HA installation.

## Final production builds

All three shared targets build with owner version 20261125.12. Actual final
images pass both generated OTA slots, target-chip checks and local release
staging/assembly. Installed physical layouts were not read. Local manifests use
a zero commit ID for uncommitted verification and were not published. The isolated
build contains only public configuration, avoiding concurrent .pio output cleanup.
Fourteen Python packaging/CA tests also pass.

| Target | Final bytes | OTA slot bytes | Spare bytes |
| --- | ---: | ---: | ---: |
| ups_v1_esp32 | 1293344 | 1310720 | 17376 |
| ups_v3_sys_esp32 | 1291776 | 1310720 | 18944 |
| ups_v4_esp32c3 | 1483216 | 1966080 | 482864 |

Artifacts: [sizes/hashes](sizes.json), [build log](build.log),
[native/Jinja results](native-tests.log), [before packets](metadata-before.json),
[after packets](metadata-after.json), [before types](metadata-size-before.json),
[after types](metadata-size-after.json), [retained inventory](discovery-inventory.json).

Next owner test: upload updated shared V1 to UPS1 and shared V3 to UPS2/UPS3,
preserving migrated NVS. Check manifest completion and the existing heap/syslog
details. Also confirm existing HA telemetry/control behavior. Device recovery
and real HA installation are pending; no agent upload was performed.
