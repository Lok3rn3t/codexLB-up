from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.release_versions import parse_tag


@pytest.mark.parametrize(
    ("tag", "publish_pypi"),
    [("v1.27.0", True), ("v1.27.0", False), ("v1.27.0-beta.1", True), ("v1.27.0-beta.1", False)],
)
def test_release_install_commands_select_the_tag(tmp_path: Path, tag: str, publish_pypi: bool) -> None:
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("The release workflow uses Bash")
    path = Path(__file__).resolve().parents[2] / ".github/workflows/release.yml"
    steps = yaml.safe_load(path.read_text(encoding="utf-8"))["jobs"]["create-github-release"]["steps"]
    script = next(step["run"] for step in steps if step.get("name") == "Append install and contributors")
    release = parse_tag(tag)
    env = {
        **os.environ,
        "TAG_NAME": tag,
        "IS_PRERELEASE": str(release.is_prerelease).lower(),
        "PYPI_VERSION": release.pypi_version,
        "PUBLISH_PYPI": str(publish_pypi).lower(),
        "GITHUB_REPOSITORY": "Lok3rn3t/codexLB-up",
        "GITHUB_REPOSITORY_OWNER": "Lok3rn3t",
    }
    subprocess.run([bash, "-c", script], cwd=tmp_path, env=env, check=True)

    lines = (tmp_path / "release_notes.md").read_text(encoding="utf-8").splitlines()
    python_commands = [line for line in lines if line.startswith("uvx ")]
    if publish_pypi:
        assert python_commands == [f'uvx --from "codexLB-up=={release.pypi_version}" codex-lb']
    elif release.is_prerelease:
        assert python_commands == []
    else:
        wheel = f"codexlb_up-{release.pypi_version}-py3-none-any.whl"
        url = f"https://github.com/Lok3rn3t/codexLB-up/releases/download/{tag}/{wheel}"
        assert python_commands == [f'uvx --from "{url}" codex-lb']
    assert f"docker pull ghcr.io/lok3rn3t/codexlb-up:{release.version}" in lines
    helm = f"helm install codex-lb oci://ghcr.io/lok3rn3t/charts/codex-lb --version {release.version}"
    assert helm + (" --devel" if release.is_prerelease else "") in lines


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


@pytest.mark.parametrize("published_tag", ["", "v1.25.0"])
def test_new_stable_release_cannot_skip_pypi(published_tag: str) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.release_metadata",
            "--tag",
            "v1.26.0",
            "--skip-pypi",
            "--published-stable-tag",
            published_tag,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "matching published stable fork tag" in result.stderr
    assert "publish_pypi=" not in result.stdout


def test_published_stable_fork_rebuild_can_skip_pypi() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.release_metadata",
            "--tag",
            "v1.27.0",
            "--skip-pypi",
            "--published-stable-tag",
            "v1.27.0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "publish_pypi=false" in result.stdout.splitlines()
    assert "is_prerelease=false" in result.stdout.splitlines()


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
