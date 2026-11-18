## MODIFIED Requirements

### Requirement: Merged beta release PRs publish GitHub prereleases

When a pull request from the same repository's `release/beta-*` branch is merged into the repository's default branch, the release automation SHALL verify that all release-managed version files agree on a beta version, require release-candidate validation evidence for the exact merged pull request head SHA, verify that the published merge commit tree matches that validated head tree, create the matching `vX.Y.Z-beta.N` tag at the merge commit, and dispatch the Release workflow once at that tag with the same tag input. The fork SHALL pass `skip_pypi=true` and the upstream repository SHALL retain PyPI publication. The publisher SHALL use the repository's `GITHUB_TOKEN` for tag creation and workflow dispatch. The dispatched workflow SHALL create the GitHub prerelease only after the required artifact checks succeed. Re-running the workflow after the tag already exists SHALL be safe and SHALL NOT create a second tag. Before merge, the beta release guard SHALL require release-candidate validation evidence for canonical `release/beta-X.Y.Z-beta.N` pull requests whose checked-out tree already contains the matching beta version, even when the release-managed version files are unchanged relative to the base branch.

#### Scenario: beta PR merge publishes a prerelease tag

- **GIVEN** a merged pull request in the fork from `release/beta-1.19.0-beta.1`
- **AND** release-managed files all contain `1.19.0-beta.1`
- **AND** the pull request body contains checked release-candidate validation evidence for the exact merged pull request head SHA
- **AND** the merge commit tree matches the validated pull request head tree
- **WHEN** the beta publish workflow runs
- **THEN** it creates tag `v1.19.0-beta.1` at the merge commit
- **AND** it dispatches Release for that tag with PyPI skipped
- **AND** the successful artifact workflow publishes the GitHub prerelease, Docker image, and Helm chart

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

#### Scenario: Retry after the tag exists

- **GIVEN** the validated beta merge already has its expected tag
- **WHEN** a maintainer retries the publish workflow
- **THEN** the workflow verifies the tag resolves to the exact merge commit before requesting publication
- **AND** a tag pointing at a different commit causes the workflow to fail before dispatch

#### Scenario: Upstream beta publication retains PyPI

- **WHEN** the upstream repository dispatches Release for a validated merged beta
- **THEN** the dispatch targets the matching tag and passes `skip_pypi=false`
