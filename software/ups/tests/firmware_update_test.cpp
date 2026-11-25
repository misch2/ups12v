#include "firmware_update.h"

#include <ArduinoJson.h>

#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

using namespace FirmwareUpdate;
const char* kVersion = "20261126.1";

std::string manifest(const Hardware::Profile& hardware) {
  JsonDocument doc;
  doc["schema"] = 1;
  doc["version"] = kVersion;
  doc["release_url"] = "https://github.com/misch2/ups12v/releases/tag/fw-20261126.1";
  doc["release_summary"] = "Test firmware";
  auto item = doc["variants"][variantName(hardware)].to<JsonObject>();
  item["hardware"]["version"] = hardware.versionName();
  item["hardware"]["mcu"] = hardware.mcu() == Hardware::MCU::ESP32_C3 ? "esp32c3" : "esp32";
  item["hardware"]["power_path"] = hardware.powerPath() == Hardware::PowerPath::PMID_WITH_SWITCHOVER ? "pmid_switchover" : "sys";
  item["url"] = std::string("https://github.com/misch2/ups12v/releases/download/fw-20261126.1/") + variantName(hardware) + ".bin";
  item["size"] = 2048;
  item["sha256"] = std::string(64, 'a');
  std::string text;
  serializeJson(doc, text);
  return text;
}
Candidate offer(const Hardware::Profile& hardware = Hardware::kV4Esp32C3) {
  Candidate value;
  assert(parseManifest(manifest(hardware), hardware, value) == Error::NONE);
  return value;
}
void manifests() {
  for (const auto hardware : {Hardware::kV1Esp32, Hardware::kV3SysEsp32, Hardware::kV4Esp32C3}) {
    const auto good = manifest(hardware);
    assert(std::strcmp(offer(hardware).version, kVersion) == 0);
    Candidate unchanged;
    std::strcpy(unchanged.version, "unchanged");
    for (const auto& invalid : {good + "garbage", good + "{}", std::string(8193, 'x')}) {
      assert(parseManifest(invalid, hardware, unchanged) != Error::NONE && std::strcmp(unchanged.version, "unchanged") == 0);
    }
    for (int defect = 0; defect < 8; ++defect) {
      JsonDocument doc;
      assert(!deserializeJson(doc, good));
      auto item = doc["variants"][variantName(hardware)].as<JsonObject>();
      if (defect == 0) doc["schema"] = 2;
      if (defect == 1) doc["version"] = "20260230.1";
      if (defect == 2) item["hardware"]["version"] = "wrong-board";
      if (defect == 3) item["url"] = "http://github.com/unsafe.bin";
      if (defect == 4) item["sha256"] = "not-a-hash";
      if (defect == 5) item["size"] = -1;
      if (defect == 6) item["size"] = true;
      if (defect == 7) item["url"] = "https://github.com/misch2/other-repo/file.bin";
      std::string changed;
      serializeJson(doc, changed);
      assert(parseManifest(changed, hardware, unchanged) != Error::NONE);
      assert(std::strcmp(unchanged.version, "unchanged") == 0);
    }
  }
  assert(newer("20261125.10", "20261125.9") && !newer("20261125.9", "20261125.10"));
  assert(newer("20261126.0", "20261125.999") && !newer(kVersion, kVersion));
  uint32_t day, revision;
  for (const auto bad : {"20260229.1", "20261125.01", "20261125.4294967296", "20261125.", "20261125.1x", "00000101.1"}) {
    assert(!parseVersion(bad, day, revision));
  }
  assert(parseVersion("20240229.1", day, revision));
  std::puts("manifest: variants, bounds, strict parsing, unchanged output, pinned URLs, calendar ordering and overflow passed");
}

