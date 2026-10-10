"""Read-only extraction of accepted Phase 2.6 evidence; not a new simulation."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent
netlist = root / "phase2-6-review.net.xml"
model = root / "phase2-6-hotplug-rlc.json"
nets = {
    net.attrib["name"]: sorted(
        (n.attrib["ref"], n.attrib["pin"]) for n in net.findall("node")
    ) for net in ET.parse(netlist).findall("./nets/net")
}
assert ("IC1", "9") in nets["VIN1"]
assert ("C9", "1") in nets["VIN1"]
assert ("R12", "1") in nets["VIN1"]
assert ("IC1", "2") in nets["VBUS"]
assert ("IC1", "3") in nets["VBUS"]
assert set(nets["VIN1"]).isdisjoint(nets["VBUS"])
data = json.loads(model.read_text())
selections = [
    (1.0, 0.2, 0.1, 2.2, 2.142),
    (1.0, 0.05, 0.1, 1.2260464879128656, 1.862),
    (10.0, 0.05, 0.1, 1.2260464879128656, 1.862),
    (1.0, 0.05, 10.0, 2.2, 2.142),
]
rows = []
for key in selections:
    matches = [r for r in data["rows"] if tuple(r[k] for k in
               ("L_uH", "Rs_ohm", "Cin_uF", "Cd_uF", "Rd_ohm")) == key]
    assert len(matches) == 1
    rows.append(matches[0])
result = {
    "date": "2026-10-10", "status": "OPEN_NO_HARDWARE_ACCEPTANCE",
    "scope": "Accepted phase2-6 exports and existing calculated cases only",
    "inputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (netlist, model)},
    "VIN1_nodes": nets["VIN1"], "VBUS_nodes": nets["VBUS"],
    "worst_model_voltage": data["worst_voltage"], "selected_cases": rows,
    "limitations": ["Single-node model does not resolve VIN1/VBUS FET states",
                    "No cable impedance measurements or guaranteed Ceff bounds",
                    "No new simulation; no CAD change; no hardware measurement"],
}
output = root / "phase3-vac1-review-summary.json"
output.write_text(json.dumps(result, indent=2) + "\n")
print("OPEN: VAC1 on VIN1 verified; VIN1/VBUS distinct; 4 prior cases extracted")
