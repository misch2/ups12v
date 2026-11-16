"""Read-only, bounded UPS MQTT capture; never publishes application messages.

Example (from repository root):
  python hardware/v4/tools/capture_mqtt.py --output hardware/v4/evidence/mqtt-ups4-test --duration 1800

Connection settings are read locally from .codex/mqtt-credentials.txt and are
never copied to the capture. Requires paho-mqtt 1.x. Create output directories
per run. Create a STOP file there to end a background capture early.
"""

import argparse
import json
import os
from pathlib import Path
import re
import signal
import ssl
import time
from datetime import datetime, timezone
from uuid import uuid4

import paho.mqtt.client as mqtt


def now():
    return datetime.now(timezone.utc).isoformat()


def credentials(path):
    result = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        result[key.strip().lower()] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration", type=int, default=1800)
    parser.add_argument("--device", default="esp76-bq25798-ups4")
    args = parser.parse_args()
    if args.duration <= 0:
        parser.error("duration must be positive")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.device):
        parser.error("device must be a single device name without MQTT wildcards")
    root = Path(__file__).resolve().parents[3]
    connection = credentials(root / ".codex/mqtt-credentials.txt")
    args.output.mkdir(parents=True, exist_ok=True)
    if (args.output / "messages.jsonl").exists():
        parser.error("output already contains a capture")
    topic = f"bq25798ups/{args.device}/state/#"
    started = time.monotonic()
    status = {
        "pid": os.getpid(), "started_at": now(), "duration_seconds": args.duration,
        "topic": topic, "read_only": True, "connected": False,
        "subscribed": False, "messages": 0, "retained_messages": 0,
        "live_messages": 0, "last_live_at": None, "finished": False,
    }
    latest_live = {}
    retained_topics = set()
    stopping = False

    def stop(*_):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    def save_json(name, data):
        destination = args.output / name
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(destination)

    with (args.output / "messages.jsonl").open("x", encoding="utf-8", buffering=1) as messages, \
            (args.output / "events.jsonl").open("x", encoding="utf-8", buffering=1) as events:
        def event(kind, **fields):
            events.write(json.dumps({"timestamp": now(), "event": kind, **fields}) + "\n")

        client = mqtt.Client(client_id="ups4-monitor-" + uuid4().hex[:16], clean_session=True)
        if connection.get("username"):
            client.username_pw_set(connection["username"], connection.get("password"))
        port = int(connection.get("port", "1883"))
        tls_setting = connection.get("tls", "").lower()
        if tls_setting in ("1", "true", "yes", "on") or port == 8883 or connection.get("tls_ca"):
            client.tls_set(ca_certs=connection.get("tls_ca"), certfile=connection.get("tls_cert"),
                           keyfile=connection.get("tls_key"), cert_reqs=ssl.CERT_REQUIRED)
        client.reconnect_delay_set(min_delay=1, max_delay=15)

        def on_connect(client, userdata, flags, rc):
            status["connected"] = rc == 0
            status["subscribed"] = False
            event("connect", result=rc)
            if rc == 0:
                client.subscribe(topic, qos=0)

        def on_subscribe(client, userdata, mid, granted_qos):
            status["subscribed"] = bool(granted_qos) and all(q != 128 for q in granted_qos)
            event("subscribe", accepted=status["subscribed"])

        def on_disconnect(client, userdata, rc):
            status["connected"] = False
            status["subscribed"] = False
            event("disconnect", result=rc)

        def on_message(client, userdata, message):
            timestamp = now()
            record = {"timestamp": timestamp, "topic": message.topic,
                      "payload": message.payload.decode("utf-8", errors="replace"),
                      "retained": bool(message.retain), "qos": message.qos}
            messages.write(json.dumps(record, ensure_ascii=False) + "\n")
            status["messages"] += 1
            if message.retain:
                status["retained_messages"] += 1
                retained_topics.add(message.topic)
            else:
                status["live_messages"] += 1
                status["last_live_at"] = timestamp
                latest_live[message.topic] = record

        client.on_connect = on_connect
        client.on_subscribe = on_subscribe
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        event("start", duration_seconds=args.duration, topic=topic)
        client.connect_async(connection["host"], port, keepalive=30)
        next_save = 0
        needs_reconnect = True
        try:
            # Single-threaded loop keeps status and file snapshots consistent.
            while not stopping and time.monotonic() - started < args.duration and not (args.output / "STOP").exists():
                try:
                    if needs_reconnect:
                        client.reconnect()
                        needs_reconnect = False
                    if client.loop(timeout=1.0) != mqtt.MQTT_ERR_SUCCESS:
                        needs_reconnect = True
                except (OSError, mqtt.WebsocketConnectionError):
                    needs_reconnect = True
                    event("connection_retry")
                    time.sleep(2)
                if time.monotonic() >= next_save:
                    status["elapsed_seconds"] = round(time.monotonic() - started, 1)
                    status["unique_live_topics"] = len(latest_live)
                    status["unique_retained_topics"] = len(retained_topics)
                    save_json("latest-live.json", latest_live)
                    save_json("status.json", status)
                    next_save = time.monotonic() + 5
        finally:
            client.disconnect()
            status["connected"] = False
            status["subscribed"] = False
            status["finished"] = True
            status["ended_at"] = now()
            status["elapsed_seconds"] = round(time.monotonic() - started, 1)
            status["unique_live_topics"] = len(latest_live)
            status["unique_retained_topics"] = len(retained_topics)
            save_json("latest-live.json", latest_live)
            save_json("status.json", status)
            event("stop")


if __name__ == "__main__":
    main()
