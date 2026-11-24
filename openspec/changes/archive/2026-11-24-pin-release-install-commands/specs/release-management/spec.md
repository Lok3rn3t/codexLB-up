## ADDED Requirements

### Requirement: Release installation commands select the published artifacts

For each GitHub Release, the generated install commands SHALL select the fork's Docker image and Helm chart at the exact release version. When Python packages are published, the uvx command SHALL pin the distribution to the PEP 440 version supplied by release metadata. A release that skips PyPI SHALL omit the Python command.

#### Scenario: Install from a stable release page after a newer release appears

- **GIVEN** a stable release with tag `v1.27.0` and published Python packages
- **WHEN** a reader follows the installation commands from that release
- **THEN** the Python requirement is `codexLB-up==1.27.0`
- **AND** the image and Helm chart use `1.27.0`

#### Scenario: Install from a prerelease page

- **GIVEN** a release with tag `v1.27.0-beta.1`
- **WHEN** the release notes are generated
- **THEN** Docker and Helm select `1.27.0-beta.1`
- **AND** Helm permits prerelease versions
- **AND** the notes include `codexLB-up==1.27.0b1` only when PyPI publication was enabled
