#!/usr/bin/env python3
"""Project the accepted Phase 3.1 XML onto the simplified final design.

This is intentionally independent of the schematic mutator.  It proves that
the old MCU/native-USB pin partitions remain, while allowing the already
approved USB series-link splits and the R11 service no-connect.
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


def read_export(path: Path):
    root = ET.parse(path).getroot()
    components = {c.attrib["ref"]: c for c in root.findall("./components/comp")}
    nets = {
        net.attrib["name"]: frozenset((node.attrib["ref"], node.attrib["pin"])
                                       for node in net.findall("node"))
        for net in root.findall("./nets/net")
    }
    return components, nets


def projected_partitions(nets, old_pins):
    projected = []
    for name, pins in nets.items():
        if name.startswith("unconnected-"):
            continue
        kept = frozenset(pin for pin in pins if pin in old_pins)
        if kept:
            projected.append(kept)
    return collections.Counter(projected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--erc", type=Path, required=True)
    parser.add_argument("--schematic", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_sha256 = hashlib.sha256(args.schematic.read_bytes()).hexdigest()
    if source_sha256 != args.expected_sha256.lower():
        raise SystemExit(f"source hash mismatch: {source_sha256}")
    if args.after.stat().st_mtime_ns < args.schematic.stat().st_mtime_ns:
        raise SystemExit("final XML is stale")
    if args.erc.stat().st_mtime_ns < args.schematic.stat().st_mtime_ns:
        raise SystemExit("ERC is stale")

    before_components, before = read_export(args.before)
    after_components, after = read_export(args.after)
    old_pins = set().union(*(pins for name, pins in before.items() if not name.startswith("unconnected-")))
    functional_after_pins = set().union(*(pins for name, pins in after.items() if not name.startswith("unconnected-")))
    lost = old_pins - functional_after_pins
    if lost != SERVICE_NO_CONNECT:
        raise SystemExit(f"unexpected lost Phase 3.1 pins: {sorted(lost)}")

    expected = []
    for name, pins in before.items():
        if name.startswith("unconnected-"):
            continue
        kept = set(pins) - USB_SPLITS - SERVICE_NO_CONNECT
        if kept:
            expected.append(frozenset(kept))
    expected.extend(frozenset({pin}) for pin in USB_SPLITS)
    actual = projected_partitions(after, old_pins)
    expected_counter = collections.Counter(expected)
    if actual != expected_counter:
        raise SystemExit(json.dumps({
            "missing_partitions": [sorted(p) for p, count in (expected_counter - actual).items() for _ in range(count)],
            "unexpected_partitions": [sorted(p) for p, count in (actual - expected_counter).items() for _ in range(count)],
        }, indent=2))

    for ref, old in before_components.items():
        if ref in {"U1"}:
            continue
        for field in ("value", "footprint"):
            if ref == "R11" and field == "value":
                continue
            if ref == "U2" and field == "footprint":
                continue
            if ref not in after_components or old.findtext(field) != after_components[ref].findtext(field):
                raise SystemExit(f"property changed for {ref}.{field}")

    required_nets = {
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
    missing_nets = {
        name: sorted(required - after.get(name, set()))
        for name, required in required_nets.items()
        if not required <= after.get(name, set())
    }
    if missing_nets:
        raise SystemExit(json.dumps({"missing_required_nets": missing_nets}, indent=2))

    erc = json.loads(args.erc.read_text(encoding="utf-8"))
    warning_labels = {
        item["description"].split("Global Label '", 1)[1].rstrip("'")
        for item in erc.get("violations", [])
        if item.get("rule") == "isolated_pin_label" and "Global Label '" in item.get("description", "")
    }
    if erc.get("errors") != 0 or erc.get("warnings") != len(EXPECTED_WARNINGS) or warning_labels != EXPECTED_WARNINGS:
        raise SystemExit(f"unexpected ERC: errors={erc.get('errors')} warnings={erc.get('warnings')} labels={sorted(warning_labels)}")

    result = {
        "status": "PASS",
        "source_sha256": source_sha256,
        "before_xml_sha256": hashlib.sha256(args.before.read_bytes()).hexdigest(),
        "after_xml_sha256": hashlib.sha256(args.after.read_bytes()).hexdigest(),
        "erc_sha256": hashlib.sha256(args.erc.read_bytes()).hexdigest(),
        "baseline_reference_count": len(before_components),
        "baseline_connected_pin_count": len(old_pins),
        "old_reference_projection_unchanged_except_declared_changes": True,
        "declared_usb_series_splits": sorted(USB_SPLITS),
        "declared_service_no_connect": sorted(SERVICE_NO_CONNECT),
        "required_mcu_usb_nets_present": True,
        "erc_errors": erc["errors"],
        "erc_warnings": erc["warnings"],
        "scope": "Phase 3.1 accepted MCU/native-USB projection into the simplified Phase 3.3 export; no PCB or hardware claim",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
