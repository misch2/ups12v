"""Bounded Phase 3.1 projection/connectivity verification.

This read-only check projects the accepted Phase 2.6 references out of the
fresh Phase 3.1 XML and requires their pin partitions to be unchanged. It then
checks only the explicitly authorized MCU/native-USB additions. It does not
claim power-domain, PCB or hardware qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def read_nets(path):
    root = ET.parse(path)
    return {
        net.attrib["name"]: {(node.attrib["ref"], node.attrib["pin"])
                             for node in net.findall("node")}
        for net in root.findall("./nets/net")
    }


def net_subset(nets, refs):
    return {
        name: {pin for pin in pins if pin[0] in refs}
        for name, pins in nets.items()
        if any(ref in refs for ref, _pin in pins)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--erc", type=Path, required=True)
    parser.add_argument("--schematic", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    actual_sha = hashlib.sha256(args.schematic.read_bytes()).hexdigest()
    assert actual_sha == args.expected_sha256, "source hash changed after export"
    assert args.after.stat().st_mtime >= args.schematic.stat().st_mtime
    assert args.erc.stat().st_mtime >= args.schematic.stat().st_mtime

    before = read_nets(args.before)
    after = read_nets(args.after)
    old_refs = {ref for pins in before.values() for ref, _pin in pins}
    assert net_subset(after, old_refs) == before, "old-reference projection changed"

    expected_refs = {
        "U1", "J7", "U2", "SW1", "SW2",
        "R13", "R14", "R15", "R16", "R17", "R18", "C27", "C28", "C29",
        "C30", "C31",
    }
    actual_refs = {ref for pins in after.values() for ref, _pin in pins}
    assert expected_refs <= actual_refs, sorted(expected_refs - actual_refs)

    expected_nets = {
        "USB_VBUS": {("J7", pin) for pin in ("A4", "A9", "B4", "B9")} |
                     {("C27", "1"), ("C28", "1")},
        "USB_DP": {("J7", "A6"), ("J7", "B6"), ("U2", "1"), ("U1", "27")},
        "USB_DN": {("J7", "A7"), ("J7", "B7"), ("U2", "2"), ("U1", "26")},
        "USB_CC1": {("J7", "A5"), ("R13", "1")},
        "USB_CC2": {("J7", "B5"), ("R14", "1")},
        "MCU3V3": {("U1", "3"), ("R15", "2"), ("R16", "2"),
                    ("R17", "2"), ("R18", "2"), ("C30", "1"), ("C31", "1")},
        "MCU_BOOT": {("U1", "23"), ("R15", "1"), ("SW1", "1")},
        "MCU_EN": {("U1", "8"), ("R16", "1"), ("SW2", "1"), ("C29", "1")},
        "MCU_BOOT_STRAP2": {("U1", "5"), ("R17", "1")},
        "MCU_BOOT_STRAP8": {("U1", "22"), ("R18", "1")},
    }
    for name, expected in expected_nets.items():
        assert expected <= after.get(name, set()), (name, sorted(expected - after.get(name, set())))

    erc = json.loads(args.erc.read_text(encoding="utf-8"))
    assert erc["errors"] == 1
    assert any("U1 Pin 3" in violation["description"]
               for violation in erc["violations"])
    result = {
        "source_sha256": actual_sha,
        "before_xml_sha256": hashlib.sha256(args.before.read_bytes()).hexdigest(),
        "after_xml_sha256": hashlib.sha256(args.after.read_bytes()).hexdigest(),
        "erc_sha256": hashlib.sha256(args.erc.read_bytes()).hexdigest(),
        "old_reference_projection_unchanged": True,
        "expected_phase3_1_nets_present": True,
        "expected_new_references": sorted(expected_refs),
        "erc_errors": erc["errors"],
        "erc_warnings": erc["warnings"],
        "known_open_erc_error": "U1 Pin 3 MCU3V3 deferred regulator/mux source",
        "scope": "MCU/native-USB schematic checkpoint only; no PCB, power-domain or hardware qualification",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
