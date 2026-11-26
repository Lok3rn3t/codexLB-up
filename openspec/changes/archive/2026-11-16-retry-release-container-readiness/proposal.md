# Retry transient release-container readiness failures

## Why

The release image was downloaded successfully, but the first readiness probe
failed with curl exit 56 while the container was starting. Curl's default retry
policy does not cover this connection reset, so a healthy image could fail before
startup completed.

## What Changes

- Retry connection resets and other transient readiness-probe errors within a
  bounded startup window.
- Preserve failure status, container diagnostics, and cleanup when readiness
  never succeeds.
- Cover startup recovery and failed smoke checks without requiring Docker.

## Impact

- Affected specification: release-management.
- Affected implementation: scripts/check-release-container.sh.
- No application or provider-request behavior changes.
