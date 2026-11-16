#!/usr/bin/env python3
"""Select executable platform images from an immutable release image index."""

from __future__ import annotations

import argparse
import json
import re
import sys

from scripts.release_versions import write_github_outputs

_INDEX_TYPES = ("application/vnd.oci.image.index.v1+json", "application/vnd.docker.distribution.manifest.list.v2+json")
_MANIFEST_TYPES = (
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
)


def resolve_platform_images(index_ref: str, index: object) -> dict[str, str]:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._:/-]*@sha256:[0-9a-f]{64}", index_ref):
        raise ValueError("release image must be an immutable sha256 index reference")
    if not isinstance(index, dict) or index.get("schemaVersion") != 2 or index.get("mediaType") not in _INDEX_TYPES:
        raise ValueError("release image must contain an OCI index or Docker manifest list")
    manifests = index.get("manifests")
    if not isinstance(manifests, list):
        raise ValueError("release image index must contain a manifest list")

    images: dict[str, str] = {}
    repository = index_ref.split("@", 1)[0]
    for descriptor in manifests:
        if not isinstance(descriptor, dict):
            raise ValueError("invalid image manifest descriptor")
        annotations = descriptor.get("annotations", {})
        if not isinstance(annotations, dict):
            raise ValueError("invalid image manifest annotations")
        if annotations.get("vnd.docker.reference.type") == "attestation-manifest":
            continue
        platform = descriptor.get("platform")
        if not isinstance(platform, dict):
            raise ValueError("image manifest descriptor is missing its platform")
        architecture = platform.get("architecture")
        if platform.get("os") != "linux" or architecture not in ("amd64", "arm64"):
            continue
        variants = (None, "") if architecture == "amd64" else (None, "", "v8")
        if platform.get("variant") not in variants or descriptor.get("mediaType") not in _MANIFEST_TYPES:
            raise ValueError(f"unsupported executable manifest for linux/{architecture}")
        digest = descriptor.get("digest")
        if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError(f"invalid manifest digest for linux/{architecture}")
        if architecture in images:
            raise ValueError(f"ambiguous executable manifests for linux/{architecture}")
        images[architecture] = f"{repository}@{digest}"

    if set(images) != {"amd64", "arm64"}:
        raise ValueError("release image index must contain both linux/amd64 and linux/arm64")
    if images["amd64"] == images["arm64"]:
        raise ValueError("release architectures must have distinct executable manifests")
    return images


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-ref", required=True, help="immutable parent index reference")
    args = parser.parse_args()
    try:
        images = resolve_platform_images(args.image_ref, json.load(sys.stdin))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    write_github_outputs(images)
    for architecture, image in images.items():
        print(f"{architecture}={image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
