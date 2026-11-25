#include "config_http.h"

#include <algorithm>
#include <cstdlib>
#include <utility>

namespace ConfigWeb {
namespace {
std::string lower(std::string value) {
  for (auto& c : value) if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
  return value;
}
std::string trim(const std::string& value) {
  const auto begin = value.find_first_not_of(" \t");
  return begin == std::string::npos ? "" : value.substr(begin, value.find_last_not_of(" \t") - begin + 1);
}
}  // namespace

void RequestParser::reset() {
  request = Request{};
  header.clear();
  headersDone = false;
  contentLength = 0;
  errorCode = 0;
}

void RequestParser::append(const char* data, size_t length) {
  if (errorCode) return;
  size_t position = 0;
  while (!headersDone && position < length) {
    const unsigned char c = data[position++];
    if ((c < 32 && c != '\r' && c != '\n' && c != '\t') || c == 127) { errorCode = 400; return; }
    header += static_cast<char>(c);
    if (header.size() > kMaxHeaders) { errorCode = 431; return; }
    if (header.size() >= 4 && header.compare(header.size() - 4, 4, "\r\n\r\n") == 0) headers();
    if (errorCode) return;
  }
  if (!headersDone) return;
  if (length - position > contentLength - request.body.size()) { errorCode = 400; return; }
  request.body.append(data + position, length - position);
}

void RequestParser::headers() {
  size_t end = header.find("\r\n");
  const auto line = header.substr(0, end);
  const auto first = line.find(' '), second = line.find(' ', first == std::string::npos ? first : first + 1);
  if (first == std::string::npos || second == std::string::npos ||
      (line.substr(second + 1) != "HTTP/1.1" && line.substr(second + 1) != "HTTP/1.0")) { errorCode = 400; return; }
  request.method = line.substr(0, first);
  request.path = line.substr(first + 1, second - first - 1);
  if (request.path.empty() || request.path[0] != '/' || request.path.size() > 64 || request.path.find_first_of("?# ") != std::string::npos) {
    errorCode = 400; return;
  }
  if (request.method != "GET" && request.method != "POST") { errorCode = 405; return; }
  bool haveLength = false, haveHost = false, haveOrigin = false, haveType = false, haveSite = false;
  size_t start = end + 2;
  while ((end = header.find("\r\n", start)) != std::string::npos && end != start) {
    const auto colon = header.find(':', start);
    if (colon == std::string::npos || colon >= end) { errorCode = 400; return; }
    const auto name = lower(header.substr(start, colon - start));
    if (name.empty() || name.find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789-!#$%&'*+.^_`|~") != std::string::npos) {
      errorCode = 400; return;
    }
    const auto value = trim(header.substr(colon + 1, end - colon - 1));
    auto once = [&](bool& seen) { if (seen) errorCode = 400; seen = true; };
    if (name == "host") { once(haveHost); request.host = lower(value); }
    else if (name == "origin") { once(haveOrigin); request.origin = lower(value); }
    else if (name == "sec-fetch-site") { once(haveSite); request.fetchSite = lower(value); }
    else if (name == "content-type") { once(haveType); request.contentType = lower(value); }
    else if (name == "content-length") {
      once(haveLength);
      if (value.empty() || value.size() > 8 || value.find_first_not_of("0123456789") != std::string::npos) { errorCode = 400; return; }
      contentLength = std::strtoul(value.c_str(), nullptr, 10);
      if (contentLength > kMaxBody) { errorCode = 413; return; }
    } else if (name == "transfer-encoding") { errorCode = 400; return; }
    else if (name == "expect") { errorCode = 417; return; }
    if (errorCode) return;
    start = end + 2;
  }
  if (!haveHost || request.host.empty()) { errorCode = 400; return; }
  if (request.method == "POST" && !haveLength) { errorCode = 411; return; }
  if (request.method == "GET" && contentLength != 0) { errorCode = 400; return; }
  headersDone = true;
  header.clear();
}

std::string responseHeaders(const Response& response) {
  return "HTTP/1.1 " + std::to_string(response.code) + " " + (response.code < 400 ? "OK" : "Request rejected") +
         "\r\nContent-Type: " + response.contentType + "\r\nContent-Length: " + std::to_string(response.body.size()) +
         "\r\nConnection: close\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nReferrer-Policy: same-origin\r\n"
         "Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'\r\n" +
         (response.attachment ? "Content-Disposition: attachment; filename=ups-settings.json\r\n" : "") + "\r\n";
}
}  // namespace ConfigWeb
