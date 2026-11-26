# Verification — 2026-11-18

Baseline: fork HEAD `a0fa5e09408cce11734316905616cde592f137b2`.
Mapping source: OpenAI Codex `ca21fe65d18a9b6326759fb4263c65dfbb645aa5`,
`codex-rs/tui/src/subscription.rs`; `hc`/`education` wire aliases are defined in
`codex-rs/protocol/src/auth.rs` at the same commit.

## Regression evidence

Before the backend patch, the new scoped regression selection produced
6 failures and 9 passes; after the patch all 15 passed. Failures reproduced
identity loss through import/API/usage refresh and incorrect fallback capacity.
The frontend dashboard regression failed on `Prolite` instead of `Pro 100`
before implementation and passed after it.

## Passed checks

- 632 backend tests across test_plan_types, test_usage, test_usage_updater,
  test_load_balancer, test_auth_manager, integration test_accounts_api and
  test_oauth_flow. These cover same-slot fresh Business identity recovery,
  legacy personal records, mismatched workspace refusal, confirmed free
  downgrade, OAuth/token refresh and fallback routing.
- 152 affected frontend tests covered across eight suites (149 initial passes,
  then 44 passes in the two suites expanded with three more regressions).
  Includes exact status/analytics mappings, rendered dashboard/account labels,
  search/selection and historical request row/detail labels.
- Backend Ruff check/format and ty on changed runtime files.
- Frontend TypeScript, ESLint on changed files and production Vite build.
- Strict OpenSpec change validation and all 67 canonical specs.
- Independent code review found no blocking issue; git diff --check passed.

The frontend checks used the existing Node 24.22.1 runtime because system
Node 22.13 fails during jsdom/undici initialization before tests start.
Dependencies and lock files were not changed.

## Visual verification

Local Playwright preview with synthetic accounts verified Business Premium,
Pro 100, Business and Enterprise in the dashboard list and displayed-label
search on Accounts. Before/after captures are local scratch evidence at
`work/plan-labels-before.png` and `work/plan-labels-after.png` relative to the
chat workspace. The before capture uses the prior built frontend and collapsed
Business metadata; the after capture supplies the restored upstream identifier.
No production account data or credentials are included in these fixtures.

No server/container changes, release publication, or historical row rewrite
were performed. Existing ambiguous rows require a future accepted upstream
refresh to acquire a more specific subscription identifier. Full release CI
was not run; this is a verified local patch, not a new published image.
