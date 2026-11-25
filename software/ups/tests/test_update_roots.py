"""Validate the actual PEM asset used by the device's HTTPS update client."""

import hashlib
from pathlib import Path
import ssl
import unittest

ROOTS = Path(__file__).resolve().parents[1] / "certs/update-roots.pem"


class UpdateRootsTests(unittest.TestCase):
    def test_trust_store_contains_only_the_reviewed_self_signed_roots(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cafile=str(ROOTS))
        self.assertEqual(
            {hashlib.sha256(der).hexdigest() for der in context.get_ca_certs(binary_form=True)},
            {
                "96bcec06264976f37460779acf28c5a7cfe8a3c0aae11a8ffcee05c0bddf08c6",  # ISRG X1
                "69729b8e15a86efc177a57afb7171dfc64add28c2fca8cf1507e34453ccb1470",  # ISRG X2
                "4ff460d54b9c86dabfbcfc5712e0400d2bed3fbc4d4fbdaa86e06adcd2a9ad7a",  # USERTrust ECC
            },
        )
        for certificate in context.get_ca_certs():
            self.assertEqual(certificate["subject"], certificate["issuer"])


if __name__ == "__main__":
    unittest.main()
