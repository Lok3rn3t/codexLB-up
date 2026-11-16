# release-management Specification

## Purpose
Governs the release channels of codex-lb: the stable path owned by release-please and the PR-driven beta channel layered on it. Beta releases must be prepared through release PRs, publish as GitHub prereleases on merge, never advance stable aliases or the stable manifest, and withdraw public release metadata when publishing fails, so stable promotion stays release-please owned and every release-managed version field is guarded.

## Requirements

### Requirement: Beta releases are prepared through release PRs

Beta releases SHALL be prepared by an automatically maintained pull request against `main` that updates the release-managed version files to `X.Y.Z-beta.N`. The beta preparation flow SHALL run after release-please completes and after pushes to `main`, SHALL derive `X.Y.Z` from the open release-please PR branch, and SHALL do nothing when there is no open release-please PR. Beta release PRs SHALL NOT update `.github/release-please-manifest.json` because stable version ownership remains with release-please.

#### Scenario: automation syncs the next beta from the release-please PR

- **GIVEN** release-please has opened or updated `release-please--branches--main` with `pyproject.toml` version `1.19.0`
- **WHEN** the beta PR sync workflow runs
- **THEN** it creates or updates a pull request that sets release-managed files to `1.19.0-beta.N`
- **AND** `N` is one higher than the highest existing `v1.19.0-beta.N` tag
- **AND** `.github/release-please-manifest.json` remains unchanged

#### Scenario: automation is idle without a release-please PR

- **GIVEN** there is no open release-please PR targeting `main`
- **WHEN** the beta PR sync workflow runs
- **THEN** it exits without creating a beta release pull request

#### Scenario: automation ignores forked release-please branch names

- **GIVEN** a fork has an open pull request whose head branch is named `release-please--branches--main`
- **WHEN** the beta PR sync workflow looks for the release-please PR
- **THEN** it ignores that pull request unless the head repository owner is the canonical repository owner
- **AND** it requests enough open pull requests to avoid missing the canonical release-please PR during high-PR-volume periods

#### Scenario: merged beta release already covers main

- **GIVEN** tag `v1.19.0-beta.1` points to `HEAD`
- **AND** release-managed files all contain `1.19.0-beta.1`
- **WHEN** the beta PR sync workflow runs for base version `1.19.0`
- **THEN** it exits without creating `1.19.0-beta.2`

#### Scenario: automation-generated beta PR starts unvalidated

- **GIVEN** the beta PR sync workflow creates or updates `release/beta-1.20.0-beta.3`
- **WHEN** it writes the pull request body
- **THEN** the body includes a `Release-candidate validation` section
- **AND** the section records the exact beta PR head SHA as the validated candidate placeholder
- **AND** backend, frontend, wheel/package, Docker/container, and live upstream/account smoke checklist items start unchecked

### Requirement: Merged beta release PRs publish GitHub prereleases

When a pull request from a `release/beta-*` branch is merged into `main`, the release automation SHALL require `RELEASE_PLEASE_TOKEN` rather than falling back to `GITHUB_TOKEN`, verify that all release-managed version files agree on a beta version, require release-candidate validation evidence for the exact merged pull request head SHA, verify that the published merge commit tree matches that validated head tree, create the matching `vX.Y.Z-beta.N` tag at the merge commit, and publish a GitHub prerelease for that tag. Re-running the workflow after the tag already exists SHALL be safe and SHALL NOT create a second tag. Before merge, the beta release guard SHALL require release-candidate validation evidence for canonical `release/beta-X.Y.Z-beta.N` pull requests whose checked-out tree already contains the matching beta version, even when the release-managed version files are unchanged relative to the base branch.

#### Scenario: beta PR merge publishes a prerelease tag

- **GIVEN** a merged pull request from `release/beta-1.19.0-beta.1`
- **AND** release-managed files all contain `1.19.0-beta.1`
- **AND** the pull request body contains checked release-candidate validation evidence for the exact merged pull request head SHA
- **AND** the merge commit tree matches the validated pull request head tree
- **AND** `RELEASE_PLEASE_TOKEN` is configured
- **WHEN** the beta publish workflow runs
- **THEN** it creates tag `v1.19.0-beta.1` at the merge commit
- **AND** it creates a GitHub prerelease for `v1.19.0-beta.1`

#### Scenario: inconsistent release metadata is blocked

- **GIVEN** a pull request changes one or more release-managed version files
- **AND** the release-managed files do not all contain the same version
- **WHEN** the CI beta release guard runs
- **THEN** it fails before deciding whether the change is stable or beta
- **AND** it reports the mismatched release-managed file versions

