"""Compile/run the real MQTT implementation with host transport/JSON stubs.

Checks scheduling, delivery retries, retention and discovery fields, not Arduino
JSON serialization or live MQTT/HA. Run from the repo root with Python and MSVC.
"""

import json
import os
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
output = root / ".pio" / "telemetry-check"
output.mkdir(parents=True, exist_ok=True)

stubs = {
    "Arduino.h": r"""
#pragma once
#include <cstdint>
#include <string>
using String = std::string;
class Stream {};
extern unsigned long testMillis;
inline unsigned long millis() { return testMillis; }
""",
    "Syslog.h": r"""
#pragma once
class Syslog {};
constexpr int LOG_ERR = 3;
""",
    "ArduinoJson.h": r"""
#pragma once
#include <map>
#include <sstream>
#include <string>
inline std::map<std::string, std::string> jsonFields, serializedFields;
struct JsonArray { void add(const String&) {} };
struct JsonValue {
  std::string path;
  JsonValue operator[](const char* key) { return {path.empty() ? key : path + "/" + key}; }
  template<typename T> void operator=(const T& value) {
    std::ostringstream stream;
    stream << std::boolalpha << value;
    jsonFields[path] = stream.str();
  }
  template<typename T> T to() { return T{}; }
};
struct JsonDocument : JsonValue { JsonDocument() { jsonFields.clear(); } };
inline void serializeJson(JsonDocument&, String& output) { serializedFields = jsonFields; output = "{}"; }
""",
    "PubSubClient.h": r"""
#pragma once
#include <vector>
enum { MQTT_CONNECTION_TIMEOUT=-4, MQTT_CONNECTION_LOST=-3, MQTT_CONNECT_FAILED=-2, MQTT_DISCONNECTED=-1,
       MQTT_CONNECTED=0, MQTT_CONNECT_BAD_PROTOCOL=1, MQTT_CONNECT_BAD_CLIENT_ID=2, MQTT_CONNECT_UNAVAILABLE=3,
       MQTT_CONNECT_BAD_CREDENTIALS=4, MQTT_CONNECT_UNAUTHORIZED=5 };
struct Message {
  String topic, value;
  bool retained;
  std::map<std::string, std::string> fields;
};
class PubSubClient {
 public:
  bool online = true, failNext = false;
  std::vector<Message> messages;
  bool connected() { return online; }
  int state() { return online ? MQTT_CONNECTED : MQTT_DISCONNECTED; }
  bool publish(const char* topic, const char* value, bool retained) {
    if (!online || failNext) { failNext = false; return false; }
    messages.push_back({topic, value, retained, serializedFields});
    return true;
  }
};
""",
}
for name, content in stubs.items():
    (output / name).write_text(content, encoding="utf-8")

# Ensure every allowlisted name is present in the installed library; no flags/masks/MPPT.
policy = (root / "include" / "telemetry_policy.h").read_text()
names = re.findall(r'"([A-Z0-9_]+)"', policy)
definitions = next((root / ".pio/libdeps/ups4/BQ25798").rglob("chip_definitions.json"))
settings = {entry["name"] for entry in json.loads(definitions.read_text())["settings"]}
assert len(names) == len(set(names)), "Duplicate policy entry"
assert not set(names) - settings, f"Unknown registers: {set(names) - settings}"
assert not any(name.endswith(("_MASK", "_FLAG")) or "MPPT" in name or name.startswith("VOC_") for name in names)
grafana_registers = {
    "AC1_PRESENT_STAT", "CHG_STAT", "DIS_ACDRV", "EN_ACDRV1", "EN_BACKUP", "EN_CHG", "EN_OTG", "IBAT_ADC", "IBUS_ADC",
    "PG_STAT", "TDIE_ADC", "TS_ADC", "VAC1_ADC", "VBAT_ADC", "VBUS_ADC", "VBUS_STAT", "VINDPM_STAT", "VSYS_ADC",
}
periodic_names = set(re.findall(r'"([A-Z0-9_]+)"', policy.split("changeOnly[]")[0]))
assert grafana_registers <= periodic_names, f"Missing Grafana periodic registers: {grafana_registers - periodic_names}"

compiler = sorted(Path(os.environ["ProgramFiles"]).glob("Microsoft Visual Studio/*/*/VC/Tools/MSVC/*/bin/Hostx64/x64/cl.exe"))[-1]
msvc = compiler.parents[3]
sdk = Path(os.environ["ProgramFiles(x86)"]) / "Windows Kits/10"
sdk_version = sorted((sdk / "Lib").glob("10.*"))[-1].name
includes = [output, root / "include", msvc / "include"]
includes += [sdk / "Include" / sdk_version / name for name in ("ucrt", "shared", "um")]
libraries = [msvc / "lib/x64", sdk / "Lib" / sdk_version / "ucrt/x64", sdk / "Lib" / sdk_version / "um/x64"]
for mode in ("production", "debug"):
    executable = output / f"telemetry_test_{mode}.exe"
    flags = ["/DDEBUG_BQ25798_SETTINGS"] if mode == "debug" else []
    subprocess.run(
        [str(compiler), "/nologo", "/std:c++17", "/EHsc", "/W4"]
        + flags
        + [f"/I{path}" for path in includes]
        + [str(root / "src/homeassistant_mqtt.cpp"), str(root / "tests/telemetry_test.cpp"), f"/Fe:{executable}", "/link"]
        + [f"/LIBPATH:{path}" for path in libraries],
        cwd=output,
        check=True,
    )
    subprocess.run([str(executable)], cwd=output, check=True)
print(f"PASS: {len(names)} selected registers exist; masks, interrupt flags and MPPT excluded")
