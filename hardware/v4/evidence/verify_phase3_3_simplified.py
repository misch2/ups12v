#!/usr/bin/env python3
"""Independent exported-netlist check for the owner-approved Phase 3.3 simplification.

The source schematic is never parsed here.  KiCad XML exports are the comparison
input; the direct ERC result is checked separately.  The script intentionally
allows only the documented component removals and pin-level net changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


REMOVED = {
    "U7", "C42", "U8", "U9", "U12", "D5", "R54", "U10", "C49", "C50",
    "C51", "U11", "C41", "C52", "R56", "R57", "Q10", "R55",
}

ADDED = {"R24"}

EXPECTED_PIN_NET_CHANGES = {
    ("U5", "2"): ("MCU_PRE3V3", "MCU3V3"),
    ("U5", "7"): ("MCU_PRE3V3", "MCU3V3"),
    ("Q7", "1"): ("CHG_LATCH", "MCU_CHG_BASE"),
    ("Q7", "2"): ("CHG_LIVE_AND", "PGND"),
    ("R46", "2"): ("MCU_CHG_LIVE", "MCU_CHG_BASE"),
    ("R47", "1"): ("CHG_LATCH", "MCU_CHG_BASE"),
    ("R50", "1"): ("MUX_PR1", "MAIN_3V3"),
    ("Q8", "1"): ("MUX_PR1", "MAIN_3V3"),
}

EXPECTED_WARNINGS = {
    "UART_RX", "UART_TX", "MCU_STATUS_LED", "MCU_GPIO1", "MCU_GPIO7", "MCU_GPIO10",
}


def export_map(path: Path) -> tuple[dict[str, str], dict[tuple[str, str], str], dict[str, set[tuple[str, str]]]]:
    root = ET.parse(path).getroot()
    components = {
        comp.attrib["ref"]: comp.findtext("value", default="")
        for comp in root.find("components").findall("comp")
    }
    pin_net: dict[tuple[str, str], str] = {}
    net_nodes: dict[str, set[tuple[str, str]]] = {}
    for net in root.find("nets").findall("net"):
        name = net.attrib.get("name", "")
        nodes = {
            (node.attrib["ref"], node.attrib["pin"])
            for node in net.findall("node")
        }
        net_nodes[name] = nodes
        for node in nodes:
            pin_net[node] = name
    return components, pin_net, net_nodes


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--final", type=Path, required=True)
    parser.add_argument("--erc", type=Path, required=True)
    parser.add_argument("--schematic", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    observed_sha256 = hashlib.sha256(args.schematic.read_bytes()).hexdigest()
    if observed_sha256 != args.expected_sha256.lower():
        fail(f"source SHA256 mismatch: {observed_sha256} != {args.expected_sha256.lower()}")

    baseline_components, baseline_pin_net, baseline_nets = export_map(args.baseline)
    final_components, final_pin_net, final_nets = export_map(args.final)

    removed_observed = set(baseline_components) - set(final_components)
    added_observed = set(final_components) - set(baseline_components)
    if removed_observed != REMOVED:
        fail(f"component removal mismatch: {sorted(removed_observed)}")
    if added_observed != ADDED:
        fail(f"component addition mismatch: {sorted(added_observed)}")
    if "8k2" not in final_components.get("R23", ""):
        fail(f"R23 divider-top value mismatch: {final_components.get('R23', '')!r}")
    if "4k7" not in final_components.get("R24", ""):
        fail(f"R24 divider-bottom value mismatch: {final_components.get('R24', '')!r}")

    changes = []
    unexpected = []
    for pin, (before_expected, after_expected) in EXPECTED_PIN_NET_CHANGES.items():
        before = baseline_pin_net.get(pin)
        after = final_pin_net.get(pin)
        if (before, after) != (before_expected, after_expected):
            unexpected.append({"pin": pin, "observed": [before, after], "expected": [before_expected, after_expected]})
        changes.append({"reference": pin[0], "pin": pin[1], "before": before, "after": after})

    retained_pin_changes = []
    retained_pin_checked_count = 0
    for pin, before in baseline_pin_net.items():
        if pin[0] in REMOVED or pin not in final_pin_net or pin in EXPECTED_PIN_NET_CHANGES:
            continue
        retained_pin_checked_count += 1
        after = final_pin_net[pin]
        if before != after:
            unexpected.append({"pin": pin, "observed": [before, after], "expected": [before, before]})
            retained_pin_changes.append({"reference": pin[0], "pin": pin[1], "before": before, "after": after})

    for net_name in ("MCU_PRE3V3", "CHG_LATCH", "CHG_LIVE_AND", "MCU_CHG_LIVE"):
        if net_name in final_nets and final_nets[net_name]:
            unexpected.append({"net": net_name, "reason": "superseded net remains populated", "nodes": sorted(final_nets[net_name])})

    key_nets = {
        "MCU3V3": {("U5", "2"), ("U5", "7"), ("U1", "3"), ("U6", "8")},
        "MAIN_3V3": {("U5", "3"), ("U5", "5"), ("U6", "1"), ("R23", "1"), ("R50", "1"), ("Q8", "1")},
        "USB3V3": {("U5", "6"), ("L3", "2")},
        "MUX_PR1": {("U5", "4"), ("R23", "2"), ("R24", "1")},
        "MCU_CHG_ARM": {("U1", "12"), ("R46", "1")},
        "MCU_CHG_BASE": {("R46", "2"), ("Q7", "1"), ("R47", "1")},
        "PGND": {("Q7", "2"), ("R24", "2")},
    }
    key_net_results = {}
    for name, required_nodes in key_nets.items():
        observed = final_nets.get(name, set())
        missing = sorted(required_nodes - observed)
        key_net_results[name] = {"required_nodes": sorted(required_nodes), "missing": missing}
        if missing:
            unexpected.append({"net": name, "reason": "required retained nodes missing", "missing": missing})

    erc = json.loads(args.erc.read_text(encoding="utf-8"))
    erc_errors = erc.get("errors")
    erc_warnings = erc.get("warnings")
    violations = erc.get("violations", [])
    warning_labels = {
        item["description"].split("Global Label '", 1)[1].rstrip("'")
        for item in violations
        if item.get("rule") == "isolated_pin_label" and "Global Label '" in item.get("description", "")
    }
    erc_result = {
        "errors": erc_errors,
        "warnings": erc_warnings,
        "warning_labels": sorted(warning_labels),
    }
    if erc_errors != 0 or erc_warnings != len(EXPECTED_WARNINGS) or warning_labels != EXPECTED_WARNINGS:
        unexpected.append({"erc": erc_result, "expected_warning_labels": sorted(EXPECTED_WARNINGS)})

    report = {
        "status": "PASS" if not unexpected else "FAIL",
        "source_sha256": observed_sha256,
        "baseline_xml_sha256": hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
        "final_xml_sha256": hashlib.sha256(args.final.read_bytes()).hexdigest(),
        "baseline_component_count": len(baseline_components),
        "final_component_count": len(final_components),
        "removed_components": sorted(REMOVED),
        "added_components": sorted(added_observed),
        "intentional_pin_net_changes": changes,
        "retained_pin_change_count": len(retained_pin_changes),
        "retained_pin_checked_count": retained_pin_checked_count,
        "key_net_results": key_net_results,
        "erc": erc_result,
        "unexpected": unexpected,
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "baseline_component_count", "final_component_count", "removed_components", "retained_pin_change_count", "erc", "unexpected")}, indent=2, sort_keys=True))
    if unexpected:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
