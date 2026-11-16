## Why

The multiarchitecture release build succeeded, but pulling the same immutable
index first as amd64 and then as arm64 failed in the runner's Docker image store
with `cannot overwrite digest`. The amd64 application smoke passed; arm64 never
started. Retrying the same index reference cannot repair this local collision.

## What Changes

- Resolve each required executable architecture to its immutable child manifest.
- Use distinct child references for startup smoke checks and the amd64 reference
  for the original beta.9 upgrade and existing vulnerability gates.
- Reject missing or ambiguous platform descriptors before running containers.
- Preserve the complete parent index, including attestations, for alias promotion.

## Impact

Release tooling only. Application behavior, migration files, data storage and
production deployment are unchanged. All existing release gates remain required.
