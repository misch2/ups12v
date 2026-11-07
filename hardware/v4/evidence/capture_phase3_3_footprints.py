#!/usr/bin/env python3
"""Capture footprint/readback checks for the simplified MCU/power checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


EXPECTED = {
    "U1": "ups_v4:ESP32-C3-MINI-1-N4X",
    "U2": "Package_TO_SOT_SMD:Texas_DRT-3",
    "U3": "Package_TO_SOT_SMD:SOT-583-8",
    "U4": "Package_TO_SOT_SMD:SOT-583-8",
    "U5": "Package_TO_SOT_SMD:SOT-583-8",
    "U6": "Package_SO:VSSOP-8_3x3mm_P0.65mm",
    "Q5": "Package_TO_SOT_SMD:SOT-23",
    "Q6": "Package_TO_SOT_SMD:SOT-23",
    "Q7": "Package_TO_SOT_SMD:SOT-23",
    "R23": "Resistor_SMD:R_0402_1005Metric",
    "R24": "Resistor_SMD:R_0402_1005Metric",
    "R46": "Resistor_SMD:R_0402_1005Metric",
    "R47": "Resistor_SMD:R_0402_1005Metric",
    "R50": "Resistor_SMD:R_0402_1005Metric",
    "R51": "Resistor_SMD:R_0402_1005Metric",
    "R52": "Resistor_SMD:R_0402_1005Metric",
    "R53": "Resistor_SMD:R_0402_1005Metric",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", type=Path, required=True)
    parser.add_argument("--schematic", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = ET.parse(args.xml).getroot()
    components = {c.attrib["ref"]: c for c in root.findall("./components/comp")}
    readback = {}
    mismatches = []
    for ref, expected_footprint in EXPECTED.items():
        component = components.get(ref)
        observed = None if component is None else component.findtext("footprint", default="")
        value = None if component is None else component.findtext("value", default="")
        readback[ref] = {"value": value, "footprint": observed}
        if observed != expected_footprint:
            mismatches.append({"reference": ref, "expected": expected_footprint, "observed": observed})

    result = {
        "status": "PASS" if not mismatches else "FAIL",
        "source_sha256": hashlib.sha256(args.schematic.read_bytes()).hexdigest(),
        "xml_sha256": hashlib.sha256(args.xml.read_bytes()).hexdigest(),
        "checked_references": readback,
        "mismatches": mismatches,
        "scope": "Fresh KiCad XML footprint fields for active MCU, USB, mux, isolation, charger gate and divider parts",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checked": len(readback), "mismatches": mismatches}, indent=2))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
