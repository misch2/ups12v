"""Stage checked application images, assemble a release, and prepare its public feed."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.error import HTTPError
from urllib.request import urlopen

from check_ota_size import check_size


VARIANTS = {
    "ups_v1_esp32": {"version": "1.0", "mcu": "esp32", "power_path": "pmid_switchover"},
    "ups_v3_sys_esp32": {"version": "3.3b-SYSmod", "mcu": "esp32", "power_path": "sys"},
    "ups_v4_esp32c3": {"version": "4.0", "mcu": "esp32c3", "power_path": "sys"},
}
MAX_MANIFEST_BYTES = 8192


def version_key(version):
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]{8}\.(0|[1-9][0-9]*)", version):
        raise ValueError("version must use YYYYMMDD.revision")
    day, revision = version.split(".")
    datetime.strptime(day, "%Y%m%d")
    return int(day), int(revision)


def read_version(header, tag=""):
    matches = re.findall(r'^\s*#\s*define\s+FIRMWARE_VERSION\s+"([^"\r\n]+)"\s*$', header.read_text(encoding="utf-8"), re.MULTILINE)
    if len(matches) != 1:
        raise ValueError("version header must define FIRMWARE_VERSION exactly once")
    version = matches[0]
    version_key(version)
    if tag and tag != "fw-" + version:
        raise ValueError("firmware tag does not match FIRMWARE_VERSION")
    return version


def validate_source(repository, commit):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or any(p in (".", "..") for p in repository.split("/")):
        raise ValueError("expected GitHub owner/repository")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("expected full source commit")


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def load_json(path):
    if path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("release metadata exceeds size limit")
    return json.loads(path.read_text(encoding="utf-8"))


def release_base(repository, version):
    return f"https://github.com/{repository}/releases/download/fw-{version}/"


def stage_variant(build, output, variant, repository, version, commit):
    validate_source(repository, commit)
    version_key(version)
    if variant not in VARIANTS:
        raise ValueError("unknown hardware variant")
    image = build / "firmware.bin"
    data = image.read_bytes()
    size = len(data)
    if size < 24 or data[:1] != b"\xe9":
        raise ValueError("not an ESP application image")
    slots = check_size(size, (build / "partitions.bin").read_bytes())
    if any(spare < 0 for _, _, _, spare in slots):
        raise ValueError("final application exceeds a generated OTA slot")
    filename = variant + ".bin"
    metadata = {
        "schema": 1, "variant": variant, "version": version, "source_commit": commit,
        "hardware": VARIANTS[variant], "url": release_base(repository, version) + filename,
        "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        "build_ota_slots": [{"name": name, "offset": offset, "size": capacity} for name, offset, capacity, _ in slots],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / filename).write_bytes(data)
    (output / (variant + ".json")).write_bytes(json_bytes(metadata))
    return metadata


def assemble(staged, output, repository, version, commit):
    validate_source(repository, commit)
    version_key(version)
    expected = {name + suffix for name in VARIANTS for suffix in (".bin", ".json")}
    if {path.name for path in staged.iterdir()} != expected:
        raise ValueError("release requires exactly all three staged images and metadata files")
    variants = {}
    images = {}
    for name, hardware in VARIANTS.items():
        metadata = load_json(staged / (name + ".json"))
        image = (staged / (name + ".bin")).read_bytes()
        if (metadata.get("schema") != 1 or metadata.get("variant") != name or metadata.get("version") != version or
                metadata.get("source_commit") != commit or metadata.get("hardware") != hardware or
                metadata.get("url") != release_base(repository, version) + name + ".bin" or
                type(metadata.get("size")) is not int or metadata["size"] != len(image) or
                metadata.get("sha256") != hashlib.sha256(image).hexdigest()):
            raise ValueError("staged image identity, source, length or hash mismatch: " + name)
        slots = metadata.get("build_ota_slots")
        if (not isinstance(slots, list) or not slots or any(not isinstance(slot, dict) for slot in slots) or
                not {slot.get("name") for slot in slots}.issuperset({"ota_0", "ota_1"}) or
                any(type(slot.get("size")) is not int or slot["size"] < len(image) for slot in slots)):
            raise ValueError("invalid staged OTA capacity: " + name)
        variants[name] = {key: metadata[key] for key in ("hardware", "url", "size", "sha256", "build_ota_slots")}
        images[name + ".bin"] = image
    manifest = {
        "schema": 1, "version": version, "source_commit": commit,
        "release_url": f"https://github.com/{repository}/releases/tag/fw-{version}",
        "release_summary": "UPS firmware " + version, "variants": variants,
    }
    encoded = json_bytes(manifest)
    if len(encoded) > MAX_MANIFEST_BYTES:
        raise ValueError("manifest exceeds client size limit")
    images["manifest.json"] = encoded
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("release output directory must be empty")
    for name, content in images.items():
        (output / name).write_bytes(content)
    checksums = "".join(f"{hashlib.sha256(content).hexdigest()}  {name}\n" for name, content in sorted(images.items()))
    (output / "SHA256SUMS").write_text(checksums, encoding="ascii")
    return manifest


def check_promotion(candidate, current):
    if not isinstance(candidate, dict) or candidate.get("schema") != 1 or set(candidate.get("variants", {})) != set(VARIANTS):
        raise ValueError("invalid candidate manifest")
    candidate_key = version_key(candidate.get("version"))
    if current is None:
        return
    if not isinstance(current, dict) or current.get("schema") != 1:
        raise ValueError("existing feed is not a supported manifest")
    current_key = version_key(current.get("version"))
    if candidate_key < current_key:
        raise ValueError("refusing to replace the stable feed with an older version")
    if candidate_key == current_key and candidate != current:
        raise ValueError("refusing to replace an existing version with different content")


def fetch_current(url):
    if not url.startswith("https://"):
        raise ValueError("stable feed must use HTTPS")
    try:
        with urlopen(url, timeout=30) as response:
            if not response.geturl().startswith("https://"):
                raise ValueError("feed redirected away from HTTPS")
            raw = response.read(MAX_MANIFEST_BYTES + 1)
    except HTTPError as error:
        if error.code == 404:
            return None  # First publication only; other failures do not erase the current feed.
        raise
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValueError("existing manifest exceeds size limit")
    return json.loads(raw)


def make_site(manifest_path, output, current):
    candidate = load_json(manifest_path)
    check_promotion(candidate, current)
    destination = output / "firmware"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(manifest_path, destination / "stable.json")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    version = commands.add_parser("version")
    stage = commands.add_parser("stage")
    bundle = commands.add_parser("assemble")
    for item in (version, stage, bundle):
        item.add_argument("--header", type=Path, required=True)
        item.add_argument("--tag", default="")
    for item in (stage, bundle):
        item.add_argument("--repository", required=True)
        item.add_argument("--commit", required=True)
        item.add_argument("--output", type=Path, required=True)
    stage.add_argument("--variant", choices=VARIANTS, required=True)
    stage.add_argument("--build", type=Path, required=True)
    bundle.add_argument("--staged", type=Path, required=True)
    site = commands.add_parser("site")
    site.add_argument("--manifest", type=Path, required=True)
    site.add_argument("--output", type=Path, required=True)
    site.add_argument("--current-url", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "site":
            make_site(args.manifest, args.output, fetch_current(args.current_url))
        else:
            value = read_version(args.header, args.tag)
            if args.command == "version":
                print(value)
            elif args.command == "stage":
                stage_variant(args.build, args.output, args.variant, args.repository, value, args.commit)
                print(args.variant + ": staged with verified image length/hash and generated-slot fit")
            else:
                assemble(args.staged, args.output, args.repository, value, args.commit)
                print("Release assembled: all three variants, manifest.json and SHA256SUMS")
    except (OSError, ValueError) as error:
        print("Release preparation failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
