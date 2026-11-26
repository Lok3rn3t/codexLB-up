## ADDED Requirements

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
