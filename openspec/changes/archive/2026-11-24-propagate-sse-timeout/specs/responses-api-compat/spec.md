## ADDED Requirements

### Requirement: SSE keepalives propagate upstream read timeouts

The SSE keepalive iterator SHALL emit a heartbeat only when its own wait interval expires. It SHALL propagate a timeout raised by the upstream iterator, including after a previous heartbeat, and finalize the iterator.

#### Scenario: The source times out after a heartbeat

- **WHEN** a pending source read fails with a timeout while the consumer processes a heartbeat
- **THEN** the next read surfaces that upstream error and closes the iterator
