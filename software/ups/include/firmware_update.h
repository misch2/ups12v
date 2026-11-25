#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

#include "hardware_profile.h"

namespace FirmwareUpdate {
constexpr size_t kMaxManifestBytes = 8192;
constexpr uint32_t kCheckIntervalMs = 6UL * 60 * 60 * 1000;
constexpr const char* kManifestUrl = "https://misch2.github.io/ups12v/firmware/stable.json";
enum class Error { NONE, BUSY, NO_OFFER, VERSION, MANIFEST, HARDWARE, URL, CAPACITY, NETWORK, LENGTH, IMAGE, HASH, FLASH, WORKER };
enum class State { IDLE, WAIT_NETWORK, WAIT_TIME, CHECKING, CURRENT, AVAILABLE, INSTALL_QUEUED, INSTALLING, REBOOT_PENDING, FAILED };
enum class JobKind { CHECK, INSTALL };
enum class NetworkStage { NONE, INIT, CONNECT, HEADERS, STATUS, REDIRECT, READ, DEADLINE, SECURITY, COMPLETE };
struct NetworkDiagnostics {
  NetworkStage stage = NetworkStage::NONE;
  int sdkError = 0, tlsSdkError = 0, tlsError = 0, verifyFlags = 0, socketError = 0, httpStatus = 0;
  uint32_t heapBefore = 0, largestBefore = 0, heapAtFailure = 0, largestAtFailure = 0;
};
const char* networkStageName(NetworkStage stage);

// Owned POD messages, safe to copy through FreeRTOS queues. No borrowed settings/credentials.
struct Candidate {
  char version[24] = {};
  char url[256] = {};
  char sha256[65] = {};
  char releaseUrl[256] = {};
  char summary[256] = {};
  uint32_t size = 0;
};
struct Result {
  JobKind kind = JobKind::CHECK;
  Error error = Error::NONE;
  Candidate candidate;
  NetworkDiagnostics network;
};
struct Progress {
  uint32_t bytes = 0;
  uint32_t total = 0;
};
const char* errorName(Error error);
const char* stateName(State state);
const char* variantName(const Hardware::Profile& hardware);
bool parseVersion(const char* value, uint32_t& day, uint32_t& revision);
bool newer(const char* candidate, const char* installed);
Error parseManifest(const std::string& json, const Hardware::Profile& hardware, Candidate& output);

class Backend {
 public:
  virtual ~Backend() = default;
  virtual bool check() = 0;
  virtual bool install(const Candidate& candidate) = 0;
  virtual bool poll(Result& result) = 0;
  virtual bool progress(Progress& progress) = 0;
  virtual uint32_t capacity() const = 0;
};

class Service {
 public:
  Service(Backend& backend, const char* installed) : backend(backend), installed(installed) {}
  void requestCheck() { checkRequested = true; }
  bool checkPending() const { return checkRequested; }
  void workerUnavailable() {
    currentState = State::FAILED;
    lastError = Error::WORKER;
    checkRequested = false;
  }
  Error validateInstall(const char* version) const;
  Error requestInstall(const char* version);
  bool cancelQueuedInstall();
  void tick(uint32_t now, bool networkReady, bool timeReady, bool mayInstall);
  State state() const { return currentState; }
  Error error() const { return lastError; }
  Error commandError() const { return lastCommandError; }
  const NetworkDiagnostics& networkDiagnostics() const { return lastNetwork; }
  uint32_t networkRevision() const { return networkGeneration; }
  void recordCommandResult(Error error) { lastCommandError = error; }
  const Candidate& offer() const { return candidate; }
  bool hasOffer() const { return haveOffer; }
  uint32_t offerRevision() const { return offerGeneration; }
  bool available() const { return haveOffer && newer(candidate.version, installed) && candidate.size <= backend.capacity(); }
  bool reserved() const { return queued || installing() || rebootPending(); }
  bool installing() const { return currentState == State::INSTALLING; }
  bool rebootPending() const { return currentState == State::REBOOT_PENDING; }
  const Progress& downloadProgress() const { return currentProgress; }
  const char* installedVersion() const { return installed; }

 private:
  Backend& backend;
  const char* installed;
  State currentState = State::IDLE;
  Error lastError = Error::NONE;
  Error lastCommandError = Error::NONE;
  NetworkDiagnostics lastNetwork;
  uint32_t networkGeneration = 0;
  Candidate candidate;
  Progress currentProgress;
  bool haveOffer = false, busy = false, queued = false, checkRequested = true, checked = false;
  uint32_t lastCheck = 0;
  uint32_t offerGeneration = 0;
};

// Both MQTT and web actions pass through the application's operating-state guard.
class Control {
 public:
  virtual ~Control() = default;
  virtual Error validateInstall(const char* version) const = 0;
  virtual Error requestInstall(const char* version) = 0;
  virtual Error requestCheck() = 0;
  virtual Error cancel() = 0;
};

std::string stateJson(const Service& service);

class Source {
 public:
  virtual ~Source() = default;
  virtual int64_t length() const = 0;
  virtual int read(uint8_t* bytes, size_t count) = 0;  // 0 = complete EOF; -1 = network/truncation error.
};
class Flash {
 public:
  virtual ~Flash() = default;
  virtual uint32_t capacity() const = 0;
  virtual bool begin(uint32_t size) = 0;
  virtual bool write(uint8_t* bytes, size_t count) = 0;
  virtual bool finish() = 0;  // Selects the next boot image only after verified download.
  virtual void abort() = 0;
};
class Digest {
 public:
  virtual ~Digest() = default;
  virtual bool begin() = 0;
  virtual bool update(const uint8_t* bytes, size_t count) = 0;
  virtual bool finish(char hex[65]) = 0;
};
class Reporter {
 public:
  virtual ~Reporter() = default;
  virtual void progress(uint32_t bytes, uint32_t total) = 0;
};
Error transfer(const Candidate& candidate, const Hardware::Profile& hardware, Source& source, Flash& flash, Digest& digest, Reporter& reporter);
}  // namespace FirmwareUpdate
