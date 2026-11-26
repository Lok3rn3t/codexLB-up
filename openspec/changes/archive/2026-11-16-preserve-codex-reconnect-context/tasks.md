## Implementation

- [x] Verify continuation behavior in current stable Codex source.
- [x] Guard anchorless WebSocket replay with full-context evidence.
- [x] Preserve same-owner agent-message full resends across HTTP reconnects.
- [x] Notify completed idle native WebSocket context loss safely.
- [x] Synchronize Responses compatibility requirements.

## Verification

- [x] Run affected unit and route regressions, including negative ownership and race cases.
- [x] Run Ruff and targeted type checks.
- [x] Validate the scoped OpenSpec change and canonical specs strictly.
- [x] Record actual results before archive.
