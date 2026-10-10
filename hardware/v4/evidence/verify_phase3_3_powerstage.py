"""Verify Phase 2.6 connectivity partitions after Phase 3.3 edits.

This compares the complete connected-pin partition projected onto the Phase
2.6 reference set. Net names are not a substitute for connectivity;
deliberate rewires and the service-only no-connect are explicit exceptions.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument("--export", type=Path, required=True)
parser.add_argument("--erc", type=Path, required=True)
parser.add_argument("--expected-sha256", required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
here = Path(__file__).resolve().parent
source = here.parent / "ups_v4" / "ups12v_v4.kicad_sch"
baseline = here / "phase2-6-review.net.xml"
digest = hashlib.sha256(source.read_bytes()).hexdigest()
assert digest == args.expected_sha256, "Saved CAD changed after hash capture"
for artifact in (args.export, args.erc):
    assert artifact.stat().st_mtime >= source.stat().st_mtime, "Stale artifact"


def read(path):
    nets = {}
    for net in ET.parse(path).findall("./nets/net"):
        name = net.attrib["name"].lstrip("/")
        assert name not in nets, f"duplicate normalized net name: {name!r} in {path}"
        nets[name] = {(node.attrib["ref"], node.attrib["pin"])
                      for node in net.findall("node")
                      if "no_connect" not in node.attrib.get("pintype", "")}
    return nets


before, after = read(baseline), read(args.export)
old_pins = {pin for pins in before.values() for pin in pins}
new_pins = {pin for pins in after.values() for pin in pins}

# R11 is retained as a connector-side service sense. Pin 1 remains on
# CHG_REQ; pin 2 is deliberately no-connect because external CHG_REQ must not
# be a charge-enable source. The retained R50/MAIN_3V3 path drives the isolated
# main-domain Q6/Q7 CE stage instead.
allowed_missing = {("R11", "2")}
assert old_pins - new_pins <= allowed_missing, sorted(old_pins - new_pins)


def projected_partitions(nets):
    return collections.Counter(
        frozenset(pin for pin in pins if pin in old_pins)
        for pins in nets.values()
        if frozenset(pin for pin in pins if pin in old_pins)
    )


expected = []
for pins in before.values():
    kept = set(pins) - allowed_missing
    if kept:
        expected.append(frozenset(kept))

# If an earlier baseline already contained MCU USB pins, Phase 3.3 series
# links intentionally split those old partitions. The current Phase 2.6
# baseline has no U1 pins, so this branch remains data-driven.
for old_net, old_pin in (("USB_DP", ("U1", "27")),
                         ("USB_DN", ("U1", "26"))):
    if old_pin in before.get(old_net, set()):
        source_partition = next(p for p in expected if old_pin in p)
        expected.remove(source_partition)
        remainder = source_partition - {old_pin}
        if remainder:
            expected.append(frozenset(remainder))
        expected.append(frozenset({old_pin}))

actual = projected_partitions(after)
expected_counter = collections.Counter(expected)
assert actual == expected_counter, json.dumps({
    "missing_partitions": [sorted(p) for p, count in (expected_counter - actual).items()
                            for _ in range(count)],
    "unexpected_partitions": [sorted(p) for p, count in (actual - expected_counter).items()
                               for _ in range(count)],
}, indent=2)

# Preserve critical Phase 2.6 named rails in addition to the complete
# partition comparison. This catches an accidental rail rename while the
# partition check catches an accidental merge or split.
for name in ("VBUS", "VIN1", "GND", "PGND", "CE_N", "CE_BIAS",
             "SYS", "BATTERY", "REGN"):
    assert name in before and name in after, name
    assert (before[name] - allowed_missing) <= {
        pin for pins in after.values() for pin in pins if pin in before[name]
    }, name

assert {("Q3", "1"), ("R10", "1")} <= after["CHG_GATE"]
assert ("R11", "1") in after["CHG_REQ"]
assert ("R11", "2") not in new_pins
assert ("R50", "1") in after["MAIN_3V3"]

erc = json.loads(args.erc.read_text(encoding="utf-8"))
result = {
    "source_sha256": digest,
    "baseline_sha256": hashlib.sha256(baseline.read_bytes()).hexdigest(),
    "export_sha256": hashlib.sha256(args.export.read_bytes()).hexdigest(),
    "erc_sha256": hashlib.sha256(args.erc.read_bytes()).hexdigest(),
    "all_phase2_6_old_reference_pins_preserved": True,
    "all_phase2_6_connected_pin_partitions_preserved": True,
    "old_reference_count": len({ref for ref, _ in old_pins}),
    "old_connected_pin_count": len(old_pins),
    "allowed_missing_old_pins": ["R11.2"],
    "intentional_phase3_2_rewires": [
        {
            "reference_pin": "R11.2",
            "from_net": "CHG_GATE",
            "to_net": None,
            "reason": "External CHG_REQ retained as DNP service sense; cannot enable charging",
        },
        {
            "reference_pin": "R50.1",
            "from_net": None,
            "to_net": "MAIN_3V3",
            "reason": "MAIN-derived Q6 bias preserves domain isolation; authorization supervisor removed",
        },
    ],
    "expected_partition_count": sum(expected_counter.values()),
    "actual_partition_count": sum(actual.values()),
    "erc_errors": erc["errors"],
    "erc_warnings": erc["warnings"],
    "scope": "Complete Phase 2.6 pin partitions projected to old references; explicit service NC and MAIN domain isolation additions",
    "not_claimed": ["PCB parity", "component/package suitability", "hardware qualification"],
}
args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in (
    "all_phase2_6_old_reference_pins_preserved",
    "all_phase2_6_connected_pin_partitions_preserved",
    "old_reference_count", "old_connected_pin_count", "allowed_missing_old_pins",
    "expected_partition_count", "actual_partition_count", "erc_errors", "erc_warnings")}))