struct FakeBackend : Backend {
  bool ready = false, accepts = true;
  int checks = 0, installs = 0;
  uint32_t slot = 0x1e0000;
  Result result;
  bool check() override {
    ++checks;
    return accepts;
  }
  bool install(const Candidate& value) override {
    ++installs;
    assert(std::strcmp(value.version, kVersion) == 0);
    return accepts;
  }
  bool poll(Result& output) override {
    if (!ready) return false;
    ready = false;
    output = result;
    return true;
  }
  bool progress(Progress&) override { return false; }
  uint32_t capacity() const override { return slot; }
  void complete(JobKind kind, Error error = Error::NONE) {
    result.kind = kind;
    result.error = error;
    result.candidate = offer();
    ready = true;
  }
};
void scheduling() {
  FakeBackend backend;
  Service service(backend, "20261125.4");
  service.tick(0, false, false, true);
  assert(service.state() == State::WAIT_NETWORK && backend.checks == 0);
  service.tick(1, true, false, true);
  assert(service.state() == State::WAIT_TIME && backend.checks == 0);
  service.tick(2, true, true, true);
  assert(service.state() == State::CHECKING && backend.installs == 0);
  for (int now = 3; now < 100; ++now) service.tick(now, true, true, true);
  assert(backend.checks == 1 && backend.installs == 0);
  backend.complete(JobKind::CHECK);
  service.tick(100, true, true, true);
  assert(service.available() && service.state() == State::AVAILABLE && backend.installs == 0);
  service.tick(101, true, true, true);
  assert(backend.installs == 0);
  assert(service.requestInstall("different-version") == Error::VERSION);
  assert(service.requestInstall(kVersion) == Error::NONE);
  assert(service.reserved() && service.requestInstall(kVersion) == Error::BUSY);
  service.tick(102, true, true, false);
  assert(backend.installs == 0 && service.state() == State::INSTALL_QUEUED);
  assert(service.cancelQueuedInstall());
  assert(service.requestInstall(kVersion) == Error::NONE);
  service.tick(103, true, true, true);
  assert(service.installing() && backend.installs == 1);
  backend.complete(JobKind::INSTALL, Error::HASH);
  service.tick(104, true, true, true);
  assert(service.state() == State::FAILED && !service.rebootPending());
  assert(service.requestInstall(kVersion) == Error::NONE);
  service.tick(105, true, true, true);
  backend.complete(JobKind::INSTALL);
  service.tick(106, true, true, true);
  assert(service.rebootPending() && service.reserved() && service.downloadProgress().bytes == 2048);
  FakeBackend periodic;
  Service timer(periodic, "20261125.4");
  const uint32_t start = UINT32_MAX - 1000;
  timer.tick(start, true, true, true);
  periodic.complete(JobKind::CHECK);
  timer.tick(start + 1, true, true, true);
  timer.tick(start + kCheckIntervalMs - 1, true, true, true);
  assert(periodic.checks == 1);
  timer.tick(start + kCheckIntervalMs, true, true, true);
  assert(periodic.checks == 2 && periodic.installs == 0);
  periodic.complete(JobKind::CHECK, Error::NETWORK);
  timer.tick(start + kCheckIntervalMs + 1, true, true, true);
  timer.tick(start + kCheckIntervalMs + 59999, true, true, true);
  assert(periodic.checks == 2);
  timer.tick(start + kCheckIntervalMs + 60000, true, true, true);
  assert(periodic.checks == 3);
  periodic.complete(JobKind::INSTALL);
  timer.tick(start + kCheckIntervalMs + 60001, true, true, true);
  assert(timer.error() == Error::WORKER && !timer.rebootPending());
  FakeBackend small;
  small.slot = 1024;
  Service blocked(small, "20261125.4");
  blocked.tick(0, true, true, true);
  small.complete(JobKind::CHECK);
  blocked.tick(1, true, true, true);
  assert(!blocked.available() && blocked.error() == Error::CAPACITY && blocked.requestInstall(kVersion) == Error::CAPACITY);
  FakeBackend same;
  Service current(same, kVersion);
  current.tick(0, true, true, true);
  same.complete(JobKind::CHECK);
  current.tick(1, true, true, true);
  assert(!current.available() && current.state() == State::CURRENT && current.requestInstall(kVersion) == Error::NO_OFFER);
  std::puts("service: boot/six-hour checks, manual-only install, version/queue locks, failed retry, rollover and actual-slot gate passed");
}

