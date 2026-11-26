## ADDED Requirements

### Requirement: Release smoke checks tolerate bounded startup connection errors

The release container readiness probe SHALL retry transient connection errors,
including connection resets, within a bounded startup window. A failed readiness
probe SHALL fail the smoke check, report container logs, remove the temporary
container, and prevent subsequent in-container validation from running.

#### Scenario: the listening socket resets a request during startup

- **GIVEN** the release image has been pulled and its container is starting
- **AND** an initial readiness request is reset by the peer
- **WHEN** a later request succeeds within the startup window
- **THEN** the smoke check continues with its application and native-worker checks
- **AND** removes the temporary container when validation finishes

#### Scenario: readiness cannot be established

- **GIVEN** a temporary release container has been created
- **WHEN** the readiness probe exhausts its retry budget
- **THEN** the smoke check exits unsuccessfully
- **AND** prints container logs and removes the container
- **AND** does not execute the remaining validation commands
