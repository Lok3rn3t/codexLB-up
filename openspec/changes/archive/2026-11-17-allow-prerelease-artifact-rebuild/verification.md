# Replacement prerelease verification

## Source candidate

`466dd50df24110792eeb7addfdcc987e7dd3aeed` is the approved replacement
`v1.26.0-beta.1` source. It was fast-forwarded into the default branch after
[PR CI](https://github.com/Lok3rn3t/codexLB-up/actions/runs/43929436577) passed and
GitHub reported the PR merge state CLEAN with no open review threads. The
[default-branch CI](https://github.com/Lok3rn3t/codexLB-up/actions/runs/43931597100)
also passed. Independent review found a cancellation cleanup race, fixed and
regression-tested before these runs.

- Unit slice: 10,739 passed, 7 documented skips, 1 existing expected failure.
- Native wire probes: 374 passed, including the actual-worker flow-control tests.
- All integration, PostgreSQL, frontend, migration, packaging, Rust, Docker,
  Helm, Nix, lint, type, OpenSpec and required CI gates passed.
- Metadata CLI tests: 41 passed locally; stable tags reject skip-PyPI.

## Publication

The owner explicitly approved replacing the existing GitHub/Docker/Helm beta.1
publication while omitting PyPI. The original source commit and image digest are
retained in the authored release notes. The Release workflow was temporarily
disabled while updating the Git tag with an exact old-SHA lease, then re-enabled
before dispatch, so the automatic tag event could not upload the used PyPI
filenames. Only one replacement Release run was started.

[Release run](https://github.com/Lok3rn3t/codexLB-up/actions/runs/43931611565)
confirmed `is_prerelease=true`, `make_latest=false`, and `publish_pypi=false`.
The publication completed successfully; PyPI was intentionally skipped.

No command, download, installation or restart was performed on the production
server or its container during this implementation/publication work.

## Published artifacts

Release: https://github.com/Lok3rn3t/codexLB-up/releases/tag/v1.26.0-beta.1

- Source tag and both image revision labels: `466dd50df24110792eeb7addfdcc987e7dd3aeed`.
- Multiarchitecture index and beta alias: `sha256:963df6fa6a3d541c48e67002fb0e646f683f68e05ea01be61776ce6c44926bf4`.
- Stable latest stayed at `sha256:0a0fbe93ce48c93aec673f955748a9c34c8f0674189656470a74978e4b9d508c`.
- linux/amd64: `sha256:ed3e60ca65163c77431ed5b135d42b707d7b8ebc278b3d5281cb327fddbf764d`.
- linux/arm64: `sha256:f64bf0d057ca65bfbe9cfbf736c2cb09140a4e1934cfaf4bed050940ab35f050`.

Native amd64 and arm64 startup, original beta.9 upgrade, and image vulnerability
gates passed. GitHub reports a published prerelease with all four expected assets.
The downloaded wheel contains receive-credit/cleanup and context-snapshot code
and bundled dashboard assets. Wheel, source archive and chart checksums match
SHA256SUMS.txt. The OCI Helm layer also matches the GitHub chart checksum.

- wheel SHA-256: `53147f21243c0c48ccffbcd3b0e3cc9af6476549ba57efa463d8ad4fc0d40e1b`.
- sdist SHA-256: `ffc6b2e0a0e821fafb99f68dca088b15a143a95c7b0416355b9219adccc745c4`.
- helm SHA-256: `3470e19976673e71c4980ce21b76bc4e517689e7b728f243baf70a083a1be8de`.
