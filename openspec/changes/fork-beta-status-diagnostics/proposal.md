## Why

The fork dashboard still links to the upstream repository. A native upstream
WebSocket receive failure also loses its classified failure phase in the
operator log, leaving repeated stream interruptions impossible to distinguish
without rebuilding with ad hoc instrumentation.

## What Changes

- Point the fixed status-bar repository link to the fork.
- Log the native WebSocket receive failure phase and safe error code, without
  logging credentials or frame contents.

## Impact

- Affected specs: `frontend-architecture`, `outbound-http-clients`.
- Affected code: status bar and native WebSocket adapter.
- No retry, account-health, or continuity policy changes.
