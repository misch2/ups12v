import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

TOOLS = Path(__file__).parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location("firmware_release", TOOLS / "firmware_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

VERSION = "20261125.3"
COMMIT = "a" * 40
REPOSITORY = "example/ups"


def partition_table(capacity=0x10000):
    entries = b"".join(struct.pack("<HBBII16sI", 0x50AA, 0, 0x10 + index, 0x10000 + index * 0x10000,
                                  capacity, b"app", 0) for index in range(2))
    checksum = b"\xeb\xeb" + b"\xff" * 14 + hashlib.md5(entries).digest()
    return (entries + checksum).ljust(3072, b"\xff")


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.header = self.root / "version.h"
        self.header.write_text(f'#define FIRMWARE_VERSION "{VERSION}"\n', encoding="utf-8")
        self.staged = self.root / "staged"
        self.bundle = self.root / "bundle"

    def stage_all(self):
        for index, name in enumerate(release.VARIANTS):
            build = self.root / name
            build.mkdir()
            (build / "firmware.bin").write_bytes(b"\xe9" + bytes([index]) * 1023)
            (build / "partitions.bin").write_bytes(partition_table())
            release.stage_variant(build, self.staged, name, REPOSITORY, VERSION, COMMIT)

    def assemble(self):
        return release.assemble(self.staged, self.bundle, REPOSITORY, VERSION, COMMIT)

    def test_version_gate(self):
        self.assertEqual(release.read_version(self.header, "fw-" + VERSION), VERSION)
        with self.assertRaises(ValueError):
            release.read_version(self.header, "fw-20261125.2")
        for version in ("20260230.1", "20261125.03", "20261125.3;echo bad", "1.2.3", "20261125.4294967296"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                release.version_key(version)
        self.header.write_text("", encoding="utf-8")
        with self.assertRaises(ValueError):
            release.read_version(self.header)

    def test_complete_bundle_and_public_urls(self):
        self.stage_all()
        manifest = self.assemble()
        self.assertEqual(set(manifest["variants"]), set(release.VARIANTS))
        self.assertEqual(manifest["source_commit"], COMMIT)
        self.assertLessEqual((self.bundle / "manifest.json").stat().st_size, release.MAX_MANIFEST_BYTES)
        for name, value in manifest["variants"].items():
            image = (self.bundle / (name + ".bin")).read_bytes()
            self.assertEqual(value["size"], len(image))
            self.assertEqual(value["sha256"], hashlib.sha256(image).hexdigest())
            self.assertEqual(value["url"], f"https://github.com/{REPOSITORY}/releases/download/fw-{VERSION}/{name}.bin")
        for line in (self.bundle / "SHA256SUMS").read_text().splitlines():
            digest, filename = line.split("  ")
            self.assertEqual(digest, hashlib.sha256((self.bundle / filename).read_bytes()).hexdigest())
        self.assertEqual(set(path.name for path in self.bundle.iterdir()),
                         {name + ".bin" for name in release.VARIANTS} | {"manifest.json", "SHA256SUMS"})

    def test_missing_variant_and_unexpected_file(self):
        self.stage_all()
        extra = self.staged / "private.txt"
        extra.write_text("must not ship", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.assemble()
        extra.unlink()
        (self.staged / "ups_v1_esp32.bin").unlink()
        with self.assertRaises(ValueError):
            self.assemble()
        self.assertFalse(self.bundle.exists())

    def test_cli_version_and_assembly(self):
        command = [sys.executable, str(TOOLS / "firmware_release.py")]
        common = ["--header", str(self.header), "--tag", "fw-" + VERSION]
        result = subprocess.run(command + ["version"] + common, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), VERSION)
        result = subprocess.run(command + ["version", "--header", str(self.header), "--tag", "fw-20261125.2"],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.stage_all()
        result = subprocess.run(command + ["assemble"] + common + ["--repository", REPOSITORY, "--commit", COMMIT,
                                "--staged", str(self.staged), "--output", str(self.bundle)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.bundle / "manifest.json").read_text())["version"], VERSION)

    def test_mixed_version_commit_hardware_or_tampered_image(self):
        self.stage_all()
        path = self.staged / "ups_v1_esp32.json"
        original = json.loads(path.read_text())
        for key, value in (("version", "20261125.2"), ("source_commit", "b" * 40), ("hardware", release.VARIANTS["ups_v4_esp32c3"]),
                           ("size", True), ("sha256", "0" * 64), ("url", "https://other.test/firmware.bin")):
            changed = dict(original, **{key: value})
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.subTest(field=key), self.assertRaises(ValueError):
                self.assemble()
        path.write_text(json.dumps(original), encoding="utf-8")
        (self.staged / "ups_v1_esp32.bin").write_bytes(b"\xe9" + b"changed" * 200)
        with self.assertRaises(ValueError):
            self.assemble()
        self.assertFalse(self.bundle.exists())

    def test_oversize_corrupt_table_and_invalid_image(self):
        build = self.root / "build"
        build.mkdir()
        image = build / "firmware.bin"
        table = build / "partitions.bin"
        table.write_bytes(partition_table())
        image.write_bytes(b"\xe9" + b"a" * 0x10000)
        with self.assertRaises(ValueError) as failure:
            release.stage_variant(build, self.staged, "ups_v1_esp32", REPOSITORY, VERSION, COMMIT)
        self.assertIn("image 65537 bytes", str(failure.exception))
        self.assertIn("ota_0: capacity 65536 bytes, excess 1 bytes", str(failure.exception))
        self.assertIn("ota_1: capacity 65536 bytes, excess 1 bytes", str(failure.exception))
        image.write_bytes(b"invalid")
        with self.assertRaises(ValueError):
            release.stage_variant(build, self.staged, "ups_v1_esp32", REPOSITORY, VERSION, COMMIT)
        image.write_bytes(b"\xe9" + b"a" * 100)
        table.write_bytes(b"bad table")
        with self.assertRaises(ValueError):
            release.stage_variant(build, self.staged, "ups_v1_esp32", REPOSITORY, VERSION, COMMIT)
        self.assertFalse(self.staged.exists())

    def test_safe_stable_promotion_and_site_bytes(self):
        self.stage_all()
        manifest = self.assemble()
        release.check_promotion(manifest, None)
        release.check_promotion(manifest, manifest)
        old = dict(manifest, version="20261125.2")
        release.check_promotion(manifest, old)
        with self.assertRaises(ValueError):
            release.check_promotion(old, manifest)
        with self.assertRaises(ValueError):
            release.check_promotion(dict(manifest, source_commit="b" * 40), manifest)
        with self.assertRaises(ValueError):
            release.check_promotion(manifest, {"schema": 2})
        site = self.root / "site"
        release.make_site(self.bundle / "manifest.json", site, old)
        self.assertEqual((site / "firmware/stable.json").read_bytes(), (self.bundle / "manifest.json").read_bytes())

    def test_feed_fetch_failures_are_not_empty_releases(self):
        url = "https://example.test/firmware/stable.json"
        with patch.object(release, "urlopen", side_effect=HTTPError(url, 404, "missing", {}, None)):
            self.assertIsNone(release.fetch_current(url))
        for code in (403, 500):
            with patch.object(release, "urlopen", side_effect=HTTPError(url, code, "failure", {}, None)), self.assertRaises(HTTPError):
                release.fetch_current(url)
        with patch.object(release, "urlopen", side_effect=TimeoutError()), self.assertRaises(TimeoutError):
            release.fetch_current(url)
        class Response(io.BytesIO):
            def geturl(self):
                return url
        with patch.object(release, "urlopen", return_value=Response(b"a" * (release.MAX_MANIFEST_BYTES + 1))), self.assertRaises(ValueError):
            release.fetch_current(url)
        with self.assertRaises(ValueError):
            release.fetch_current("http://example.test/stable.json")


if __name__ == "__main__":
    unittest.main()
