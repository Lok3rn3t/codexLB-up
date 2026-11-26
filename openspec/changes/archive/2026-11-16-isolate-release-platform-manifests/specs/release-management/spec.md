## ADDED Requirements

### Requirement: Release checks isolate executable platform manifests

The release workflow SHALL resolve the built immutable image index to exactly
one executable child manifest for each required architecture, linux/amd64 and
linux/arm64. Attestation manifests SHALL NOT be selected as executable images.
Missing or ambiguous required platforms or malformed manifest digests SHALL
fail resolution. Startup smoke checks SHALL pull and run each architecture by
its distinct immutable child reference. The original beta.9 upgrade and existing
image vulnerability gates SHALL use the resolved amd64 child. Alias promotion
SHALL retain the original multiarchitecture index after all required gates pass.

#### Scenario: Both architectures are resolved from one index

- **GIVEN** a built image index contains amd64, arm64, and attestation descriptors
- **WHEN** release checks resolve executable platform references
- **THEN** each smoke check pulls and runs its matching immutable child manifest
- **AND** the amd64 upgrade and vulnerability gates use the same resolved amd64 child
- **AND** promotion retains both architectures and attestations in the parent index

#### Scenario: A required platform cannot be resolved uniquely

- **GIVEN** an image index lacks a required architecture or has ambiguous executable descriptors
- **WHEN** release checks resolve executable platform references
- **THEN** resolution fails before container checks and release promotion

### Requirement: Release runtime checks use native architecture runners

Each executable release architecture SHALL pass startup smoke checks on a runner
with the same native CPU architecture. Both native checks SHALL succeed before
image upgrade validation, vulnerability gates, alias promotion, PyPI publication,
and GitHub Release creation can proceed. Runtime smoke assertions and bounded
readiness waits SHALL remain enforced on both architectures.

#### Scenario: Native ARM64 startup is verified independently

- **GIVEN** the release build has produced both immutable executable manifests
- **WHEN** amd64 and arm64 startup checks run
- **THEN** amd64 runs on an x64 runner and arm64 runs on an ARM64 runner
- **AND** failure of either architecture prevents image promotion and final publication
