## ADDED Requirements

### Requirement: GPT-6.2 Astra and Sol have bundled usage prices

When no upstream-metadata catalog price takes precedence, API-key usage, request logs, reservations, and aggregates MUST use the bundled rates below. Fast and priority MUST use Fast rates and flex MUST use Standard rates. Above 272,000 input tokens, long-context rates MUST apply to the entire request. Otherwise short-context rates MUST apply. Without an exact price, versioned and snapshot aliases MUST use the canonical entry.

#### Scenario: Apply the bundled rates

- **GIVEN** a model and tier in the table
- **WHEN** bundled pricing applies
- **THEN** the input, cached input, and output rates in USD per million tokens are as follows

| Model | Standard short | Standard long | Fast short | Fast long |
| --- | --- | --- | --- | --- |
| `gpt-6.2-astra` | 8 / 0.40 / 40 | 16 / 0.80 / 60 | 16 / 0.80 / 80 | 32 / 1.60 / 120 |
| `gpt-6.2-sol` | 2 / 0.10 / 10 | 4 / 0.20 / 15 | 4 / 0.20 / 20 | 8 / 0.40 / 30 |

#### Scenario: A dated Astra snapshot uses Fast long-context rates

- **GIVEN** the bundled fallback is active
- **WHEN** `gpt-6.2-astra-2026-11-21` is requested with `fast`, 272,001 input tokens including 100,000 cached tokens, and 100,000 output tokens
- **THEN** its token cost is `$17.664032`
