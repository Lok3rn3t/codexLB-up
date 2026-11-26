## Why

The maintainer requested current frontend dependencies for the 1.25.0 release.
The newer i18next and MSW versions require small compatibility migrations.

## What Changes

- Refresh the frontend dependency manifest, Bun lockfile, and generated Nix package data.
- Pass an empty options object to translations whose interpolation values are absent.
- Preserve strict handling of unmocked requests with MSW 3's `onUnhandledFrame` option.
- Assert legend background colors through the CSS color longhand so equivalent shorthand serialization does not change test results.

## Impact

Frontend dependency and test infrastructure only. Existing dashboard behavior and API contracts remain the acceptance criteria in `openspec/specs/frontend-architecture/spec.md`.
