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

This review records candidates only. No upstream PR was merged or cherry-picked as part of the review.
