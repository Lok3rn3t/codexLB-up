# Fork release

The user requested a GitHub prerelease and a separately named PyPI package for
Lok3rn3t/codexLB-up. The upstream `codex-lb` namespace must remain independent.
The first fork candidate is `v1.25.0-beta.10` (`1.25.0b10` on PyPI).

The Trusted Publisher configuration is GitHub owner `Lok3rn3t`, repository
`codexLB-up`, workflow `release.yml`, environment `pypi`. Package-name
normalization follows Python packaging rules; import packages and console
commands retain their established names. Installing both distributions into
one Python environment would overlap their `app` module and commands, so use
an isolated environment or `uvx --from codexLB-up==1.25.0b10 codex-lb`.

The two frontend failures found during release validation are unchanged
upstream assertions with US-formatted numeric literals. Expected strings must
use the same locale-sensitive formatting contract as the existing UI.

The fork's default branch is `codexLB-up`. This initial fork release uses an
explicit version tag and OIDC publishing, without the upstream
`RELEASE_PLEASE_TOKEN` setup. Inherited release-please automation and container
publishing jobs are restricted to the upstream repository. The CI push trigger
tracks the fork branch, while the inherited `main` branch remains available.
The fork-specific distribution guide is the package's PyPI long description.

Validation uses local release-tooling regressions, the installed wheel and its
packaged migrations/static assets, frontend build/lint, and workflow lint.
Provider traffic and Nix builds are outside this release verification.

Observed verification: 68 release-tooling tests passed; 26 telemetry tests
passed; both locale-sensitive UI suites passed (12 tests); frontend build and
lint passed. Fork wheel/sdist passed Twine, included 84 JS and one CSS asset,
and the installed-wheel smoke passed migrations, CLI, health, and static routes.
Actionlint passed for all changed workflows. The complete frontend suite is
also rerun after the assertion fixes, with its result recorded in release notes.

## Stable release and original beta.9 upgrade

The stable 1.25.0 flow extends the first prerelease to Docker amd64/arm64 and
Helm publishing for this fork. Image promotion requires startup smoke checks,
the Trivy severity gate, and an upgrade check from the immutable upstream beta.9
image. PyPI and GitHub publication follow the required image/chart checks.

The user explicitly requested an additional README migration block. A short
Quick Start subsection links to the full backup, cutover and rollback procedure
in `docs/distribution.md`. The original data mount and encryption key must stay
together; the database engine and PostgreSQL version do not change.

The original `codex-lb==1.25.0b9` schema predates three inherited revisions.
All 261 original revision files remain unchanged. A local isolated upgrade
using the verified published source preserved common-column contents across
67 retained tables, including encrypted credentials, password/TOTP, API keys,
settings and history. The container gate separately exercises both real images
and a subsequent restart on one disposable volume without external networking.
The removed subscription-overflow storage is an intentional upstream retirement;
the old app cannot safely restart against the upgraded schema. Rollback must
use the old image and pre-upgrade backup. Disabling schema migrations causes
the expected older-schema startup refusal; stamping or replacing the database
is not an upgrade workaround.

The real Docker upgrade and restart check passed on `c8ac36d7` in
CI job `133185472572`. Its evidence was preserved locally before the maintainer
requested removal of the old Actions runs; subsequent CI reruns the same gate.
This confirms the original beta.9 image-to-fork transition on disposable Linux
amd64 SQLite data; no production database was accessed or modified.

## Platform-specific release checks

One Docker runner can reject a second architecture pulled under the same index
digest with `cannot overwrite digest`. Release checks resolve the built index
using `docker buildx imagetools inspect --raw`, then load each executable child
by its own digest. For example, amd64 and arm64 smoke checks use distinct
`repository@sha256:...` references even though both belong to one release index.
The amd64 child also feeds the upgrade and vulnerability checks. Missing or
ambiguous platforms fail resolution; attestation descriptors are excluded from
execution but retained when the complete parent index is promoted.

Docker documents the index and attestation descriptor shapes in its
[imagetools inspect reference](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/).
