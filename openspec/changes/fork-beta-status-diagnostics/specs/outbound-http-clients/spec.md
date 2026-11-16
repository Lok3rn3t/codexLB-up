## ADDED Requirements

### Requirement: Native WebSocket receive failure logs safe provenance

When the native upstream WebSocket adapter receives a typed failure, it MUST
log the failure phase and classified error code without logging the underlying
exception text, credentials, or frame contents. It MUST preserve the existing
downstream error and account-health classification.

#### Scenario: Native transport receive fails

- **WHEN** the native helper reports a transport-phase receive failure
- **THEN** the operator log records `phase=transport` and the safe error code
- **AND** the underlying exception text is not logged
