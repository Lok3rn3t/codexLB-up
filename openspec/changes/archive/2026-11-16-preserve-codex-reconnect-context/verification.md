# Verification — 2026-11-16

The implementation is included in commit `3d1d6398db979c0db220bc89ec1584a2927fc5a4`. The examined Codex client is `rust-v0.169.0` (`d32063f96c2dff1dc96af839b3952abb6acfeda4`); source and upstream implementation attribution are in `context.md`.

## Regression evidence

Before the implementation, the unknown-anchor delta unit regression failed because the replay classifier returned `True`. The fresh HTTP agent-message route regression failed because the replacement upstream still received a stale `previous_response_id`.

After implementation:

- Focused unknown-anchor, restated-delta, same-owner agent-message, idle-loss and race regressions: **35 passed**.
- The prewarm-close route regression from upstream #2575: **2 passed**, covering `/v1/responses` and `/backend-api/codex/responses` without adopting its narrower runtime optimization.
- The final local continuation regression selection: **243 passed**. The unrelated pre-existing repeated-capacity-marker test was corrected to probe one startup event rather than waiting for an intentionally blocked second event.
- Ruff checks and formatting checks on the eleven modified proxy/test files passed; targeted `ty` checks on the five modified runtime files passed.
- Strict OpenSpec validation passed the scoped change and all **67 canonical specs**.

## GitHub evidence

[CI run 43813251422](https://github.com/Lok3rn3t/codexLB-up/actions/runs/43813251422) ran against the exact commit above:

- [Integration bridge](https://github.com/Lok3rn3t/codexLB-up/actions/runs/43813251422/job/133119504176): **378 passed**. This includes the HTTP bridge and direct WebSocket product paths.
- [Integration core 1](https://github.com/Lok3rn3t/codexLB-up/actions/runs/43813251422/job/133119504315): **932 passed, 346 skipped**.
- OpenSpec validation, Ruff and type checking passed.
- The unit job reported **10,676 passed, 7 skipped, 1 xfailed**, with 11 failures in dependency, packaging and reference checks outside this continuation change. The whole CI run was not green: those failures and separate deployment/database jobs remained under repair when this scoped change was archived.

This is validation of proxy recovery and ownership contracts with controlled upstream fixtures. It does not establish the cause of a particular production error or claim that every `previous_response_not_found` can be recovered transparently. Native Codex continues to receive the canonical sanitized recovery signal when the proxy cannot prove a safe full-context replay.
