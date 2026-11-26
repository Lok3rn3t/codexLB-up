from __future__ import annotations

import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from scripts.release_platform_images import resolve_platform_images

pytestmark = pytest.mark.unit
_ROOT = Path(__file__).resolve().parents[2]
_REPOSITORY = "ghcr.io/example/image"
_INDEX_REF = f"{_REPOSITORY}@sha256:{'0' * 64}"
_AMD64_REF = f"{_REPOSITORY}@sha256:{'a' * 64}"
_ARM64_REF = f"{_REPOSITORY}@sha256:{'b' * 64}"


def _index() -> dict[str, Any]:
    return {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.index.v1+json",
        "manifests": [
            {
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "digest": f"sha256:{digest * 64}",
                "platform": {"os": "linux", "architecture": architecture},
            }
            for architecture, digest in (("amd64", "a"), ("arm64", "b"))
        ],
    }


@pytest.mark.parametrize("docker_media_types", [False, True])
@pytest.mark.parametrize("arm64_variant", [None, "v8"])
def test_resolves_distinct_images_and_excludes_attestations(
    docker_media_types: bool, arm64_variant: str | None
) -> None:
    index = _index()
    if docker_media_types:
        index["mediaType"] = "application/vnd.docker.distribution.manifest.list.v2+json"
        for descriptor in index["manifests"]:
            descriptor["mediaType"] = "application/vnd.docker.distribution.manifest.v2+json"
    if arm64_variant is not None:
        index["manifests"][1]["platform"]["variant"] = arm64_variant
    # BuildKit attestations normally use unknown/unknown. The annotation must
    # still exclude an attestation if it claims the executable platform.
    for platform in ({"os": "unknown", "architecture": "unknown"}, {"os": "linux", "architecture": "amd64"}):
        index["manifests"].insert(
            0,
            {
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "digest": f"sha256:{'c' * 64}",
                "platform": platform,
                "annotations": {"vnd.docker.reference.type": "attestation-manifest"},
            },
        )

    assert resolve_platform_images(_INDEX_REF, index) == {"amd64": _AMD64_REF, "arm64": _ARM64_REF}


@pytest.mark.parametrize("architecture", ["amd64", "arm64"])
def test_rejects_missing_or_attestation_only_architecture(architecture: str) -> None:
    index = _index()
    missing = next(item for item in index["manifests"] if item["platform"]["architecture"] == architecture)
    index["manifests"].remove(missing)
    with pytest.raises(ValueError, match="must contain both"):
        resolve_platform_images(_INDEX_REF, index)

    missing["annotations"] = {"vnd.docker.reference.type": "attestation-manifest"}
    index["manifests"].append(missing)
    with pytest.raises(ValueError, match="must contain both"):
        resolve_platform_images(_INDEX_REF, index)


@pytest.mark.parametrize("same_digest", [False, True])
def test_rejects_duplicate_architecture_even_for_identical_digest(same_digest: bool) -> None:
    index = _index()
    duplicate = deepcopy(index["manifests"][1])
    if not same_digest:
        duplicate["digest"] = f"sha256:{'d' * 64}"
    index["manifests"].append(duplicate)
    with pytest.raises(ValueError, match="ambiguous.*linux/arm64"):
        resolve_platform_images(_INDEX_REF, index)


@pytest.mark.parametrize("digest", [None, "", "sha256:short", f"sha256:{'g' * 64}", f"sha256:{'b' * 64}\n"])
def test_rejects_malformed_child_digest(digest: str | None) -> None:
    index = _index()
    index["manifests"][1]["digest"] = digest
    with pytest.raises(ValueError, match="invalid manifest digest"):
        resolve_platform_images(_INDEX_REF, index)


def test_rejects_shared_digest_between_architectures() -> None:
    index = _index()
    index["manifests"][1]["digest"] = index["manifests"][0]["digest"]
    with pytest.raises(ValueError, match="distinct executable manifests"):
        resolve_platform_images(_INDEX_REF, index)


@pytest.mark.parametrize("field,value", [("mediaType", "application/vnd.oci.image.index.v1+json"), ("variant", "v9")])
def test_rejects_non_executable_or_unsupported_platform(field: str, value: str) -> None:
    index = _index()
    descriptor = index["manifests"][1]
    if field == "variant":
        descriptor["platform"][field] = value
    else:
        descriptor[field] = value
    with pytest.raises(ValueError, match="unsupported executable manifest"):
        resolve_platform_images(_INDEX_REF, index)


@pytest.mark.parametrize(
    "index", [[], {}, {"schemaVersion": 2, "mediaType": "application/vnd.oci.image.manifest.v1+json"}]
)
def test_rejects_non_index_input(index: object) -> None:
    with pytest.raises(ValueError, match="OCI index or Docker manifest list"):
        resolve_platform_images(_INDEX_REF, index)


@pytest.mark.parametrize("reference", [f"{_REPOSITORY}:1.25.0", f"{_REPOSITORY}@sha256:short", _INDEX_REF + "\n"])
def test_requires_immutable_parent_reference(reference: str) -> None:
    with pytest.raises(ValueError, match="immutable sha256 index reference"):
        resolve_platform_images(reference, _index())


@pytest.mark.parametrize("valid", [False, True])
def test_cli_emits_all_outputs_only_after_successful_resolution(tmp_path: Path, valid: bool) -> None:
    index = _index()
    if not valid:
        index["manifests"].append(deepcopy(index["manifests"][1]))
    output_file = tmp_path / "github-output"
    output_file.write_text("existing=retained\n", encoding="utf-8")
    env = os.environ | {"GITHUB_OUTPUT": str(output_file)}
    result = subprocess.run(
        [sys.executable, "-m", "scripts.release_platform_images", "--image-ref", _INDEX_REF],
        cwd=_ROOT,
        env=env,
        input=json.dumps(index),
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )
    if valid:
        assert result.returncode == 0, result.stderr
        expected = f"amd64={_AMD64_REF}\narm64={_ARM64_REF}\n"
        assert result.stdout == expected
        assert output_file.read_text(encoding="utf-8") == "existing=retained\n" + expected
    else:
        assert result.returncode != 0
        assert "ambiguous" in result.stderr
        assert not result.stdout
        assert output_file.read_text(encoding="utf-8") == "existing=retained\n"
