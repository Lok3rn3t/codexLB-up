## Why

The operator already runs the original `codex-lb==1.25.0b9` Docker image and
needs to replace it with this distribution without losing accounts, credentials,
dashboard configuration, API keys, or usage history. A fresh-container smoke test
does not exercise an existing upstream database.

## What Changes

- Add an upgrade check using the immutable upstream beta.9 image and a temporary
  SQLite volume containing representative encrypted account and dashboard data.
- Run the target image against that existing volume through its normal entrypoint,
  then verify data preservation, schema compatibility, readiness, and restart.
- Gate CI and release image promotion on that upgrade check.
- Document the single-container cutover, backup, and rollback procedure.

## Impact

Release verification and operator instructions. Preserve the existing database
engine and Alembic migration history; no PostgreSQL upgrade or new schema revision
is introduced. Tests use generated credentials and disposable data only.
