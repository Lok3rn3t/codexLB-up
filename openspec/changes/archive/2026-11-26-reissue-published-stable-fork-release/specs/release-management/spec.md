## MODIFIED Requirements

### Requirement: Explicit prerelease rebuild can omit PyPI

A manually dispatched prerelease publication MAY explicitly skip PyPI upload.
For a stable release the fork MAY accept this option only on manual dispatch after verifying that the same tag already has a public stable GitHub Release. Normal
publication MUST continue to require PyPI success. An explicitly skipped PyPI
job MUST permit GitHub publication only after Docker, Helm, metadata
and their build and verification dependencies succeed. Release instructions
MUST omit PyPI installation commands when that publication was skipped.

#### Scenario: Withdrawn prerelease is rebuilt for container users

- **GIVEN** a manual dispatch explicitly skips PyPI for a prerelease tag
- **WHEN** all required artifact and runtime checks succeed
- **THEN** Docker, Helm and GitHub prerelease artifacts are published
- **AND** no Python distribution is uploaded to PyPI or advertised as uploaded

#### Scenario: First stable publication requires PyPI

- **WHEN** a manual dispatch requests skipping PyPI for a stable tag without a matching published stable release in the fork
- **THEN** release metadata validation fails before publication

#### Scenario: An existing stable fork release is reissued

- **GIVEN** the fork has a public stable GitHub Release for the exact tag
- **WHEN** a maintainer dispatches a rebuild with PyPI explicitly skipped
- **THEN** the wheel, source distribution, Helm chart and verified multi-platform image are rebuilt from the tag
- **AND** the release page gives an install command for its GitHub-hosted wheel

#### Scenario: Ordinary release retains its publication gate

- **WHEN** a publication does not explicitly skip PyPI
- **THEN** GitHub Release creation still requires successful PyPI publication

### Requirement: Release installation commands select the published artifacts

For each GitHub Release, the generated install commands SHALL select the fork's Docker image and Helm chart at the exact release version. When Python packages are published, the uvx command SHALL pin the distribution to the PEP 440 version supplied by release metadata. A prerelease that skips PyPI SHALL omit the Python command. A stable fork rebuild that skips PyPI SHALL link the wheel from that GitHub Release.

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
