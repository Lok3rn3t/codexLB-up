## ADDED Requirements

### Requirement: Native WebSocket consumers control upstream reads

The adapter MUST require `websocket_receive_credit_v1` before dispatch. Each socket MUST allow only one unconsumed data message across IPC. The helper MUST pause upstream reads when its receive credit is exhausted and resume after Python returns credit. Accepted frames MUST NOT be discarded on consumer delay or helper exit. Local send, close, cancellation and sibling operations MUST remain available during the pause. Pausing MUST NOT produce a pong timeout caused by the locally paused reader. Concurrent receives MUST serialize credit ownership. Cancellation MUST finish a dispatched credit return within the existing command timeout before propagating, and ambiguous dispatch failure MUST terminate that socket without replaying credit. An unavailable native permit MUST fail the socket without panicking the helper.

#### Scenario: Fast upstream and slow consumer

- **WHEN** upstream sends more than 64 data messages while the consumer pauses
- **THEN** the consumer receives every message in order after resuming
- **AND** no consumer-backpressure terminal replaces the response

#### Scenario: Paused socket does not block peers or shutdown

- **WHEN** one socket has exhausted receive credit
- **THEN** another socket can receive and acknowledge sends
- **AND** the paused socket can close or cancel without draining its data

#### Scenario: Credit return is interrupted

- **WHEN** cancellation or a dispatch failure interrupts credit return
- **THEN** the adapter never dispatches duplicate credit
- **AND** successful dispatch preserves the next message while ambiguous failure closes only that socket

### Requirement: Native WebSocket diagnostics exclude arbitrary text

Native relay failures and logs MUST retain an allowlisted failure phase, numeric close code when supplied, and counts of data events and UTF-8 text or binary payload bytes received from that socket. Counters MUST exclude IPC metadata and control frames. Missing close codes MUST remain unknown. Unknown phase values MUST be rendered as `unknown`. Arbitrary exception text and peer close reasons MUST NOT be added to public failure messages or diagnostic logs. Consumer-backpressure and helper failures MUST remain account-neutral and distinguishable from remote transport errors.

#### Scenario: Failure after data

- **WHEN** native egress fails after delivering data to the relay
- **THEN** the client-visible disconnect detail and log contain the safe phase, close code and socket payload counters
- **AND** private data embedded in exception or close-reason text is absent from both
