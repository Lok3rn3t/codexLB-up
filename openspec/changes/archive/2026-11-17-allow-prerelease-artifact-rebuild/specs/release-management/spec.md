## ADDED Requirements

### Requirement: Explicit prerelease rebuild can omit PyPI

A manually dispatched prerelease publication MAY explicitly skip PyPI upload.
The metadata validator MUST reject this option for a stable release. Normal
publication MUST continue to require PyPI success. An explicitly skipped PyPI
job MUST permit GitHub prerelease creation only after Docker, Helm, metadata
and their build and verification dependencies succeed. Release instructions
MUST omit PyPI installation commands when that publication was skipped.

#### Scenario: Withdrawn prerelease is rebuilt for container users

- **GIVEN** a manual dispatch explicitly skips PyPI for a prerelease tag
- **WHEN** all required artifact and runtime checks succeed
- **THEN** Docker, Helm and GitHub prerelease artifacts are published
- **AND** no Python distribution is uploaded to PyPI or advertised as uploaded

#### Scenario: Stable publication cannot bypass PyPI

- **WHEN** a manual dispatch requests skipping PyPI for a stable tag
- **THEN** release metadata validation fails before publication

#### Scenario: Ordinary release retains its publication gate

- **WHEN** a publication does not explicitly skip PyPI
- **THEN** GitHub Release creation still requires successful PyPI publication
