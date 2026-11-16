## ADDED Requirements

### Requirement: Complete HTTP resends honor dead-anchor fences on acquisition fallback keys

When a generated HTTP turn state resolves to one durable continuity record and
session acquisition can use its scoped thread or legacy-session fallback key,
the proxy MUST consult that fallback key's active anchor quarantine or abandonment
tombstone before injecting a proxy-owned anchor and trimming input. A proven
complete resend MUST retain its full input and resolved account owner. Incomplete
history MUST fail closed; explicit client anchors MUST retain their existing
validation, and fences MUST remain isolated by thread and API-key scope.

#### Scenario: Complete history recovers across split durable records

- **GIVEN** an old turn-state record retains an anchor and input prefix
- **AND** its same-account acquisition fallback key fences that anchor
- **WHEN** the client resends complete history through either HTTP Responses route
- **THEN** the full input is dispatched on the resolved owner without the proxy-owned anchor
- **AND** a subsequent continuation can complete

#### Scenario: A cached miss is corrected on the next complete resend

- **GIVEN** planning cached a retry-circuit miss before a fallback fence was written
- **WHEN** submission discovers the fence and rejects the prepared anchor
- **THEN** the next complete resend honors the known fence before anchor injection

#### Scenario: Missing context cannot become a fresh conversation

- **WHEN** the fenced request carries only a delta or incomplete cumulative history
- **THEN** the proxy refuses the unsafe dispatch instead of dropping required context

#### Scenario: Explicit anchors and unrelated scopes retain their contract

- **WHEN** the request explicitly supplies an anchor or belongs to an unrelated thread or API key
- **THEN** fallback handling does not silently remove its anchor or import another scope's fence

## MODIFIED Requirements

### Requirement: Silent HTTP bridge sessions are quarantined from re-attach and reuse

When an HTTP bridge session proves silent/wedged, the proxy MUST quarantine its session key for a bounded window so later requests stop attaching to it. A session proves silent/wedged when either (a) a pending request being failed or retired carried a proxy-injected `previous_response_id`, had sent `response.create`, observed upstream response events, and never had `response.created` assigned, (b) the session key hits two consecutive eventless `missing_response_created_timeout` retires, or (c) the hard-affinity retry circuit for the key opens on an eventless poison-class failure (`stream_incomplete` or `stream_idle_timeout`), in which case the quarantine reason MUST be `retry_circuit_poisoned_anchor`. This holds for every path that fails or retires the request — partial stale-holder cleanup, the reader-failure funnel, and direct all-stale session retirement alike. The quarantine MUST be evaluated only when a request is already being failed or its session retired — never against a live owned turn — so a stream whose `response.created` was observed (including deferred-reasoning streams with long event gaps) MUST NOT be quarantined, and mere event silence during an owned live turn MUST NOT trigger quarantine by itself.

While a session key is quarantined: an existing session under that key MUST NOT be selected for reuse (a new request detaches it and proceeds on a fresh session), and for durable-anchor selection a quarantined session that is still open MUST count as absent, exactly as if it were already gone. The quarantine registry verdict is authoritative for the key: any session under the key while the quarantine window is active — including a freshly created replacement whose own completion has not yet cleared the quarantine — is equally excluded from reuse and equally absent for anchor selection. A fresh reattach whose incoming payload is verified to be a safe full conversation resend — its stored durable prefix is trimmable and its fresh suffix retains the prior output or exactly matches the pending tool-call manifest — MUST NOT receive a proxy-injected durable anchor through any injection point — the fresh-reattach injection, session-state hydration of the durable anchor, or the session-level injection — so the dispatch goes upstream genuinely unanchored with the client's own untrimmed payload. When a cumulative payload without an explicit client anchor cannot be verified to carry the required prior context and the durable anchor is quarantined, the request MUST fail closed as `bridge_previous_response_not_found` before upstream dispatch instead of sending incomplete history unanchored. A payload that does not look like a full resend (a genuine delta-only continuation) MUST still receive the durable anchor, because it has no other way to convey prior conversation state. When no anchor exists anywhere for such a payload — the client supplied none and durable continuity was abandoned — and the key carries poison evidence (an active poison quarantine, or a durable circuit row still recording the poison episode), planning MUST fail the request closed as `bridge_previous_response_not_found` instead of dispatching it unanchored as a new conversation.

