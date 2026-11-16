#!/usr/bin/env bash
set -euo pipefail

image_ref="${1:?image reference is required}"
expected_version="${2:?expected version is required}"
platform="${3:?platform is required}"
container_id=""

cleanup() {
  status=$?
  if [ -n "${container_id}" ]; then
    if [ "${status}" -ne 0 ]; then
      docker logs "${container_id}" || true
    fi
    docker rm -f "${container_id}" >/dev/null || true
  fi
  exit "${status}"
}
trap cleanup EXIT

docker pull --platform "${platform}" "${image_ref}"
container_id="$(docker run -d --platform "${platform}" -p 127.0.0.1::2455 "${image_ref}")"
address="$(docker port "${container_id}" 2455/tcp)"

curl --fail --silent --show-error --retry 60 --retry-delay 2 \
  --retry-connrefused --max-time 5 "http://${address}/health/ready"

docker exec -i "${container_id}" python - "${expected_version}" <<'PY'
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import app

assert app.__version__ == sys.argv[1], (app.__version__, sys.argv[1])
hello = {"type": "client_hello", "min_protocol_version": 1, "max_protocol_version": 1}
native = subprocess.run(
    ["codex-lb-native-egress"], input=json.dumps(hello) + "\n",
    text=True, capture_output=True, check=True, timeout=30,
)
reply = json.loads(native.stdout.splitlines()[0])
assert reply["type"] == "server_hello", reply
assert "http" in reply["capabilities"] and "websocket" in reply["capabilities"], reply

root = "http://127.0.0.1:2455"
with urllib.request.urlopen(root + "/health", timeout=10) as response:
    assert json.load(response)["status"] == "ok"
with urllib.request.urlopen(root + "/", timeout=10) as response:
    assert response.headers.get_content_type() == "text/html"
    index = response.read().decode()
assets = re.findall(r'(?:src|href)="([^\"]+\.(?:js|css))"', index)
assert any(path.endswith(".js") for path in assets)
assert any(path.endswith(".css") for path in assets)
for asset in assets:
    with urllib.request.urlopen(root + asset, timeout=10) as response:
        assert response.status == 200 and response.read()
assert Path("/var/lib/codex-lb/store.db").exists()
print(f"Container smoke passed: {app.__version__}; native IPC, migrations, health and {len(assets)} assets")
PY

printf 'Release container verified: %s (%s)\n' "${image_ref}" "${platform}"
