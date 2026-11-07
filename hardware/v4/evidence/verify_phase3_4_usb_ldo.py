#!/usr/bin/env python3
"""Independent XML preservation check for the Phase 3.2 service-LDO follow-up.

The checker consumes KiCad's true kicadxml netlists.  It is intentionally scoped
to the USB buck-to-LDO change and does not bless PCB geometry or thermal
performance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


REMOVED = {"C34", "C38", "C44", "C46", "L3", "R34", "R38", "R39"}
STALE_NETS = {"BST_USB", "SW_USB", "USB_EN", "USB_FB", "USB_SS"}
ALLOWED_PIN_CHANGES = {"U4.1", "U4.2", "U4.3", "U4.4", "U4.5", "U4.6", "U4.7", "U4.8", "C40.1", "R35.1"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm(name: str | None) -> str:
    return (name or "").lstrip("/")


def read_xml(path: Path):
    return ET.parse(path).getroot()


def components(root):
    return {c.attrib["ref"]: c for c in root.findall(".//components/comp")}


def props(comp):
    result = {}
    for p in comp.findall("property"):
        result[p.attrib.get("name", "")] = p.attrib.get("value", "")
    return result


def pins_by_net(root):
    result = {}
    for net in root.findall(".//nets/net"):
        name = norm(net.attrib.get("name"))
        for node in net.findall("node"):
            result[(node.attrib["ref"], node.attrib["pin"])] = name
    return result


def pin_map(root, ref: str):
    by_net = pins_by_net(root)
    refs = {pin: net for (r, pin), net in by_net.items() if r == ref}
    return refs


def values(root):
    result = {}
    for ref, comp in components(root).items():
        result[ref] = comp.findtext("value", default="")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", type=Path, required=True)
    ap.add_argument("--after", type=Path, required=True)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--erc", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--expected-source-sha256", required=True)
    args = ap.parse_args()

    before = read_xml(args.before)
    after = read_xml(args.after)
    before_comps = components(before)
    after_comps = components(after)
    before_pins = pins_by_net(before)
    after_pins = pins_by_net(after)

    removed = sorted(set(before_comps) - set(after_comps))
    added = sorted(set(after_comps) - set(before_comps))
    changed = []
    for key in sorted(set(before_pins) | set(after_pins)):
        if before_pins.get(key) != after_pins.get(key):
            changed.append({"ref": key[0], "pin": key[1], "before": before_pins.get(key), "after": after_pins.get(key)})
    changed_keys = {f"{x['ref']}.{x['pin']}" for x in changed if x["ref"] not in REMOVED}

    u4 = after_comps.get("U4")
    u4_props = props(u4) if u4 is not None else {}
    cvals = values(after)
    erc = json.loads(args.erc.read_text(encoding="utf-8"))
    erc_errors = erc.get("errors")
    erc_warnings = erc.get("warnings")

    checks = {
        "removed_refs_exact": set(removed) == REMOVED,
        "no_unexpected_added_refs": added == [],
        "u4_library": u4 is not None and u4.find("libsource").attrib.get("part") == "AP7361C-33E",
        "u4_value": cvals.get("U4") == "AP7361C-33E-13 USB 3V3 LDO",
        "u4_footprint": u4 is not None and u4.findtext("footprint") == "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        "u4_mpn": u4_props.get("MPN") == "AP7361C-33E-13",
        "u4_manufacturer": u4_props.get("Manufacturer") == "Diodes Incorporated",
        "u4_lcsc": u4_props.get("Source/LCSC Part") == "C500795",
        "u4_datasheet": u4 is not None and u4.findtext("datasheet") == "https://www.diodes.com/datasheet/download/AP7361C.pdf",
        "c27_value": cvals.get("C27") == "4.7u 10V USB LDO IN",
        "c40_value": cvals.get("C40") == "100n USB LDO OUT",
        "r35_value": cvals.get("R35") == "10k USB3V3 BLEED",
        "u4_pin_map": pin_map(after, "U4") == {"1": "USB_VBUS", "2": "PGND", "3": "USB3V3"},
        "usb_input_caps": set(pin_map(after, "C27").values()) == {"USB_VBUS", "PGND"} and set(pin_map(after, "C28").values()) == {"USB_VBUS", "PGND"},
        "usb_output_caps": set(pin_map(after, "C35").values()) == {"USB3V3", "PGND"} and set(pin_map(after, "C40").values()) == {"USB3V3", "PGND"},
        "usb_output_bleeder": pin_map(after, "R35") == {"1": "USB3V3", "2": "PGND"},
        "mux_usb_input": pin_map(after, "U5").get("6") == "USB3V3",
        "stale_usb_nets_absent": not (STALE_NETS & set(norm(n.attrib.get("name")) for n in after.findall(".//nets/net"))),
        "retained_pin_changes_scoped": changed_keys <= ALLOWED_PIN_CHANGES,
        "erc_zero_errors": erc_errors == 0,
        "erc_warning_count": erc_warnings == 6,
        "source_hash": sha256(args.source) == args.expected_source_sha256,
    }

    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "source_sha256": sha256(args.source),
        "before_xml_sha256": sha256(args.before),
        "after_xml_sha256": sha256(args.after),
        "erc": {"errors": erc_errors, "warnings": erc_warnings},
        "removed_refs": removed,
        "expected_removed_refs": sorted(REMOVED),
        "added_refs": added,
        "pin_net_changes": changed,
        "allowed_pin_change_keys": sorted(ALLOWED_PIN_CHANGES),
        "checks": checks,
        "notes": [
            "USB service power is USB_VBUS -> U4 AP7361C-33E-13 -> USB3V3 -> U5 VIN2.",
            "C27/C28 are the connector-side USB_VBUS input bypass; C35/C40 are the retained USB3V3 output capacitance; R35 is the 10k USB3V3 bleeder.",
            "ERC warnings are the six pre-existing isolated MCU/UART labels; no new error was introduced.",
            "This XML check does not prove PCB copper, thermal performance, USB port current capability, or prototype behavior.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "removed": removed, "added": added, "pin_changes": changed, "failed_checks": [k for k, v in checks.items() if not v]}, separators=(",", ":")))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
