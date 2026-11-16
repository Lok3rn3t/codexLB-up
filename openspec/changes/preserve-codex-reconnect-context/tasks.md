## Implementation

- [ ] Verify continuation behavior in current stable Codex source.
- [ ] Guard anchorless WebSocket replay with full-context evidence.
- [ ] Preserve same-owner agent-message full resends across HTTP reconnects.
- [ ] Notify completed idle native WebSocket context loss safely.
- [ ] Synchronize Responses compatibility requirements.

## Verification

- [ ] Run affected unit and route regressions, including negative ownership and race cases.
- [ ] Run Ruff and targeted type checks.
- [ ] Validate the scoped OpenSpec change and canonical specs strictly.
- [ ] Record actual results before archive.
