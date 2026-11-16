# Why

The fork contains the initial protections from upstream PR #2731, but marks an
injected WebSocket anchor as complete context even when it was recorded from a
client-anchored delta. A subsequent resend can therefore be replayed without
the earlier conversation. Reading the mutable continuity state after admission
awaits would also associate coverage from a different completion with the
selected anchor.

# What Changes

- Snapshot the selected anchor's context coverage before asynchronous admission.
- Carry that coverage into the completed request's continuity record.
- Verify the native WebSocket route refuses a later anchorless replay of a
  restated delta, and cover continuity mutation during admission.

# Impact

Responses WebSocket preparation and regression tests only. No deployment,
configuration, account selection, or upstream transport changes.
