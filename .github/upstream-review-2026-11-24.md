# CodexLB-up 1.27.0 — conversation recovery, load balancing, and Ultrafast

The stable 1.27.0 release includes conversation recovery, Ultrafast accounting, and dashboard token reporting from the 1.26.0 prereleases. The changes after beta.4 update the Python, Docker, and Helm installation commands. This review records the source examined on November 24, 2026. The build section identifies the beta.4 commit and image digest. The command below pulls the stable image. [Stable 1.27.0 release](https://github.com/Lok3rn3t/codexLB-up/releases/tag/v1.27.0) · [Beta.4 release](https://github.com/Lok3rn3t/codexLB-up/releases/tag/v1.26.0-beta.4)

```bash
docker pull ghcr.io/lok3rn3t/codexlb-up:1.27.0
```

November 24, 2026. This release includes the fixes from PR #5. The index lists all 147 open pull requests and 128 open issues in Soju06/codex-lb on the review date. The analysis focuses on WebSocket and SSE behavior, account selection, quotas, and models. [PR #5](https://github.com/Lok3rn3t/codexLB-up/pull/5) · [Beta.4 release](https://github.com/Lok3rn3t/codexLB-up/releases/tag/v1.26.0-beta.4)

## What changed in beta.4

| Scenario | Proxy behavior |
| --- | --- |
| The client sends the full history and a new turn on a new WebSocket | The proxy checks the original input, the number of output items, and the SHA-256 fingerprint of the last completed turn's actual output. If the history matches and contains no account-bound objects, the proxy forwards it without inserting the old `previous_response_id`. Fingerprints and item counts are sufficient for this check. [WebSocket fix](https://github.com/Lok3rn3t/codexLB-up/commit/57ef379e) |
| Tools finish in a different order | The proxy matches each result to its call by type and `call_id`. An unmatched call, a duplicate, or a mismatch makes the history ineligible for replay on a fresh connection. Replayed assistant messages retain `annotations` and `logprobs`, including empty arrays. [Implementation and regression tests](https://github.com/Lok3rn3t/codexLB-up/commit/57ef379e) |
| The request contains only new messages, an explicit parent ID, or a file reference | Automatic replay on a new socket requires a verifiable full history and must respect account ownership. If the provider has lost the parent response, the client needs its conversation history to recover. [Beta.4 replay rules](https://github.com/Lok3rn3t/codexLB-up/blob/1539da2892c9c2472090b9dd6609cdedb55d6620/app/modules/proxy/_service/websocket/helpers.py#L738-L867) |
| An SSE source raises `TimeoutError` during a read | The client receives the error and the stream closes. The proxy sends heartbeats at the configured interval while a read is still pending. [SSE fix](https://github.com/Lok3rn3t/codexLB-up/commit/fc10f4d5) |
| The provider processes the response with Ultrafast | The proxy calculates the final charge using the actual service tier when reported, together with the model, request time, context length, and cached input. [Accounting fix](https://github.com/Lok3rn3t/codexLB-up/commit/2525877d) |

OpenAI caches previous responses on a connection for its lifetime, which can be up to 60 minutes. After reconnecting, a client can reuse a stored response with a valid ID. On `previous_response_not_found`, the client can send its full context without the ID. After `/responses/compact`, the client can use the returned compacted window as the base and append new input. Removing the ID from a delta-only request would discard the earlier conversation. [OpenAI Responses WebSocket recovery](https://developers.openai.com/api/docs/guides/websocket-mode)

## How OmniRoute selects a ChatGPT or Codex account

1. **Session affinity.** OmniRoute prefers the session's pinned account while the account is available, permitted by the key, and eligible under the requested quota. A change in account ranking alone leaves the pin in place. This helps preserve conversation ownership. Requests that depend on a cached previous response also depend on the specific connection. [Account selection](https://github.com/cheaper-inference/OmniRoute/blob/474f533172b8f7cc5cebae51810237a7babed876/src/sse/services/sessionAffinityPin.ts#L508-L609)
2. **WebSocket slots.** The route checks eligible accounts and their quotas, then tries to acquire a slot immediately. It excludes busy accounts from the current search and makes up to eight attempts. When no concurrency limit is configured, the default is one slot per account. Each OmniRoute process tracks its own allocations and releases, so separate replicas have independent counters. [WebSocket route](https://github.com/cheaper-inference/OmniRoute/blob/474f533172b8f7cc5cebae51810237a7babed876/src/app/api/internal/codex-responses-ws/route.ts#L453-L497) · [Slot implementation](https://github.com/cheaper-inference/OmniRoute/blob/474f533172b8f7cc5cebae51810237a7babed876/src/sse/services/codexWsLease.ts#L7-L39)
3. **Quotas and temporary capacity limits.** OmniRoute tracks Codex and Spark quotas separately for each account. Each has its own five-hour and seven-day measurements and reset times. The observation time determines which cached or header-derived measurement is newer. When an HTTP 429 response identifies temporary model congestion, other account capabilities can remain available. [Quota windows](https://github.com/cheaper-inference/OmniRoute/blob/474f533172b8f7cc5cebae51810237a7babed876/open-sse/services/codexAccount/index.ts#L39-L125) · [HTTP 429 classification](https://github.com/cheaper-inference/OmniRoute/blob/474f533172b8f7cc5cebae51810237a7babed876/open-sse/services/codexAccount/capacity429.ts)
4. **Conversation recovery.** With full request logging enabled, OmniRoute can reconstruct the conversation from the input actually sent, the response, and the new messages. Records are scoped to the API key, and recovery checks for completeness and truncation. Beta.4 applies the same principle of verifying actual output. The client supplies the history, and CodexLB-up compares it with the stored fingerprint and matches tool calls to results. [OmniRoute continuation store](https://github.com/cheaper-inference/OmniRoute/blob/474f533172b8f7cc5cebae51810237a7babed876/src/lib/db/responsesContinuationStore.ts) · [Tool history handling](https://github.com/cheaper-inference/OmniRoute/blob/474f533172b8f7cc5cebae51810237a7babed876/open-sse/translator/helpers/responsesToolHistory.ts) · [CodexLB-up implementation](https://github.com/Lok3rn3t/codexLB-up/commit/57ef379e)
5. **Read timeouts.** OmniRoute limits the wait for the first chunk and for each subsequent chunk. A long response can continue while data keeps arriving. Beta.4 addresses a related SSE failure by propagating a timeout already raised by the source. [OmniRoute body reads](https://github.com/cheaper-inference/OmniRoute/blob/474f533172b8f7cc5cebae51810237a7babed876/open-sse/executors/codex/bodyTimeout.ts) · [Beta.4 fix](https://github.com/Lok3rn3t/codexLB-up/commit/fc10f4d5) · [Soju06 #2681](https://github.com/Soju06/codex-lb/pull/2681)

## Relevant changes in Frozen811

The comparison uses Frozen811's `main` at commit `9d223218`. Since their common ancestor, Soju06 had 50 commits unique to its history and Frozen811 had 124, including merges. Frozen811's `community-hardened-release` branch was 117 commits behind its `main`. [Reviewed main branch](https://github.com/Frozen811/codex-lb/tree/9d22321892602f2a762e166894bc63a7a74aa41b) · [Community release branch](https://github.com/Frozen811/codex-lb/tree/76d32e33244f6671bf2538235e698910223eed74)

| Change | Relevance to CodexLB-up |
| --- | --- |
| Verify tool history and account ownership | On a new direct WebSocket, beta.4 checks both the input prefix and the entire previous output. The original Frozen811 commit also covers the HTTP bridge and authentication. [Frozen811 change](https://github.com/Frozen811/codex-lb/commit/71c5332ca24666455aa6836f0bd05f9e8b304cc2) · [Beta.4 implementation](https://github.com/Lok3rn3t/codexLB-up/commit/57ef379e) |
| The conversation owner is outside the API key's allowed account pool | Frozen811 fails the request immediately because waiting for a slot cannot grant the key access to that account. Evaluating this change in CodexLB-up calls for a test with a restricted account pool. [Frozen811 owner check](https://github.com/Frozen811/codex-lb/commit/5fd5b8141a13bde635ba0b38b283c6c81009a4ee) |
| The client sends its next turn before the connection changes | Frozen811 retains a completed downstream read during handoff. This is a candidate for testing when the first message after a connection switch goes missing. [Frozen811 handoff fix](https://github.com/Frozen811/codex-lb/commit/3205f09fa7dbd1de0d44f17c7dff5d8e138d8604) |
| Monthly quota window for Team | Frozen811 retains the measured monthly window and its reset date. A weekly percentage alone cannot establish the exact remaining monthly credit balance. [Frozen811 quota fix](https://github.com/Frozen811/codex-lb/commit/2483ea459e24b4ff7e5e681326e944a96f47a18c) |

## Soju06 pull requests and issues related to disconnects

| Symptom | Findings from the source and issue reports |
| --- | --- |
| `Previous response was not found` after a disconnect | PR #2731 prevents a delta-only retry from silently dropping earlier history. Beta.4 also verifies a full history resent on a new WebSocket so the proxy can forward it without inserting a stale ID. [PR #2731](https://github.com/Soju06/codex-lb/pull/2731) · [Issue #2730](https://github.com/Soju06/codex-lb/issues/2730) · [Fork fix](https://github.com/Lok3rn3t/codexLB-up/commit/57ef379e) |
| `Upstream websocket receive failed / 1011` during a burst | PR #2711 regulates message delivery from Rust to Python and preserves read-failure diagnostics. This fix reached the fork before beta.4. Related work on message bursts landed in Soju06 #2709. The phase and transport error are needed to diagnose an individual closure with code 1011. [PR #2711](https://github.com/Soju06/codex-lb/pull/2711) · [Fork commit](https://github.com/Lok3rn3t/codexLB-up/commit/5d98cf60) · [PR #2709](https://github.com/Soju06/codex-lb/pull/2709) |
| An idle WebSocket closes between turns | PR #2636 sends close code 1012 to prompt the client to reconnect. Issue #2658 describes an HTTP bridge reusing a connection beyond the one-hour limit. [PR #2636](https://github.com/Soju06/codex-lb/pull/2636) · [Issue #2658](https://github.com/Soju06/codex-lb/issues/2658) · [OpenAI connection lifetime](https://developers.openai.com/api/docs/guides/websocket-mode) |
| The HTTP bridge closes before its first event | PR #2712 proposes one retry on a fresh socket if the response has yet to start, there is no buffered output, and ownership permits replay. Retrying after output begins can duplicate work or text. The proposal applies specifically to the HTTP bridge. [PR #2712](https://github.com/Soju06/codex-lb/pull/2712) |
| A request fails after tool use or an account change | PR #2666 covers complete tool history in native HTTP. PR #2617 covers completed call/result pairs at the start of the history. PR #2398 addresses replaying history on a different account after quota exhaustion. [PR #2666](https://github.com/Soju06/codex-lb/pull/2666) · [PR #2617](https://github.com/Soju06/codex-lb/pull/2617) · [PR #2398](https://github.com/Soju06/codex-lb/pull/2398) |
| The first turn or developer instructions disappear | Separate issues cover connections opened in advance and the recovery of developer-message history. [Issue #2574](https://github.com/Soju06/codex-lb/issues/2574) · [Issue #2563](https://github.com/Soju06/codex-lb/issues/2563) |
| A request with an image disconnects | PR #2732 clarifies the HTTP bridge limits for inline images. The proposed limits are 5,000,000 decoded bytes per image and 64 MiB for the final frame. Exceeding the frame limit can produce close code 1009. [PR #2732](https://github.com/Soju06/codex-lb/pull/2732) · [PR #2534](https://github.com/Soju06/codex-lb/pull/2534) |
| A desktop notification appears or a plan repeats | Issue #2740 describes unclear Desktop notifications. Issue #2737 covers repeated plans. Identifying a WebSocket close cause requires separate transport evidence. [Issue #2740](https://github.com/Soju06/codex-lb/issues/2740) · [Issue #2737](https://github.com/Soju06/codex-lb/issues/2737) |

## Ultrafast, token usage, and credits

OpenAI lists four models with Ultrafast support. On a WebSocket, the client sends `"service_tier": "ultrafast"` in each `response.create` event. CodexLB-up checks eligibility against the individual account's catalog. It reserves budget at the requested tier and settles it at the actual tier when the provider reports one. [OpenAI Ultrafast guide](https://developers.openai.com/api/docs/guides/ultrafast-mode) · [Catalog eligibility](https://github.com/Lok3rn3t/codexLB-up/blob/1539da2892c9c2472090b9dd6609cdedb55d6620/openspec/specs/model-catalog-compat/spec.md#requirement-ultrafast-routing-follows-live-account-entitlement) · [Fork accounting rules](https://github.com/Lok3rn3t/codexLB-up/blob/1539da2892c9c2472090b9dd6609cdedb55d6620/openspec/specs/api-keys/spec.md#requirement-ultrafast-token-cost-follows-model-request-time-and-context-length)

The table gives the short-context Ultrafast rates in USD per million tokens at the time of release. Each cell lists regular input, cached input, and output, in that order. For GPT-6.2 Astra and Sol, Ultrafast costs 3× Standard through February 28, 2027, and 6× starting March 1, 2027, Pacific time. Beta.4 applies long-context rates to the entire request above 272,000 input tokens, including cached tokens. Both input rates double, and the output rate increases by a factor of 1.5. A request with exactly 272,000 input tokens uses short-context rates. [OpenAI API pricing](https://developers.openai.com/api/docs/pricing) · [Beta.4 implementation](https://github.com/Lok3rn3t/codexLB-up/blob/1539da2892c9c2472090b9dd6609cdedb55d6620/app/core/usage/pricing.py#L457-L543)

| Model | Through February 28, 2027 | From March 1, 2027 |
| --- | ---: | ---: |
| GPT-6.2 Astra | 24 / 1.20 / 120 | 48 / 2.40 / 240 |
| GPT-6.2 Sol | 6 / 0.30 / 30 | 12 / 0.60 / 60 |
| GPT-6 Astra | 60 / 6 / 300 | 60 / 6 / 300 |
| GPT-6.1 Sol | 12 / 0.60 / 60 | 12 / 0.60 / 60 |

- **Tokens.** With complete `usage` data, total usage is `input_tokens + output_tokens`. Cached tokens are already included in `input_tokens` and have their own price. If the stream disconnects before final `usage` arrives, the available data may give only a lower bound. [Responses API schema](https://developers.openai.com/api/reference/resources/responses)
- **Cost in USD.** Historical recalculation uses the request date. The models.dev and LiteLLM adapters accept explicit Ultrafast prices. Known models have fallback rates, including the scheduled GPT-6.2 price change. A Standard price alone is insufficient to calculate an Ultrafast price for an unknown model variant. [Accounting change](https://github.com/Lok3rn3t/codexLB-up/commit/2525877d) · [Soju06 #2547](https://github.com/Soju06/codex-lb/pull/2547) · [Offline metadata #2653](https://github.com/Soju06/codex-lb/pull/2653)
- **Credits and subscription balances.** In beta.4, API key limits denominated in `CREDITS` still record zero usage. Soju06 #2686 proposes a per-key budget based on published credit rates. An exact subscription balance requires provider measurements. A five-hour or seven-day quota percentage alone cannot establish the remaining number of tokens or credits. [Beta.4 implementation](https://github.com/Lok3rn3t/codexLB-up/blob/1539da2892c9c2472090b9dd6609cdedb55d6620/app/modules/api_keys/service.py#L1851-L1868) · [PR #2686](https://github.com/Soju06/codex-lb/pull/2686) · [Issue #2556](https://github.com/Soju06/codex-lb/issues/2556) · [Codex credit rates](https://learn.chatgpt.com/docs/pricing?codex-pricing-speed=ultrafast)

Other discussions cover the cost of cache writes, stopping account use before paid credits are consumed, retaining quota reset deadlines, and the precision of quota recovery timestamps. [PR #2504](https://github.com/Soju06/codex-lb/pull/2504) · [Issue #2736](https://github.com/Soju06/codex-lb/issues/2736) · [PR #2728](https://github.com/Soju06/codex-lb/pull/2728) · [PR #2710](https://github.com/Soju06/codex-lb/pull/2710)

## Beta.4 build and verification

Beta.4 incorporates changes from open Soju06 pull requests covering Standard and Fast fallback prices for GPT-6.2 Astra and Sol, a direct Images API example, and a connection-refusal test that uses a known closed local port. [Model pricing #2739](https://github.com/Soju06/codex-lb/pull/2739) · [Images API #2733](https://github.com/Soju06/codex-lb/pull/2733) · [Networking test #2738](https://github.com/Soju06/codex-lb/pull/2738)

PR #5 also updated `url` to 2.5.9 and `form_urlencoded` to 1.2.3. PR #6 prepared the release. On the PR #5 commit, 10,837 Linux unit tests passed. On release commit `1539da2892c9`, the unit, integration, end-to-end, and browser tests passed, along with the Rust, Docker, and Helm checks. [PR #5 CI](https://github.com/Lok3rn3t/codexLB-up/actions/runs/45386745014) · [Release commit CI](https://github.com/Lok3rn3t/codexLB-up/actions/runs/45390467786) · [Release build](https://github.com/Lok3rn3t/codexLB-up/actions/runs/45390509097) · [PR #6](https://github.com/Lok3rn3t/codexLB-up/pull/6) · [RustSec advisory](https://rustsec.org/advisories/RUSTSEC-2026-0592.html)

The beta.4 image is available for Linux amd64 and arm64. Its image index digest is `sha256:f8c06d738a5b58c7c3e763a4a137354fdb28889978bbdfc464e8bbb1f55ee79f`. The GitHub release also provides a wheel, a Python source distribution, a Helm chart, and package checksums. [Beta.4 release assets](https://github.com/Lok3rn3t/codexLB-up/releases/tag/v1.26.0-beta.4)

## Scope of the review

The index records the titles and links of all open Soju06 pull requests and issues on November 24, 2026. Recent open pull requests included Python, frontend, and Bun updates. Recent merges covered WebSocket bursts, dependency updates, account sorting, and importing multiple authentication files. PR #2502 adds MySQL and MariaDB support at the storage layer and requires separate migration testing. [Reviewed main branch](https://github.com/Soju06/codex-lb/commits/b3b42e785c1fdcc1f96607d4ccbc15865c537cbf/) · [PR #2502](https://github.com/Soju06/codex-lb/pull/2502) · [Open pull requests](https://github.com/Soju06/codex-lb/pulls) · [Open issues](https://github.com/Soju06/codex-lb/issues)

## Open pull requests (147)

| GitHub | Title |
| --- | --- |
| [#2745](https://github.com/Soju06/codex-lb/pull/2745) | chore(deps): bump the python-minor-patch group across 1 directory with 12 updates |
| [#2744](https://github.com/Soju06/codex-lb/pull/2744) | chore(deps): bump the frontend-minor-patch group across 1 directory with 21 updates |
| [#2741](https://github.com/Soju06/codex-lb/pull/2741) | chore(docker): bump oven/bun from 1.4.4-alpine to 1.4.5-alpine |
| [#2739](https://github.com/Soju06/codex-lb/pull/2739) | fix(usage): price gpt-6.2 astra and sol |
| [#2738](https://github.com/Soju06/codex-lb/pull/2738) | test(native): use a closed port for the refused fallback probes |
| [#2733](https://github.com/Soju06/codex-lb/pull/2733) | docs(images): clarify model discovery and direct API usage |
| [#2732](https://github.com/Soju06/codex-lb/pull/2732) | fix(proxy): bounded inline images on the HTTP responses bridge |
| [#2731](https://github.com/Soju06/codex-lb/pull/2731) | fix(proxy): do not replay an unknown WebSocket anchor's delta without the anchor |
| [#2728](https://github.com/Soju06/codex-lb/pull/2728) | fix(proxy): retain upstream usage-limit reset deadline in deferred keyed health penalties |
| [#2727](https://github.com/Soju06/codex-lb/pull/2727) | chore(deps): bump dnspython from 2.8.0 to 2.9.2 |
| [#2726](https://github.com/Soju06/codex-lb/pull/2726) | chore(deps): bump opentelemetry-api from 1.44.0 to 1.45.2 |
| [#2725](https://github.com/Soju06/codex-lb/pull/2725) | feat(accounts): redeem all eligible reset credits in one action |
| [#2724](https://github.com/Soju06/codex-lb/pull/2724) | fix(model-sources): preserve client collaboration namespace when source declares multi-agent support |
| [#2720](https://github.com/Soju06/codex-lb/pull/2720) | chore(deps): bump jsdom from 30.1.3 to 31.0.1 in /frontend |
| [#2718](https://github.com/Soju06/codex-lb/pull/2718) | chore(docker): bump astral-sh/uv from 0.13.7 to 0.13.9 |
| [#2717](https://github.com/Soju06/codex-lb/pull/2717) | chore(ci): bump github/codeql-action/upload-sarif from 4.39.3 to 4.39.4 |
| [#2715](https://github.com/Soju06/codex-lb/pull/2715) | chore(ci): bump docker/login-action from 4.7.0 to 4.8.0 |
| [#2714](https://github.com/Soju06/codex-lb/pull/2714) | chore(ci): bump softprops/action-gh-release from 3.0.3 to 3.0.4 |
| [#2713](https://github.com/Soju06/codex-lb/pull/2713) | docs: add optional desktop Dot recipe for codex-lb routing |
| [#2712](https://github.com/Soju06/codex-lb/pull/2712) | fix(proxy): retry zero-event bridge socket drops once |
| [#2711](https://github.com/Soju06/codex-lb/pull/2711) | fix(proxy): prevent native websocket burst drops and preserve diagnostics |
| [#2710](https://github.com/Soju06/codex-lb/pull/2710) | fix(usage): align reset recovery baseline timestamp precision |
| [#2708](https://github.com/Soju06/codex-lb/pull/2708) | feat(request-logs): add upstream facet to dashboard request logs |
| [#2707](https://github.com/Soju06/codex-lb/pull/2707) | feat(proxy): automatically route Daybreak Blue requests per API key |
| [#2705](https://github.com/Soju06/codex-lb/pull/2705) | fix(docker): upgrade apt runtime packages |
| [#2704](https://github.com/Soju06/codex-lb/pull/2704) | fix(proxy): mark proven pre-dispatch selector refusals |
| [#2702](https://github.com/Soju06/codex-lb/pull/2702) | fix(usage): recover accounts after confirmed quota resets |
| [#2701](https://github.com/Soju06/codex-lb/pull/2701) | fix(egress): enable TCP and HTTP/2 keepalive in native client pool |
| [#2700](https://github.com/Soju06/codex-lb/pull/2700) | fix(proxy): recover stateless quota failover |
| [#2692](https://github.com/Soju06/codex-lb/pull/2692) | fix(chat): preserve non-strict tool defaults during conversion |
| [#2689](https://github.com/Soju06/codex-lb/pull/2689) | feat(routing): add account diagnostic controls |
| [#2686](https://github.com/Soju06/codex-lb/pull/2686) | fix(api-keys): accrue and enforce credit limits |
| [#2682](https://github.com/Soju06/codex-lb/pull/2682) | fix(proxy): accept encrypted output in Responses include |
| [#2681](https://github.com/Soju06/codex-lb/pull/2681) | fix(sse): propagate source timeouts instead of spinning heartbeats |
| [#2673](https://github.com/Soju06/codex-lb/pull/2673) | chore(docker): bump python from 3.14-slim-trixie to 3.15-slim-trixie |
| [#2668](https://github.com/Soju06/codex-lb/pull/2668) | chore(async): own OAuth and refresh completion tasks |
| [#2667](https://github.com/Soju06/codex-lb/pull/2667) | fix(proxy): classify controlled interruptions as cancelled |
| [#2666](https://github.com/Soju06/codex-lb/pull/2666) | fix(proxy): recover complete native HTTP tool resends |
| [#2665](https://github.com/Soju06/codex-lb/pull/2665) | fix(proxy): use configuration&#95;update reasoning effort |
| [#2659](https://github.com/Soju06/codex-lb/pull/2659) | perf(dashboard): precompute durable dashboard and report snapshots |
| [#2654](https://github.com/Soju06/codex-lb/pull/2654) | fix(api-keys): bound expired-limit sweep progress |
| [#2653](https://github.com/Soju06/codex-lb/pull/2653) | chore(metadata): refresh model pricing and Codex version |
| [#2643](https://github.com/Soju06/codex-lb/pull/2643) | fix(accounts): honor proxy routes in probes and quota warmup |
| [#2640](https://github.com/Soju06/codex-lb/pull/2640) | fix(usage): lift the 429 cooldown after an upstream-confirmed reset credit |
| [#2638](https://github.com/Soju06/codex-lb/pull/2638) | fix(accounts): recognize the promax plan with Pro-equivalent capacity |
| [#2636](https://github.com/Soju06/codex-lb/pull/2636) | fix(proxy): notify Codex clients when idle upstream context is lost |
| [#2635](https://github.com/Soju06/codex-lb/pull/2635) | fix(native): preserve bounded WebSocket bursts |
| [#2634](https://github.com/Soju06/codex-lb/pull/2634) | fix(proxy): reject paused accounts on open WebSockets |
| [#2633](https://github.com/Soju06/codex-lb/pull/2633) | fix(health): authorize internal drain from raw socket peer |
| [#2632](https://github.com/Soju06/codex-lb/pull/2632) | fix(auth): bind trusted-header identity to raw socket peer |
| [#2631](https://github.com/Soju06/codex-lb/pull/2631) | fix(deploy): forward startup migration termination signals |
| [#2630](https://github.com/Soju06/codex-lb/pull/2630) | fix(shutdown): bound managed HTTP client close |
| [#2628](https://github.com/Soju06/codex-lb/pull/2628) | fix(proxy): honor poisoned fallback keys before bridge anchor planning |
| [#2625](https://github.com/Soju06/codex-lb/pull/2625) | fix(api-keys): expire elapsed samples in the /v1/usage aggregate |
| [#2618](https://github.com/Soju06/codex-lb/pull/2618) | fix(http-bridge): recover from draining owner rejection |
| [#2617](https://github.com/Soju06/codex-lb/pull/2617) | fix(proxy): allow prefix-settled replay outputs |
| [#2614](https://github.com/Soju06/codex-lb/pull/2614) | feat(model-sources): route decisions and systemone to capable sources |
| [#2604](https://github.com/Soju06/codex-lb/pull/2604) | fix(ui): keep password-manager suggestions clickable over dialogs |
| [#2599](https://github.com/Soju06/codex-lb/pull/2599) | feat(archive): re-encode closed conversation archive hours as zstd |
| [#2597](https://github.com/Soju06/codex-lb/pull/2597) | feat(desktop): bridge ChatGPT auth to local CodexLB |
| [#2593](https://github.com/Soju06/codex-lb/pull/2593) | fix(images): allow GPT Image 2 transparent PNG and WebP |
| [#2579](https://github.com/Soju06/codex-lb/pull/2579) | fix(proxy): fence HTTP bridge writes by dispatch generation |
| [#2553](https://github.com/Soju06/codex-lb/pull/2553) | feat(helm): make startup probe configurable |
| [#2548](https://github.com/Soju06/codex-lb/pull/2548) | fix(auth): honor configured admin session lifetime |
| [#2547](https://github.com/Soju06/codex-lb/pull/2547) | fix(usage): account for Astra ultrafast token pricing |
| [#2546](https://github.com/Soju06/codex-lb/pull/2546) | feat(accounts): support Pro Max routing and quota coverage |
| [#2543](https://github.com/Soju06/codex-lb/pull/2543) | docs(codex): enable API-key model discovery in setup examples |
| [#2539](https://github.com/Soju06/codex-lb/pull/2539) | fix(proxy): treat websocket close 1009 as terminal payload&#95;too&#95;large |
| [#2534](https://github.com/Soju06/codex-lb/pull/2534) | feat(proxy): admit bounded inline images on the HTTP responses bridge |
| [#2531](https://github.com/Soju06/codex-lb/pull/2531) | fix(proxy): normalize parallel&#95;tool&#95;calls for Responses-Lite upstream |
| [#2530](https://github.com/Soju06/codex-lb/pull/2530) | fix(http-bridge): parse multiline websocket JSON messages |
| [#2508](https://github.com/Soju06/codex-lb/pull/2508) | fix(proxy): reuse bridge sessions for inline images |
| [#2507](https://github.com/Soju06/codex-lb/pull/2507) | feat(cli): add --log-level and --log-file; stop the metrics server resetting logging |
| [#2506](https://github.com/Soju06/codex-lb/pull/2506) | fix(shutdown): let DB-owning background tasks finish before cancelling them |
| [#2504](https://github.com/Soju06/codex-lb/pull/2504) | fix(usage): account for cache-write tokens |
| [#2503](https://github.com/Soju06/codex-lb/pull/2503) | fix(http-bridge): keep replayed history images on the bridge |
| [#2502](https://github.com/Soju06/codex-lb/pull/2502) | MySQL / MariaDB support |
| [#2497](https://github.com/Soju06/codex-lb/pull/2497) | feat(accounts): show reset credits for paused accounts |
| [#2488](https://github.com/Soju06/codex-lb/pull/2488) | fix(proxy): handle CRLF and malformed UTF-8 in owner forwarding |
| [#2487](https://github.com/Soju06/codex-lb/pull/2487) | fix(auth): reject non-ASCII TOTP digits safely |
| [#2486](https://github.com/Soju06/codex-lb/pull/2486) | fix(balancer): admit a hard continuity owner serving its own transient backoff |
| [#2472](https://github.com/Soju06/codex-lb/pull/2472) | fix(proxy): surface native transport give-up terminals |
| [#2464](https://github.com/Soju06/codex-lb/pull/2464) | feat(ui): add compact and fullscreen dashboard account views |
| [#2463](https://github.com/Soju06/codex-lb/pull/2463) | feat(api-keys): add estimated usage-share limits |
| [#2458](https://github.com/Soju06/codex-lb/pull/2458) | fix(proxy): release a bridge-bypassed turn-state owner on quota evidence |
| [#2457](https://github.com/Soju06/codex-lb/pull/2457) | fix(proxy): classify Windows route errors 1231/1232 as host network loss |
| [#2451](https://github.com/Soju06/codex-lb/pull/2451) | fix(proxy): refuse remote compaction for model-source models before account selection |
| [#2448](https://github.com/Soju06/codex-lb/pull/2448) | feat(proxy): diversify subagents from parent accounts |
| [#2444](https://github.com/Soju06/codex-lb/pull/2444) | fix(metrics): separate observed generation timing from request latency |
| [#2439](https://github.com/Soju06/codex-lb/pull/2439) | fix(proxy): preserve upstream quota reset metadata on terminal errors |
| [#2430](https://github.com/Soju06/codex-lb/pull/2430) | feat(proxy): add transcript core storage |
| [#2429](https://github.com/Soju06/codex-lb/pull/2429) | refactor(auth): preserve fixed guardian idle keepalive |
| [#2428](https://github.com/Soju06/codex-lb/pull/2428) | feat(proxy): decide relocation once, and rebuild a conversation from the durable spool |
| [#2423](https://github.com/Soju06/codex-lb/pull/2423) | fix(proxy): reject a dead client anchor instead of asking for a retry |
| [#2421](https://github.com/Soju06/codex-lb/pull/2421) | chore: release v1.25.0-beta.10 |
| [#2403](https://github.com/Soju06/codex-lb/pull/2403) | feat(proxy): classify usage-limit rejections and answer pool-walk exclusion |
| [#2398](https://github.com/Soju06/codex-lb/pull/2398) | fix(proxy): prepare portable WebSocket full resends for quota replay |
| [#2391](https://github.com/Soju06/codex-lb/pull/2391) | feat(proxy): shape the failover decision around the pool and render its terminal |
| [#2377](https://github.com/Soju06/codex-lb/pull/2377) | fix(dashboard): calm the telemetry consent dialog |
| [#2345](https://github.com/Soju06/codex-lb/pull/2345) | fix(proxy): preserve local quarantine evidence during completion |
| [#2344](https://github.com/Soju06/codex-lb/pull/2344) | feat(health): expose request-persistence ownership during drain |
| [#2332](https://github.com/Soju06/codex-lb/pull/2332) | fix(proxy): fail over account-local model rejection |
| [#2326](https://github.com/Soju06/codex-lb/pull/2326) | fix(warmup): preserve live reset evidence across skipped polls |
| [#2325](https://github.com/Soju06/codex-lb/pull/2325) | feat(cli): bound whole-home retag planning and report progress |
| [#2324](https://github.com/Soju06/codex-lb/pull/2324) | feat(proxy): forward explicit compact requests to model sources |
| [#2323](https://github.com/Soju06/codex-lb/pull/2323) | feat(cli): add targeted session metadata preview and repair |
| [#2322](https://github.com/Soju06/codex-lb/pull/2322) | feat(db): explain guarded migration recovery stamping |
| [#2321](https://github.com/Soju06/codex-lb/pull/2321) | fix(accounts): preserve observed monthly quota across plans |
| [#2319](https://github.com/Soju06/codex-lb/pull/2319) | fix(proxy): contain post-terminal health write failures |
| [#2317](https://github.com/Soju06/codex-lb/pull/2317) | fix(proxy): align compact budget with responses stream |
| [#2312](https://github.com/Soju06/codex-lb/pull/2312) | docs: use GPT-6 Astra in current client examples |
| [#2310](https://github.com/Soju06/codex-lb/pull/2310) | docs: align agent instructions with Astra prompt guidance |
| [#2307](https://github.com/Soju06/codex-lb/pull/2307) | feat(db): log per-revision migration progress |
| [#2303](https://github.com/Soju06/codex-lb/pull/2303) | perf(http-bridge): drain queued transcript batches without interval waits |
| [#2294](https://github.com/Soju06/codex-lb/pull/2294) | feat(telemetry): expand anonymous telemetry to schema v2 with summable day aggregates and histograms |
| [#2280](https://github.com/Soju06/codex-lb/pull/2280) | fix(proxy): preserve newer retry state during scheduled cleanup |
| [#2278](https://github.com/Soju06/codex-lb/pull/2278) | fix(proxy): count incomplete responses toward bridge retries |
| [#2277](https://github.com/Soju06/codex-lb/pull/2277) | fix(proxy): preserve continuation anchors during input normalization |
| [#2276](https://github.com/Soju06/codex-lb/pull/2276) | fix(proxy): preserve newer quarantine during response cleanup |
| [#2146](https://github.com/Soju06/codex-lb/pull/2146) | feat(dashboard): add request heatmap on dashboard |
| [#2133](https://github.com/Soju06/codex-lb/pull/2133) | fix(proxy): isolate bridge heartbeat from maintenance |
| [#2122](https://github.com/Soju06/codex-lb/pull/2122) | fix(warmup): restore reset usage threshold |
| [#2121](https://github.com/Soju06/codex-lb/pull/2121) | fix(proxy): recover tool-complete goal followups from unavailable owners |
| [#2120](https://github.com/Soju06/codex-lb/pull/2120) | fix(auth): retain unexpired access on refresh preflight failure |
| [#2118](https://github.com/Soju06/codex-lb/pull/2118) | feat(ui): add Japanese dashboard localization |
| [#2117](https://github.com/Soju06/codex-lb/pull/2117) | fix(proxy): retire revoked stream accounts |
| [#2115](https://github.com/Soju06/codex-lb/pull/2115) | feat(proxy): support Astra steering with transport-owned dispatch |
| [#2112](https://github.com/Soju06/codex-lb/pull/2112) | fix(observability): record HTTP upstream phase timings |
| [#2102](https://github.com/Soju06/codex-lb/pull/2102) | feat(proxy): support Codex history and notes across account pools |
| [#2101](https://github.com/Soju06/codex-lb/pull/2101) | fix(proxy): add native history and notes routes with account-local ownership |
| [#2099](https://github.com/Soju06/codex-lb/pull/2099) | feat(proxy): preserve async tool results across continuations |
| [#2098](https://github.com/Soju06/codex-lb/pull/2098) | fix(docker): isolate host OAuth callback port by default |
| [#2097](https://github.com/Soju06/codex-lb/pull/2097) | feat(proxy): enforce Astra configuration-update policy |
| [#2088](https://github.com/Soju06/codex-lb/pull/2088) | fix(http-bridge): wait for aborted bridge owner before retrying admission |
| [#2085](https://github.com/Soju06/codex-lb/pull/2085) | feat(models): add gpt-6 astra catalog support |
| [#2075](https://github.com/Soju06/codex-lb/pull/2075) | fix(proxy): keep frameless bridge drops account neutral |
| [#2069](https://github.com/Soju06/codex-lb/pull/2069) | fix(proxy): recover unanchored quota replay |
| [#2048](https://github.com/Soju06/codex-lb/pull/2048) | fix(proxy): preserve exhausted sticky failover |
| [#2001](https://github.com/Soju06/codex-lb/pull/2001) | fix(proxy): release payload owner after pre-visible quota rejection |
| [#1962](https://github.com/Soju06/codex-lb/pull/1962) | fix(proxy): preserve half-open probe ownership during cleanup |
| [#1952](https://github.com/Soju06/codex-lb/pull/1952) | fix(proxy): preserve tool search pairs through replay |
| [#1938](https://github.com/Soju06/codex-lb/pull/1938) | feat(accounts): add encrypted portable account bundles |
| [#1932](https://github.com/Soju06/codex-lb/pull/1932) | feat(db): add safe SQLite compaction |
| [#1922](https://github.com/Soju06/codex-lb/pull/1922) | chore(main): release 1.25.0 |
| [#1905](https://github.com/Soju06/codex-lb/pull/1905) | fix(proxy): preserve continuation ownership across source routing |
| [#1903](https://github.com/Soju06/codex-lb/pull/1903) | fix(proxy): bound memory used by paused bridge streams |
| [#1528](https://github.com/Soju06/codex-lb/pull/1528) | feat(accounts): add per-account usage limits |

## Open issues (128)

| GitHub | Title |
| --- | --- |
| [#2740](https://github.com/Soju06/codex-lb/issues/2740) | bug: Codex Desktop can display opaque async notifications through the relay |
| [#2737](https://github.com/Soju06/codex-lb/issues/2737) | bug: Codex repeats proposed plan and remains in Plan mode |
| [#2736](https://github.com/Soju06/codex-lb/issues/2736) | feat: per-account cutoff to avoid paid credits |
| [#2730](https://github.com/Soju06/codex-lb/issues/2730) | bug(proxy): WebSocket replay sends a delta without its anchor after an interrupted turn or any anchor the connection did not complete |
| [#2703](https://github.com/Soju06/codex-lb/issues/2703) | Automatically route Daybreak requests to Trusted Cyber accounts |
| [#2693](https://github.com/Soju06/codex-lb/issues/2693) | bug(accounts): overview reports 0 reset credits while the dashboard shows the live count (per-replica snapshot vs live fetch) |
| [#2691](https://github.com/Soju06/codex-lb/issues/2691) | bug: chat-to-Responses conversion loses non-strict tool defaults |
| [#2688](https://github.com/Soju06/codex-lb/issues/2688) | bug: one client's large response.create requests can OOM-kill the whole proxy |
| [#2684](https://github.com/Soju06/codex-lb/issues/2684) | bug: Codex desktop app requests rejected with "Invalid request payload" (param=include) — &#96;output.encrypted&#95;content&#96; not in include allowlist |
| [#2669](https://github.com/Soju06/codex-lb/issues/2669) | docs: verified workaround for missing desktop Dot while keeping codex-lb routing |
| [#2664](https://github.com/Soju06/codex-lb/issues/2664) | bug(proxy): configuration&#95;update effort is ignored |
| [#2663](https://github.com/Soju06/codex-lb/issues/2663) | feat: Add configurable daily active hours to the Weekly credits pace forecast |
| [#2658](https://github.com/Soju06/codex-lb/issues/2658) | HTTP bridge reuses prompt-cache upstream websocket past the 60-minute limit → 400 websocket&#95;connection&#95;limit&#95;reached |
| [#2655](https://github.com/Soju06/codex-lb/issues/2655) | bug: cross-replica owner forwarding always fails with bridge&#95;forward&#95;invalid because thread affinity keys start with LF |
| [#2652](https://github.com/Soju06/codex-lb/issues/2652) | bug: &#96;ApiKeysRepository.reset&#95;expired&#95;limits&#96; busy-loops forever on SQLite when &#96;reset&#95;at&#96; is stored without microseconds |
| [#2637](https://github.com/Soju06/codex-lb/issues/2637) | bug(accounts): promax plan is not recognized, so Pro Max accounts get free-tier capacity and are skipped by routing |
| [#2605](https://github.com/Soju06/codex-lb/issues/2605) | feat: expose subscription renewal and cancellation state separately from period end |
| [#2603](https://github.com/Soju06/codex-lb/issues/2603) | bug: Apple Passwords suggestions can't be chosen inside dashboard dialogs in Chrome (TOTP, step-up, password) |
| [#2602](https://github.com/Soju06/codex-lb/issues/2602) | bug(accounts): self&#95;serve&#95;business&#95;prolite weekly-only accounts stay rate&#95;limited after early reset; plan not recognized |
| [#2601](https://github.com/Soju06/codex-lb/issues/2601) | bug(oauth): outbound connection failures return unhandled 500 in PKCE callback and device start |
| [#2596](https://github.com/Soju06/codex-lb/issues/2596) | CODEX&#95;LB&#95;CONVERSATION&#95;ARCHIVE&#95;ENABLED doesn't work with k8s / multiple instances |
| [#2582](https://github.com/Soju06/codex-lb/issues/2582) | bug(proxy): subagent messages block recovery after HTTP bridge reconnect |
| [#2580](https://github.com/Soju06/codex-lb/issues/2580) | Daybreak toggle in Codex Desktop disappears when model&#95;provider = "codex-lb" |
| [#2574](https://github.com/Soju06/codex-lb/issues/2574) | DATA LOSS: WebSocket replay drops the prewarm anchor and sends the first Codex turn without its context |
| [#2563](https://github.com/Soju06/codex-lb/issues/2563) | DATA LOSS: codex-lb silently drops developer messages from chained requests (moves them into &#96;instructions&#96;, which &#96;previous&#95;response&#95;id&#96; does not carry) |
| [#2560](https://github.com/Soju06/codex-lb/issues/2560) | bug: CCodex gateway traffic (originator ccodex-internal) is treated as non-native and rewritten to codex&#95;cli&#95;rs/0.144.0, so OpenAI rejects gpt-6 models |
| [#2559](https://github.com/Soju06/codex-lb/issues/2559) | feat: not a feature request, can you check discussions? |
| [#2557](https://github.com/Soju06/codex-lb/issues/2557) | bug(accounts): plan capacity constants are unmeasured; every weekly value is 5h × 33.6 |
| [#2556](https://github.com/Soju06/codex-lb/issues/2556) | bug(api-keys): &#96;credits&#96; limits never accrue usage, so they are never enforced. Bug, or manual override by design? |
| [#2554](https://github.com/Soju06/codex-lb/issues/2554) | bug(routing): leased-token pressure divides tokens by plan credits, so one open stream makes a Plus account look 100% used |
| [#2552](https://github.com/Soju06/codex-lb/issues/2552) | feat: add blacklisted models for an api key |
| [#2551](https://github.com/Soju06/codex-lb/issues/2551) | feat: option to auto redeem reset on quota exceeded |
| [#2538](https://github.com/Soju06/codex-lb/issues/2538) | bug(http-bridge): upstream error responses silently swallowed as timeouts — pretty JSON parsing + Responses-Lite parallel&#95;tool&#95;calls |
| [#2514](https://github.com/Soju06/codex-lb/issues/2514) | feat(accounts): redeem all eligible reset credits in one action |
| [#2511](https://github.com/Soju06/codex-lb/issues/2511) | bug(accounts): self&#95;serve&#95;business&#95;prolite usage plan is rejected as unknown |
| [#2505](https://github.com/Soju06/codex-lb/issues/2505) | bug: shutdown cancels schedulers and the leader-lease keeper mid-DB-work (SQLite pool CancelledError, unreleased lease, unclean run-state) |
| [#2501](https://github.com/Soju06/codex-lb/issues/2501) | bug: native HTTP upstream regressed in 1.25.0-beta.7 with native upstream request failures |
| [#2500](https://github.com/Soju06/codex-lb/issues/2500) | bug: #1968 shield-loop livelock still ships in latest stable 1.24.0; please cut a stable patch with #1969 |
| [#2499](https://github.com/Soju06/codex-lb/issues/2499) | bug(model-sources): multi-agent capability does not preserve client collaboration tools |
| [#2493](https://github.com/Soju06/codex-lb/issues/2493) | bug: Beta.9 HTTP bridge can close native stream without terminal event after proxy-injected anchor rejection |
| [#2492](https://github.com/Soju06/codex-lb/issues/2492) | feat: Reset API key limit usage from dashboard without regenerating keys |
| [#2471](https://github.com/Soju06/codex-lb/issues/2471) | bug(proxy): with upstream&#95;stream&#95;transport=http the native egress multiplexes every account's streams onto ONE shared HTTP/2 connection — one transport failure kills all in-flight streams of all accounts, is logged with no reason/status, and is never retried |
| [#2470](https://github.com/Soju06/codex-lb/issues/2470) | bug(proxy): direct-HTTP stream that dies with "Native upstream transport ended before a terminal event" never releases its account stream lease → per-account cap wedges (every request waits, then &#96;account&#95;stream&#95;cap&#96;) until restart |
| [#2465](https://github.com/Soju06/codex-lb/issues/2465) | bug: beta.9 sticky bridge lineages wedge permanently; image+tools path sends invalid parallel&#95;tool&#95;calls |
| [#2456](https://github.com/Soju06/codex-lb/issues/2456) | bug(proxy): Windows route errors 1231/1232 bypass shared-client recovery |
| [#2455](https://github.com/Soju06/codex-lb/issues/2455) | bug(proxy): bridge payload bypass blocks verified quota failover |
| [#2443](https://github.com/Soju06/codex-lb/issues/2443) | bug(metrics): dashboard/report TPS uses post-settlement latency and reasoning-inclusive TTFT |
| [#2442](https://github.com/Soju06/codex-lb/issues/2442) | bug(proxy): early token&#95;expired reauth account poisons fresh Codex HTTP routing |
| [#2426](https://github.com/Soju06/codex-lb/issues/2426) | bug(metrics): populate account counts and expose availability for alerting |
| [#2425](https://github.com/Soju06/codex-lb/issues/2425) | bug: input&#95;image requests still fail ~35% during overload on beta.8 — the HTTP bridge bypass, not the upstream transport, is the cause (follow-up to #2363/#2386) |
| [#2420](https://github.com/Soju06/codex-lb/issues/2420) | bug(accounts): Hard-coded Pro and Pro Lite credit capacities disagree with observed quota consumption, distorting pooled credit reporting |
| [#2413](https://github.com/Soju06/codex-lb/issues/2413) | feat: Luna Reserve (gpt-reserve) fallback when chat quota is exhausted |
| [#2409](https://github.com/Soju06/codex-lb/issues/2409) | bug(proxy): intermittent cache misses on Astra/SOL with the same Pro account across HTTP and WebSocket (195k–777k input) |
| [#2389](https://github.com/Soju06/codex-lb/issues/2389) | bug(http-bridge): a model-transition fork rescues one turn, then re-derives the same owner conflict |
| [#2388](https://github.com/Soju06/codex-lb/issues/2388) | bug(proxy): other HTTP-bridge local refusals still reach native Codex clients as an empty 200 |
| [#2356](https://github.com/Soju06/codex-lb/issues/2356) | bug(proxy): experimental context management returns 405 for native notes v2 calls |
| [#2343](https://github.com/Soju06/codex-lb/issues/2343) | feat(health): expose request-persistence ownership during drain |
| [#2327](https://github.com/Soju06/codex-lb/issues/2327) | fix(accounts): recover stale holds after verified matching operator probes |
| [#2318](https://github.com/Soju06/codex-lb/issues/2318) | feat(proxy): forward explicit compact requests to Responses model sources |
| [#2314](https://github.com/Soju06/codex-lb/issues/2314) | ci: reconcile issue and PR status-label ownership and lifecycle |
| [#2311](https://github.com/Soju06/codex-lb/issues/2311) | docs: use GPT-6 Astra in current client examples |
| [#2309](https://github.com/Soju06/codex-lb/issues/2309) | docs: align agent instructions with Astra prompt guidance |
| [#2304](https://github.com/Soju06/codex-lb/issues/2304) | feat(images): support GPT Image 2.5 Flare and Sunburst in the Images API |
| [#2302](https://github.com/Soju06/codex-lb/issues/2302) | fix(a11y): name model-source capability checkboxes |
| [#2292](https://github.com/Soju06/codex-lb/issues/2292) | feat(db): gate PostgreSQL-only support on a verified SQLite migration path |
| [#2291](https://github.com/Soju06/codex-lb/issues/2291) | bug: queued transcript batches wait between flushes |
| [#2290](https://github.com/Soju06/codex-lb/issues/2290) | feat(model-sources): discover CLIProxyAPI catalogs and retain unavailable ownership |
| [#2274](https://github.com/Soju06/codex-lb/issues/2274) | bug: continuations can be routed to the wrong account |
| [#2273](https://github.com/Soju06/codex-lb/issues/2273) | bug: incomplete responses can bypass bridge retry limits |
| [#2272](https://github.com/Soju06/codex-lb/issues/2272) | bug: bridge retries can stay blocked after cooldown ends |
| [#2271](https://github.com/Soju06/codex-lb/issues/2271) | bug: retry claims can stay locked after their owner exits |
| [#2270](https://github.com/Soju06/codex-lb/issues/2270) | bug: retry cleanup can delete state changed by a newer request |
| [#2269](https://github.com/Soju06/codex-lb/issues/2269) | bug: forwarded continuations can lose required conversation history |
| [#2268](https://github.com/Soju06/codex-lb/issues/2268) | bug: old bridge requests can clear a newer session's quarantine |
| [#2266](https://github.com/Soju06/codex-lb/issues/2266) | bug: paused streams can keep growing worker memory |
| [#2262](https://github.com/Soju06/codex-lb/issues/2262) | feat(proxy): preserve built-in OpenAI provider when routing ChatGPT-authenticated Codex Desktop through codex-lb |
| [#2169](https://github.com/Soju06/codex-lb/issues/2169) | test: make native SSE fallback refusal fixture portable on macOS |
| [#2128](https://github.com/Soju06/codex-lb/issues/2128) | bug(proxy): standalone web search fails on v1 and duplicates native Content-Type |
| [#2108](https://github.com/Soju06/codex-lb/issues/2108) | bug: HTTP Responses logs omit observed upstream phase timings |
| [#2090](https://github.com/Soju06/codex-lb/issues/2090) | fix(proxy): reconcile reservations after late HTTP-bridge anchor injection |
| [#2081](https://github.com/Soju06/codex-lb/issues/2081) | bug: direct websocket terminal failures lose transport and owner evidence |
| [#2076](https://github.com/Soju06/codex-lb/issues/2076) | bug: default Docker port 1455 mapping can intercept Codex Desktop OAuth callbacks |
| [#2074](https://github.com/Soju06/codex-lb/issues/2074) | bug: post-output frame-less bridge drops still penalize account health |
| [#2068](https://github.com/Soju06/codex-lb/issues/2068) | bug(proxy): quota failover stalls unanchored full-resend threads |
| [#2064](https://github.com/Soju06/codex-lb/issues/2064) | bug(proxy): revoked access tokens repeatedly re-enter reauth routing |
| [#2038](https://github.com/Soju06/codex-lb/issues/2038) | Visual Studio Copilot requires GET /v1/models/{model&#95;id} |
| [#2033](https://github.com/Soju06/codex-lb/issues/2033) | proxy: a failing post-terminal health write emits a second terminal stream frame |
| [#2028](https://github.com/Soju06/codex-lb/issues/2028) | fix(logging): shared log-redaction patterns leave credential tails for auth-param lists, quoted keys, and whitespace-separated tokens |
| [#1981](https://github.com/Soju06/codex-lb/issues/1981) | bug: wedged-teardown interrupt fails with "Cannot operate on a closed database", then the process holds the SQLite write lock permanently (55 min of database-is-locked while /health stays 200) |
| [#1979](https://github.com/Soju06/codex-lb/issues/1979) | feat(automations): add an opt-in verified weekly-window prestart preset |
| [#1976](https://github.com/Soju06/codex-lb/issues/1976) | bug(warmup): staggered idle slots can be unreachable for sliding reset&#95;at |
| [#1975](https://github.com/Soju06/codex-lb/issues/1975) | bug(warmup): live usage ingestion can consume reset evidence without invoking limit warm-up |
| [#1959](https://github.com/Soju06/codex-lb/issues/1959) | feat: Would you be interested in an optional auto re-login feature? |
| [#1950](https://github.com/Soju06/codex-lb/issues/1950) | bug(compact): hosted computer screenshots can still hard-fail compaction and wedge image-heavy threads |
| [#1946](https://github.com/Soju06/codex-lb/issues/1946) | UI account section bug |
| [#1935](https://github.com/Soju06/codex-lb/issues/1935) | feat: retry upstream model-capacity responses for Codex goals |
| [#1924](https://github.com/Soju06/codex-lb/issues/1924) | bug(proxy): inline-image 429 can prevent prompt-cache failover |
| [#1901](https://github.com/Soju06/codex-lb/issues/1901) | bug(reports): /api/reports takes ~120 s for a 7-day window (~543k rows) while equivalent raw SQL finishes in ~2.5 s |
| [#1898](https://github.com/Soju06/codex-lb/issues/1898) | fix(proxy): persist complete HTTP bridge replay transcripts |
| [#1895](https://github.com/Soju06/codex-lb/issues/1895) | bug(warmup): /v1/warmup fails with 404 (compact payload) and account probe fails with 400 (max&#95;output&#95;tokens=1) — windows cannot be auto-started |
| [#1870](https://github.com/Soju06/codex-lb/issues/1870) | feat: add an upstream facet to dashboard request logs |
| [#1844](https://github.com/Soju06/codex-lb/issues/1844) | Telemetry opt-out: close the consent/send race and follow-up hardening |
| [#1799](https://github.com/Soju06/codex-lb/issues/1799) | bug: HTTP responses session bridge returns 503: "preserving an incompatible admission handoff" |
| [#1793](https://github.com/Soju06/codex-lb/issues/1793) | feat: weekly limits estimation in $ |
| [#1758](https://github.com/Soju06/codex-lb/issues/1758) | http-bridge: evicting an inflight waiter does not cancel its creator, so multiple creators race one session key |
| [#1708](https://github.com/Soju06/codex-lb/issues/1708) | ux/docs: make routing, sticky affinity, quota thresholds, warm-up, and account eligibility understandable in the dashboard |
| [#1707](https://github.com/Soju06/codex-lb/issues/1707) | bug: existing Codex thread can remain unusable on dead hard-affinity owner while fresh/side chat works |
| [#1682](https://github.com/Soju06/codex-lb/issues/1682) | bug: leader lease loss on single-instance SQLite causes a self-sustaining 17-minute &#96;database is locked&#96; stall that blocks leader re-election |
| [#1636](https://github.com/Soju06/codex-lb/issues/1636) | Add safe targeted Codex session metadata repair |
| [#1595](https://github.com/Soju06/codex-lb/issues/1595) | feat: try fuzzing for testing |
| [#1576](https://github.com/Soju06/codex-lb/issues/1576) | feat: add strict model-to-ChatGPT OAuth account routing |
| [#1572](https://github.com/Soju06/codex-lb/issues/1572) | feat: support CODEX&#95;LB&#95;ENCRYPTION&#95;KEY for stateless replicas |
| [#1471](https://github.com/Soju06/codex-lb/issues/1471) | ci(db): gate long-running migrations with a production-scale duration check |
| [#1470](https://github.com/Soju06/codex-lb/issues/1470) | feat(db): make data-backfill migrations non-blocking, resumable, and observable |
| [#1467](https://github.com/Soju06/codex-lb/issues/1467) | bug: gpt-5.3-codex-spark works on Pro but is missing from /v1/models |
| [#1415](https://github.com/Soju06/codex-lb/issues/1415) | perf(balancer): optimize low-TTFT routing for large account pools under bursts |
| [#1413](https://github.com/Soju06/codex-lb/issues/1413) | feat(accounts): support explicit access-token-only credential imports |
| [#1367](https://github.com/Soju06/codex-lb/issues/1367) | bug(accounts): Team 30d quota is displayed as 5h |
| [#1307](https://github.com/Soju06/codex-lb/issues/1307) | feat: subagent prompt-cache affinity TTL |
| [#1304](https://github.com/Soju06/codex-lb/issues/1304) | WebSocket clean-close handoff can consume a queued turn |
| [#1208](https://github.com/Soju06/codex-lb/issues/1208) | feat: Improve upstream transport parity and eliminate the easily identifiable codex-lb fingerprint |
| [#1130](https://github.com/Soju06/codex-lb/issues/1130) | feat: support for (personal) access token accounts (for business/enterprise) |
| [#986](https://github.com/Soju06/codex-lb/issues/986) | feat: optional sticky account switchover only after compaction boundary |
| [#956](https://github.com/Soju06/codex-lb/issues/956) | feat: pace-aware throttling to land exactly on reset boundaries |
| [#850](https://github.com/Soju06/codex-lb/issues/850) | &#91;Feature&#93; Full Account Backup &amp; Restore |
| [#631](https://github.com/Soju06/codex-lb/issues/631) | Account limit restriction |
| [#620](https://github.com/Soju06/codex-lb/issues/620) | Complete deferred Images API fan-out and observability tasks |
| [#578](https://github.com/Soju06/codex-lb/issues/578) | &#91;design&#93; Reconsider budget-safe routing gate vs health-tier overlap and per-window thresholds |
