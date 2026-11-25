#include "config_web_server.h"

#include <esp_random.h>
#include <lwip/sockets.h>

#include <algorithm>
#include <cerrno>
#include <cstdio>

namespace ConfigWeb {
void LanServer::begin() {
  char token[33];
  for (int i = 0; i < 4; ++i) std::snprintf(token + 8 * i, 9, "%08lx", static_cast<unsigned long>(esp_random()));
  controller.begin(token);
}

void LanServer::close() {
  client.stop();
  parser.reset();
  response = Response{};
  headers.clear();
  sent = 0;
  sending = false;
}

void LanServer::loop(const char* hostname, Observation observation, bool apReady) {
  const uint32_t now = millis();
  if (WiFi.status() != WL_CONNECTED && !apReady) {
    close();
    if (listening) listener.end();
    listening = false;
    return;
  }
  if (!listening) {
    listener.begin();
    listener.setNoDelay(true);
    listening = true;
  }
  if (client.fd() < 0) {
    client = listener.accept();
    if (client.fd() < 0) return;
    acceptedAt = now;
  }
  if (uint32_t(now - acceptedAt) >= 5000) { close(); return; }
  if (!sending) {
    char buffer[1024];
    const int received = ::recv(client.fd(), buffer, sizeof(buffer), MSG_DONTWAIT);
    if (received == 0) { close(); return; }
    if (received < 0) {
      if (errno != EWOULDBLOCK && errno != EAGAIN) close();
      return;
    }
    parser.append(buffer, static_cast<size_t>(received));
    if (parser.error()) {
      response.code = parser.error();
      response.contentType = "text/plain; charset=utf-8";
      response.body = "Malformed, unsupported or oversized request.";
    } else if (parser.complete()) {
      response = controller.handle(parser.value(), hostname, client.localIP().toString().c_str(), observation);
    } else return;
    headers = responseHeaders(response);
    sending = true;
    return;  // Power service gets another turn before any response socket write.
  }
  const bool writingHeaders = sent < headers.size();
  const size_t offset = writingHeaders ? sent : sent - headers.size();
  const auto& data = writingHeaders ? headers : response.body;
  const size_t length = std::min(size_t(1024), data.size() - offset);
  if (length) {
    const int written = ::send(client.fd(), data.data() + offset, length, MSG_DONTWAIT);
    if (written < 0) {
      if (errno != EWOULDBLOCK && errno != EAGAIN) close();
      return;
    }
    if (written == 0) { close(); return; }
    sent += static_cast<size_t>(written);
  }
  if (sent == headers.size() + response.body.size()) {
    controller.responseSent(response, now);
    close();
  }
}
}  // namespace ConfigWeb
