## MODIFIED Requirements

### Requirement: Measurement timing is explicit

Displayed token counts SHALL update from reported upstream usage. The dashboard
overview MUST omit the refresh-timing explanation beneath the summary cards.
Usage displays MUST NOT claim that visible text deltas reveal hidden
reasoning, server-side context or cache counts. No character-to-token constant
SHALL be introduced as an authoritative live usage counter.

#### Scenario: Generation is still running
- **WHEN** the upstream stream has not supplied token usage
- **THEN** the interface does not present a fabricated exact usage count
