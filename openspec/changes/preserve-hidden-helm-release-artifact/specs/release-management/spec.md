## ADDED Requirements

### Requirement: Packaged Helm release artifact is required

The release workflow SHALL upload the packaged Helm chart even when its selected
path is inside a hidden build directory. A missing chart file SHALL fail the
upload job. The GitHub Release SHALL contain the chart archive and its SHA-256
checksum alongside the Python distribution artifacts.

#### Scenario: Chart package is written inside a hidden directory

- **GIVEN** Helm packaging creates the versioned chart archive in `.helm-pkg`
- **WHEN** the workflow uploads its chart artifact
- **THEN** the selected archive is included and can be downloaded by the release job
- **AND** absence of the archive fails the upload rather than producing a successful empty job
