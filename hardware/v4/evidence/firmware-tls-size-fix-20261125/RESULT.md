# HTTPS trust-store size correction - 2026-11-25

Actual run: https://github.com/misch2/ups12v/actions/runs/45655231995
Baseline: fa9b7bc, version 20261125.6 preserved.

| Variant | Job | Result |
| --- | --- | --- |
| V1 | 139350152432 | LTO program size 1370558; exceeds 1310720 by 59838. |
| V3 | 139350152231 | LTO program size 1369486; exceeds 1310720 by 58766. |
| V4 | 139350152482 | Build, nine native suites and staging passed. |

The retained V1 diagnostic artifact (15043370258) was downloaded through the GitHub
connector and analyzed locally. Its map places x509_crt_bundle at 0x3f421ecc with
length 0x10d7b (68987 bytes). The old pre-updater local map discarded that blob;
attaching the default SDK bundle brings it into the application image.

The updater now supplies an embedded three-root PEM via esp_http_client cert_pem.
Asset length including NUL is 3678 bytes, reducing certificate data by 65309 bytes.
Root sources and fingerprints: software/ups/certs/README.md. No server/leaf pins,
insecure fallback, changed partitions or relaxed size/hash checks are introduced.
Final image savings depend on linking and alignment and have not been measured.

## Performed validation

- Worker production-module suite passed against simulated SDK/RTOS/crypto/flash.
- Thirteen Python tests passed, including loading the actual PEM asset with an
  empty trust store and checking the three reviewed root DER fingerprints.
- Native objcopy produced the expected _binary_certs_update_roots_pem_start symbol.
  PlatformIO effective config embeds the same text asset for all three variants.
- Desktop Python/OpenSSL with only these roots verified four real GitHub hosts
  and a GitHub release redirect (HEAD, HTTP 200). No extra OS trust store was used
  for this restricted-root test. Earlier discovery used system-verified chains.
- No target build, firmware upload, ESP32 TLS/flash/power test, push or release was
  performed. CI must verify final image sizes and target linking.

Full diagnostic archive, ELF/map, verified-chain PEMs and temporary analysis remain
in ignored .tmp/firmware-size-analysis/. This directory retains compact test/TLS
results. Trust-store maintenance and existing push OTA/USB recovery are described
in the certificate README.
