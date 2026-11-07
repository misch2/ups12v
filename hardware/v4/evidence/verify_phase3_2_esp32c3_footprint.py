"Read back the project-local ESP32-C3-MINI-1-N4X footprint geometry."
import hashlib
import json
import re
from pathlib import Path

path = Path(__file__).parent.parent / "ups_v4" / "ups_v4.pretty" / "ESP32-C3-MINI-1-N4X.kicad_mod"
text = path.read_text(encoding="utf-8")
pads = re.findall(r'\(pad "([^"]+)" smd [^\n]*?\(at ([^ ]+) ([^ )]+)', text)
numbers = [number for number, _, _ in pads]
centers = [(float(x), float(y)) for number, x, y in pads if number == "49"]
result = {
    "footprint": str(path),
    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "physical_pad_count": len(pads),
    "unique_pad_count": len(set(numbers)),
    "pad49_segment_count": len(centers),
    "pad49_centers_mm": centers,
    "expected_center_array_mm": 5.4,
    "expected_center_offsets_mm": [-1.975, 0.0, 1.975],
    "courtyard_present": "F.CrtYd" in text,
    "source": "Espressif ESP32-C3-MINI-1 Datasheet v2.2 Section 11.1 Figure 11-1",
    "source_files": [
        "hardware/v4/evidence/references/esp32-c3-mini-1-v2.2.pdf",
        "hardware/v4/evidence/references/esp32-c3-mini-1-v2.2-land.png",
    ],
    "scope": "Schematic footprint readback only; no PCB placement or thermal-via validation",
}
assert result["physical_pad_count"] == 61
assert result["unique_pad_count"] == 53
assert result["pad49_segment_count"] == 9
assert sorted({round(x, 3) for x, _ in centers}) == [-1.975, 0.0, 1.975]
assert sorted({round(y, 3) for _, y in centers}) == [-1.975, 0.0, 1.975]
assert result["courtyard_present"]
out = path.parent.parent.parent / "evidence" / "phase3-2-esp32c3-footprint-readback.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: result[key] for key in (
    "physical_pad_count", "unique_pad_count", "pad49_segment_count",
    "expected_center_array_mm", "courtyard_present", "sha256")}))
