import hashlib
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location("check_ota_size", Path(__file__).parents[1] / "tools" / "check_ota_size.py")
ota = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ota)


def entry(subtype, offset, size):
    return struct.pack("<HBBII16sI", 0x50AA, 0, subtype, offset, size, b"app", 0)


def table(entries, checksum=True):
    raw = b"".join(entries)
    if checksum:
        raw += b"\xeb\xeb" + b"\xff" * 14 + hashlib.md5(raw).digest()
    return raw.ljust(3072, b"\xff")


class CapacityTests(unittest.TestCase):
    def test_both_slots_and_exact_fit(self):
        data = table([entry(0x10, 0x10000, 0x1E0000), entry(0x11, 0x1F0000, 0x1E0000)])
        self.assertTrue(all(row[3] == 0 for row in ota.check_size(0x1E0000, data)))
        self.assertTrue(all(row[3] == -1 for row in ota.check_size(0x1E0001, data)))
        self.assertTrue(all(row[3] > 0 for row in ota.check_size(1000000, data)))

    def test_smaller_inactive_slot_is_not_ignored(self):
        data = table([entry(0x10, 0x10000, 0x1E0000), entry(0x11, 0x1F0000, 0x140000)])
        self.assertEqual([row[3] for row in ota.check_size(0x140001, data)], [0x9FFFF, -1])

    def test_bad_tables(self):
        good = table([entry(0x10, 0x10000, 0x100000), entry(0x11, 0x110000, 0x100000)])
        invalid = [b"", good[:-1], b"bad!" * 8, good[:32] + b"\0" + good[33:],
                   good[:80] + bytes([good[80] ^ 1]) + good[81:],
                   table([entry(0x10, 0x10000, 0x100000)]),
                   table([entry(0x10, 0x10000, 0x100000), entry(0x10, 0x110000, 0x100000)]),
                   table([entry(0x10, 0x10000, 0x180000), entry(0x11, 0x110000, 0x100000)]),
                   table([entry(0x10, 0x10001, 0xFFFFF), entry(0x11, 0x110000, 0x100000)])]
        for data in invalid:
            with self.subTest(data_length=len(data)), self.assertRaises(ValueError):
                ota.check_size(1, data)

    def test_older_table_without_checksum(self):
        data = table([entry(0x10, 0x10000, 0x100000), entry(0x11, 0x110000, 0x100000)], checksum=False)
        self.assertEqual(len(ota.check_size(1, data)), 2)
        with self.assertRaises(ValueError):
            ota.check_size(0, data)


if __name__ == "__main__":
    unittest.main()
