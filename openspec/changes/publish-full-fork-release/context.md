# Stable fork distribution

The maintainer explicitly requested replacing the GitHub beta release with a
normal stable release, English notes, PyPI publication, and the same Docker
and Helm distribution channels as upstream. This authorizes the fork's manual
stable tag release; no 48-hour production soak is claimed.

The fork continues to use `codexLB-up` on PyPI, `codex-lb` as its executable,
`ghcr.io/lok3rn3t/codexlb-up` for Docker, and
`oci://ghcr.io/lok3rn3t/charts/codex-lb` for Helm. The stable workflow rebuilds
artifacts with version 1.25.0 instead of retagging beta package bytes. The old
GitHub prerelease is removed only after its replacement is published.

Container smoke checks use isolated data and no provider accounts. They prove
packaged startup and dashboard availability, not live upstream inference or
production-scale operation.

Pre-publication validation: version consistency, Actionlint, Bash syntax, strict
OpenSpec validation, frontend build, Twine, and an installed-wheel smoke passed.
Deployment regressions: 76 Helm tests and 26 Docker-related tests passed.
Both architecture runtime checks are executed by the release workflow before
PyPI and GitHub publication; their result is required before archival.
