"""Independent all-connected-pin partition review against accepted Phase 3.1.

Only declared changes: R11.2 becomes a service no-connect; U1.26/27 get USB links.
This checks connectivity preservation, not electrical suitability or hardware.
"""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "ups_v4/ups12v_v4.kicad_sch"
CURRENT = HERE / "phase3-2-mcu-power.net.xml"
ERC = HERE / "phase3-2-erc-clean.json"
BASELINE = HERE / "phase3-1-mcu-usb.net.xml"


def partitions(path):
    root = ET.parse(path).getroot()
    comps = {c.attrib["ref"]: c for c in root.findall("./components/comp")}
    nets = {n.attrib["name"]: frozenset((p.attrib["ref"], p.attrib["pin"])
                                       for p in n.findall("node"))
            for n in root.findall("./nets/net")}
    return comps, nets


before_comps, before = partitions(BASELINE)
after_comps, after = partitions(CURRENT)
assert set(before_comps) <= set(after_comps), "Old component removed"
old_pins = set().union(*before.values())
new_pins = set().union(*after.values())
declared_no_connect = {("R11", "2")}
assert old_pins <= new_pins, f"Unexpected lost pins: {old_pins - new_pins}"
declared_splits = {("U1", "26"), ("U1", "27"), ("R11", "2")}
assert declared_splits <= old_pins
expected = {pins - declared_splits - declared_no_connect for pins in before.values()}
expected.discard(frozenset())
expected.update(frozenset([p]) for p in declared_splits)
actual = {pins & old_pins for pins in after.values()}
actual.discard(frozenset())
assert actual == expected, {
    "unexpected_missing_or_split": [sorted(p) for p in expected - actual],
    "unexpected_joined_or_changed": [sorted(p) for p in actual - expected],
}
assert any(name.startswith("unconnected-") and pins == frozenset(declared_no_connect)
           for name, pins in after.items()), "R11 service no-connect not exported"
for ref, old in before_comps.items():
    if ref == "U1":
        continue  # Deliberate N4X value and project-local footprint selection.
    for field in ("value", "footprint"):
        if ref == "R11" and field == "value":
            assert after_comps[ref].findtext(field) == "4k7 SERVICE CHG_REQ SENSE DNP"
            continue
        if ref == "U2" and field == "footprint":
            assert after_comps[ref].findtext(field) == "Package_TO_SOT_SMD:Texas_DRT-3"
            continue
        assert old.findtext(field) == after_comps[ref].findtext(field), (ref, field)
for artifact in (CURRENT, ERC):
    assert artifact.stat().st_mtime_ns >= SOURCE.stat().st_mtime_ns, "Stale evidence"
erc = json.loads(ERC.read_text(encoding="utf-8"))
assert erc["errors"] == 0, "ERC errors remain"
result = {
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
    "export_sha256": hashlib.sha256(CURRENT.read_bytes()).hexdigest(),
    "erc_sha256": hashlib.sha256(ERC.read_bytes()).hexdigest(),
    "baseline_reference_count": len(before_comps),
    "baseline_connected_pin_count": len(old_pins),
    "all_connected_pin_partitions_match_explicit_expected_changes": True,
    "declared_pin_splits": sorted(declared_splits),
    "declared_service_no_connect": sorted(declared_no_connect),
    "old_properties_preserved_except_U1_N4X_R11_service_U2_DRT3": True,
    "erc_errors": erc["errors"], "erc_warnings": erc["warnings"],
    "limits": "Does not validate new circuit behavior, unconnected NC pin geometry, PCB or hardware",
}
(HERE / "phase3-2-independent-preservation.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, separators=(",", ":")))
