#include "config_web.h"

#include <ArduinoJson.h>

#include <cerrno>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <utility>
#include <vector>

namespace ConfigWeb {
namespace {
enum class Type { TEXT, INTEGER, REAL, BOOLEAN, PROFILE, BACKUP };
enum class Scope { ALL, PMID, V4 };
struct Field {
  const char* key;
  const char* label;
  Type type;
  int group;
  Scope scope = Scope::ALL;
  Field(const char* key, const char* label, Type type, int group, Scope scope = Scope::ALL)
      : key(key), label(label), type(type), group(group), scope(scope) {}
};
const Field kFields[] = {
    {"network.mqtt.haDeviceName", "Device ID (fixed after commissioning)", Type::TEXT, 0},
    {"network.mqtt.serverHostname", "MQTT server", Type::TEXT, 0},
    {"network.mqtt.serverPort", "MQTT port", Type::INTEGER, 0},
    {"network.syslog.serverHostname", "Syslog server", Type::TEXT, 0},
    {"network.syslog.serverPort", "Syslog port", Type::INTEGER, 0},
    {"network.syslog.myHostname", "Syslog device name", Type::TEXT, 0},
    {"network.syslog.myAppname", "Syslog application name", Type::TEXT, 0},
    {"battery.cell.name", "Cell description", Type::TEXT, 1},
    {"battery.pack.capacity_mAh", "Pack capacity (mAh)", Type::INTEGER, 1},
    {"battery.pack.maxChargeCurrent_mA", "Battery charge-current ceiling (mA; 0 inhibits charging)", Type::INTEGER, 1},
    {"battery.cell.approx80PercentCapacity_mV", "Approx. 80% target (mV per cell)", Type::INTEGER, 1},
    {"battery.cell.approx20PercentCapacityUnderMaxLoad_mV", "Low-battery warning under load (mV per cell; 0 unspecified)", Type::INTEGER, 1},
    {"battery.cell.overrideLimits.stopCell_mV", "Stop diagnostic tests below (mV per cell)", Type::INTEGER, 1},
    {"battery.cell.overrideLimits.startCell_mV", "Allow diagnostic tests above (mV per cell)", Type::INTEGER, 1},
    {"power.charger.chargeProfile.mode", "Charge profile", Type::PROFILE, 2},
    {"power.charger.chargeProfile.fullCell_mV", "Full-charge target (mV per cell)", Type::INTEGER, 2},
    {"power.charger.chargeProfile.rechargeOffset_mV", "Recharge offset (mV per pack; 0 preserves IC value)", Type::INTEGER, 2},
    {"power.charger.ICHG_mA", "Requested charge current (mA; capped by battery ceiling)", Type::INTEGER, 2},
    {"power.charger.minCellVoltage_mV", "Battery-percent estimate: empty (mV per cell)", Type::INTEGER, 2},
    {"power.charger.maxCellVoltage_mV", "Battery-percent estimate: full (mV per cell)", Type::INTEGER, 2},
    {"power.charger.vbatChgEnableIfCellBelow_mV", "Legacy: enable charging below (mV per cell)", Type::INTEGER, 2},
    {"power.charger.vbatChgDisableIfCellAbove_mV", "Legacy: disable charging above (mV per cell)", Type::INTEGER, 2},
    {"power.input.IINDPM_mA", "Input current limit (mA; 0 preserves IC value)", Type::INTEGER, 3},
    {"power.input.VINDPM_mV", "Input voltage DPM threshold (mV; 0 preserves IC value)", Type::INTEGER, 3},
    {"power.input.retryUnqualifiedAdapter", "Retry unqualified input detection", Type::BOOLEAN, 3, Scope::V4},
    {"power.input.VBUSBackupPercentage", "Backup trigger (% of configured output voltage)", Type::BACKUP, 3, Scope::PMID},
    {"power.output.VOTG_mV", "Output voltage (mV; 0 preserves IC value)", Type::INTEGER, 3, Scope::PMID},
    {"power.output.IOTG_mA", "Output current (mA; 0 preserves IC value)", Type::INTEGER, 3, Scope::PMID},
    {"ACRecoveryPeriodSeconds", "Input recovery delay (seconds)", Type::INTEGER, 3, Scope::PMID},
    {"temperatureSensor.resistance_25degC", "NTC resistance at 25 C (ohms)", Type::REAL, 4},
    {"temperatureSensor.beta", "NTC beta (K)", Type::REAL, 4},
};
bool applicable(const Field& field, const Hardware::Profile& hardware) {
  return field.scope == Scope::ALL || (field.scope == Scope::V4 && hardware.version == Hardware::Version::V4_0) ||
         (field.scope == Scope::PMID && hardware.powerPath() == Hardware::PowerPath::PMID_WITH_SWITCHOVER);
}
std::string escape(const std::string& text) {
  std::string result;
  for (unsigned char c : text) {
    switch (c) {
      case '&': result += "&amp;"; break;
      case '<': result += "&lt;"; break;
      case '>': result += "&gt;"; break;
      case '"': result += "&quot;"; break;
      case '\'': result += "&#39;"; break;
      default: if (c >= 32 || c == '\n' || c == '\t') result += static_cast<char>(c);
    }
  }
  return result;
}
int hex(char c) {
  if (c >= '0' && c <= '9') return c - '0';
  if (c >= 'a' && c <= 'f') return c - 'a' + 10;
  if (c >= 'A' && c <= 'F') return c - 'A' + 10;
  return -1;
}
bool decode(const std::string& source, std::string& target) {
  for (size_t i = 0; i < source.size(); ++i) {
    char c = source[i];
    if (c == '+') c = ' ';
    else if (c == '%') {
      if (i + 2 >= source.size() || hex(source[i + 1]) < 0 || hex(source[i + 2]) < 0) return false;
      c = static_cast<char>(hex(source[i + 1]) * 16 + hex(source[i + 2]));
      i += 2;
    }
    if (!c) return false;
    target += c;
  }
  return true;
}
struct Form {
  std::vector<std::pair<std::string, std::string>> values;
  const std::string* find(const std::string& name) const {
    for (const auto& field : values) if (field.first == name) return &field.second;
    return nullptr;
  }
  bool parse(const std::string& body) {
    if (body.empty() || body.size() > kMaxBody) return false;
    size_t start = 0;
    while (start < body.size()) {
      const auto end = body.find('&', start);
      const auto pair = body.substr(start, end == std::string::npos ? end : end - start);
      const auto equal = pair.find('=');
      if (equal == std::string::npos) return false;
      std::string key, value;
      if (!decode(pair.substr(0, equal), key) || !decode(pair.substr(equal + 1), value) || key.empty() || key.size() > 96 ||
          value.size() > Settings::kMaxRecordBytes || find(key) || values.size() >= 48) return false;
      values.emplace_back(std::move(key), std::move(value));
      if (end == std::string::npos) break;
      start = end + 1;
      if (start == body.size()) return false;
    }
    return true;
  }
};
bool integer(const std::string& text, int& value) {
  if (text.empty() || text.find_first_not_of("-0123456789") != std::string::npos) return false;
  errno = 0;
  char* end;
  const long result = std::strtol(text.c_str(), &end, 10);
  if (errno || *end || result < INT_MIN || result > INT_MAX) return false;
  value = static_cast<int>(result);
  return true;
}
bool setValue(JsonVariant value, Type type, const std::string& text) {
  if (type == Type::TEXT) return value.set(text);
  if (type == Type::REAL) {
    errno = 0;
    char* end;
    const double number = std::strtod(text.c_str(), &end);
    return !text.empty() && !errno && !*end && std::isfinite(number) && value.set(number);
  }
  int number;
  if (!integer(text, number)) return false;
  if (type == Type::BOOLEAN) return (number == 0 || number == 1) && value.set(number == 1);
  return value.set(number);
}
std::string errorText(const Settings::Result& result) {
  return std::string(Settings::statusName(result.status)) + (result.detail ? std::string(": ") + result.detail : "");
}
bool copyCredentials(const RuntimeSettings& source, RuntimeSettings& candidate) {
  candidate.network.mqtt.user = source.network.mqtt.user;
  candidate.network.mqtt.password = source.network.mqtt.password;
  return candidate.network.mqtt.user.length() == source.network.mqtt.user.length() &&
         candidate.network.mqtt.password.length() == source.network.mqtt.password.length();
}
bool updateSecret(const Form& form, const char* key, const char* clearKey, String& target) {
  const auto value = form.find(key), clear = form.find(clearKey);
  if (clear && *clear != "1") return false;
  if (clear && value && !value->empty()) return false;
  if (clear) target = "";
  else if (value && !value->empty()) {
    target = value->c_str();
    if (target.length() != value->size()) return false;
  }
  return true;
}
std::string hidden(const std::string& token, uint32_t revision) {
  return "<input type=hidden name=token value=\"" + escape(token) + "\"><input type=hidden name=revision value=\"" +
         std::to_string(revision) + "\">";
}
const char* stateName(Settings::ApplyState state) {
  switch (state) {
    case Settings::ApplyState::APPLIED: return "Applied and verified";
    case Settings::ApplyState::PENDING: return "Pending verification";
    case Settings::ApplyState::DEFERRED: return "Waiting for suitable charger/input state";
    case Settings::ApplyState::FAILED: return "Application failed; retry pending";
    default: return "Not commissioned; restart required after setup";
  }
}
}  // namespace

const RuntimeSettings& Controller::desired() const {
  return settings.status().desiredRevision ? settings.desired() : defaults;
}

Response Controller::page(Observation observation, int code, const std::string& message) {
  Response response;
  response.code = code;
  auto& html = response.body;
  html = "<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content=\"width=device-width,initial-scale=1\">"
         "<title>UPS configuration</title><style>body{font:16px system-ui;max-width:850px;margin:2rem auto;padding:0 1rem;color:#182537;"
         "background:#f4f6f9}fieldset{background:white;border:1px solid #bbc5d1;border-radius:8px;margin:1.2rem 0;padding:1rem}"
         "legend,h1{font-weight:650}label{display:block;margin:.8rem 0}input:not([type=checkbox]),select,textarea{display:block;box-sizing:"
         "border-box;width:100%;padding:.5rem;margin-top:.3rem;font:inherit}button,a{color:#15549c}button{font:inherit;padding:.6rem 1rem;"
         "cursor:pointer}p{line-height:1.5}.notice{padding:1rem;border-left:4px solid #267bbd;background:#e6eff8}small{display:block}"
         "</style><h1>UPS configuration</h1>";
  if (!message.empty()) html += "<p class=notice role=status>" + escape(message) + "</p>";
  html += "<p><a href=/firmware>Firmware updates</a></p>";
  const auto& status = settings.status();
  html += "<p>Hardware " + escape(hardware.versionName()) + " · " +
          (hardware.mcu() == Hardware::MCU::ESP32_C3 ? "ESP32-C3" : "ESP32") + " · " +
          (hardware.powerPath() == Hardware::PowerPath::VSYS_UNINTERRUPTED ? "SYS power path" : "PMID switchover") +
          "<br>Charger: " + (observation.chargerReady ? "ready" : "unavailable") + " · Cells: " +
          (observation.cells > 0 ? std::to_string(observation.cells) : "unavailable") + " (read-only)</p>";
  html += std::string("<p>Power settings: ") + stateName(status.powerState);
  if (status.detail) html += "<br>" + escape(status.detail);
  if (status.inputClamped) html += "<br>External input limit: " + std::to_string(status.actualInput_mA) + " mA";
  html += std::string("<br>Network settings: ") + (status.restartRequired ? "saved; restart required" : "active") + "</p>";
  html += "<p><a href=/>Refresh status</a> · <a href=/export>Export settings</a></p>";
  std::string exported;
  const auto encoded = Settings::encodeExport(desired(), hardware, exported);
  if (!encoded.ok()) {
    html += "<p>Cannot display settings: " + escape(errorText(encoded)) + "</p></html>";
    response.code = 503;
    return response;
  }
  JsonDocument document;
  if (deserializeJson(document, exported)) { response.code = 503; html += "<p>Cannot display settings.</p></html>"; return response; }
  const auto values = document["settings"].as<JsonObjectConst>();
  const auto controls = hidden(token, status.desiredRevision);
  html += "<form method=post action=/save>" + controls;
  const char* groups[] = {"Device and services", "Battery", "Charging", "Input and output", "Temperature sensor"};
  for (int group = 0; group < 5; ++group) {
    html += std::string("<fieldset><legend>") + groups[group] + "</legend>";
    if (group == 0) html += "<p>Service changes require restart. Customize display names in Home Assistant.</p>";
    if (group == 1) html += "<p>Choose battery limits for the fitted cells. The 80% target is a voltage preset, not a measured state of charge.</p>";
    if (group == 2) html += "<p>Legacy uses voltage thresholds and leaves VREG unchanged. Managed profiles use the charger's termination/recharge.</p>";
    for (const auto& field : kFields) {
      if (field.group != group || !applicable(field, hardware)) continue;
      const auto value = values[field.key];
      html += "<label>" + escape(field.label);
      const std::string name = " name=\"" + std::string(field.key) + "\"";
      if (field.type == Type::BOOLEAN || field.type == Type::PROFILE || field.type == Type::BACKUP) {
        html += "<select" + name + ">";
        const int count = field.type == Type::BOOLEAN ? 2 : field.type == Type::PROFILE ? 3 : 4;
        const int selected = field.type == Type::BOOLEAN ? static_cast<int>(value.as<bool>()) : value.as<int>();
        for (int i = 0; i < count; ++i) {
          const char* profiles[] = {"Legacy", "Full", "Approx. 80%"};
          const std::string label = field.type == Type::BOOLEAN ? (i ? "Yes" : "No") :
                                    field.type == Type::PROFILE ? profiles[i] : std::to_string(40 + i * 20) + "%";
          html += "<option value=\"" + std::to_string(i) + "\"" + (i == selected ? " selected" : "") + ">" + label + "</option>";
        }
        html += "</select>";
      } else {
        std::string text;
        if (field.type == Type::TEXT) text = value.as<const char*>() ? value.as<const char*>() : "";
        else serializeJson(value, text);
        const bool identity = std::strcmp(field.key, "network.mqtt.haDeviceName") == 0;
        const bool identityLocked = status.desiredRevision != 0;
        if (identity && !identityLocked) text.clear();
        html += "<input" + name + " type=" + (field.type == Type::TEXT ? "text" : "number") +
                (field.type == Type::REAL ? " step=any" : "") + " value=\"" + escape(text) + "\"" +
                (identity ? (identityLocked ? " readonly" : " required maxlength=31") : "") + ">";
      }
      html += "</label>";
    }
    if (group == 0) {
      html += "<label>New MQTT username<input name=mqtt_user autocomplete=off></label>"
              "<label><input type=checkbox name=clear_mqtt_user value=1> Clear MQTT username</label>"
              "<label>New MQTT password<input type=password name=mqtt_password autocomplete=new-password></label>"
              "<label><input type=checkbox name=clear_mqtt_password value=1> Clear MQTT password</label>"
              "<small>Blank credentials keep the saved values. Use Clear to remove a value.</small>";
    }
    html += "</fieldset>";
  }
  html += "<button>Save settings</button></form>";
  Settings::WifiCredentials current, pending;
  const auto currentResult = wifi.current(current), pendingResult = wifi.pending(pending);
  html += "<fieldset><legend>Wi-Fi</legend><p>Current saved network: " + escape(currentResult.ok() ? current.ssid : "unavailable") + "</p>";
  if (pendingResult.ok()) html += "<p>Staged network: " + escape(pending.ssid) + "; restart required.</p>";
  else if (pendingResult.status != Settings::Status::MISSING) html += "<p>Staged Wi-Fi cannot be read: " + escape(errorText(pendingResult)) + "</p>";
  html += "<p>Wi-Fi is saved separately. Changes take effect on restart. If Wi-Fi is unavailable for two minutes, "
          "the protected recovery AP starts automatically.</p><form method=post action=/wifi>" + controls +
          "<label>Network name (SSID)<input name=ssid maxlength=32 required value=\"" + escape(pendingResult.ok() ? pending.ssid : current.ssid) +
          "\"></label><label>New Wi-Fi password<input type=password name=wifi_password maxlength=64 autocomplete=new-password></label>"
          "<label><input type=checkbox name=clear_wifi_password value=1> Clear password for an open network</label>"
          "<small>Blank keeps the staged password, or the current password when no change is staged.</small><button>Stage Wi-Fi change</button></form>";
  if (pendingResult.ok()) html += "<form method=post action=/wifi/cancel>" + controls + "<button>Cancel staged Wi-Fi change</button></form>";
  html += "</fieldset><fieldset><legend>Import settings</legend><p>Paste an exported JSON record. Export/import excludes Wi-Fi and MQTT "
          "credentials; local credentials are preserved.</p><form method=post action=/import>" + controls +
          "<label>Settings JSON<textarea name=settings_json rows=7 maxlength=8192 required></textarea></label><button>Import and save</button></form>"
          "</fieldset><form method=post action=/restart>" + controls +
          "<p>Restart activates saved service settings and any staged Wi-Fi change. Reopen this page at the device's network address.</p>"
          "<button>Restart device</button></form>";
  if (recovery) {
    html += "<fieldset><legend>Setup and recovery</legend>";
    if (recovery->available()) {
      html += "<p>AP name: <strong>" + escape(recovery->ssid()) + "</strong><br>AP password: <strong>" +
              escape(recovery->password()) + "</strong><br>Address: <a href=http://192.168.4.1/>http://192.168.4.1/</a><br>Status: " +
              (recovery->active() ? "active" : "off") + "</p>";
      if (recovery->failed()) html += "<p>AP operation failed; retry pending.</p>";
      html += "<p>Keep the AP password for offline recovery. Automatic fallback closes after Wi-Fi returns; manual recovery stays on until stopped. "
              "Setup stays available until commissioning and Wi-Fi are saved and the device restarts.</p>"
              "<form method=post action=/recovery/start>" + controls + "<button>Start recovery AP</button></form>"
              "<form method=post action=/recovery/stop>" + controls + "<button>Stop manual recovery AP</button></form>";
    } else html += "<p>Protected recovery unavailable. Check USB serial for the storage error.</p>";
    html += "<details><summary>Reset options</summary><p>Forget Wi-Fi clears saved/staged Wi-Fi only. Device ID, MQTT and operating settings stay. "
            "Type FORGET WIFI to confirm.</p><form method=post action=/wifi/reset>" + controls +
            "<label>Confirmation<input name=confirmation required autocomplete=off></label><button>Forget Wi-Fi and restart</button></form>"
            "<p>Full settings reset removes operating settings, MQTT credentials, the device ID and Wi-Fi. The recovery AP password is kept. "
            "Charging stays inhibited until configured again. Existing HA entities are not deleted. Type RESET SETTINGS to confirm.</p>"
            "<form method=post action=/settings/reset>" + controls +
            "<label>Confirmation<input name=confirmation required autocomplete=off></label><button>Reset settings and restart</button></form>"
            "</details></fieldset>";
  }
  html += "</html>";
  return response;
}

Response Controller::firmwarePage(int code, const std::string& message) {
  Response response;
  response.code = code;
  auto& html = response.body;
  html = "<!doctype html><html><head><meta charset=utf-8><title>UPS firmware</title>";
  if (code == 202 || (firmware && (firmware->reserved() || firmware->checkPending() || firmware->state() == FirmwareUpdate::State::CHECKING ||
                                   pendingAction == DeviceAction::INSTALL_FIRMWARE)))
    html += "<meta http-equiv=refresh content=\"3;url=/firmware\">";
  html += "</head><body><h1>Firmware updates</h1><p><a href=/>Configuration</a> · <a href=/firmware>Refresh status</a></p>";
  if (!message.empty()) html += "<p role=status>" + escape(message) + "</p>";
  if (!firmware || !firmwareControl) {
    html += "<p>Updater unavailable.</p></body></html>";
    return response;
  }
  html += "<p>Installed: <strong>" + escape(firmware->installedVersion()) + "</strong><br>Hardware: " + escape(hardware.versionName()) +
          "<br>Status: " + FirmwareUpdate::stateName(firmware->state()) + "</p>";
  if (pendingAction == DeviceAction::INSTALL_FIRMWARE) html += "<p>Installation request scheduled.</p>";
  if (firmware->error() != FirmwareUpdate::Error::NONE) html += std::string("<p>Update error: ") + FirmwareUpdate::errorName(firmware->error()) + "</p>";
  if (firmware->commandError() != FirmwareUpdate::Error::NONE)
    html += std::string("<p>Last request: ") + FirmwareUpdate::errorName(firmware->commandError()) + "</p>";
  if (firmware->hasOffer()) {
    const auto& offer = firmware->offer();
    html += "<p>Latest checked release: <strong>" + escape(offer.version) + "</strong><br>" + escape(offer.summary) + "<br><a href=\"" +
            escape(offer.releaseUrl) + "\">Release notes</a></p>";
  } else
    html += "<p>No release has been verified yet.</p>";
  if (firmware->reserved()) {
    const auto& progress = firmware->downloadProgress();
    const auto percent = progress.total ? uint64_t(progress.bytes) * 100 / progress.total : 0;
    html += "<p>Progress: " + std::to_string(percent) + "% (" + std::to_string(progress.bytes) + "/" + std::to_string(progress.total) + " bytes)</p>";
  }
  const auto controls = hidden(token, settings.status().desiredRevision);
  if (code != 202 && !firmware->reserved() && !actionPending()) {
    html += "<form method=post action=/firmware/check>" + controls + "<button>Check for updates</button></form>";
    if (firmware->available()) {
      html += "<p>Installing restarts the UPS controller. Saved settings are kept.</p><form method=post action=/firmware/install>" + controls +
              "<input type=hidden name=version value=\"" + escape(firmware->offer().version) + "\"><button>Install " + escape(firmware->offer().version) +
              "</button></form>";
    }
  }
  if (firmware->state() == FirmwareUpdate::State::INSTALL_QUEUED)
    html += "<form method=post action=/firmware/cancel>" + controls + "<button>Cancel queued installation</button></form>";
  html += "</body></html>";
  return response;
}

Response Controller::handle(const Request& request, const std::string& hostname, const std::string& ip, Observation observation) {
  std::string host = request.host;
  std::string normalizedName = hostname;
  for (auto& c : normalizedName)
    if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
  if (host.size() > 3 && host.compare(host.size() - 3, 3, ":80") == 0) host.resize(host.size() - 3);
  if (host != ip && host != normalizedName && host != normalizedName + ".local") {
    Response rejected;
    rejected.code = 403;
    rejected.body = "Use the device IP address or hostname.";
    return rejected;
  }
  if (token.size() != 32) {
    Response unavailable;
    unavailable.code = 503;
    unavailable.body = "Configuration unavailable.";
    return unavailable;
  }
  if (request.method == "GET") {
    if (request.path == "/firmware") return firmwarePage();
    if (request.path == "/firmware/status" && firmware) {
      Response response;
      response.contentType = "application/json";
      response.body = FirmwareUpdate::stateJson(*firmware);
      return response;
    }
    if (request.path == "/") return page(observation);
    if (request.path == "/export") {
      Response response;
      const auto result = Settings::encodeExport(desired(), hardware, response.body);
      if (!result.ok()) return page(observation, 503, errorText(result));
      response.contentType = "application/json";
      response.attachment = true;
      return response;
    }
    return page(observation, 404, "Page not found.");
  }
  if (request.method != "POST") return page(observation, 405, "Use the configuration forms.");
  if ((!request.origin.empty() && request.origin != "http://" + request.host) || request.fetchSite == "cross-site") {
    return page(observation, 403, "Cross-site submission rejected.");
  }
  const auto semicolon = request.contentType.find(';');
  if (request.contentType.substr(0, semicolon) != "application/x-www-form-urlencoded") return page(observation, 415, "Unsupported form encoding.");
  Form form;
  if (!form.parse(request.body)) return page(observation, 400, "Malformed or oversized form.");
  const auto submittedToken = form.find("token"), revision = form.find("revision");
  if (!submittedToken || *submittedToken != token) return page(observation, 403, "Request token expired or missing. Reload this page.");
  if (!revision || *revision != std::to_string(settings.status().desiredRevision)) return page(observation, 409, "Settings changed. Reload before saving.");
  const bool firmwarePath = request.path.compare(0, 10, "/firmware/") == 0;
  if (writesLocked && request.path != "/firmware/cancel")
    return page(observation, 423, "Firmware installation is in progress. Changes and restarts are temporarily unavailable.");
  if (restarting || pendingAction != DeviceAction::NONE) return page(observation, 409, "Device action already scheduled.");
  if (firmwarePath) {
    if (!firmware || !firmwareControl) return firmwarePage(503, "Updater unavailable.");
    for (const auto& entry : form.values)
      if (entry.first != "token" && entry.first != "revision" && !(request.path == "/firmware/install" && entry.first == "version"))
        return firmwarePage(400, "Unknown firmware form field.");
    FirmwareUpdate::Error result;
    if (request.path == "/firmware/check")
      result = firmwareControl->requestCheck();
    else if (request.path == "/firmware/cancel")
      result = firmwareControl->cancel();
    else if (request.path == "/firmware/install") {
      const auto version = form.find("version");
      if (!version || version->size() >= 24 || version->find('\0') != std::string::npos) return firmwarePage(400, "Invalid release version.");
      result = firmwareControl->validateInstall(version->c_str());
      if (result == FirmwareUpdate::Error::NONE) {
        auto response = firmwarePage(202, "Installation request accepted. Status refreshes automatically.");
        response.action = DeviceAction::INSTALL_FIRMWARE;
        response.actionValue = *version;
        return response;
      }
    } else
      return firmwarePage(404, "Page not found.");
    firmware->recordCommandResult(result);
    const auto message = result == FirmwareUpdate::Error::NONE
                             ? (request.path == "/firmware/check" ? "Update check requested." : "Queued installation cancelled.")
                             : FirmwareUpdate::errorName(result);
    return firmwarePage(result == FirmwareUpdate::Error::NONE ? 200 : 409, message);
  }
  for (const auto& entry : form.values) {
    if (entry.first == "token" || entry.first == "revision") continue;
    bool allowed = false;
    if (request.path == "/save") {
      allowed = entry.first == "mqtt_user" || entry.first == "mqtt_password" || entry.first == "clear_mqtt_user" || entry.first == "clear_mqtt_password";
      for (const auto& field : kFields)
        if (entry.first == field.key && applicable(field, hardware)) allowed = true;
    } else if (request.path == "/import")
      allowed = entry.first == "settings_json";
    else if (request.path == "/wifi")
      allowed = entry.first == "ssid" || entry.first == "wifi_password" || entry.first == "clear_wifi_password";
    else if (request.path == "/wifi/reset" || request.path == "/settings/reset")
      allowed = entry.first == "confirmation";
    if (!allowed) return page(observation, 400, "Unknown or inapplicable form field.");
  }
  if (request.path == "/restart") {
    Response response = page(observation, 200, "Restart requested. This page will disconnect; reconnect using the device hostname or new IP address.");
    response.restart = true;
    return response;
  }
  if (request.path == "/recovery/start" || request.path == "/recovery/stop" || request.path == "/wifi/reset" || request.path == "/settings/reset") {
    if (!recovery) return page(observation, 503, "Recovery service unavailable.");
    DeviceAction action;
    if (request.path == "/recovery/start") {
      if (!recovery->available()) return page(observation, 503, "Protected recovery unavailable; check USB serial.");
      action = DeviceAction::START_RECOVERY;
    } else if (request.path == "/recovery/stop") action = DeviceAction::STOP_RECOVERY;
    else {
      const auto confirmation = form.find("confirmation");
      const bool networkOnly = request.path == "/wifi/reset";
      if (!confirmation || *confirmation != (networkOnly ? "FORGET WIFI" : "RESET SETTINGS")) {
        return page(observation, 400, "Enter the exact reset confirmation shown on the form.");
      }
      action = networkOnly ? DeviceAction::RESET_WIFI : DeviceAction::RESET_SETTINGS;
    }
    auto response = page(observation, 200, "Action requested. Recovery/reset runs after this reply. Check the AP or USB serial if connectivity changes.");
    response.action = action;
    return response;
  }
  if (request.path == "/wifi/cancel") {
    const auto result = wifi.cancel();
    return page(observation, result.ok() ? 200 : 400, result.ok() ? "Staged Wi-Fi change cancelled." : errorText(result));
  }
  if (request.path == "/wifi") {
    Settings::WifiCredentials candidate;
    const auto pending = wifi.pending(candidate);
    const auto result = pending.status == Settings::Status::MISSING ? wifi.current(candidate) : pending;
    if (!result.ok()) return page(observation, 400, errorText(result));
    const auto ssid = form.find("ssid"), password = form.find("wifi_password"), clear = form.find("clear_wifi_password");
    if (!ssid || (clear && (*clear != "1" || (password && !password->empty())))) return page(observation, 400, "Invalid Wi-Fi form.");
    candidate.ssid = *ssid;
    if (clear) candidate.password.clear();
    else if (password && !password->empty()) candidate.password = *password;
    const auto staged = wifi.stage(candidate);
    return page(observation, staged.ok() ? 200 : 400, staged.ok() ? "Wi-Fi change saved. Restart when ready." : errorText(staged));
  }
  if (request.path != "/save" && request.path != "/import") return page(observation, 404, "Page not found.");
  RuntimeSettings candidate;
  if (!copyCredentials(desired(), candidate)) return page(observation, 503, "Cannot prepare settings.");
  std::string exported;
  if (request.path == "/import") {
    const auto record = form.find("settings_json");
    if (!record) return page(observation, 400, "Missing settings JSON.");
    exported = *record;
  } else {
    const auto result = Settings::encodeExport(desired(), hardware, exported);
    if (!result.ok()) return page(observation, 400, errorText(result));
    JsonDocument document;
    if (deserializeJson(document, exported)) return page(observation, 503, "Cannot prepare settings.");
    for (const auto& field : kFields) {
      const auto value = form.find(field.key);
      if (value && !setValue(document["settings"][field.key], field.type, *value)) return page(observation, 400, std::string("Invalid value: ") + field.label);
    }
    if (document.overflowed()) return page(observation, 503, "Cannot prepare settings.");
    exported.clear();
    serializeJson(document, exported);
  }
  const auto decoded = Settings::decodeExport(exported, hardware, candidate);
  if (!decoded.ok()) return page(observation, 400, errorText(decoded));
  if (request.path == "/save" && (!updateSecret(form, "mqtt_user", "clear_mqtt_user", candidate.network.mqtt.user) ||
                                  !updateSecret(form, "mqtt_password", "clear_mqtt_password", candidate.network.mqtt.password))) {
    return page(observation, 400, "Provide a new credential or select Clear, not both.");
  }
  const auto saved = settings.propose(candidate);
  return page(observation, saved.ok() ? 200 : 400, saved.ok() ? "Settings saved. Power changes are queued for verification; service changes require restart." :
                                                                      errorText(saved));
}

void Controller::responseSent(bool restart, uint32_t now) {
  if (!restart) return;
  restarting = true;
  restartAt = now;
}
bool Controller::restartDue(uint32_t now) const { return restarting && uint32_t(now - restartAt) >= 300; }

void Controller::responseSent(const Response& response, uint32_t now) {
  responseSent(response.restart, now);
  if (response.action == DeviceAction::NONE) return;
  pendingAction = response.action;
  if (response.action == DeviceAction::INSTALL_FIRMWARE) pendingFirmwareVersion = response.actionValue;
  actionAt = now;
}

DeviceAction Controller::takeAction(uint32_t now) {
  if (pendingAction == DeviceAction::NONE || uint32_t(now - actionAt) < 300) return DeviceAction::NONE;
  const auto action = pendingAction;
  pendingAction = DeviceAction::NONE;
  if (action == DeviceAction::INSTALL_FIRMWARE) {
    if (firmware && firmwareControl) firmware->recordCommandResult(firmwareControl->requestInstall(pendingFirmwareVersion.c_str()));
    pendingFirmwareVersion.clear();
    return DeviceAction::NONE;
  }
  return action;
}
}  // namespace ConfigWeb
