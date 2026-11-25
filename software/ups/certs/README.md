# Firmware update trust roots

`update-roots.pem` is the reviewed source trust store. The checked-in
`../x509_crt_bundle` is its 1115-byte compact ESP-IDF representation (subjects and
public keys). PlatformIO embeds it as binary using that exact filename, supplying
the SDK's `_binary_x509_crt_bundle_start/end` symbols in place of the full default
bundle. The HTTPS client uses `esp_crt_bundle_attach`, with hostname checking
enabled. It trusts only the same three roots below; there is no insecure fallback.
Keeping CA keys in flash avoids parsing three complete PEM roots into RAM during
every handshake. On-device RAM savings and successful installation remain to be
measured; the change follows a real `MBEDTLS_ERR_CIPHER_ALLOC_FAILED` report.

Verified on 2026-11-25:

| Root | DER SHA-256 | Source |
| --- | --- | --- |
| ISRG Root X1 | `96bcec06264976f37460779acf28c5a7cfe8a3c0aae11a8ffcee05c0bddf08c6` | [Let's Encrypt](https://letsencrypt.org/certs/isrgrootx1.pem) |
| ISRG Root X2 | `69729b8e15a86efc177a57afb7171dfc64add28c2fca8cf1507e34453ccb1470` | [Let's Encrypt](https://letsencrypt.org/certs/isrg-root-x2.pem) |
| USERTrust ECC Certification Authority | `4ff460d54b9c86dabfbcfc5712e0400d2bed3fbc4d4fbdaa86e06adcd2a9ad7a` | [Certifi's Mozilla trust store](https://github.com/certifi/python-certifi/blob/master/certifi/cacert.pem) |

ISRG roots were downloaded from the CA. USERTrust ECC was matched byte-for-byte
against both the system-verified GitHub certificate chain and Certifi's Mozilla
store; its manufacturer download endpoint was unavailable from this environment.
Current Pages and release-asset chains verified through X1; github.com verified
through USERTrust ECC. X2 also covers Let's Encrypt's other supported hierarchy.
See [the CA's chain documentation](https://letsencrypt.org/certificates/).

Desktop TLS verification with **only these roots** succeeded for
`misch2.github.io`, `github.com`, `release-assets.githubusercontent.com` and
`objects.githubusercontent.com`, including a real GitHub release redirect.
This does not establish TLS compatibility on ESP32 hardware.

The failed ESP32 linker map contained a 68,987-byte SDK certificate blob. This PEM
asset is 3,678 bytes including its terminating NUL, a 65,309-byte data reduction.
That earlier PEM comparison excludes changes to verification code and linker
alignment. The compact bundle now replaces that PEM in firmware; final fit
remains a CI check. Check each final ELF/map to ensure the selected bundle is
1115 bytes and the SDK's full certificate blob was discarded.

## Regenerating the bundle

Use [ESP-IDF v5.5.5's generator](https://github.com/espressif/esp-idf/blob/v5.5.5/components/mbedtls/esp_crt_bundle/gen_crt_bundle.py)
with Python and `cryptography`, running from `software/ups`:

```text
python <path-to-IDF-5.5.5-gen_crt_bundle.py> --input certs/update-roots.pem
```

It writes `x509_crt_bundle`. The older Arduino `tools/gen_crt_bundle.py` emits a
different format and must not be used with this SDK. Ordinary firmware builds
use the checked-in asset and do not need generator dependencies. Python tests
validate the reviewed PEM roots plus the bundle's sorted subjects/public keys.
Current bundle SHA-256:
`3b7c8ab7345b64e8b1d1a599fcfe7c469c19ea436fe6e698fb64b74168a4afc7`.

When refreshing roots, verify CA provenance and DER fingerprints, update the PEM
and its behavioral data test, and repeat restricted-root TLS checks through the
release redirect. Keep the installed partition limits enforced. A host moving to
a CA outside this store requires a root update; existing Arduino push OTA/USB
remains the recovery route if an installed device cannot validate the new chain.
