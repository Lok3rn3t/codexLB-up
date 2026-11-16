## Why

A slow Python consumer can overflow the native WebSocket adapter's 64-message queue, losing accepted response events and closing an otherwise healthy upstream stream. The upstream receive-credit fix must be adapted without exposing arbitrary native errors or peer close reasons through diagnostics.

## What Changes

- Backport the flow-control and cancellation handling from upstream PR #2711 at `a39d2ff98490bd3f88b1565ce253dc1d7bb073f9`.
- Negotiate a one-message receive-credit window and preserve accepted messages on helper exit.
- Keep peer operations, send acknowledgements and local shutdown available while reads pause.
- Report allowlisted phases, numeric close codes and payload counters; exclude arbitrary error and close-reason text.

## Impact

Updates the bundled native helper protocol and Python WebSocket adapter together. Addresses the queue-overflow mechanism reported in upstream #2594; it does not establish the cause of historical production disconnects.
