## ADDED Requirements

### Requirement: Fork distribution identity is independent from upstream

The fork SHALL publish its Python distribution as `codexLB-up` while retaining
the `codex-lb` and `codex-lb-db` console commands. Release version preparation
and guards SHALL locate the editable lockfile distribution using the normalized
project name from the same revision's `pyproject.toml`. Generated release
installation commands and the PyPI publishing environment URL SHALL identify
the fork distribution.

#### Scenario: the fork prepares a new beta

- **GIVEN** the project name is `codexLB-up` and its normalized lockfile entry is `codexlb-up`
- **WHEN** beta preparation updates release-managed versions
- **THEN** it updates the fork's editable package entry
- **AND** all version guards accept consistent fork metadata

#### Scenario: release guards compare historical upstream metadata

- **GIVEN** a base revision uses project name `codex-lb`
- **AND** the current revision uses project name `codexLB-up`
- **WHEN** release guards compare version fields
- **THEN** each revision's lockfile package is resolved from its own project metadata
- **AND** a name change cannot hide an inconsistent release version

### Requirement: Fork release tags publish Python packages independently

Tag pushes and manual dispatches SHALL verify versions, build the frontend
and Python packages, publish using the `pypi` environment, and create a GitHub
Release after PyPI publication succeeds. Prerelease tags SHALL remain
prereleases. Fork publication SHALL NOT require upstream container publishing
or release-please credentials.

#### Scenario: a beta tag publishes the fork

- **GIVEN** tag `v1.25.0-beta.10` identifies consistent fork version metadata
- **WHEN** the Release workflow completes successfully
- **THEN** PyPI contains `codexLB-up` version `1.25.0b10`
- **AND** GitHub contains a prerelease with wheel and source distribution
- **AND** the installation instructions select the fork distribution

### Requirement: Fork CI follows the default branch

The fork SHALL use `codexLB-up` as its default branch and SHALL run CI and
release guards on pushes to that branch.

#### Scenario: default branch receives a commit

- **GIVEN** `codexLB-up` is the repository default branch
- **WHEN** a new commit is pushed to that branch
- **THEN** the CI and release guard workflows are eligible to run
