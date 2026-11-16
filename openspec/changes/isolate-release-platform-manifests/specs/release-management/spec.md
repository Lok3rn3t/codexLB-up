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

#### Scenario: Both architectures are checked on one Docker daemon

- **GIVEN** a built image index contains amd64, arm64, and attestation descriptors
- **WHEN** release checks resolve executable platform references
- **THEN** each smoke check pulls and runs its matching immutable child manifest
- **AND** the amd64 upgrade and vulnerability gates use the same resolved amd64 child
- **AND** promotion retains both architectures and attestations in the parent index

#### Scenario: A required platform cannot be resolved uniquely

- **GIVEN** an image index lacks a required architecture or has ambiguous executable descriptors
- **WHEN** release checks resolve executable platform references
- **THEN** resolution fails before container checks and release promotion
