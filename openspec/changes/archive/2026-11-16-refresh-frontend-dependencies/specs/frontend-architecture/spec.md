## ADDED Requirements

### Requirement: Dependency refreshes preserve frontend compatibility checks

Frontend dependency refreshes SHALL preserve translation of labels without interpolation values and SHALL keep unexpected requests rejected by the test mock server. The generated Nix dependency manifest SHALL agree with the committed Bun lockfile.

#### Scenario: translation has no interpolation values

- **WHEN** a label is translated without an options object
- **THEN** the translation wrapper supplies valid options for the installed i18next API
- **AND** the resulting label retains its existing translation

#### Scenario: a test sends an unmocked request

- **WHEN** a frontend test sends a request with no matching mock handler
- **THEN** the mock server treats it as an error
- **AND** does not silently bypass interception

#### Scenario: dependencies change

- **WHEN** the Bun lockfile is refreshed
- **THEN** regenerating `bun.nix` produces no difference from the committed file
