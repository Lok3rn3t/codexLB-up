from __future__ import annotations

import os
import shutil
import socket
import struct
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
_ROOT = Path(__file__).resolve().parents[2]


def _bash() -> str:
    if os.name == "nt":
        git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
        if git_bash.is_file():
            return str(git_bash)
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("Bash is required to exercise the release smoke script")
    return bash


def _run_smoke(
    tmp_path: Path, *, port: int = 1, fail_pull: bool = False, fail_readiness: bool = False
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    mocks = tmp_path / "smoke-mocks.sh"
    calls = tmp_path / "calls.txt"
    mocks.write_text(
        """docker() {
  printf '%s\\n' "$*" >> "$SMOKE_CALLS"
  case "$1" in
    pull) [ "$SMOKE_FAIL_PULL" != true ] ;;
    run) printf 'smoke-container\\n' ;;
    port) printf '127.0.0.1:%s\\n' "$SMOKE_PORT" ;;
    exec) cat >/dev/null ;;
    logs) printf 'container startup diagnostics\\n' ;;
    rm) return 0 ;;
    *) return 99 ;;
  esac
}
sleep() { :; }
if [ "$SMOKE_FAIL_READINESS" = true ]; then
  curl() { return 56; }
fi
""",
        encoding="utf-8",
        newline="\n",
    )
    env = os.environ.copy()
    env.update(
        BASH_ENV=mocks.as_posix(),
        SMOKE_CALLS=calls.as_posix(),
        SMOKE_PORT=str(port),
        SMOKE_FAIL_PULL=str(fail_pull).lower(),
        SMOKE_FAIL_READINESS=str(fail_readiness).lower(),
        NO_PROXY="127.0.0.1,localhost",
    )
    result = subprocess.run(
        [
            _bash(),
            str(_ROOT / "scripts/check-release-container.sh"),
            "example/image@sha256:test",
            "1.25.0",
            "linux/amd64",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    return result, calls.read_text(encoding="utf-8").splitlines()


def test_readiness_connection_reset_is_retried_before_container_validation(tmp_path: Path) -> None:
    attempts: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            attempts.append(self.path)
            if len(attempts) == 1:
                linger = struct.pack("HH" if os.name == "nt" else "ii", 1, 0)
                self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, linger)
                self.connection.close()
                self.close_connection = True
                return
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, format: str, *args: object) -> None:
            pass

    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            result, calls = _run_smoke(tmp_path, port=server.server_port)
        finally:
            server.shutdown()
            worker.join(timeout=5)

    assert result.returncode == 0, result.stdout + result.stderr
    assert attempts == ["/health/ready", "/health/ready"]
    assert "curl: (56)" in result.stderr
    assert any(call.startswith("exec -i smoke-container") for call in calls)
    assert calls[-1] == "rm -f smoke-container"
    assert "logs smoke-container" not in calls


def test_failed_readiness_preserves_failure_and_cleans_up_container(tmp_path: Path) -> None:
    result, calls = _run_smoke(tmp_path, fail_readiness=True)

    assert result.returncode == 56
    assert "container startup diagnostics" in result.stdout
    assert calls[-2:] == ["logs smoke-container", "rm -f smoke-container"]
    assert not any(call.startswith("exec ") for call in calls)


def test_failed_image_pull_stops_after_five_attempts(tmp_path: Path) -> None:
    result, calls = _run_smoke(tmp_path, fail_pull=True)

    assert result.returncode == 1
    assert len(calls) == 5
    assert all(call.startswith("pull --platform linux/amd64 ") for call in calls)
    assert "after 5 attempts" in result.stderr
