# Scope and provenance

The source is the upstream `codex-lb==1.25.0b9` distribution, corresponding to
Docker tag `ghcr.io/soju06/codex-lb:1.25.0-beta.9`. Its immutable image index is
`sha256:093344377e618acab906a36a4ed23d23e4b2f0fd2882e38df545b170d4278832`.
The published source distribution SHA256 is
`bf690c012c9266608945a652df70da7d6cb53b25350a492627816eb0c77d67bb`.

The requested transition preserves the existing database engine and data. It
does not authorize changing the operator's deployed database or upgrading
PostgreSQL. The existing image entrypoint applies existing Alembic revisions by
default. This must be explained separately from changing database engines.

Example: stop the original container, back up its entire data directory including
`store.db` and `encryption.key`, and start the new image with the same mount and
configuration. Test data never contains real user credentials or provider calls.
An unknown or incompatible database must fail visibly rather than being stamped
as current or silently recreated. Rollback restores the pre-upgrade data before
the old image is restarted.

The user also explicitly requested a supplemental migration block in README.
The README therefore includes a short subsection under Quick Start, linked to
the complete procedure in `docs/distribution.md`; canonical requirements stay
in the release-management specification.

Exact source comparison found 261 unchanged existing revision files and three
additional inherited revisions: SCIM tokens, retired subscription-overflow
schema removal, and their merge. On a database created with the exact beta.9
source, disabling migrations fails at the expected older-head check. The normal
upgrade advances from `20260913_000000_add_oidc_provider_flow` to
`20260918_000000_merge_scim_and_overflow_heads`; policy and drift checks pass.
No new migration revision is necessary. The retired feature's storage is
explicitly excluded from the live-schema preservation claim, and rollback
requires the pre-upgrade backup because beta.9 still maps the removed columns.

Full container and seeded-data results are recorded after verification.
