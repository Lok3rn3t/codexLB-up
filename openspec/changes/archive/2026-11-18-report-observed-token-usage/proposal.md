# Report observed token usage

## Why

Partial token usage is summed differently by request logs and dashboard metrics,
and missing measurements can look like an exact zero. Subscription credit totals
are derived from static plan capacities although upstream reports percentages
and a separate credit balance. Users need observable quantities with explicit
limits, rather than invented exact token allowances.

## What Changes

- Make request and activity totals use the same non-duplicating token arithmetic.
- Expose completeness for recorded usage and distinguish missing data from zero.
- Show upstream quota percentages and credit balances; do not present static
  plan-derived subscription quantities as authoritative available tokens/credits.
- Account for terminal failed/incomplete responses when upstream reports actual
  token usage, preserving reservation idempotency and unknown-usage behavior.
- Keep confirmed totals separate from estimates and make the timing of updates
  clear. No synthetic exact live count or fabricated token allowance is added.

## Impact

Local backend and frontend behavior, additive dashboard contracts and tests.
No deployment, release, production diagnostics, or historical usage invention.
Existing account identity and subscription label work is preserved.
