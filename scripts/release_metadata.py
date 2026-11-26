#!/usr/bin/env python3
"""Emit release metadata for a tag."""

from __future__ import annotations

import argparse
import os

from scripts.release_versions import parse_tag, write_github_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default=os.environ.get("RELEASE_TAG", ""), help="release tag, e.g. v1.2.3")
    parser.add_argument(
        "--skip-pypi", action="store_true", help="rebuild eligible release artifacts without uploading to PyPI"
    )
    parser.add_argument(
        "--published-stable-tag", default="", help="existing public stable tag verified by the workflow"
    )
    args = parser.parse_args()

    if not args.tag:
        raise SystemExit("missing release tag")
    release = parse_tag(args.tag)
    if args.skip_pypi and not release.is_prerelease and args.published_stable_tag != release.tag:
        raise SystemExit("--skip-pypi requires a prerelease or the matching published stable fork tag")
    outputs = {
        "tag": release.tag,
        "version": release.version,
        "base_version": release.base,
        "channel": release.channel,
        "is_prerelease": release.is_prerelease,
        "pypi_version": release.pypi_version,
        "make_latest": "false" if release.is_prerelease else "legacy",
        "publish_pypi": not args.skip_pypi,
    }
    write_github_outputs(outputs)
    for key, value in outputs.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
