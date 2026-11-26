#!/usr/bin/env bash
set -euo pipefail

target_image="${1:?target image reference is required}"
target_version="${2:?target version is required}"
platform="${3:-linux/amd64}"
source_image="ghcr.io/soju06/codex-lb@sha256:093344377e618acab906a36a4ed23d23e4b2f0fd2882e38df545b170d4278832"
fixture="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/upstream_upgrade_fixture.py"
volume=""
source_container=""
target_container=""

cleanup() {
  status=$?
  for container in "${source_container}" "${target_container}"; do
    if [ -n "${container}" ]; then
      if [ "${status}" -ne 0 ]; then
        docker logs "${container}" || true
      fi
      docker rm -f "${container}" >/dev/null || true
    fi
  done
  if [ -n "${volume}" ]; then
    docker volume rm "${volume}" >/dev/null || true
  fi
  exit "${status}"
}
trap cleanup EXIT

wait_ready() {
  docker exec -i "$1" python - <<'PY'
import time
import urllib.error
import urllib.request

deadline = time.monotonic() + 180
while True:
    try:
        with urllib.request.urlopen("http://127.0.0.1:2455/health/ready", timeout=5) as response:
            assert response.status == 200
        break
    except (OSError, urllib.error.URLError):
        if time.monotonic() >= deadline:
            raise
        time.sleep(2)
PY
}

docker pull --platform "${platform}" "${source_image}"
# CI supplies a loaded local image; releases supply an immutable platform manifest.
if [[ "${target_image}" == *@sha256:* ]]; then
  docker pull --platform "${platform}" "${target_image}"
fi
docker image inspect "${target_image}" >/dev/null
volume="$(docker volume create --label codex-lb.test=upstream-beta9-upgrade)"
run_options=(--platform "${platform}" --network none
  --mount "type=volume,source=${volume},target=/var/lib/codex-lb"
  -e CODEX_LB_TELEMETRY_ENABLED=false
  -e CODEX_LB_AUTH_GUARDIAN_ENABLED=false
  -e CODEX_LB_RATE_LIMIT_RESET_CREDITS_REFRESH_ENABLED=false
  -e CODEX_LB_AUTOMATIONS_SCHEDULER_ENABLED=false)

source_container="$(docker run -d "${run_options[@]}" "${source_image}")"
wait_ready "${source_container}"
docker stop --time 30 "${source_container}" >/dev/null
# Seed using the original image's ORM after its normal startup has created the
# real beta.9 schema. Neither image can contact external providers.
docker run --rm -i "${run_options[@]}" --entrypoint python "${source_image}" - seed < "${fixture}"
docker run --rm -i "${run_options[@]}" --entrypoint python "${source_image}" - verify 1.25.0-beta.9 < "${fixture}"

target_container="$(docker run -d "${run_options[@]}" "${target_image}")"
wait_ready "${target_container}"
docker exec -i "${target_container}" python - verify "${target_version}" < "${fixture}"
docker restart --time 30 "${target_container}" >/dev/null
wait_ready "${target_container}"
docker exec -i "${target_container}" python - verify "${target_version}" < "${fixture}"
printf 'Original beta.9 container upgrade passed: %s (%s)\n' "${target_image}" "${platform}"
