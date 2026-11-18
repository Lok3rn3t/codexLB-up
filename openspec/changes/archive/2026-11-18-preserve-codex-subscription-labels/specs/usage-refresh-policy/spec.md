## ADDED Requirements

### Requirement: Account metadata preserves Business Premium identity

Import, OAuth, token refresh, accepted usage refresh and account API responses
MUST preserve the upstream `self_serve_business_prolite` identifier separately
from personal `prolite`. Policy normalization MUST continue using the existing
Pro Lite capacity and eligibility classification. Usage identity and downgrade
checks MUST retain their previous policy semantics and workspace safety fences.
Existing `prolite` records MUST NOT be relabeled as Business Premium without a
fresh accepted upstream observation identifying that subscription.

#### Scenario: Accepted refresh restores a previously collapsed identity

- **GIVEN** an account previously stored as `prolite`
- **WHEN** an accepted usage response identifies it as `self_serve_business_prolite`
- **THEN** its stored and API plan identifier becomes `self_serve_business_prolite`
- **AND** capacity and eligibility retain their existing policy classification

#### Scenario: Conflicting workspace cannot rename an account

- **GIVEN** an account bound to one workspace
- **WHEN** a Business Premium usage payload explicitly identifies a different workspace
- **THEN** the payload is rejected by the existing identity guard
- **AND** the stored plan and usage are not rewritten

#### Scenario: An ambiguous historical Pro Lite record stays personal

- **GIVEN** a stored `prolite` record without a fresh upstream Business Premium observation
- **WHEN** account metadata is returned to the dashboard
- **THEN** its identifier remains `prolite`

## MODIFIED Requirements

### Requirement: Usage capacity recognizes upstream ChatGPT plan types

The system MUST recognize upstream account plans for capacity. Business Premium
(`self_serve_business_prolite`) MUST retain its identifier in account metadata.
Capacity, model eligibility, usage identity comparisons, and rate-limit policy
MUST continue normalizing it to the existing `prolite` category. Pro Lite MUST use `1125.0` primary and `37800.0` secondary capacity.
`promax` MUST retain its stored identifier and use Pro estimates of `1500.0`
primary and `50400.0` secondary credits. Existing identity, status, quota, and
operator-policy gates MUST remain in force.

#### Scenario: Pro Lite account contributes aggregate remaining credits

- **GIVEN** an active account whose stored `plan_type` is `prolite`
- **AND** its latest primary and secondary usage rows report `used_percent` below 100
- **WHEN** the system builds usage window summaries or per-account remaining credit values
- **THEN** the account contributes `1125.0` primary capacity and `37800.0` secondary capacity
- **AND** the computed remaining credits are non-zero according to the reported usage percent

#### Scenario: Business Pro Lite refresh uses the existing Pro Lite tier

- **GIVEN** a workspace-less account with a recognized paid plan
- **WHEN** usage refresh returns a valid payload with `plan_type` `self_serve_business_prolite`
- **THEN** the usage sample is written and the account plan becomes `self_serve_business_prolite`
- **AND** capacity, model eligibility, and rate-limit projection use the existing `prolite` policy category

#### Scenario: Pro Max capacity preserves its plan identifier

- **GIVEN** an active account whose stored `plan_type` is `promax`
- **WHEN** the dashboard builds usage summaries and remaining credits
- **THEN** its primary and secondary capacity estimates are `1500.0` and `50400.0`
- **AND** its displayed plan remains `promax`

#### Scenario: Pro Max capacity-aware routing avoids the unknown-plan fallback

- **GIVEN** active `promax` and `pro` accounts with equal usage and reset deadlines
- **AND** the `promax` account has no explicit capacity override
- **WHEN** capacity-weighted or relative-availability routing selects an account
- **THEN** both accounts use the same Pro capacity estimate
