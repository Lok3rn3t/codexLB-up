from __future__ import annotations

import subprocess
import sys

import pytest


@pytest.mark.parametrize("tag", ["v1.26.0", "v1.26.0-beta.1"])
def test_release_metadata_requires_pypi_by_default(tag: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.release_metadata", "--tag", tag],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "publish_pypi=true" in result.stdout.splitlines()


def test_prerelease_rebuild_can_skip_pypi() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.release_metadata", "--tag", "v1.26.0-beta.1", "--skip-pypi"],
        check=True,
        capture_output=True,
        text=True,
    )
    outputs = result.stdout.splitlines()
    assert "publish_pypi=false" in outputs
    assert "is_prerelease=true" in outputs
    assert "make_latest=false" in outputs


def test_stable_release_cannot_skip_pypi() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.release_metadata", "--tag", "v1.26.0", "--skip-pypi"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "only allowed for prereleases" in result.stderr
    assert "publish_pypi=" not in result.stdout
