"""Extract real serviceInputDetection for the native fault-injection tests.

Run from repository root: python software/ups/tests/input_detection_host_check.py
Compile tests/input_detection_test.cpp with include/ and the printed output
directory on the include path, then run the executable. No hardware is used.
"""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "src/UPS.ino").read_text(encoding="utf-8")
signature = "bool serviceInputDetection() {"
start = source.index(signature)
opening = source.index("{", start)
depth = 1
end = opening + 1
while depth:
    depth += (source[end] == "{") - (source[end] == "}")
    end += 1

assert "!checkForError() && applyChargeProfile() && serviceInputDetection()" in source
assert "inputDetectionRetry.resetInput();" in source.split("bool onetimeSetupIfNeeded(", 1)[1].split("bool serviceInputDetection()", 1)[0]
board = (root / "include/boards/v4/ups4_esp76/board_config.h").read_text()
assert "cfg.power.input.retryUnqualifiedAdapter = true;" in board
assert "bool retryUnqualifiedAdapter = false;" in (root / "include/config.h").read_text()
for legacy in ("example", "ups1_esp18", "ups2_esp27", "ups3_esp19"):
    assert "retryUnqualifiedAdapter = true" not in (root / f"include/boards/{legacy}/board_config.h").read_text()

output = root / ".pio/input-detection-check"
output.mkdir(parents=True, exist_ok=True)
(output / "input_detection_service.inc").write_text(source[start:end] + "\n", encoding="utf-8")
print(f"Generated serviceInputDetection fixture in {output}")
