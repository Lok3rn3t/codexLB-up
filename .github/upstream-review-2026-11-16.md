# Upstream PR and issue review — 2026-11-16

Snapshot of [Soju06/codex-lb](https://github.com/Soju06/codex-lb) on 2026-11-16: **178 open pull requests** and **126 open issues**. This is a triage snapshot, not a claim that every proposal is ready to merge or every issue is reproduced in this fork. Counts and statuses will change.

## Already represented in this fork

The fork's [`d3865a73`](https://github.com/Lok3rn3t/codexLB-up/commit/d3865a73bead839a23a533cbd9df6708842b6699) addresses trusted socket-peer authorization, encrypted Responses includes, non-strict Chat tool defaults, Business Pro Lite and Pro Max recognition, and the bounded expired API-key limit sweep. Its upstream submission is [PR #2729](https://github.com/Soju06/codex-lb/pull/2729). Relevant upstream reports include [#2684](https://github.com/Soju06/codex-lb/issues/2684), [#2691](https://github.com/Soju06/codex-lb/issues/2691), [#2652](https://github.com/Soju06/codex-lb/issues/2652), [#2637](https://github.com/Soju06/codex-lb/issues/2637), and [#2511](https://github.com/Soju06/codex-lb/issues/2511). Open upstream status does not imply the fork fix is absent.

## Highest-priority areas to verify next

| Area | Upstream evidence | Why it matters |
| --- | --- | --- |
| WebSocket replay and lost context | [issue #2730](https://github.com/Soju06/codex-lb/issues/2730), [PR #2731](https://github.com/Soju06/codex-lb/pull/2731), [issue #2574](https://github.com/Soju06/codex-lb/issues/2574) | A replayed delta without its anchor can corrupt a conversation. Review the PR and run product-path regressions before adoption. |
| Memory pressure from client payloads | [issue #2688](https://github.com/Soju06/codex-lb/issues/2688), [PR #2732](https://github.com/Soju06/codex-lb/pull/2732) | Bounded image handling may protect the proxy from oversized requests. Check limits and compatibility. |
| Native WebSocket burst handling | [issue #2594](https://github.com/Soju06/codex-lb/issues/2594), [PR #2709](https://github.com/Soju06/codex-lb/pull/2709), [PR #2711](https://github.com/Soju06/codex-lb/pull/2711) | The two PRs overlap; compare their behavior and tests before choosing either. |
| HTTP bridge and account ownership | [issue #2655](https://github.com/Soju06/codex-lb/issues/2655), [issue #2470](https://github.com/Soju06/codex-lb/issues/2470), [PR #2712](https://github.com/Soju06/codex-lb/pull/2712), [PR #2700](https://github.com/Soju06/codex-lb/pull/2700) | Forwarding, retry, and lease settlement need joint regression checks to avoid cross-account routing or stuck capacity. |
| Reset-credit accuracy | [issue #2693](https://github.com/Soju06/codex-lb/issues/2693), [PR #2702](https://github.com/Soju06/codex-lb/pull/2702), [PR #2710](https://github.com/Soju06/codex-lb/pull/2710) | Dashboard and routing should agree on the live credit state. |

## Other active work

- [PR #2724](https://github.com/Soju06/codex-lb/pull/2724) addresses multi-agent collaboration tools; [issue #2499](https://github.com/Soju06/codex-lb/issues/2499) describes the client failure.
- [PR #2725](https://github.com/Soju06/codex-lb/pull/2725) and [issue #2514](https://github.com/Soju06/codex-lb/issues/2514) concern redeeming multiple reset credits.
- [PR #2707](https://github.com/Soju06/codex-lb/pull/2707) and [issue #2703](https://github.com/Soju06/codex-lb/issues/2703) concern Daybreak routing.
- [PR #2686](https://github.com/Soju06/codex-lb/pull/2686) and [issue #2556](https://github.com/Soju06/codex-lb/issues/2556) concern credit-based API-key limits.
- Dependency PRs should be updated as a tested group rather than merged solely because their versions are newer.

The initial review recorded candidates only. The subsequent 1.25.0 release work
compared the continuation protocol with `openai/codex` `rust-v0.169.0` and adapted
the fixes and regression tests from PRs #2731, #2581 and #2636. Their exact source
commits and ownership constraints are recorded in the OpenSpec change
`preserve-codex-reconnect-context`. These changes preserve the client's canonical
recovery signal; they do not promise that a genuinely lost response anchor will
never produce `previous_response_not_found`.

The release also adapts PR #2627 (related to #2486) to allow an otherwise
eligible proven conversation owner through transient backoff without bypassing
quota, account status, security, file ownership, or scope constraints. Its
regression reproduced the owner-unavailable failure before the fix; 455 focused
tests passed afterward. Evidence is archived in
`openspec/changes/archive/2026-11-16-recover-owned-session-backoff/`.

PR #2628 adds scoped fallback-anchor fencing and incomplete-history refusal.
All 48 complete-history split-record cases already passed on this fork's
baseline; the newly reproduced failure was an incomplete resend dispatched
without required context. The updated route selection passes 49 cases and the
related unit selection passes 98. Evidence is recorded in
`honor-poisoned-http-fallback-anchors`. This is context-preservation coverage,
not proof that all reported production retries have been diagnosed or removed.

## Follow-up: replacement 1.26.0-beta.1 candidate

The owner requested a replacement of the withdrawn beta.1 publication and
explicitly approved replacing its GitHub, Docker and Helm tags without a new
PyPI upload. The original tag pointed to `3a6b1187d03010bae447a9c654a2c8a066a6469c`;
the retained image index was
`sha256:f4495212a108cb527b2b7f9a7847de5982fa48e0b1b4565981113d535a8cbc6d`.

Selected after code and issue review:

- PR #2711 at `a39d2ff98490bd3f88b1565ce253dc1d7bb073f9`: negotiated
  one-frame receive credit to prevent native WebSocket burst queue loss. The
  fork adaptation retains only allowlisted phases, close codes and counters;
  arbitrary exception text and close reasons are excluded from diagnostics.
- Remaining PR #2731 at `ace4d91eb8523b21fd253b0ef91821b8e9991f44`: inherit
  context coverage from the selected injected anchor, additionally snapshotting
  it before admission awaits to avoid racing another completion.
- PR #2569 at `778e10f4ab7111c7ab5539b448df2763fabc1987`, related to issue
  #2563: preserve developer messages in Responses input for continuation.

PR #2709 is not layered over #2711: they offer overlapping queue fixes.
Broader changes such as #2732 payload-memory limits and #2665 dynamic reasoning
policy were deferred to avoid mixing unrelated behavior into transport recovery.
Each selected fix has its own OpenSpec provenance and regression evidence.
These are reproduced code defects, not proof that every observed production
1011 or missing-anchor error shares the same cause. Production was not changed.
