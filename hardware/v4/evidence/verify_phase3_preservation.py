"""Check all previously exported pin partitions after additive Phase 3 work.

Does not validate newly added circuits, package suitability, PCB or hardware.
Never mutates CAD. Do not use once intentional old-circuit rewiring is needed
without recording and implementing the explicit expected changes separately.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
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
    return {n.attrib["name"]: {(p.attrib["ref"], p.attrib["pin"])
                              for p in n.findall("node")}
            for n in ET.parse(path).findall("./nets/net")}


before, after = read(baseline), read(args.export)
old_refs = {r for pins in before.values() for r, p in pins}
projected = {name: {(r, p) for r, p in pins if r in old_refs}
             for name, pins in after.items()}
before_sets = {frozenset(pins) for pins in before.values() if pins}
after_sets = {frozenset(pins) for pins in projected.values() if pins}
assert before_sets == after_sets, {
    "missing_or_split": [sorted(s) for s in before_sets - after_sets],
    "unexpected_or_merged": [sorted(s) for s in after_sets - before_sets],
}
for name in ("VBUS", "VIN1", "GND", "PGND", "CE_N", "CE_BIAS",
             "SYS", "BATTERY", "REGN"):
    assert projected[name] == before[name], "Critical net renamed or changed: " + name
erc = json.loads(args.erc.read_text(encoding="utf-8"))
result = {
    "source_sha256": digest,
    "baseline_sha256": hashlib.sha256(baseline.read_bytes()).hexdigest(),
    "export_sha256": hashlib.sha256(args.export.read_bytes()).hexdigest(),
    "erc_sha256": hashlib.sha256(args.erc.read_bytes()).hexdigest(),
    "all_phase2_6_old_reference_pin_partitions_preserved": True,
    "old_reference_count": len(old_refs),
    "old_connected_pin_count": sum(map(len, before.values())),
    "new_reference_count": len({r for pins in after.values() for r, p in pins} - old_refs),
    "erc_errors": erc["errors"], "erc_warnings": erc["warnings"],
    "scope": "Old-circuit preservation only; new circuits need separate endpoint checks",
    "not_claimed": ["New block electrically accepted", "Clean ERC", "PCB parity",
                    "Component/package suitability", "Hardware qualification"],
}
args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in (
    "all_phase2_6_old_reference_pin_partitions_preserved", "old_reference_count",
    "old_connected_pin_count", "erc_errors", "erc_warnings")}))
