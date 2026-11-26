## ADDED Requirements

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
