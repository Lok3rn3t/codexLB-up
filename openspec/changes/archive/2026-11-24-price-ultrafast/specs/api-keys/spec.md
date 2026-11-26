## ADDED Requirements

### Requirement: Ultrafast token cost follows model, request time, and context length

USD token estimates for upstream-reported Ultrafast usage SHALL use Ultrafast input, cached input, and output prices. Reservations SHALL use the requested tier and settlement SHALL use the effective billed tier. The price lookup SHALL use the request or reservation time when available, including when rebuilding a historical breakdown. Persisted totals SHALL retain their recorded value.

#### Scenario: GPT-6.2 promotion ends at Pacific midnight

- **WHEN** a GPT-6.2 Astra or Sol Ultrafast request starts before March 1, 2027 at 00:00 Pacific time
- **THEN** the published promotional API rates apply
- **AND** a request at or after that instant uses the published list rates

#### Scenario: Long input changes the price of the entire request

- **WHEN** a supported model receives more than 272,000 input tokens including cached input
- **THEN** the long-context Ultrafast prices apply to all three token categories
- **AND** exactly 272,000 input tokens use short-context rates

#### Scenario: A provider advertises a service tier without a price

- **WHEN** a catalog has no usable Ultrafast rates for a documented model
- **THEN** the official bundled schedule supplies the missing rates
- **AND** pricing alone grants no account access to the model or service tier
