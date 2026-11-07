#!/usr/bin/env python3
"""Independent projection of the accepted Phase 3.1 MCU/native-USB baseline.

This deliberately checks only old partitions and required USB/MCU nets.  The
new service-LDO block is checked separately by verify_phase3_4_usb_ldo.py.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


USB_SPLITS = {("U1", "26"), ("U1", "27")}
SERVICE_NO_CONNECT = {("R11", "2")}
EXPECTED_WARNINGS = {"UART_RX", "UART_TX", "MCU_STATUS_LED", "MCU_GPIO1", "MCU_GPIO7", "MCU_GPIO10"}
ALLOWED_PROPERTY_CHANGES = {("C27", "value"), ("R11", "value"), ("U1", "value"), ("U1", "footprint"), ("U2", "footprint")}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    root = ET.parse(path).getroot()
    comps = {c.attrib["ref"]: c for c in root.findall("./components/comp")}
    nets = {n.attrib["name"].lstrip("/"): frozenset((x.attrib["ref"], x.attrib["pin"]) for x in n.findall("node")) for n in root.findall("./nets/net")}
    return comps, nets


def project(nets, old_pins):
    out = []
    for name, pins in nets.items():
        if name.startswith("unconnected-"):
            continue
        kept = frozenset(p for p in pins if p in old_pins)
        if kept:
            out.append(kept)
    return collections.Counter(out)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--before", type=Path, required=True)
    p.add_argument("--after", type=Path, required=True)
    p.add_argument("--erc", type=Path, required=True)
    p.add_argument("--schematic", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    source_sha = sha(a.schematic)
    before_components, before = read(a.before)
    after_components, after = read(a.after)
    old_pins = set().union(*(pins for name, pins in before.items() if not name.startswith("unconnected-")))
    actual_pins = set().union(*(pins for name, pins in after.items() if not name.startswith("unconnected-")))
    lost = old_pins - actual_pins
    expected_lost = SERVICE_NO_CONNECT

    expected = []
    for name, pins in before.items():
        if name.startswith("unconnected-"):
            continue
        kept = set(pins) - USB_SPLITS - SERVICE_NO_CONNECT
        if kept:
            expected.append(frozenset(kept))
    expected.extend(frozenset({pin}) for pin in USB_SPLITS)

    property_changes = []
    for ref, old in before_components.items():
        if ref not in after_components:
            continue
        for field in ("value", "footprint"):
            old_value = old.findtext(field)
            new_value = after_components[ref].findtext(field)
            if old_value != new_value:
                property_changes.append({"ref": ref, "field": field, "before": old_value, "after": new_value})

    required = {
        "USB_VBUS": {("J7", pin) for pin in ("A4", "A9", "B4", "B9")} | {("C27", "1"), ("C28", "1")},
        "USB_DP": {("J7", "A6"), ("J7", "B6"), ("U2", "1")},
        "USB_DN": {("J7", "A7"), ("J7", "B7"), ("U2", "2")},
        "USB_CC1": {("J7", "A5"), ("R13", "1")},
        "USB_CC2": {("J7", "B5"), ("R14", "1")},
        "MCU3V3": {("U1", "3"), ("R15", "2"), ("R16", "2"), ("R17", "2"), ("R18", "2"), ("C30", "1"), ("C31", "1")},
        "MCU_BOOT": {("U1", "23"), ("R15", "1"), ("SW1", "1")},
        "MCU_EN": {("U1", "8"), ("R16", "1"), ("SW2", "1"), ("C29", "1")},
        "MCU_BOOT_STRAP2": {("U1", "5"), ("R17", "1")},
        "MCU_BOOT_STRAP8": {("U1", "22"), ("R18", "1")},
    }
    missing = {name: sorted(req - after.get(name, set())) for name, req in required.items() if not req <= after.get(name, set())}
    erc = json.loads(a.erc.read_text(encoding="utf-8"))
    warning_labels = {item["description"].split("Global Label '", 1)[1].rstrip("'") for item in erc.get("violations", []) if item.get("rule") == "isolated_pin_label" and "Global Label '" in item.get("description", "")}
    checks = {
        "source_hash": source_sha == a.expected_sha256.lower(),
        "final_xml_fresh": a.after.stat().st_mtime_ns >= a.schematic.stat().st_mtime_ns,
        "erc_fresh": a.erc.stat().st_mtime_ns >= a.schematic.stat().st_mtime_ns,
        "phase31_lost_pins_scoped": lost == expected_lost,
        "old_partitions_preserved": project(after, old_pins) == collections.Counter(expected),
        "property_changes_scoped": {(x["ref"], x["field"]) for x in property_changes} <= ALLOWED_PROPERTY_CHANGES,
        "required_mcu_usb_nets_present": not missing,
        "erc_expected": erc.get("errors") == 0 and erc.get("warnings") == len(EXPECTED_WARNINGS) and warning_labels == EXPECTED_WARNINGS,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "source_sha256": source_sha,
        "before_xml_sha256": sha(a.before),
        "after_xml_sha256": sha(a.after),
        "erc_sha256": sha(a.erc),
        "baseline_reference_count": len(before_components),
        "final_reference_count": len(after_components),
        "property_changes": property_changes,
        "lost_pins": sorted(lost),
        "missing_required_nets": missing,
        "checks": checks,
        "scope": "Phase 3.1 accepted MCU/native-USB projection into the Phase 3.2 service-LDO follow-up; no PCB or hardware claim",
    }
    a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "failed_checks": [k for k, v in checks.items() if not v], "property_changes": property_changes}, separators=(",", ":")))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
