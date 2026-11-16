## Why

The maintainer requested a stable release with English notes and the original
project's distribution channels: PyPI, multi-platform Docker images, Helm, and
GitHub Release. The first fork prerelease only published Python packages.

## What Changes

- Prepare version 1.25.0 across release-managed metadata.
- Enable Docker and Helm publishing for this fork, with fork image defaults.
- Verify container startup and bundled assets before publishing release metadata.
- Publish English installation instructions for all distribution channels.

## Impact

Release workflow, distribution/deployment metadata, operator documentation, and
packaging checks. The application fixes remain those already validated in beta.10.