#### Scenario: canonical beta PR with unchanged metadata still requires validation

- **GIVEN** `main` already contains release-managed files set to `1.20.0-beta.3`
- **AND** a pull request from `release/beta-1.20.0-beta.3` targets `main`
- **WHEN** the beta release guard evaluates the pull request before merge
- **THEN** it requires release-candidate validation evidence for the pull request head SHA
- **AND** it fails while that evidence is missing, even though the release-managed version files are unchanged relative to `main`

### Requirement: Prerelease artifacts do not advance stable aliases

The release publishing workflow SHALL accept both stable tags (`vX.Y.Z`) and prerelease tags (`vX.Y.Z-alpha.N`, `vX.Y.Z-beta.N`, `vX.Y.Z-rc.N`). For prerelease tags, Docker publishing SHALL NOT update `latest`, `X`, or `X.Y` aliases, and the GitHub Release SHALL remain marked as a prerelease and not latest. Stable tags SHALL retain existing stable aliases and latest-release behavior.

#### Scenario: beta release publishes beta-only Docker tags

- **GIVEN** release tag `v1.19.0-beta.1`
- **WHEN** the release publishing workflow builds the Docker image
- **THEN** it publishes the exact version tag `1.19.0-beta.1`
- **AND** it MAY publish channel tag `beta`
- **AND** it MUST NOT publish or update `latest`, `1`, or `1.19`

### Requirement: Stable release promotion remains release-please owned

A beta-tested release train SHALL be promoted by merging the normal
release-please stable release PR for the corresponding base version. Stable
promotion SHALL rebuild PyPI, Docker, Helm, and GitHub Release artifacts with
the stable version instead of retagging prerelease artifacts.

Before the stable release PR for `X.Y.Z` is merged, every change in the
release candidate SHALL either be covered by a `vX.Y.Z-beta.N` prerelease
that has been published and deployed to at least one production-scale
environment for a soak of at least 48 hours without new regressions
attributable to the release train, or fall under the safe-delta exception
below. The unsoaked delta — every change not covered by such a soaked
prerelease, whether because no prerelease of the train completed a soak or
because the change landed after the last soaked prerelease — qualifies for
the exception only when it consists solely of documentation, CI, or
release-tooling changes, an urgent security or outage hotfix, or a
combination of these; otherwise the train SHALL soak (again) as a new
prerelease before stable promotion. When promotion relies on the exception,
the exception and its reason SHALL be recorded on the stable release PR
before merge.

When the release train contains Alembic revisions, the maintainer SHALL review
the revisions between the previous stable tag and the release candidate
directly for data-backfill migrations and SHALL estimate their startup impact
against a production-scale dataset before merging the stable release PR.
Generated changelog titles SHALL NOT be treated as sufficient evidence that
the train contains no data backfills.

#### Scenario: beta train is promoted to stable

- **GIVEN** `v1.19.0-beta.2` was published from `main`
- **AND** release-please has prepared the stable release PR for `1.19.0`
- **WHEN** the stable release PR is merged
- **THEN** release-please creates the stable `v1.19.0` release
- **AND** the release publishing workflow publishes stable artifacts for `1.19.0`
- **AND** stable Docker aliases `latest`, `1`, and `1.19` are updated only by the stable release

#### Scenario: stable promotion waits for the beta soak

- **GIVEN** `v1.20.0-beta.1` was published 12 hours ago and is deployed on a
  production-scale environment
- **WHEN** a maintainer considers merging the stable release PR for `1.20.0`
- **THEN** promotion waits until the beta has soaked for at least 48 hours
  without new regressions attributable to the release train

#### Scenario: stable promotion without a soaked beta records an exception

- **GIVEN** no `v1.21.1-beta.N` prerelease has completed a 48-hour soak
- **AND** the entire delta since `v1.21.0` consists of an urgent security
  hotfix and CI changes only
- **WHEN** a maintainer merges the stable release PR for `1.21.1` with the
  exception and its reason recorded on the PR
- **THEN** the promotion is compliant with this requirement

#### Scenario: unrelated unsoaked changes cannot ride a hotfix exception

- **GIVEN** no `v1.22.0-beta.N` prerelease has completed a 48-hour soak
- **AND** the delta since the previous stable release contains an urgent
  hotfix alongside unrelated feature or migration changes
- **WHEN** a maintainer considers promoting `1.22.0` directly to stable
- **THEN** the hotfix exception does not apply to the train
- **AND** the train either soaks as a beta or the hotfix is released
  separately

#### Scenario: changes landing after the soaked beta restart the soak