Quarantine state MUST be bounded and self-recovering: it is in-memory and session-scoped, expires by TTL (a live session that outlives its quarantine window MUST become reusable again), is cleared when a response completes on the same session key, and MUST NOT write account health or alter account selection.

A quarantine armed for reason `retry_circuit_poisoned_anchor` MUST NOT have that reason replaced by a weaker session-scoped fence while it is still active: the registry holds one entry per key, and the wedged-reattach and repeated-eventless fences carry no evidence about the anchor, so letting either overwrite the reason erases the only record that the anchor was proven dead.

The durable anchor abandonment MUST use the same capped threshold as the rest of this capability, in every funnel that can reach it. One poisoned anchor MUST be abandoned once per episode; a fenced or failed abandonment leaves it owed so the next strike retries — any next strike: the episode's owed poison class is recorded with it and MUST survive a later non-poison strike overwriting the durable failure detail, honored only against the exact reconciled lineage so a replaced row never inherits the stale owed state — and every funnel whose abandonment confirms MUST record the episode marker even while its circuit settlement remains outstanding, because the next strike finds empty continuity and cannot retry a settlement-only debt. The marker MUST reset whenever a durable load adopts a write this worker did not produce, so a replacement episode arriving at an equal or higher failure count is still allowed its one abandonment. The owed poison debt is carried by the durable row itself: an at-threshold poison detail MUST be sticky in the strike merge against non-poison overwrites — only a reset, settle, supersession, or another poison-class strike may change it — because counts and epochs cannot distinguish same-lineage advancement from a reset-and-overtaken replacement, and the sticky detail is what every replica re-derives the debt from; the process-local owed record still dies with every foreign write and re-arms from the adopted row. The process-local debt arms only when the recording strike is at or over the threshold: a below-threshold poison strike owes nothing yet, and a clean opener MUST NOT resurrect its detail into an owed clear against an episode that reached the threshold on non-poison evidence. Every funnel MUST derive its settlement from the failed request and the pending survivors snapshotted at decision time; none may settle unconditionally. An abandonment is owed only while its failure episode is still the registered one: a circuit settled by a concurrent success ends the episode, and a stale strike's captured count MUST NOT clear the fresh anchor that success persisted. An abandonment is also owed only while continuity actually remains: a durable session whose continuity columns are all empty owes nothing, because a clear there removes no failure cause, and the settle it authorized would reset a circuit cooling on genuinely unanchored failures. The continuity clear itself MUST be fenced on both continuity columns — the response anchor and the turn state — captured together when the episode was validated, and a completion MUST adopt any durable-only circuit row before capturing its quarantine fence and pre-settle poison detail — the settle's own load would otherwise arm a quarantine the already-captured fence can never clear, and a failed registration would find no detail to re-seed — and a completion MUST settle the circuit before it registers its fresh anchor, so a clear authorized against the poisoned anchor matches nothing once fresh continuity exists. When that settlement fails and the old episode is restored, the completion MUST NOT clear the quarantine, and the restored episode's owed abandonment MUST be suppressed as a transitional fence applied before the fresh anchor is published — a concurrent consult whose continuity read lands after publication would otherwise validate the old poison row and fence its rebind on the anchor just registered, deleting it — and that suppression MUST be rolled back when the registration then fails, restoring the owed clear so the old poisoned anchor is never left stored with no funnel willing to clear it — restored only onto the exact captured episode and lineage, since a state replaced or reconciled during the registration owns the key and never inherits the ended lineage's owed evidence; the cooldown stands until the next settle opportunity. A later poison-class strike recorded over the supersession sentinel MUST reset the one-clear marker: it is evidence against the freshly registered anchor and begins a new abandonment story of its own. The transitional suppression applies only to episodes carrying poison evidence — a clean episode owes no abandonment, and marking it would refuse the clear a later poison strike genuinely owes. That suppression MUST also be persisted by rewriting the surviving row's failure detail to a non-poison anchor-superseded class under the row's version fence — the local marker protects only its own worker, and another replica loading the surviving at-threshold poison row would otherwise arm quarantine against the fresh anchor and authorize an abandonment for failures recorded against the superseded one. The rewrite MUST NOT charge a failure or advance the row's version, so a concurrent strike merges onto the row in either order and its poison class outranks the supersession; a failed or outraced rewrite leaves the suppression process-local. Its fence MUST carry the observed failure count alongside the version, because a lagging-clock strike merges without moving the version while every landed merge increments the count — the count is what makes a strike that slipped in ahead of the rewrite outrank it. The fence MUST also carry the expected prior detail, forward and back: two completions can otherwise both believe they own the supersession of one shared row, and the loser's rollback would destroy the winner's, re-poisoning a freshly registered anchor; with the detail in the fence exactly one write owns each transition. A retired request that still holds a safe replay MUST NOT strike the circuit or trigger the abandonment on any funnel, matching the terminal and grouped paths. A request whose response has started holds no replay — the retry path refuses to dispatch one for it — so it MUST NOT block a settlement either, or the circuit is left cooling for its full backoff after a successful abandonment, protecting a replay that can never run; started means a counted response event or the deferred-reasoning prelude evidence that deliberately leaves the event count at zero. A funnel that drains or finalizes its requests before its settlement decision MUST carry the drained states into that decision — as a frozen snapshot when finalization empties the container it was handed — so a drained safe-replay holder still blocks the settle; only a handoff with genuinely no request states keeps striking. A completed verified stale-anchor replay MUST keep the source key's circuit and its durable row, and the one-clear marker on that surviving episode is process-local (see this change's `design.md` for the accepted tradeoff).

