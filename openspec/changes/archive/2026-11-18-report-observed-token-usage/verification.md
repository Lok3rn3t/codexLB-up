# Verification - 2026-11-18

## Backend

- 220 tests passed, one platform-specific `tzset` test skipped on Windows across
  request-log APIs, dashboard, conversations, account usage/folding, builders,
  account service and observed usage regressions.
- 196 API-key coverage, API and service tests passed.
- 37 native terminal settlement integration and 27 focused unit tests passed.
  New database regressions failed before the fix (4 failed / 26 passed) and
  pass after it, including actual nonzero and zero usage on failure, incomplete
  usage release, repeated settlement and cancellation ownership.
- Ruff check/format, `ty check app` and `git diff --check` passed on the affected
  backend changes.

These checks use synthetic accounts and local test databases. They do not prove
provider-wide billing reconciliation, full physical-attempt accounting on compact
retries, or recovery of missing historical token observations.

## Frontend and specification

- 172 targeted frontend tests covered token completeness, exact lower-bound
  formatting, quota percentages, request/account/conversation displays, API-key
  coverage and legacy preferences. Three stale compact-format assertions were
  updated and their 36-test subset rerun successfully.
- TypeScript project checking, ESLint over `src`, production Vite build and
  frontend diff checking passed. After visual review made unknown quota tracks
  neutral rather than depleted red, the account-card (13) and list (15) suites,
  scoped lint and production build passed again.
- Playwright preview used only synthetic fixtures. Cards and list view show
  reported quota percentages and purchased credits, with no synthetic Subscription
  column. Request rows distinguish 150 complete, at least 130 partial, unavailable,
  and measured zero. The overview shows at least 280 with coverage 2/1/1/0.
  Evidence is in the chat workspace at `output/playwright/token-usage-before.png`,
  `token-usage-after.png` and `token-usage-list-after.png`.
- Independent review covered raw/folded arithmetic, deduplication, coverage and
  quota units; no unresolved blocking finding remained. Compact physical-attempt
  accounting remains the explicit design limitation above.
- The active change passed strict OpenSpec validation. Canonical specs were synced
  during archive and all 68 passed strict validation after filling the generated
  purpose section. Browser console showed no errors or warnings.

## Operational boundary

No release, deployment, commit or push was performed for this change. The existing
subscription-label patch is preserved. Separate remote diagnostics used only
read-only state/log inspection and did not alter the server or container.

## Release preparation follow-up

After publication was requested, GitHub's browser smoke test exposed a Node ESM
import failure: API schemas imported the usage formatter, which initialized
browser i18n and loaded JSON locales without Node import attributes. The same
failure was reproduced locally through Playwright test discovery. Moving the
coverage schema and its inferred type into `src/schemas/token-usage.ts` keeps
API validation independent of browser formatting. Discovery now lists all eight
existing browser smoke tests; 92 affected formatter/schema/overview tests,
TypeScript checking and scoped ESLint passed. Full hosted acceptance remains a
release gate for the final commit.
