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

The cloud Docker check remains pending. It must use the actual pinned source
image, target normal entrypoint, shared disposable volume, no external network,
and a subsequent restart before this change is archived.
