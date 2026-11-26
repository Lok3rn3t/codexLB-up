## Why

`dwnmf/codex-lb` uses an IP allowlist and middleware to protect its proxy routes. The React migration left `Soju06/codex-lb` without that firewall.

Restore the API and its middleware so operators can manage the allowlist in the React dashboard and the backend can enforce it.

## What Changes

- Add a backend firewall module with a CRUD API for IP allowlist entries at `/api/firewall/ips`.
- Apply the allowlist to the protected proxy routes under `/backend-api/codex/*` and `/v1/*`.
- Add settings to resolve the client IP from headers supplied by proxies in trusted CIDR ranges.
- Add a `/firewall` page and a navigation link so operators can manage the allowlist.
- Add a database migration for the allowlist table.
- Cover the API contract with backend unit, integration, and frontend tests.

## Capabilities

### Added Capabilities

- `api-firewall` manages the IP allowlist and enforces it on proxy endpoints.

### Modified Capabilities

- `frontend-architecture` adds the Firewall page to the router and navigation.

## Impact

- Backend changes affect `app/core/config/settings.py`, `app/core/middleware/*`, `app/db/models.py`, `app/db/alembic/versions/*`, `app/modules/firewall/*`, `app/dependencies.py`, and `app/main.py`.
- Frontend changes affect `frontend/src/App.tsx`, `frontend/src/components/layout/app-header.tsx`, and `frontend/src/features/firewall/*`.
- Backend and frontend unit and integration tests cover the firewall.
