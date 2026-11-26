## ADDED Requirements

### Requirement: Injected WebSocket anchor coverage belongs to the selected completion

When direct WebSocket preparation injects a stored response anchor, the service
MUST snapshot that anchor's context coverage before the next asynchronous
operation. The prepared request and its completed continuity record MUST inherit
that snapshot. A completion recorded from a client-anchored delta MUST NOT become
proof of complete context merely because its response ID was injected by the
proxy. Concurrent updates to session continuity MUST NOT replace the coverage of
the anchor already selected for the request.

#### Scenario: Injection preserves incomplete context across a completed turn
- **WHEN** a client-anchored delta completes and the proxy injects its anchor into a matching follow-up
- **AND** that follow-up completes
- **THEN** a later explicitly anchored resend of that stored prefix remains ineligible for anchorless replay
- **AND** an upstream continuity miss reaches the native client as sanitized `previous_response_not_found`

#### Scenario: Admission overlaps another completion
- **WHEN** a request selects an anchor and asynchronous admission updates shared continuity to another completion
- **THEN** the prepared request retains the original selected anchor's coverage

#### Scenario: Complete context remains complete
- **WHEN** the selected anchor was recorded from complete context
- **THEN** the injected request retains complete coverage and existing safe full-resend recovery remains available
