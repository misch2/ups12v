#pragma once

#include <cstdint>
#include <string>

namespace ConfigWeb {
constexpr size_t kMaxHeaders = 2048;
constexpr size_t kMaxBody = 3 * 8192 + 4096;  // A percent-encoded settings export plus form fields.

struct Request {
  std::string method, path, host, origin, contentType, fetchSite, body;
};

// Incremental, bounded HTTP/1 request parser. No socket reads or waiting here.
class RequestParser {
 public:
  void reset();
  void append(const char* data, size_t length);
  bool complete() const { return headersDone && request.body.size() == contentLength && !errorCode; }
  int error() const { return errorCode; }
  const Request& value() const { return request; }

 private:
  void headers();
  Request request;
  std::string header;
  bool headersDone = false;
  size_t contentLength = 0;
  int errorCode = 0;
};

struct Response {
  int code = 200;
  std::string contentType = "text/html; charset=utf-8";
  std::string body;
  bool restart = false;
  bool attachment = false;
};

std::string responseHeaders(const Response& response);
}  // namespace ConfigWeb