A quarantine armed for reason `retry_circuit_poisoned_anchor` MUST remain in force for at least the remaining cooldown of the circuit that armed it plus that circuit's half-open lease, because the probe it exists to protect is only admitted once that cooldown expires and may then be admitted anywhere inside the lease that follows. A suppression that assumes a remote half-open lease MUST be driven only by a confirmed dispatch-claim loss — a durable CAS that answered and matched nothing — never by a claim that timed out or errored, which is infrastructure trouble no probe owns. The quarantine registry's size cap MUST NOT evict such an entry before that deadline: the cap evicts only expired or weaker-fence entries and holds as a correctness bound rather than an unconditional one during an incident that quarantines more keys than the cap at once. The default TTL alone MUST NOT be relied on for this: it equals the circuit's maximum cooldown, so at that cooldown the quarantine would otherwise lapse in the same instant the cooldown does and hand the poisoned anchor back to the very request the cooldown was holding.

#### Scenario: Reattach streams events but response.created is never assigned (#1534)

- **GIVEN** a durable HTTP bridge session with a stored anchor whose fresh reattach injected a proxy-owned `previous_response_id`
- **AND** the reattached upstream stream delivers response events but `response.created` is never assigned
- **WHEN** the stream fails or the session is retired with that request still pending
- **THEN** the request fails terminally as before
- **AND** the session key is quarantined with reason `reattach_missing_response_created`

#### Scenario: All-stale direct retirement still quarantines the key

- **GIVEN** a wedged reattach (proxy-injected `previous_response_id`, `response.create` sent, response events observed, `response.created` never assigned) that is the ONLY stale pending request on its session
- **WHEN** the stuck-gate watchdog retires the session directly instead of failing the stale holder individually
- **THEN** the session key is quarantined with reason `reattach_missing_response_created`
- **AND** the next request takes the fresh no-anchor path instead of rebuilding the identical anchored reattach

#### Scenario: Next request after the wedge completes on the fresh path

- **GIVEN** a session key quarantined after a reattach that streamed events without `response.created`
- **WHEN** a later request arrives for the same key with a verified safe full-conversation-resend payload and no client `previous_response_id`
- **THEN** the proxy does not inject the durable anchor for that request
- **AND** the request is sent upstream unanchored with the client's own full payload
- **AND** the request can complete normally instead of rebuilding the identical wedged reattach

#### Scenario: Safe fresh resend does not rehydrate a suppressed anchor

