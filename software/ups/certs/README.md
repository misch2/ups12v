# Firmware update trust roots

`update-roots.pem` is embedded as NUL-terminated text using PlatformIO's
`board_build.embed_txtfiles`. The HTTPS update client passes it to ESP-IDF as
`cert_pem`, with hostname checking enabled. It does not attach the full SDK bundle
or use an insecure fallback. These are CA roots, not pinned server certificates.

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
That comparison excludes changes to verification code and linker alignment;
final firmware fit remains a CI check.

When refreshing roots, verify CA provenance and DER fingerprints, update the PEM
and its behavioral data test, and repeat restricted-root TLS checks through the
release redirect. Keep the installed partition limits enforced. A host moving to
a CA outside this store requires a root update; existing Arduino push OTA/USB
remains the recovery route if an installed device cannot validate the new chain.
