# Universal firmware checkpoint 3

Date: 2026-11-25. Baseline: `5086657`. Scope: saved-settings boot, session identity
and cooperative network connection attempts. No checkpoint 4 configuration service.

Saved records are authoritative before clients initialize. Missing records alone
may be seeded; invalid/unsupported records are preserved without compiled fallback.
V4 ARM stays LOW on failure, with best-effort EN_CHG-off/readback on legacy boards.
USB and saved-Wi-Fi OTA remain available under a MAC-specific service hostname.
The blocking portal no longer runs; replacement LAN/AP forms are later work.

Identity freezes per session. The actual HA serializer retains its existing topic,
unique-ID and default-entity-ID formulas. New ID validation avoids truncation and
case/underscore aliases. A connection worker isolates DNS/TCP/MQTT waits and owns
the client exclusively until a queue result hands it back. Normal publication and
OTA retain the existing libraries' main-loop waits; no real-time guarantee is made.

Three native boot/discovery/worker test groups pass; see
[boot-network-tests.txt](boot-network-tests.txt). The five checkpoint 2 persistence
groups also pass with the updated text adapter. Production modules compile with
C++11, -Wall -Wextra -Werror, real ArduinoJson 7.4.3 and substituted platform APIs.
No source extraction, local credentials or live broker is involved. Installed SDK
headers were checked for hostname size, OTA, queue/task and client APIs; a native
test symbol also represents Arduino's global Network object to catch collisions.

Tests cover boot precedence, protected/blank/error paths, immutable identity,
actual serializer IDs in two legacy namespaces, publisher isolation while work
is pending, DNS/task failures and retry rollover. Queue scheduling is simulated.
Main-loop integration and the unconfigured charger branch received focused source
review. No firmware target build/upload, real flash/network operation or hardware
test was performed. Binary/OTA-slot sizes, heap/stack and matching 2S/4S power/network
validation remain owner checks. Instructions: [STARTUP.md](../../../../software/ups/STARTUP.md).
