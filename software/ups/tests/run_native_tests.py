"""Compile and run production-module behavioral tests with host platform substitutes."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
CODEC_STORE = ["src/settings_codec.cpp", "src/settings_store.cpp"]
SUITES = {
    "charge_current": ["tests/charge_current_test.cpp"],
    "charge_profile": ["tests/charge_profile_test.cpp"],
    "settings_store": ["tests/settings_store_test.cpp", *CODEC_STORE, "src/settings_nvs.cpp"],
    "boot_network": ["tests/boot_network_test.cpp", "src/boot_settings.cpp", *CODEC_STORE,
                     "src/homeassistant_mqtt.cpp", "src/network_worker.cpp"],
    "settings_service": ["tests/settings_service_test.cpp", "src/settings_service.cpp", *CODEC_STORE],
    "config_web": ["tests/config_web_test.cpp", "src/config_http.cpp", "src/config_web.cpp", "src/config_web_server.cpp",
                   "src/recovery.cpp", "src/wifi_settings.cpp", "src/wifi_settings_esp32.cpp", "src/settings_service.cpp", "src/firmware_update.cpp", *CODEC_STORE],
    "recovery": ["tests/recovery_test.cpp", "src/recovery.cpp", "src/recovery_esp32.cpp", "src/boot_settings.cpp",
                 "src/wifi_settings.cpp", "src/settings_service.cpp", *CODEC_STORE],
    "firmware_update": ["tests/firmware_update_test.cpp", "src/firmware_update.cpp"],
    "firmware_update_worker": ["tests/firmware_update_worker_test.cpp", "src/firmware_update.cpp", "src/firmware_update_esp32.cpp"],
    "firmware_update_mqtt": ["tests/firmware_update_mqtt_test.cpp", "src/firmware_update.cpp", "src/firmware_update_mqtt.cpp", "src/homeassistant_mqtt.cpp"],
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default="g++")
    parser.add_argument("--json-include", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / ".tmp/firmware-host-tests")
    parser.add_argument("--suite", action="append", choices=SUITES)
    args = parser.parse_args(argv)
    compiler = shutil.which(args.compiler)
    if not compiler:
        parser.error("host g++ compiler unavailable; provide --compiler with its path")
    candidates = sorted((PROJECT / ".pio/libdeps").glob("*/ArduinoJson/src"))
    include = args.json_include or (candidates[0] if candidates else None)
    if not include or not include.is_dir():
        parser.error("ArduinoJson headers unavailable; build a target first or provide --json-include")
    args.output.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PATH"] = str(Path(compiler).parent) + os.pathsep + environment.get("PATH", "")
    for name in args.suite or SUITES:
        executable = args.output.resolve() / (name + (".exe" if os.name == "nt" else ""))
        command = [compiler, "-std=c++11", "-Wall", "-Wextra", "-Werror", "-I" + str(PROJECT / "tests/support"),
                   "-I" + str(PROJECT / "include"), "-I" + str(include.resolve()),
                   *(str(PROJECT / path) for path in SUITES[name]), "-o", str(executable)]
        result = subprocess.run(command, capture_output=True, text=True, env=environment)
        log = args.output / (name + "-compile.log")
        log.write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            print(f"{name}: compile failed; see {log}", file=sys.stderr)
            print("\n".join((result.stdout + result.stderr).splitlines()[-10:]), file=sys.stderr)
            return 1
        run = [str(executable)]
        fixture = args.output.resolve() / "firmware-update-wire.json"
        if name == "firmware_update_mqtt":
            run.append(str(fixture))
        result = subprocess.run(run, capture_output=True, text=True, env=environment)
        log = args.output / (name + "-run.log")
        log.write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            print(f"{name}: behavioral test failed; see {log}\n{result.stdout}{result.stderr}", file=sys.stderr)
            return 1
        print(name + ": PASS")
        if name == "firmware_update_mqtt":
            rendered = subprocess.run([sys.executable, str(PROJECT / "tests/mqtt_templates_test.py"), str(fixture)],
                                      capture_output=True, text=True, env=environment)
            log = args.output / "mqtt-templates-run.log"
            log.write_text(rendered.stdout + rendered.stderr, encoding="utf-8")
            if rendered.returncode:
                print(f"MQTT template rendering failed; see {log}\n{rendered.stdout}{rendered.stderr}", file=sys.stderr)
                return 1
            print("mqtt_templates: PASS (4 sandbox rendering checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
