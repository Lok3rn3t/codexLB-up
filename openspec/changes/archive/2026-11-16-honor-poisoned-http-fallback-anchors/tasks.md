## 1. Reproduce and implement

- [x] 1.1 Compare complete-history retry cases with the baseline and reproduce unsafe incomplete-history dispatch.
- [x] 1.2 Apply fallback-key fences during durable-anchor planning and delta refusal.
- [x] 1.3 Reconcile with existing subagent context, explicit-anchor, and transient-backoff recovery.

## 2. Verify

- [x] 2.1 Pass all 48 split-record route cases and affected quarantine routes.
- [x] 2.2 Pass related poison, quarantine, tombstone, and recovery unit tests.
- [x] 2.3 Pass lint, focused type checks, strict OpenSpec validation, and sync/archive.
