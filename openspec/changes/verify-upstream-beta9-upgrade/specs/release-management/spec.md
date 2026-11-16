## ADDED Requirements

### Requirement: Original beta.9 container upgrade compatibility

The distribution SHALL verify the upgrade from the original `codex-lb==1.25.0b9`
Docker image using an immutable source image reference and disposable SQLite data
created by that source image. The target image SHALL start through its normal
entrypoint with the same data mount and encryption key. The verification SHALL
cover encrypted account credentials, API keys and their account assignments,
dashboard authentication and settings, usage history, and request history. The
verification SHALL fail on data loss, unreadable credentials, schema drift, or
unhealthy startup. It SHALL also verify a subsequent restart. CI and release
image promotion SHALL require this check to pass.

#### Scenario: Replace the original image while preserving existing data

- **GIVEN** the pinned original beta.9 image has created a populated SQLite volume
- **WHEN** the target image starts with that volume using the existing migration path
- **THEN** the original records and encryption key are preserved and credentials remain decryptable
- **AND** schema checks and application readiness succeed before and after restart
- **AND** the upgrade does not change the database engine

### Requirement: Single-container upgrade instructions

The distribution SHALL document a single-container upgrade that preserves the
existing mounts, environment, published ports, and networks. The instructions
SHALL require a consistent backup of existing data and the encryption key before
cutover, explain that normal startup may update the existing database schema,
and provide rollback using the old image and pre-upgrade backup. An operator
prohibiting schema changes SHALL be able to keep startup migrations disabled;
the instructions SHALL explain that incompatible schemas then prevent startup.

#### Scenario: Existing Docker deployment switches distributions

- **GIVEN** an operator runs the original beta.9 image through `docker run`
- **WHEN** the operator follows the upgrade instructions
- **THEN** only the application image is replaced and the previous configuration and persistent data are retained
- **AND** a backup made before schema updates is available for rollback
- **AND** no PostgreSQL major-version conversion is required or started
