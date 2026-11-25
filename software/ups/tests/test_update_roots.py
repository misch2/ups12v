"""Validate the reviewed PEM roots and the compact SDK trust-bundle asset."""

import hashlib
from pathlib import Path
import ssl
import struct
import unittest

ROOTS = Path(__file__).resolve().parents[1] / "certs/update-roots.pem"


class UpdateRootsTests(unittest.TestCase):
    def test_sdk_bundle_contains_only_the_reviewed_subjects_and_public_keys(self):
        data = (ROOTS.parent.parent / "x509_crt_bundle").read_bytes()
        count = struct.unpack_from("<I", data)[0] // 4
        self.assertEqual(count, 3)
        subjects, keys = [], set()
        for index in range(count):
            offset = struct.unpack_from("<I", data, index * 4)[0]
            end = struct.unpack_from("<I", data, (index + 1) * 4)[0] if index + 1 < count else len(data)
            name_size, key_size = struct.unpack_from("<HH", data, offset)
            self.assertEqual(offset + 4 + name_size + key_size, end)
            subject = data[offset + 4:offset + 4 + name_size]
            key = data[offset + 4 + name_size:end]
            subjects.append(subject)
            keys.add((hashlib.sha256(subject).hexdigest(), hashlib.sha256(key).hexdigest()))
        self.assertEqual(subjects, sorted(subjects))
        self.assertEqual(keys, {
            ("f6db2fbd9dd85d9259ddb3c6de7d7b2fec3f3e0cef1761bcbf3320571e2d30f8", "0b9fa5a59eed715c26c1020c711b4f6ec42d58b0015e14337a39dad301c5afc3"),
            ("74d0322c9c0b177966cfa1bf6ca9a42caf69170366bee3198653dd7972c484ab", "762195c225586ee6c0237456e2107dc54f1efc21f61a792ebd515913cce68332"),
            ("56bdb66f422bf34749590f21f227de10933315224b7b3d8f77bf8b4182146faf", "2021917e98263945c859c43f1d73cb4139053c414fa03ca3bc7ee88614298f3b"),
        })

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
