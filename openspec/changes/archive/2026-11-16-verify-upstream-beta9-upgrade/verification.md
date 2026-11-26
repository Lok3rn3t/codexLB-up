# Verification

- Verified PyPI source hash and original GHCR image index digest.
- Compared migration history: 261 unchanged source revisions, three inherited additions.
- Created a populated database with the exact beta.9 source. On its copied
  database, the fork's normal migration command completed with no schema drift.
- Compared all common columns across 67 retained tables; values matched.
- Verified unchanged encryption key, OAuth token/TOTP decryption, bcrypt
  password, API-key ownership/scope, settings and usage/request history.
- Ran the committed fixture through source seed/source verify/target upgrade/
  target verify; all passed. These local runs use source subprocesses, not Docker.
- Scoped Ruff, formatting, Ty, Bash syntax, actionlint, strict documentation
  build and README simplicity budgets passed.

The actual cloud Docker check passed on commit
`c8ac36d7044372e8f1c48eca702e6ed508955d63` in CI job `133185472572`.
It used the pinned original image and a loaded target image on Linux amd64 with
one disposable volume and no external network. Source verification, target
verification, and target verification after restart all passed. The same Docker
job's Trivy gate passed. The overall CI run separately found one HTTP bridge
test failure; that is outside this upgrade check and must be resolved before
the stable release.

The maintainer subsequently requested removal of all 15 existing Actions runs.
Run metadata and this job's logs were preserved locally before that cleanup.
The upgrade check remains required in subsequent CI and release runs.