- **GIVEN** a quarantined session key and a full-conversation-resend payload whose stored durable prefix is trimmable and whose fresh suffix retains the prior output or exactly matches the pending tool-call manifest
- **WHEN** the fresh-reattach durable-anchor injection is skipped because of the quarantine
- **THEN** the durable anchor is not rehydrated into the fresh session's completed-response state
- **AND** the session-level injection does not re-add the same anchor or trim the stored prefix
- **AND** the dispatch goes upstream genuinely unanchored with the client's untrimmed payload
- **AND** the suppression applies even when the fresh-reattach injection was already ineligible for other reasons (for example a conversation-scoped payload, a live alias session, or an active-owner forward that falls back to a local rebind)

#### Scenario: Incomplete fresh resend is refused before dispatch

- **GIVEN** a quarantined session key and a cumulative resend without an explicit client anchor
- **AND** its stored durable prefix is trimmable but its fresh suffix omits the prior output and does not exactly match the pending tool-call manifest
- **WHEN** the proxy plans recovery from the durable anchor
- **THEN** the request fails with `bridge_previous_response_not_found` before upstream dispatch
- **AND** the incomplete payload is not sent unanchored without the context its anchor provides

#### Scenario: A poison quarantine outlives the cooldown that armed it

- **GIVEN** repeated eventless poison-class failures have driven a hard-affinity circuit to its maximum cooldown
- **WHEN** the quarantine is armed with reason `retry_circuit_poisoned_anchor` at that same instant
- **THEN** the quarantine window extends past the cooldown deadline by at least the circuit's half-open lease
- **AND** the probe admitted once that cooldown expires is still planned without the poisoned anchor

#### Scenario: Quarantined session is excluded from reuse selection

- **GIVEN** a session marked quarantined that is still live or retained for admission handoff
- **WHEN** a new request looks up that session key
- **THEN** the session is not considered reusable
- **AND** the request proceeds on a fresh session instead
- **AND** a replacement session created under the same still-quarantined key is likewise not reusable until a completion or the TTL clears the quarantine

#### Scenario: Repeated eventless timeouts quarantine the key

- **GIVEN** a session key whose pending request already retired once with the eventless `missing_response_created_timeout`
- **WHEN** a subsequent attach on the same key retires with the same eventless timeout before any response completes on the key
- **THEN** the session key is quarantined with reason `repeated_eventless_timeout`
- **AND** the first timeout alone does not quarantine the key

#### Scenario: Deferred-reasoning live turn is never quarantined

- **GIVEN** an owned live turn whose `response.created` was observed and whose events flow with long gaps (deferred reasoning)
- **WHEN** its stream later fails or its session is retired
- **THEN** the session key is not quarantined
- **AND** later requests keep the existing reuse and anchor-injection behavior

#### Scenario: Delta-only payloads keep their anchor while quarantined

- **GIVEN** a quarantined session key — including one whose quarantined session is still open with other active requests
- **WHEN** a later request arrives whose payload does not look like a full conversation resend
- **THEN** the still-open quarantined session counts as absent for durable-anchor selection
- **AND** the durable anchor is still injected for that request, preserving the client's only way to convey prior context

#### Scenario: Quarantine is bounded and self-clearing

- **GIVEN** a quarantined session key
- **WHEN** a response completes on that session key, or the quarantine TTL elapses
- **THEN** the quarantine (and its eventless strike counter) is cleared
- **AND** a session that survived the quarantine window is reusable again instead of staying rejected forever
- **AND** no durable row, janitor work, or account-health write was involved at any point

#### Scenario: Retry circuit opened by eventless failures quarantines the key

- **GIVEN** a hard-affinity bridge key whose retry circuit has one recorded eventless `stream_incomplete` failure
- **WHEN** a second eventless `stream_incomplete` failure opens the circuit
- **THEN** the session key is quarantined with reason `retry_circuit_poisoned_anchor`
- **AND** a subsequent verified safe full-resend request on that key is dispatched unanchored through the existing fresh path
- **AND** a subsequent delta-only request on that key still receives the durable anchor

#### Scenario: Retry circuit opened by clean closes leaves the key unquarantined

- **GIVEN** a hard-affinity bridge key whose retry circuit has one recorded `clean_close` failure
- **WHEN** a second `clean_close` failure opens the circuit
- **THEN** the session key is not quarantined
