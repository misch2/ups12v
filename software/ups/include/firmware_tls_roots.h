#pragma once

namespace FirmwareUpdate {
// PlatformIO's binary embedding supplies this NUL-terminated PEM asset.
extern const char kTlsRootCertificates[] asm("_binary_certs_update_roots_pem_start");
}  // namespace FirmwareUpdate
