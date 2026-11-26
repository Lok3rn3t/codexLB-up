## REMOVED Requirements

### Requirement: Dashboard usage donuts present credits as stacked remaining and capacity

**Reason**: The dashboard now measures average remaining quota for each window using reported account percentages.
**Migration**: Use the measured-average requirements in `account-quota-presentation` and the responsive quota-card layout below.

## ADDED Requirements

### Requirement: Dashboard quota cards keep account measurements readable

Each overview quota card MUST identify its window and measured average. When available, its forecast MUST appear separately with an estimate label. At compact card widths, the legend MUST leave room for both account identity and percentage. If an identity is truncated, the full display label MUST be available subject to the dashboard privacy setting.

#### Scenario: Compact quota legend

- **WHEN** the 5-hour and weekly cards render long account identities at a narrow viewport
- **THEN** each account row displays both its identity and its percentage within the card
- **AND** the forecast is distinguishable from the measured average
- **AND** private account identities remain concealed when the privacy setting is enabled

### Requirement: Dashboard token total provides compact and exact counts

The overview Tokens card MUST use compact K, M and B notation with at most one fractional digit for large totals. The exact recorded token count MUST be available from the card. For incomplete usage, both presentations MUST retain the ≥ lower-bound indicator and the compact value MUST round down so the displayed bound never exceeds the observed total.

#### Scenario: Partial token total in the weekly overview

- **WHEN** the seven-day token total includes 12,345,678 recorded tokens and some requests lack usage
- **THEN** the card shows ≥ 12.3M
- **AND** inspecting the card's total reveals the exact lower bound of 12,345,678 tokens

### Requirement: Request-log plan badges fit their own column

The dashboard request log MUST show the entire plan label inside its Plan cell at the default and manually reduced column widths. The adjacent API Key text MUST remain independently readable.

#### Scenario: Long plan label beside an API key

- **WHEN** the Plan and API Key columns are visible in a row with Business Premium or Academic Researchers Plus
- **THEN** the full plan name is readable in the cell and exposed to assistive technology
- **AND** the badge stays within its Plan cell and does not cover the key text
