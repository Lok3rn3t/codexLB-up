## MODIFIED Requirements

### Requirement: WebSocket full-resend previous-response misses retry without stale anchor
When a direct WebSocket `response.create` request includes both `previous_response_id` and a self-contained full resend payload, the service MUST retain a safe replay body without `previous_response_id`. If upstream rejects the anchor with `previous_response_not_found` before `response.created`, the service MUST reconnect and replay the retained full payload as a fresh turn instead of forwarding the raw upstream invalid-request error. A payload that only carries incremental tool outputs for tool calls that are not also present in the same request is not self-contained and MUST NOT be replayed as a fresh turn without `previous_response_id`.

A client-supplied `previous_response_id` payload counts as a full resend only when the anchor is the response this downstream connection last completed, that response's request input covered its whole context (it had no anchor, a proxy-injected anchor, or was itself a proven full resend), and the payload's input restates that stored input prefix. A completion recorded from a client-anchored delta stores only the delta, so it never proves a later anchorless replay. Clients such as Codex send `previous_response_id` with only the incremental input, so for any other anchor (one this connection never completed, such as an interrupted response, an accepted prewarm, or a response from an earlier connection) the service cannot tell a delta from a full history. It MUST NOT retain or send an anchorless replay body for such a payload, and a pre-output continuity miss MUST reach the client through the existing route-specific recovery contract: sanitized `previous_response_not_found` for native Codex, or `stream_incomplete` for public `/v1/responses`.

#### Scenario: full-resend WebSocket follow-up loses just-completed anchor
- **WHEN** a WebSocket `/v1/responses` or `/backend-api/codex/responses` follow-up has `previous_response_id`
- **AND** that anchor is the response this connection last completed
- **AND** the request payload restates that response's stored input prefix, so it carries enough input to be treated as a full resend
- **AND** upstream emits `previous_response_not_found` before assigning a response id
- **THEN** the service reconnects the upstream WebSocket
- **AND** it replays the same request without `previous_response_id`
- **AND** the downstream client receives the recovered response events, not the raw `previous_response_not_found` error

#### Scenario: output-only WebSocket tool delta is not replayed as a fresh turn
- **WHEN** a WebSocket `/v1/responses` or `/backend-api/codex/responses` follow-up has `previous_response_id`
- **AND** the request payload carries `function_call_output`, `custom_tool_call_output`, or `apply_patch_call_output` items without their matching tool-call items in the same payload
- **AND** upstream emits `previous_response_not_found` before assigning a response id
- **THEN** the service MUST NOT replay that payload as a fresh turn without `previous_response_id`
- **AND** the downstream client receives a retryable continuity failure rather than a fabricated fresh turn

#### Scenario: delta after an anchor the connection never completed is not replayed as a fresh turn
- **WHEN** a WebSocket `/v1/responses` or `/backend-api/codex/responses` follow-up has `previous_response_id`
- **AND** that anchor is not the response this connection last completed (for example a response that ended `response.incomplete`, an accepted `generate=false` prewarm, or a response from another connection)
- **AND** the request payload is self-contained but carries only the turn's new items, such as a user message
- **THEN** the service MUST NOT retain an anchorless replay body for that request
- **AND** if upstream emits `previous_response_not_found` before assigning a response id, the downstream client receives the route-specific retryable continuity failure rather than a fresh turn built from the new items alone

#### Scenario: restated delta of a client-anchored completion is not replayed as a fresh turn
- **WHEN** a WebSocket `/v1/responses` or `/backend-api/codex/responses` follow-up has `previous_response_id`
- **AND** that anchor is the response this connection last completed, but that response's request was itself anchored by the client and carried only a delta
- **AND** the follow-up input restates that delta and adds new items
- **THEN** the service MUST NOT retain an anchorless replay body for that request
- **AND** if upstream emits `previous_response_not_found` before assigning a response id, the downstream client receives the route-specific retryable continuity failure rather than a fresh turn that omits the earlier context

## ADDED Requirements

### Requirement: Durable same-owner context proof accepts agent-message follow-ups

For a prefix-verified durable HTTP bridge full resend, the service SHALL accept
well-formed `agent_message` items as fresh same-owner input after retained
completed assistant output, or after a complete direct tool-call/output suffix
that exactly settles the durable prior-response manifest. Agent messages MUST
NOT substitute for missing prior output, missing tool calls, or missing tool
outputs. Unknown or malformed agent-message shapes MUST NOT authorize replay.

The fresh bridge and bounded explicit stale-anchor recovery paths SHALL retain
the original input items and their order, including reasoning and encrypted
agent-message content, while omitting the stale `previous_response_id`.
The request MUST remain pinned to the proven durable account and MUST fail
closed if that account is unavailable. This proof MUST NOT make an agent-message
payload eligible for account-neutral replay or relax existing operation fences,
replay limits, or the ban on replay after visible response output.

#### Scenario: Subagent message follows a settled tool loop on a replacement socket
- **GIVEN** the full input matches the durable stored prefix and settles every call in its manifest
- **AND** a new agent message follows those tool outputs
- **WHEN** the client resumes on a fresh HTTP bridge
- **THEN** the original full input is sent to the durable owner without a previous-response anchor
- **AND** encrypted content and item identifiers are preserved

#### Scenario: Same owner explicitly rejects the anchor
- **GIVEN** a prefix-verified full resend containing a valid agent follow-up
- **WHEN** upstream rejects its anchor before any response output
- **THEN** the existing fenced one-shot replacement sends the original full input without the rejected anchor to the same owner

#### Scenario: Agent message cannot cover incomplete history
- **GIVEN** a resend omits a manifest call or its output, lacks a known manifest and retained assistant output, or contains a malformed agent message
- **WHEN** the bridge verifies same-owner context
- **THEN** the agent message does not authorize unanchored replay

#### Scenario: Unavailable owner cannot move encrypted agent context
- **GIVEN** a full resend passes the same-owner proof and contains an agent message
- **WHEN** its durable owner is unavailable
- **THEN** no alternate account receives the request


### Requirement: Idle upstream loss invalidates the Codex downstream transport
When an ordinary Codex WebSocket upstream ends after completed work and there are no pending or replay-owned requests, the proxy MUST close the downstream with reconnect code 1012 and retire only the continuity anchor belonging to that physical upstream. It MUST NOT silently attach a later delta to a new physical upstream. Durable account ownership MUST remain unchanged. Active request termination and public OpenAI-compatible WebSocket behavior MUST retain their existing contracts.

#### Scenario: Completed upstream disappears
- **WHEN** an upstream closes or fails after a completed Codex response with no pending request
- **THEN** the downstream receives close code 1012 before a subsequent turn
- **AND** a full-context reconnect does not receive an injected anchor from the lost socket

#### Scenario: Preparation overlaps the idle close
- **WHEN** a new turn is received but request preparation or admission has not completed when the idle close commits
- **THEN** that turn MUST NOT be dispatched upstream after the downstream reconnect notification
- **AND** its reservation and admission ownership MUST be finalized

#### Scenario: Another connection owns the newer anchor
- **WHEN** an idle upstream ends after another connection has established the shared continuity anchor
- **THEN** the newer connection's anchor remains intact

#### Scenario: Active work or public route
- **WHEN** an upstream ends while work is pending, replay-owned, or on the public OpenAI-compatible route
- **THEN** its existing terminal and replay behavior is preserved