- **GIVEN** `v1.23.0-beta.1` completed a 48-hour production-scale soak
- **AND** a feature or migration change lands on `main` afterwards, before
  the stable release PR for `1.23.0` is merged
- **WHEN** a maintainer considers promoting `1.23.0` to stable
- **THEN** the post-beta change is part of the unsoaked delta
- **AND** because a feature or migration change is not exception-eligible,
  promotion requires a new soaked prerelease covering it

#### Scenario: data backfills are identified from Alembic revisions

- **GIVEN** the release train adds revisions under `app/db/alembic/versions`
  since the previous stable tag
- **WHEN** the maintainer prepares to merge the stable release PR
- **THEN** they review those revisions directly for data-backfill operations
- **AND** changelog titles alone are not treated as evidence that no backfill
  is present

### Requirement: Stable release promotions guard every release-managed version field

Stable release promotion pull requests SHALL fail CI unless every release-managed version field agrees on the stable version and every field that previously held the prior release train version advances together. The guarded fields SHALL include `pyproject.toml`, `app/__init__.py`, `frontend/package.json`, both Helm chart version fields, and the editable `codex-lb` entry in `uv.lock`.

#### Scenario: release-please stable PR misses uv.lock

- **GIVEN** a beta-tested release train has release-managed files at `1.20.0-beta.3`
- **AND** a release-please stable PR changes `pyproject.toml`, `app/__init__.py`, `frontend/package.json`, and Helm chart versions to `1.20.0`
- **BUT** leaves `uv.lock` at `1.20.0-beta.3`
- **WHEN** CI evaluates the stable release guard
- **THEN** the guard fails before the PR can merge
- **AND** the failure identifies `uv.lock` as a release-managed version field that must be updated

#### Scenario: release-please stable PR updates all release-managed fields

- **GIVEN** a beta-tested release train has release-managed files at `1.20.0-beta.3`
- **WHEN** a release-please stable PR changes all release-managed version fields to `1.20.0`
- **THEN** the stable release guard passes

### Requirement: Failed release publishing withdraws public release metadata

If the Release workflow is triggered by a public GitHub Release event and any required publishing job fails, the workflow SHALL make that GitHub Release draft again before exiting. This prevents `/releases/latest` and dashboard update checks from advertising a version whose PyPI, Docker, or Helm artifacts are incomplete.

#### Scenario: stable release workflow fails before artifacts publish

- **GIVEN** GitHub Release `v1.20.0` was published and triggered the Release workflow
- **AND** the workflow fails before PyPI, Docker, and Helm artifacts are all published
- **WHEN** the failure cleanup job runs
- **THEN** the GitHub Release is changed back to draft
- **AND** the release no longer appears as the public latest release

### Requirement: Fork distribution identity is independent from upstream

The fork SHALL publish its Python distribution as `codexLB-up` while retaining
the `codex-lb` and `codex-lb-db` console commands. Release version preparation
and guards SHALL locate the editable lockfile distribution using the normalized
project name from the same revision's `pyproject.toml`. Generated release
installation commands and the PyPI publishing environment URL SHALL identify
the fork distribution.

#### Scenario: the fork prepares a new beta

- **GIVEN** the project name is `codexLB-up` and its normalized lockfile entry is `codexlb-up`
- **WHEN** beta preparation updates release-managed versions
- **THEN** it updates the fork's editable package entry
- **AND** all version guards accept consistent fork metadata

#### Scenario: release guards compare historical upstream metadata

- **GIVEN** a base revision uses project name `codex-lb`
- **AND** the current revision uses project name `codexLB-up`
- **WHEN** release guards compare version fields
- **THEN** each revision's lockfile package is resolved from its own project metadata
- **AND** a name change cannot hide an inconsistent release version

### Requirement: Fork release tags publish Python packages independently

Tag pushes and manual dispatches SHALL verify release versions and publish
the fork's Python distribution, Docker images, and Helm chart using the fork's
registries. The GitHub Release SHALL publish only after all required channels
succeed. Stable tags SHALL publish stable aliases and a non-prerelease GitHub
Release; prerelease tags SHALL remain prereleases. This flow SHALL NOT require
upstream release-please credentials.

#### Scenario: a beta tag publishes the fork

- **GIVEN** tag `v1.25.0-beta.10` identifies consistent fork version metadata
- **WHEN** the Release workflow completes successfully
- **THEN** PyPI contains `codexLB-up` version `1.25.0b10`
- **AND** GitHub contains a prerelease with wheel and source distribution
- **AND** the installation instructions select the fork distribution

#### Scenario: a stable tag publishes the complete fork release

