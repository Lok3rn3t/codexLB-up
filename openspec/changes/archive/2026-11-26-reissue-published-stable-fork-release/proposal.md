# Reissue an existing stable fork release

## Why

The fork distributes the stable wheel from GitHub Releases. An image security update requires rebuilding an existing version across GitHub and GHCR.

## What Changes

- Verify the matching public stable release before an explicit GitHub-only rebuild.
- Run package, Docker, native smoke, upgrade, security, and Helm checks for the rebuilt artifacts.
- Point the stable installation command at the wheel attached to that release.

## Impact

- Affected spec: release-management
- Affected code: release workflow and metadata validation
