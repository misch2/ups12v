"""Maintainer commands for the tagged firmware release workflow."""

import argparse
import os
from pathlib import Path
import subprocess
import sys

from firmware_release import read_version, version_key


ROOT = Path(__file__).resolve().parents[3]
VERSION_HEADER = "software/ups/include/version.h"
WORKFLOW = ".github/workflows/firmware-release.yml"
REPOSITORY = "misch2/ups12v"


def run(*args, **kwargs):
    return subprocess.run(args, cwd=ROOT, text=True, **kwargs)


def publish(requested_version):
    version = read_version(ROOT / VERSION_HEADER)
    if requested_version and requested_version != version:
        raise ValueError(f"VERSION differs from {VERSION_HEADER} ({version})")

    commit = run("git", "rev-parse", "--verify", "HEAD", check=True, stdout=subprocess.PIPE).stdout.strip()
    pending = run(
        "git", "status", "--porcelain", "--untracked-files=normal", "--",
        WORKFLOW, "software/ups", ":(exclude,glob)software/ups/**/*.md",
        check=True, stdout=subprocess.PIPE,
    ).stdout
    if pending:
        raise ValueError("commit firmware and release workflow changes before publishing:\n" + pending.rstrip())
    run("git", "cat-file", "-e", f"{commit}:{WORKFLOW}", check=True)

    tag = f"fw-{version}"
    ref = f"refs/tags/{tag}"
    existing = run("git", "ls-remote", "--exit-code", "--refs", "origin", ref, stdout=subprocess.PIPE)
    if existing.returncode == 0:
        raise ValueError(f"{tag} already exists on origin. Use a new version for another release.")
    if existing.returncode != 2:
        existing.check_returncode()

    print(f"Pushing {tag} at {commit} to origin to start the firmware release workflow.", flush=True)
    run("git", "push", "--no-follow-tags", "origin", f"{commit}:{ref}", check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("publish", "mark-latest"))
    action = parser.parse_args().action
    version = os.environ.get("FIRMWARE_RELEASE_VERSION", "")
    try:
        if action == "publish":
            publish(version)
        else:
            if not version:
                raise ValueError("specify VERSION=YYYYMMDD.revision for mark-latest")
            version_key(version)
            run("gh", "release", "edit", f"fw-{version}", "--repo", REPOSITORY, "--latest", check=True)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Firmware release: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
