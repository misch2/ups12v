# Predictable HA entity defaults - 2026-11-18

The shared firmware discovery serializer adds `default_entity_id` as
`<component>.<normalized deviceName_config_key>`. Normalization lowercases the
object part and replaces characters outside ASCII letters, digits and underscore
with underscore. Existing `unique_id`, names and MQTT topics are preserved.

## Verification

- Reviewed the focused firmware/README diff; `git diff --check` passed.
- Read-only, five-second MQTT subscription scoped to
  `homeassistant/+/esp77-bq25798-ups5/+/config`, with a unique client ID.
  Connection settings were read locally; no application messages were published.
- Received 134 retained configs, saved in `discovery-before.jsonl`.
  Retained discovery does not prove current device health or firmware version.
- `projected-analysis.json` records the expected new ID for each captured config
  and sizes after adding that field to compact JSON. Zero normalized ID collisions
  among the captured configs. Maximum projected PubSubClient buffer requirement
  is 1,007 bytes, including its conservative five-byte header reservation,
  two-byte topic-length field, UTF-8 topic and payload; configured buffer is 2,048.
- VBAT, all three AC1 presence representations, charging inhibit and reset button
  have the agreed defaults documented in `software/ups/README.md`.

These are broker-data projections and code review, not behavioral execution of
the changed production module. Coverage is limited to captured UPS5 configs;
future/debug entities and other board payloads were not measured. No source-text
assertions, function extraction, firmware build/upload, charger commands or HA
registry edits were used. A host compiler was not on PATH; Docker host validation
was unavailable because access to its configuration/engine was denied.

Owner validation pending: build affected firmware, upload through the separately
authorized workflow, then check that a newly registered entity receives its
specified ID despite an HA device friendly-name change, existing entities retain
their IDs, and MQTT reconnect republishes the field. Test against an unused ID;
HA can append a suffix when the requested ID is occupied.
