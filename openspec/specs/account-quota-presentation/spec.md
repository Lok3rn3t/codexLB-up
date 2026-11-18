# account-quota-presentation Specification

## Purpose
Governs how account quota windows are presented across the dashboard when an account does not fit the paid 5h/7d shape. Free accounts report a single monthly window, and rendering it as weekly produced wrong bars, trends, donut totals, and assigned-account badges. This capability keeps monthly-only accounts labelled as such, omits zero-credit accounts from window totals they cannot contribute to, and keeps quota refreshes visually stable.

## Requirements

### Requirement: Free-account quota surfaces are monthly-only

When an account's normalized quota model is monthly-only, account-facing quota surfaces SHALL present only the monthly window and MUST NOT render synthetic 5h or 7d bars for that account.

#### Scenario: Account surfaces show only monthly quota
- **WHEN** an account summary carries a normalized monthly quota window with no normalized 5h or 7d windows
- **THEN** the account card, account list row, and account detail usage panel show a single `Monthly` quota bar
- **AND** those surfaces do not render `5h` or `Weekly` bars for that account

### Requirement: Free-account overview quota hides 5h and 7d semantics

Overview and aggregate quota surfaces SHALL treat normalized monthly-only free-account quota as a 30d window and MUST NOT present that account as a weekly-only or dual-window account.

#### Scenario: Overview uses monthly semantics for free accounts
- **WHEN** overview data includes a free account with only a normalized monthly quota window
- **THEN** the overview account quota display shows only the 30d window for that account
- **AND** the account and API navigation progress logic uses monthly-only quota state for that account

### Requirement: Monthly quota remains visible in recent-trend displays

The account usage trend SHALL preserve the recent 7-day trend timeframe while identifying monthly-only quota lines as monthly quota.

#### Scenario: Monthly account trend labels the monthly line
- **WHEN** an account trend view renders a monthly-only free account
- **THEN** the trend legend identifies the quota line as `Monthly`
- **AND** the trend view still identifies itself as a 7-day trend

### Requirement: Account quota refreshes preserve visual continuity

Account-facing quota surfaces MUST keep an existing quota row mounted during
the bounded continuity hold when a refresh reports an unknown or non-finite
value, but MUST display the current measurement as unavailable instead of
presenting the retained percentage as current or substituting zero. The last
known value MAY be retained internally as the animation starting point. When
a later valid percentage arrives, the number and bar MUST ease to the new
value at 0.1 percent display resolution. Reduced-motion preferences MUST update
without animation. Raw sorting and routing percentages MUST remain unchanged.

#### Scenario: Temporary unknown value does not drain the bar
- **GIVEN** an account quota row displays a valid remaining percentage
- **WHEN** a refresh temporarily reports an unknown or non-finite percentage
- **THEN** the row remains mounted during the bounded continuity hold
- **AND** the value is shown as unavailable, not zero or a current stale percentage
- **AND** the prior value is retained only for a subsequent animation

#### Scenario: Fresh percentage replaces the held value smoothly
- **GIVEN** an account quota row has a retained valid percentage
- **WHEN** a later refresh reports a valid percentage
- **THEN** the display eases from the retained animation value to the new percentage
- **AND** the visible number can change in 0.1 percent increments
- **AND** the raw percentage used by sorting and routing is unchanged

#### Scenario: Reduced motion skips the transition
- **GIVEN** the user prefers reduced motion
- **WHEN** a fresh valid percentage replaces an unavailable or valid measurement
- **THEN** the quota surface displays the fresh percentage without animation

### Requirement: Account labels follow Codex subscription display names

All user-facing account and request-log plan labels SHALL use the status mapping
from OpenAI Codex commit `ca21fe65d18a9b6326759fb4263c65dfbb645aa5`.
The shared formatter MUST distinguish status and analytics modes. The protocol
aliases `hc` and `education` MUST use the labels for `enterprise` and `edu`. Account search
and plan-label sorting MUST recognize the displayed status names. Labels MUST
NOT change the plan identifier used for account identity or routing.

