## Source and design

The user selected the official Codex mapping at
https://github.com/openai/codex/blob/ca21fe65d18a9b6326759fb4263c65dfbb645aa5/codex-rs/tui/src/subscription.rs#L11-L39.
It deliberately distinguishes status labels from broader analytics labels.
In particular, `business` displays as Enterprise in status, while
`self_serve_business_prolite` displays as Business Premium.

Account `plan_type` already supports opaque strings, so a redundant raw field or
database migration is unnecessary. Canonicalization for metadata preserves the
normalized spelling of the Business Premium identifier. Policy normalization
continues mapping it to the existing `prolite` category for capacity estimates,
model eligibility, rate-limit projection and coarse telemetry. Identity checks
must compare those policy categories, maintaining all existing workspace fences
and confirmed-downgrade behavior.

Existing `prolite` rows are ambiguous. They remain Pro 100 until a fresh accepted
upstream metadata observation supplies the Business Premium identifier. Historical
logs are not rewritten. Existing capacity estimates are retained, not asserted to
be authoritative allowances for the differently named subscriptions.

All user-facing account labels use status mode. Analytics mode is an explicit
formatter option and does not alter telemetry grouping or routing policy.
