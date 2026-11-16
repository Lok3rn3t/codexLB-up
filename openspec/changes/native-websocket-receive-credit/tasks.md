## Implementation

- [x] Add negotiated receive credits, bounded cancellation deferral and ambiguous-dispatch cleanup.
- [x] Add safe structured diagnostics and account-neutral local-backpressure classification.
- [x] Add native and product-route regressions, including burst delivery and privacy.
- [x] Run focused Python tests, Rust tests/clippy/fmt and strict change validation locally.
- [x] Synchronize normative specification and context.
- [ ] Complete current-head Linux CI and archive the verified change.

## Local verification

- Built native worker: 13 flow-control tests passed, including a 100-event burst, concurrent receives, sibling progress, paused close/cancel, cancellation, timed-out/ambiguous credit dispatch and cancellation during abort cleanup.
- Rust workspace: 29 tests passed; clippy and fmt passed.
- WebSocket product-route/client suites: 236 passed; four pre-existing environment tests delete the proxy value on case-insensitive Windows. Linux CI must verify these fixtures.
- Five new diagnostics regressions failed before the implementation and passed afterward. The accepted-frame-on-helper-exit regression also fails with the original `3a6b118` method injected in memory and passes with the new method.
- No production server changes or production validation were performed.

- The abort-cleanup cancellation regression fails with the prior `5d98cf6` receive method injected in memory (`cancel_dispatched=False`) and passes after shielding the bounded cleanup. The cancel command is dispatched before the original cancellation propagates, and closure is verified at the real local upstream.