- **GIVEN** tag `v1.25.0` identifies consistent fork version metadata
- **WHEN** the Release workflow completes successfully
- **THEN** PyPI contains `codexLB-up` version `1.25.0`
- **AND** GHCR contains the fork image for Linux amd64 and arm64 with a `latest` alias
- **AND** the Helm chart defaults to the fork image
- **AND** GitHub contains a stable release with English installation instructions

### Requirement: Fork CI follows the default branch

The fork SHALL use `codexLB-up` as its default branch and SHALL run CI and
release guards on pushes to that branch.

#### Scenario: default branch receives a commit

- **GIVEN** `codexLB-up` is the repository default branch
- **WHEN** a new commit is pushed to that branch
- **THEN** the CI and release guard workflows are eligible to run

### Requirement: Release smoke checks tolerate bounded startup connection errors

The release container readiness probe SHALL retry transient connection errors,
including connection resets, within a bounded startup window. A failed readiness
probe SHALL fail the smoke check, report container logs, remove the temporary
container, and prevent subsequent in-container validation from running.

#### Scenario: the listening socket resets a request during startup

- **GIVEN** the release image has been pulled and its container is starting
- **AND** an initial readiness request is reset by the peer
- **WHEN** a later request succeeds within the startup window
- **THEN** the smoke check continues with its application and native-worker checks
- **AND** removes the temporary container when validation finishes

#### Scenario: readiness cannot be established

- **GIVEN** a temporary release container has been created
- **WHEN** the readiness probe exhausts its retry budget
- **THEN** the smoke check exits unsuccessfully
- **AND** prints container logs and removes the container
- **AND** does not execute the remaining validation commands

### Requirement: Release containers pass startup smoke checks

Published container images SHALL be smoke-tested for each released architecture
before GitHub release metadata is published. Checks SHALL verify the application
version, bundled native egress executable, startup migrations, health endpoint,
and bundled dashboard. Failed container checks SHALL fail the release workflow.

#### Scenario: a released container starts with a fresh database

- **GIVEN** a built fork image for a released architecture
- **WHEN** the container starts with an isolated empty data directory
- **THEN** its health endpoint and dashboard become available
- **AND** its application version matches the release tag
- **AND** its native egress executable is present and runnable

### Requirement: Original beta.9 container upgrade compatibility

The distribution SHALL verify the upgrade from the original `codex-lb==1.25.0b9`
Docker image using an immutable source image reference and disposable SQLite data
created by that source image. The target image SHALL start through its normal
entrypoint with the same data mount and encryption key. The verification SHALL
cover encrypted account credentials, API keys and their account assignments,
dashboard authentication and settings, usage history, and request history. The
verification SHALL fail on data loss, unreadable credentials, schema drift, or
unhealthy startup. It SHALL also verify a subsequent restart. CI and release
image promotion SHALL require this check to pass.

#### Scenario: Replace the original image while preserving existing data

- **GIVEN** the pinned original beta.9 image has created a populated SQLite volume
- **WHEN** the target image starts with that volume using the existing migration path
- **THEN** the original records and encryption key are preserved and credentials remain decryptable
- **AND** schema checks and application readiness succeed before and after restart
- **AND** the upgrade does not change the database engine

### Requirement: Single-container upgrade instructions

The distribution SHALL document a single-container upgrade that preserves the
existing mounts, environment, published ports, and networks. The instructions
SHALL require a consistent backup of existing data and the encryption key before
cutover, explain that normal startup may update the existing database schema,
and provide rollback using the old image and pre-upgrade backup. An operator
prohibiting schema changes SHALL be able to keep startup migrations disabled;
the instructions SHALL explain that incompatible schemas then prevent startup.

#### Scenario: Existing Docker deployment switches distributions

- **GIVEN** an operator runs the original beta.9 image through `docker run`
- **WHEN** the operator follows the upgrade instructions
- **THEN** only the application image is replaced and the previous configuration and persistent data are retained
- **AND** a backup made before schema updates is available for rollback
- **AND** no PostgreSQL major-version conversion is required or started

### Requirement: Packaged Helm release artifact is required

The release workflow SHALL upload the packaged Helm chart even when its selected
path is inside a hidden build directory. A missing chart file SHALL fail the
upload job. The GitHub Release SHALL contain the chart archive and its SHA-256
checksum alongside the Python distribution artifacts.

#### Scenario: Chart package is written inside a hidden directory

- **GIVEN** Helm packaging creates the versioned chart archive in `.helm-pkg`
- **WHEN** the workflow uploads its chart artifact
- **THEN** the selected archive is included and can be downloaded by the release job
- **AND** absence of the archive fails the upload rather than producing a successful empty job

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
