#pragma once

#include <cstddef>

constexpr int MSG_DONTWAIT = 0x40;
int recv(int socket, char* buffer, size_t length, int flags);
int send(int socket, const char* buffer, size_t length, int flags);
