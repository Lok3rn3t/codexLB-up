from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml


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


def test_beta_publisher_dispatches_once_after_candidate_validation() -> None:
    path = Path(__file__).resolve().parents[2] / ".github/workflows/publish-beta-release.yml"
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    steps = workflow["jobs"]["publish-beta-release"]["steps"]
    commands = [step["run"] for step in steps if "run" in step]
    guard = next(i for i, command in enumerate(commands) if "scripts.guard_beta_release --mode publish" in command)
    publishers = [step for step in steps if "gh workflow run release.yml" in step.get("run", "")]
    assert len(publishers) == 1
    publisher = publishers[0]
    assert commands.index(publisher["run"]) > guard
    assert publisher["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert publisher["env"]["SKIP_PYPI"] == "${{ github.repository != 'Soju06/codex-lb' }}"
    assert '--ref "${TAG}"' in publisher["run"]
    assert '-f tag="${TAG}" -f skip_pypi="${SKIP_PYPI}"' in publisher["run"]
    assert all("gh release create" not in command for command in commands)
