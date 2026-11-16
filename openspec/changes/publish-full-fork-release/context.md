# Stable fork distribution

The maintainer explicitly requested replacing the GitHub beta release with a
normal stable release, English notes, PyPI publication, and the same Docker
and Helm distribution channels as upstream. This authorizes the fork's manual
stable tag release; no 48-hour production soak is claimed.

The fork continues to use `codexLB-up` on PyPI, `codex-lb` as its executable,
`ghcr.io/lok3rn3t/codexlb-up` for Docker, and
`oci://ghcr.io/lok3rn3t/charts/codex-lb` for Helm. The stable workflow rebuilds
artifacts with version 1.25.0 instead of retagging beta package bytes. Existing
prerelease artifacts are independent of this stable build.

Container smoke checks use isolated data and no provider accounts. They prove
packaged startup and dashboard availability, not live upstream inference or
production-scale operation.

Pre-publication validation: version consistency, Actionlint, Bash syntax, strict
OpenSpec validation, frontend build, Twine, and an installed-wheel smoke passed.
Deployment regressions: 76 Helm tests and 26 Docker-related tests passed.
Both architecture runtime checks are executed by the release workflow before
PyPI and GitHub publication; their result is required before archival.

The maintainer requested preserving the database behavior. The release keeps
SQLAlchemy on the updated 2.0 series (`>=2.0.57,<2.1`) and leaves the original
Alembic environment, migration revisions, schema, and URL handling unchanged.
No deployed database is connected to or modified by this work. CI uses its
existing disposable databases to verify the unchanged migration contract.

Security checks include pip-audit of all locked runtime extras, cargo-deny,
Bun audit, and the upstream Trivy HIGH/CRITICAL gate. The runtime Docker build
updates zlib1g from the distribution security repository. The development-only
shadcn dependency still brings deepmerge 4.3.1, affected by the low-severity
GHSA-gcqx-w48m-w2h4 advisory; there is no patched published deepmerge version
at the time of this review. It is not part of the Python runtime or a server
dependency. Cloudflare skills were installed and reviewed as deployment
guidance; no Cloudflare account configuration was audited or changed.
