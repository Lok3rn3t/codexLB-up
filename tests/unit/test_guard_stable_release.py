from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.unit.test_guard_beta_release import (
    event_file,
    git,
    init_repo_with_beta_commit,
    rename_distribution,
    update_project_versions,
)


def run_stable_guard(project_root: Path, repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key not in {"GITHUB_EVENT_PATH", "GITHUB_HEAD_REF"}}
    return subprocess.run(
        [sys.executable, "-m", "scripts.guard_stable_release", "--root", str(repo_root), *args],
        cwd=project_root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


@pytest.mark.parametrize("stale_lock", [False, True])
def test_stable_guard_compares_fork_release_with_upstream_package_name(tmp_path: Path, stale_lock: bool) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    base = init_repo_with_beta_commit(repo)
    rename_distribution(repo)
    update_project_versions(repo, "1.20.0")
    if stale_lock:
        path = repo / "uv.lock"
        path.write_text(path.read_text(encoding="utf-8").replace('"1.20.0"', '"1.20.0-beta.3"'), encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "chore: promote fork release")
    sha = git(repo, "rev-parse", "HEAD")
    branch = "release-please--branches--main"
    event = event_file(tmp_path, head_ref=branch, head_sha=sha, body="")

    result = run_stable_guard(
        Path(__file__).resolve().parents[2],
        repo,
        "--base-ref",
        base,
        "--head-ref",
        branch,
        "--event-path",
        str(event),
    )

    if stale_lock:
        assert result.returncode == 1
        assert "Stable release-managed version files must agree" in result.stderr
        assert "uv.lock='1.20.0-beta.3'" in result.stderr
    else:
        assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("branch_source", ["repository", "pull_request"])
@pytest.mark.parametrize("head_branch", ["codexLB-up", "main"])
def test_stable_guard_uses_fork_release_target(tmp_path: Path, branch_source: str, head_branch: str) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    base = init_repo_with_beta_commit(repo)
    update_project_versions(repo, "1.20.0")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "chore: promote fork release")
    sha = git(repo, "rev-parse", "HEAD")
    branch = f"release-please--branches--{head_branch}"
    event = event_file(tmp_path, head_ref=branch, head_sha=sha, body="")
    payload = json.loads(event.read_text(encoding="utf-8"))
    if branch_source == "repository":
        payload["repository"]["default_branch"] = "codexLB-up"
    else:
        payload["repository"]["default_branch"] = "main"
        payload["pull_request"]["base"]["ref"] = "codexLB-up"
    event.write_text(json.dumps(payload), encoding="utf-8")
    git(repo, "update-ref", "refs/remotes/origin/codexLB-up", base)
    git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/codexLB-up")

    result = run_stable_guard(
        Path(__file__).resolve().parents[2],
        repo,
        "--head-ref",
        branch,
        "--event-path",
        str(event),
    )

    if head_branch == "codexLB-up":
        assert result.returncode == 0, result.stderr
        assert "Stable release guard passed for 1.20.0" in result.stdout
    else:
        assert result.returncode == 1
        assert "Expected head branch: release-please--branches--codexLB-up" in result.stderr


def test_stable_guard_rejects_release_please_pr_missing_uv_lock_update(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo_with_beta_commit(repo, version="1.20.0-beta.3")
    base = git(repo, "rev-parse", "HEAD")

    update_project_versions(repo, "1.20.0")
    (repo / "uv.lock").write_text(
        '[[package]]\nname = "codex-lb"\nversion = "1.20.0-beta.3"\nsource = { editable = "." }\n',
        encoding="utf-8",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-m", "chore(main): release 1.20.0")
    sha = git(repo, "rev-parse", "HEAD")
    event = event_file(tmp_path, head_ref="release-please--branches--main", head_sha=sha, body="")

    result = run_stable_guard(
        Path(__file__).resolve().parents[2],
        repo,
        "--base-ref",
        base,
        "--head-ref",
        "release-please--branches--main",
        "--event-path",
        str(event),
    )

    assert result.returncode == 1
    assert "Stable release-managed version files must agree" in result.stderr
    assert "uv.lock='1.20.0-beta.3'" in result.stderr
    assert "pyproject.toml='1.20.0'" in result.stderr


def test_stable_guard_accepts_consistent_release_please_stable_pr(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo_with_beta_commit(repo, version="1.20.0-beta.3")
    base = git(repo, "rev-parse", "HEAD")

    update_project_versions(repo, "1.20.0")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "chore(main): release 1.20.0")
    sha = git(repo, "rev-parse", "HEAD")
    event = event_file(tmp_path, head_ref="release-please--branches--main", head_sha=sha, body="")

    result = run_stable_guard(
        Path(__file__).resolve().parents[2],
        repo,
        "--base-ref",
        base,
        "--head-ref",
        "release-please--branches--main",
        "--event-path",
        str(event),
    )

    assert result.returncode == 0, result.stderr
    assert "Stable release guard passed for 1.20.0" in result.stdout


def test_stable_guard_rejects_stable_promotion_from_non_release_please_branch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo_with_beta_commit(repo, version="1.20.0-beta.3")
    base = git(repo, "rev-parse", "HEAD")

    update_project_versions(repo, "1.20.0")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "chore(main): release 1.20.0")
    sha = git(repo, "rev-parse", "HEAD")
    event = event_file(tmp_path, head_ref="fix/manual-stable-promotion", head_sha=sha, body="")

    result = run_stable_guard(
        Path(__file__).resolve().parents[2],
        repo,
        "--base-ref",
        base,
        "--head-ref",
        "fix/manual-stable-promotion",
        "--event-path",
        str(event),
    )

    assert result.returncode == 1
    assert "Stable release promotions must come from the release-please branch" in result.stderr
    assert "Actual head branch: fix/manual-stable-promotion" in result.stderr


def test_stable_guard_accepts_merge_queue_without_head_ref_after_pr_gate(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo_with_beta_commit(repo, version="1.20.0-beta.3")
    base = git(repo, "rev-parse", "HEAD")

    update_project_versions(repo, "1.20.0")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "chore(main): release 1.20.0")

    result = run_stable_guard(
        Path(__file__).resolve().parents[2],
        repo,
        "--base-ref",
        base,
        "--head-ref",
        "",
    )

    assert result.returncode == 0, result.stderr
    assert "No PR head branch available" in result.stdout
    assert "Stable release guard passed for 1.20.0" in result.stdout


def test_stable_guard_allows_non_promotion_metadata_repair_branch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo_with_beta_commit(repo, version="1.20.0-beta.3")
    update_project_versions(repo, "1.20.0")
    (repo / "uv.lock").write_text(
        '[[package]]\nname = "codex-lb"\nversion = "1.20.0-beta.3"\nsource = { editable = "." }\n',
        encoding="utf-8",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-m", "chore(main): release 1.20.0 with stale lock")
    base = git(repo, "rev-parse", "HEAD")

    (repo / "uv.lock").write_text(
        '[[package]]\nname = "codex-lb"\nversion = "1.20.0"\nsource = { editable = "." }\n',
        encoding="utf-8",
    )
    git(repo, "add", "uv.lock")
    git(repo, "commit", "-m", "fix(release): restore uv lock version")

    result = run_stable_guard(
        Path(__file__).resolve().parents[2],
        repo,
        "--base-ref",
        base,
        "--head-ref",
        "fix/stable-release-artifact-gate",
    )

    assert result.returncode == 0, result.stderr
    assert "No stable release promotion detected" in result.stdout
