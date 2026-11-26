## 1. Backend firewall domain

- [x] 1.1 Add the IP allowlist table to the ORM and create an Alembic migration.
- [x] 1.2 Implement the schemas, repository, service, and API in `app/modules/firewall` using the existing typing conventions.
- [x] 1.3 Apply the firewall middleware only to protected proxy routes.
- [x] 1.4 Pass through the `firewall_trust_proxy_headers` and `firewall_trusted_proxy_cidrs` settings.
- [x] 1.5 Connect the firewall API router, middleware, and dependency injection in `main.py` and `dependencies.py`.

## 2. React dashboard integration

- [x] 2.1 Add the firewall schemas, API client, hooks, and components under `frontend/src/features/firewall`.
- [x] 2.2 Add the `/firewall` route and a Firewall link to the header.
- [x] 2.3 Let operators list, add, and remove IP addresses. Show loading and error states.

## 3. Tests

- [x] 3.1 Add or update backend unit tests for the firewall service and client IP resolution.
- [x] 3.2 Add backend integration tests for the firewall API and middleware enforcement.
- [x] 3.3 Test the frontend schemas, API client, hooks, and component interactions.

## 4. Spec delta

- [x] 4.1 Add the `api-firewall` spec delta.
- [x] 4.2 Update the `frontend-architecture` delta for routing and the Firewall page.
- [ ] 4.3 Run `openspec validate --specs`.
