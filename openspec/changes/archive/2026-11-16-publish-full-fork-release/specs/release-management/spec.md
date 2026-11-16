## MODIFIED Requirements

### Requirement: Fork release tags publish Python packages independently

Tag pushes and manual dispatches SHALL verify release versions and publish
the fork's Python distribution, Docker images, and Helm chart using the fork's
registries. The GitHub Release SHALL publish only after all required channels
succeed. Stable tags SHALL publish stable aliases and a non-prerelease GitHub
Release; prerelease tags SHALL remain prereleases. This flow SHALL NOT require
upstream release-please credentials.

#### Scenario: a beta tag publishes the fork

- **GIVEN** tag `v1.25.0-beta.10` identifies consistent fork version metadata
- **WHEN** the Release workflow completes successfully
- **THEN** PyPI contains `codexLB-up` version `1.25.0b10`
- **AND** GitHub contains a prerelease with wheel and source distribution
- **AND** the installation instructions select the fork distribution

#### Scenario: a stable tag publishes the complete fork release

- **GIVEN** tag `v1.25.0` identifies consistent fork version metadata
- **WHEN** the Release workflow completes successfully
- **THEN** PyPI contains `codexLB-up` version `1.25.0`
- **AND** GHCR contains the fork image for Linux amd64 and arm64 with a `latest` alias
- **AND** the Helm chart defaults to the fork image
- **AND** GitHub contains a stable release with English installation instructions

## ADDED Requirements

### Requirement: Release containers pass startup smoke checks

Published container images SHALL be smoke-tested for each released architecture
before GitHub release metadata is published. Checks SHALL verify the application
version, bundled native egress executable, startup migrations, health endpoint,
and bundled dashboard. Failed container checks SHALL fail the release workflow.

#### Scenario: a released container starts with a fresh database

- **GIVEN** a built fork image for a released architecture
- **WHEN** the container starts with an isolated empty data directory
- **THEN** its health endpoint and dashboard become available
- **AND** its application version matches the release tag
- **AND** its native egress executable is present and runnable
