#pragma once
#include <cstddef>
#include <cstdint>
struct mbedtls_sha256_context {
  size_t bytes = 0;
};
void mbedtls_sha256_init(mbedtls_sha256_context* context);
void mbedtls_sha256_free(mbedtls_sha256_context* context);
int mbedtls_sha256_starts(mbedtls_sha256_context* context, int is224);
int mbedtls_sha256_update(mbedtls_sha256_context* context, const uint8_t* bytes, size_t count);
int mbedtls_sha256_finish(mbedtls_sha256_context* context, uint8_t output[32]);