struct FakeSource : Source {
  std::vector<uint8_t> image;
  size_t position = 0;
  int64_t declared = 2048;
  explicit FakeSource(bool c3 = true) : image(2048, 0x11) {
    image[0] = 0xe9;
    image[12] = c3 ? 5 : 0;
    image[13] = 0;
  }
  int64_t length() const override { return declared; }
  int read(uint8_t* output, size_t count) override {
    count = std::min(std::min(count, size_t(13)), image.size() - position);
    std::memcpy(output, image.data() + position, count);
    position += count;
    return count;
  }
};
struct FakeFlash : Flash {
  uint32_t slot = 4096;
  bool began = false, aborted = false, selected = false, writeOk = true, finishOk = true;
  std::vector<uint8_t> image;
  uint32_t capacity() const override { return slot; }
  bool begin(uint32_t) override {
    began = true;
    return true;
  }
  bool write(uint8_t* bytes, size_t count) override {
    image.insert(image.end(), bytes, bytes + count);
    return writeOk;
  }
  bool finish() override {
    selected = finishOk;
    return finishOk;
  }
  void abort() override { aborted = true; }
};
struct FakeDigest : Digest {
  std::vector<uint8_t> image;
  bool good = true;
  bool begin() override { return true; }
  bool update(const uint8_t* bytes, size_t count) override {
    image.insert(image.end(), bytes, bytes + count);
    return true;
  }
  bool finish(char hex[65]) override {
    std::memset(hex, good ? 'a' : 'b', 64);
    hex[64] = 0;
    return true;
  }
};
struct FakeReporter : Reporter {
  uint32_t bytes = 0;
  void progress(uint32_t current, uint32_t total) override {
    assert(current >= bytes && current <= total);
    bytes = current;
  }
};
void imageTransfer() {
  for (const auto hardware : {Hardware::kV1Esp32, Hardware::kV3SysEsp32, Hardware::kV4Esp32C3}) {
    FakeSource source(hardware.mcu() == Hardware::MCU::ESP32_C3);
    FakeFlash flash;
    FakeDigest digest;
    FakeReporter progress;
    assert(transfer(offer(hardware), hardware, source, flash, digest, progress) == Error::NONE);
    assert(flash.selected && !flash.aborted && digest.image == source.image && flash.image == source.image && progress.bytes == 2048);
  }
  FakeSource chunked;
  chunked.declared = -1;
  FakeFlash target;
  FakeDigest hash;
  FakeReporter report;
  assert(transfer(offer(), Hardware::kV4Esp32C3, chunked, target, hash, report) == Error::NONE && target.selected);
  for (int fault = 0; fault < 7; ++fault) {
    FakeSource source;
    FakeFlash flash;
    FakeDigest digest;
    FakeReporter progress;
    if (fault == 0) source.declared = 2047;
    if (fault == 1) flash.slot = 1024;
    if (fault == 2) source.image[12] = 0;
    if (fault == 3) source.image.resize(1500);
    if (fault == 4) digest.good = false;
    if (fault == 5) flash.writeOk = false;
    if (fault == 6) flash.finishOk = false;
    assert(transfer(offer(), Hardware::kV4Esp32C3, source, flash, digest, progress) != Error::NONE);
    assert(!flash.selected && (fault < 3 ? !flash.began : flash.aborted));
  }
  std::puts("transfer: fragmented headers, ESP32/C3 identity, capacity/length/truncation/hash/write/commit failures; verified boot selection passed");
}
int main() {
  manifests();
  scheduling();
  imageTransfer();
  std::puts("firmware_update: behavioral checks passed (network, flash and digest substituted)");
}
