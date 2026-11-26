#include "firmware_update.h"

#include <ArduinoJson.h>

#include <algorithm>
#include <cstring>

namespace FirmwareUpdate {
namespace {
constexpr const char* kReleaseBase = "https://github.com/misch2/ups12v/releases/";
template <size_t N>
bool copy(const char* value, char (&output)[N]) {
  if (!value || std::strlen(value) >= N) return false;
  std::memcpy(output, value, std::strlen(value) + 1);
  return true;
}
template <size_t N>
bool field(JsonObjectConst object, const char* key, char (&output)[N]) {
  const auto value = object[key].as<JsonString>();
  return !value.isNull() && std::strlen(value.c_str()) == value.size() && copy(value.c_str(), output);
}
bool validHash(const char* value) { return std::strlen(value) == 64 && std::strspn(value, "0123456789abcdef") == 64; }
}  // namespace

const char* variantName(const Hardware::Profile& hardware) {
  return hardware.version == Hardware::Version::V1_0            ? "ups_v1_esp32"
         : hardware.version == Hardware::Version::V3_3B_SYS_MOD ? "ups_v3_sys_esp32"
                                                                : "ups_v4_esp32c3";
}

bool parseVersion(const char* value, uint32_t& day, uint32_t& revision) {
  if (!value || std::strlen(value) < 10 || std::strlen(value) >= 24 || value[8] != '.') return false;
  day = revision = 0;
  for (int i = 0; i < 8; ++i) {
    if (value[i] < '0' || value[i] > '9') return false;
    day = day * 10 + value[i] - '0';
  }
  if (value[9] == '0' && value[10]) return false;
  for (const char* p = value + 9; *p; ++p) {
    if (*p < '0' || *p > '9' || revision > (UINT32_MAX - uint32_t(*p - '0')) / 10) return false;
    revision = revision * 10 + *p - '0';
  }
  const int year = day / 10000, month = day / 100 % 100, date = day % 100;
  const int days[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  const bool leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
  return year > 0 && month >= 1 && month <= 12 && date >= 1 && date <= days[month - 1] + (month == 2 && leap ? 1 : 0);
}
bool newer(const char* candidate, const char* installed) {
  uint32_t a, b, c, d;
  return parseVersion(candidate, a, b) && parseVersion(installed, c, d) && (a > c || (a == c && b > d));
}

Error parseManifest(const std::string& json, const Hardware::Profile& hardware, Candidate& output) {
  if (json.empty() || json.size() > kMaxManifestBytes || json.find('\0') != std::string::npos) return Error::MANIFEST;
  JsonDocument document;
  // The consumed byte count rejects a valid JSON prefix followed by a second document/garbage.
  struct Input {
    const std::string& text;
    size_t position = 0;
    explicit Input(const std::string& text) : text(text) {}
    int read() { return position < text.size() ? static_cast<unsigned char>(text[position++]) : -1; }
    size_t readBytes(char* bytes, size_t count) {
      count = std::min(count, text.size() - position);
      std::memcpy(bytes, text.data() + position, count);
      position += count;
      return count;
    }
  } input(json);
  if (deserializeJson(document, input) || document.overflowed() || !document.is<JsonObject>()) return Error::MANIFEST;
  if (json.find_first_not_of(" \r\n\t", input.position) != std::string::npos) return Error::MANIFEST;
  if (!document["schema"].is<int>() || document["schema"].as<int>() != 1) return Error::MANIFEST;
  Candidate candidate;
  const auto root = document.as<JsonObjectConst>();
  uint32_t day, revision;
  if (!field(root, "version", candidate.version) || !parseVersion(candidate.version, day, revision)) return Error::VERSION;
  if (!field(root, "release_url", candidate.releaseUrl) || !field(root, "release_summary", candidate.summary)) return Error::MANIFEST;
  const std::string releaseTag = std::string("fw-") + candidate.version;
  if (std::string(candidate.releaseUrl) != std::string(kReleaseBase) + "tag/" + releaseTag) return Error::URL;
  const auto variant = document["variants"][variantName(hardware)].as<JsonObjectConst>();
  if (variant.isNull()) return Error::HARDWARE;
  const auto identity = variant["hardware"].as<JsonObjectConst>();
  if (identity["version"] != hardware.versionName() || identity["mcu"] != (hardware.mcu() == Hardware::MCU::ESP32_C3 ? "esp32c3" : "esp32") ||
      identity["power_path"] != (hardware.powerPath() == Hardware::PowerPath::PMID_WITH_SWITCHOVER ? "pmid_switchover" : "sys"))
    return Error::HARDWARE;
  if (!field(variant, "url", candidate.url) ||
      std::string(candidate.url) != std::string(kReleaseBase) + "download/" + releaseTag + "/" + variantName(hardware) + ".bin")
    return Error::URL;
  if (!variant["size"].is<uint32_t>() || variant["size"].as<uint32_t>() < 24) return Error::LENGTH;
  candidate.size = variant["size"].as<uint32_t>();
  if (!field(variant, "sha256", candidate.sha256) || !validHash(candidate.sha256)) return Error::HASH;
  output = candidate;
  return Error::NONE;
}

Error Service::validateInstall(const char* version) const {
  if (busy || reserved()) return Error::BUSY;
  if (!haveOffer || !newer(candidate.version, installed)) return Error::NO_OFFER;
  if (!version || std::strcmp(version, candidate.version) != 0) return Error::VERSION;
  if (candidate.size > backend.capacity()) return Error::CAPACITY;
  return Error::NONE;
}
Error Service::requestInstall(const char* version) {
  lastCommandError = validateInstall(version);
  if (lastCommandError != Error::NONE) return lastCommandError;
  queued = true;
  currentState = State::INSTALL_QUEUED;
  lastError = Error::NONE;
  return Error::NONE;
}

std::string stateJson(const Service& service) {
  JsonDocument document;
  auto update = document["update"].to<JsonObject>();
  update["installed_version"] = service.installedVersion();
  update["title"] = "UPS firmware";
  update["in_progress"] = service.reserved();
  if (service.reserved()) {
    const auto& progress = service.downloadProgress();
    update["update_percentage"] = progress.total ? std::min(uint64_t(100), uint64_t(progress.bytes) * 100 / progress.total) : 0;
  } else
    update["update_percentage"] = nullptr;
  if (service.hasOffer()) {
    const auto& offer = service.offer();
    update["latest_version"] = newer(offer.version, service.installedVersion()) ? offer.version : service.installedVersion();
    update["release_url"] = offer.releaseUrl;
    update["release_summary"] = offer.summary;
  }
  auto details = document["details"].to<JsonObject>();
  details["status"] = stateName(service.state());
  details["error"] = errorName(service.error());
  details["command_error"] = errorName(service.commandError());
  details["checked"] = service.hasOffer();
  details["check_pending"] = service.checkPending();
  details["available"] = service.available();
  details["received_bytes"] = service.downloadProgress().bytes;
  details["total_bytes"] = service.downloadProgress().total;
  const auto& network = service.networkDiagnostics();
  auto diagnostics = details["network"].to<JsonObject>();
  diagnostics["stage"] = networkStageName(network.stage);
  diagnostics["http_status"] = network.httpStatus;
  diagnostics["sdk_error"] = network.sdkError;
  diagnostics["tls_sdk_error"] = network.tlsSdkError;
  diagnostics["tls_error"] = network.tlsError;
  diagnostics["verify_flags"] = network.verifyFlags;
  diagnostics["socket_errno"] = network.socketError;
  diagnostics["heap_before"] = network.heapBefore;
  diagnostics["largest_block_before"] = network.largestBefore;
  diagnostics["heap_at_failure"] = network.heapAtFailure;
  diagnostics["largest_block_at_failure"] = network.largestAtFailure;
  if (service.hasOffer()) details["feed_version"] = service.offer().version;
  std::string output;
  serializeJson(document, output);
  return output;
}
bool Service::cancelQueuedInstall() {
  if (!queued || busy) return false;
  queued = false;
  currentState = available() ? State::AVAILABLE : State::CURRENT;
  return true;
}
void Service::tick(uint32_t now, bool networkReady, bool timeReady, bool mayInstall) {
  Progress progress;
  while (backend.progress(progress))
    if (installing()) currentProgress = progress;
  Result result;
  if (busy && backend.poll(result)) {
    const bool wasInstalling = installing();
    busy = false;
    if ((result.kind == JobKind::INSTALL) != wasInstalling) {
      lastError = Error::WORKER;
      currentState = State::FAILED;
      return;
    }
    lastError = result.error;
    lastNetwork = result.network;
    ++networkGeneration;
    if (result.error != Error::NONE)
      currentState = State::FAILED;
    else if (result.kind == JobKind::CHECK) {
      candidate = result.candidate;
      haveOffer = true;
      ++offerGeneration;
      if (newer(candidate.version, installed) && candidate.size > backend.capacity()) {
        lastError = Error::CAPACITY;
        currentState = State::FAILED;
      } else
        currentState = available() ? State::AVAILABLE : State::CURRENT;
    } else {
      currentState = State::REBOOT_PENDING;
      currentProgress.bytes = currentProgress.total = candidate.size;
    }
    return;  // The caller observes completion before another job can start.
  }
  if (busy || rebootPending()) return;
  const uint32_t interval = lastError == Error::NETWORK || lastError == Error::WORKER ? 60000 : kCheckIntervalMs;
  if (!queued && !checkRequested && checked && uint32_t(now - lastCheck) < interval) return;
  if (!networkReady) {
    if (!queued) currentState = State::WAIT_NETWORK;
    return;
  }
  if (!timeReady) {
    if (!queued) currentState = State::WAIT_TIME;
    return;
  }
  if (queued) {
    if (!mayInstall) return;
    if (candidate.size > backend.capacity()) {
      queued = false;
      lastError = Error::CAPACITY;
      currentState = State::FAILED;
      return;
    }
    if (!backend.install(candidate)) {
      queued = false;
      lastError = Error::WORKER;
      currentState = State::FAILED;
      return;
    }
    queued = false;
    busy = true;
    currentProgress = Progress{};
    currentState = State::INSTALLING;
  } else {
    lastCheck = now;
    checked = true;
    checkRequested = false;
    if (!backend.check()) {
      lastError = Error::WORKER;
      currentState = State::FAILED;
      return;
    }
    busy = true;
    currentState = State::CHECKING;
  }
}

Error transfer(const Candidate& candidate, const Hardware::Profile& hardware, Source& source, Flash& flash, Digest& digest, Reporter& reporter) {
  if (candidate.size < 24 || (source.length() >= 0 && source.length() != candidate.size)) return Error::LENGTH;
  if (candidate.size > flash.capacity()) return Error::CAPACITY;
  if (!validHash(candidate.sha256)) return Error::HASH;
  uint8_t buffer[1024];
  size_t header = 0;
  while (header < 24) {
    const int count = source.read(buffer + header, 24 - header);
    if (count <= 0 || static_cast<size_t>(count) > 24 - header) return Error::NETWORK;
    header += count;
  }
  // ESP image format: common 8-byte header + extended header, chip_id at offset 12.
  // Espressif esptool ESP32FirmwareImage / target IMAGE_CHIP_ID: ESP32=0, ESP32-C3=5.
  const int chip = buffer[12] | int(buffer[13]) << 8;
  if (buffer[0] != 0xe9 || chip != (hardware.mcu() == Hardware::MCU::ESP32_C3 ? 5 : 0)) return Error::IMAGE;
  if (!digest.begin()) return Error::HASH;
  if (!flash.begin(candidate.size)) {
    flash.abort();
    return Error::FLASH;
  }
  auto fail = [&](Error error) {
    flash.abort();
    return error;
  };
  if (!digest.update(buffer, header)) return fail(Error::HASH);
  if (!flash.write(buffer, header)) return fail(Error::FLASH);
  uint32_t bytes = header;
  reporter.progress(bytes, candidate.size);
  while (bytes < candidate.size) {
    const size_t wanted = std::min(sizeof(buffer), static_cast<size_t>(candidate.size - bytes));
    const int count = source.read(buffer, wanted);
    if (count <= 0 || static_cast<size_t>(count) > wanted) return fail(Error::NETWORK);
    if (!digest.update(buffer, count)) return fail(Error::HASH);
    if (!flash.write(buffer, count)) return fail(Error::FLASH);
    bytes += count;
    reporter.progress(bytes, candidate.size);
  }
  const int trailing = source.read(buffer, 1);
  if (trailing < 0) return fail(Error::NETWORK);
  if (trailing > 0) return fail(Error::LENGTH);
  char actual[65];
  if (!digest.finish(actual) || std::strcmp(actual, candidate.sha256) != 0) return fail(Error::HASH);
  if (!flash.finish()) return fail(Error::FLASH);
  return Error::NONE;
}

const char* errorName(Error error) {
  switch (error) {
    case Error::NONE:
      return "none";
    case Error::BUSY:
      return "update busy";
    case Error::NO_OFFER:
      return "no newer validated release";
    case Error::VERSION:
      return "version mismatch";
    case Error::MANIFEST:
      return "invalid manifest";
    case Error::HARDWARE:
      return "incompatible hardware";
    case Error::URL:
      return "untrusted release URL";
    case Error::CAPACITY:
      return "installed OTA slot too small";
    case Error::NETWORK:
      return "HTTPS/read failure";
    case Error::LENGTH:
      return "image length mismatch";
    case Error::IMAGE:
      return "wrong ESP image/chip";
    case Error::HASH:
      return "SHA-256 mismatch";
    case Error::FLASH:
      return "flash update failed";
    default:
      return "update worker unavailable";
  }
}

const char* networkStageName(NetworkStage stage) {
  switch (stage) {
    case NetworkStage::INIT:
      return "init";
    case NetworkStage::CONNECT:
      return "connect";
    case NetworkStage::HEADERS:
      return "headers";
    case NetworkStage::STATUS:
      return "http status";
    case NetworkStage::REDIRECT:
      return "redirect";
    case NetworkStage::READ:
      return "read";
    case NetworkStage::DEADLINE:
      return "deadline";
    case NetworkStage::SECURITY:
      return "HTTPS required";
    case NetworkStage::COMPLETE:
      return "complete";
    default:
      return "none";
  }
}

const char* stateName(State state) {
  switch (state) {
    case State::WAIT_NETWORK:
      return "waiting for network";
    case State::WAIT_TIME:
      return "waiting for clock";
    case State::CHECKING:
      return "checking";
    case State::CURRENT:
      return "current";
    case State::AVAILABLE:
      return "update available";
    case State::INSTALL_QUEUED:
      return "install queued";
    case State::INSTALLING:
      return "installing";
    case State::REBOOT_PENDING:
      return "verified; restart pending";
    case State::FAILED:
      return "failed";
    default:
      return "idle";
  }
}
}  // namespace FirmwareUpdate
