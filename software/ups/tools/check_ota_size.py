"""Check a final application image against both OTA slots in an installed partition table."""

import argparse
import hashlib
from pathlib import Path
import struct
import sys


def ota_slots(table: bytes):
    if not table or len(table) > 4096 or len(table) % 32:
        raise ValueError("partition table must contain 32-byte entries (up to 4096 bytes)")
    slots = {}
    ranges = []
    for position in range(0, len(table), 32):
        entry = table[position:position + 32]
        magic = struct.unpack_from("<H", entry)[0]
        if magic == 0xFFFF:
            if any(byte != 0xFF for byte in table[position:]):
                raise ValueError("unexpected bytes after partition terminator")
            break
        if magic == 0xEBEB:
            if entry[:16] != b"\xeb\xeb" + b"\xff" * 14:
                raise ValueError("malformed partition checksum entry")
            if hashlib.md5(table[:position]).digest() != entry[16:]:
                raise ValueError("partition-table checksum mismatch")
            if any(byte != 0xFF for byte in table[position + 32:]):
                raise ValueError("unexpected bytes after partition checksum")
            break
        if magic != 0x50AA:
            raise ValueError("invalid partition entry magic")
        _, kind, subtype, offset, size, _, _ = struct.unpack("<HBBII16sI", entry)
        if not size or offset + size > 2**32:
            raise ValueError("invalid partition range")
        if any(offset < end and offset + size > start for start, end in ranges):
            raise ValueError("overlapping partitions")
        ranges.append((offset, offset + size))
        if kind == 0 and 0x10 <= subtype <= 0x1F:
            if subtype in slots:
                raise ValueError("duplicate OTA slot")
            if offset % 0x10000:
                raise ValueError("application partition is not 64 KiB aligned")
            slots[subtype] = (offset, size)
    if 0x10 not in slots or 0x11 not in slots:
        raise ValueError("both ota_0 and ota_1 must be present")
    return slots


def check_size(size: int, table: bytes):
    if size <= 0:
        raise ValueError("application image is empty")
    return [(f"ota_{subtype - 0x10}", offset, capacity, capacity - size)
            for subtype, (offset, capacity) in sorted(ota_slots(table).items())]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firmware", type=Path, required=True, help="final firmware.bin from the selected hardware build")
    parser.add_argument("--installed-partitions", type=Path, required=True,
                        help="binary partition table from the device or a verified matching backup")
    args = parser.parse_args(argv)
    try:
        size = args.firmware.stat().st_size
        rows = check_size(size, args.installed_partitions.read_bytes())
    except (OSError, ValueError) as error:
        print(f"Cannot check OTA capacity: {error}", file=sys.stderr)
        return 2
    print(f"Final application: {size} bytes")
    for label, offset, capacity, spare in rows:
        print(f"{label}: offset=0x{offset:x}, capacity={capacity}, spare={spare} bytes")
    if any(spare < 0 for _, _, _, spare in rows):
        print("FAIL: image exceeds an installed OTA slot; do not upload.")
        return 1
    print("PASS: image fits both OTA slots. Installed-table provenance must be verified separately.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
