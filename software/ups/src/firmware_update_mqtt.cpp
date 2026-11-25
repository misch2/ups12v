#include "firmware_update_mqtt.h"

#include <cstring>

namespace FirmwareUpdate {
void Mqtt::connected(const char* value) {
  nonce = value && std::strlen(value) == 32 && std::strspn(value, "0123456789abcdef") == 32 ? value : "";
  configured = false;
  advertisedVersion = "";
  entity.hasSentState = false;
  haveSnapshot = false;
}

bool Mqtt::handleCommand(const char* topic, const uint8_t* payload, size_t length) {
  if (!topic || commandTopic() != topic) return false;
  Error error = Error::VERSION;
  if (configured && payloadInstall.length() && payload && length == payloadInstall.length() && std::memcmp(payload, payloadInstall.c_str(), length) == 0) {
    error = control.requestInstall(advertisedVersion.c_str());
  }
  service.recordCommandResult(error);
  return true;
}

void Mqtt::publish() {
  if (!mqtt.readyToPublish()) return;
  Snapshot current;
  current.state = service.state();
  current.error = service.error();
  current.commandError = service.commandError();
  current.pending = service.checkPending();
  current.available = service.available();
  current.offer = service.offerRevision();
  current.installable = current.available && nonce.length() && control.validateInstall(service.offer().version) == Error::NONE;
  current.progress = service.downloadProgress();
  const bool changed = !haveSnapshot || current.state != last.state || current.error != last.error || current.commandError != last.commandError ||
                       current.pending != last.pending || current.available != last.available || current.installable != last.installable ||
                       current.offer != last.offer;
  if (configured && !changed) {
    if (current.progress.bytes == last.progress.bytes && current.progress.total == last.progress.total) return;
    if (uint32_t(millis() - lastPublished) < 1000) return;  // Progress at most once per second; transitions publish immediately.
  }
  const bool installable = current.installable;
  const String payload = installable ? String("INSTALL ") + service.offer().version + " " + nonce : String();
  if (!configured || payload != payloadInstall) {
    payloadInstall = payload;
    if (!mqtt.publishConfiguration(&entity, payloadInstall.c_str())) {
      configured = false;
      return;
    }
    configured = true;
    advertisedVersion = installable ? service.offer().version : "";
  }
  const auto state = stateJson(service);
  mqtt.publishStateIfNeeded(&entity, state.c_str());
  if (entity.hasSentState && entity.lastSentValue == state.c_str()) {
    last = current;
    haveSnapshot = true;
    lastPublished = millis();
  }
}
}  // namespace FirmwareUpdate