| Upstream identifier | Status | Analytics |
| --- | --- | --- |
| free | Free | Free |
| go | Go | Go |
| plus | Plus | Plus |
| pro | Pro 200 | Pro 200 |
| prolite | Pro 100 | Pro 100 |
| promax | Pro 500 | Pro 500 |
| team | Business | Business |
| self_serve_business_usage_based | Business | Business |
| business | Enterprise | Business |
| self_serve_business_prolite | Business Premium | Business |
| enterprise_cbp_automation | Enterprise (Automation) | Enterprise |
| enterprise | Enterprise | Enterprise |
| ent26 | Enterprise | Enterprise |
| enterprise_cbp_usage_based | Enterprise | Enterprise |
| edu | Edu | Education |
| edu_plus | Edu Plus | Education |
| edu_pro | Edu Pro | Education |
| sci | Academic Researchers | Academic Researchers |
| sci_plus | Academic Researchers Plus | Academic Researchers Plus |
| unknown or unrecognized | Unknown | Account |

#### Scenario: Business Premium remains distinct from personal Pro 100

- **GIVEN** separate accounts with `self_serve_business_prolite` and `prolite` identifiers
- **WHEN** the account list, detail, dashboard, account picker or request log displays their plans
- **THEN** their status labels are Business Premium and Pro 100 respectively
- **AND** searching for Business Premium matches the Business account

#### Scenario: Unknown plans do not claim a known subscription

- **GIVEN** an unrecognized upstream plan identifier
- **WHEN** the shared formatter renders status or analytics
- **THEN** it returns Unknown or Account respectively
- **AND** the original backend identifier is preserved

### Requirement: Aggregate quota displays use measured account percentages

Aggregate quota donuts SHALL use equally weighted upstream remaining percentages
for accounts with a known corresponding quota window. Accounts without that
window or without a finite percentage MUST be omitted. A measured zero remaining
percentage MUST remain in the average. Static plan-derived credit capacity MUST
NOT weight these quota displays. Titles and legends SHALL identify their
percentage and average semantics.

#### Scenario: Account without a measured window does not contribute
- **WHEN** an assigned account has no known remaining percentage for a quota window
- **THEN** that account is excluded from that window's average and legend

#### Scenario: Depleted measured account contributes zero
- **WHEN** one eligible account reports zero percent and another reports 80 percent remaining
- **THEN** the displayed average remaining quota is 40 percent
- **AND** different plan capacity estimates do not change the average

### Requirement: Overview quota percentages preserve useful precision

The 5-hour and weekly quota cards SHALL round numeric percentages to at most two fractional digits for display and omit trailing zeros. This applies to the measured average, per-account values, consumed percentage, quota tooltip percentages and the safe-line estimate. The dashboard MUST retain full numeric precision for averages, chart geometry and forecasts. An unavailable measurement MUST remain distinguishable from a measured zero.

#### Scenario: Fractional measurements and estimates

- **WHEN** the reporting accounts have 1.234 and 2.234 percent remaining and the safe-line estimate is 84.50001 percent
- **THEN** the account labels show 1.23% and 2.23%, the center shows 1.73%, and the forecast shows 84.5%
- **AND** corresponding tooltip percentages follow the same precision

#### Scenario: Unavailable quota window

- **WHEN** no account reports the selected window and no forecast is available
- **THEN** the measured average is unavailable and the forecast is omitted

### Requirement: Account list identifies estimated subscription credits

The dashboard account list SHALL label the plan-based remaining subscription credits as an estimate. It SHALL select monthly credits for a monthly-only account, secondary credits for a weekly-only account, and otherwise secondary credits with a primary fallback. A missing estimate SHALL display as `-`, and zero SHALL display as `0.00`. The list SHALL sort the raw estimates numerically in both directions with missing values last, independently of reported quota percentages and purchased credits. A saved subscription-credit sort SHALL retain its direction. The estimate MUST NOT be presented as a measured upstream balance or converted into tokens.

#### Scenario: Depleted weekly estimate with a purchased balance

- **WHEN** an account reports zero weekly remaining model credits, a positive primary estimate and 42.5 purchased credits
- **THEN** its subscription estimate shows 0.00 and its purchased balance shows 42.50

#### Scenario: Selected estimate unavailable

- **WHEN** a weekly-only account has no secondary estimate or a monthly-only account has no monthly estimate
- **THEN** its subscription estimate shows `-` and sorts after every numeric estimate in either direction
- **AND** purchased credits continue to show their own numeric balance, Unlimited state or unavailable marker
