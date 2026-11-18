## Why

The dashboard can expose excessive precision in a quota forecast while rounding away small differences between measured account balances. Long identities compete with percentages in narrow cards. Large token totals take up space, and long plan badges can obscure the next request-log column.

## What Changes

- Show up to two decimal places in quota percentages. Give the forecast its own label and make account rows readable at compact widths.
- Abbreviate large token totals in the overview. Keep the exact recorded count available and identify incomplete totals as lower bounds.
- Keep plan labels inside their request-log cells, including after resizing the column.
- Restore the account list's sortable subscription-credit estimate alongside reported quota percentages and purchased credits.

## Capabilities

### Modified Capabilities

- `account-quota-presentation` governs the precision of measured percentages and forecasts.
- `frontend-architecture` governs the quota cards, token summary and request-log layout.

## Impact

Dashboard rendering and its regression coverage change. Existing overview and request-log responses supply the values.
