## ADDED Requirements

### Requirement: Token totals do not double count subsets

Request logs and dashboard activity SHALL use input plus output tokens when
both are reported. Cached input MUST NOT be added again to input and reasoning
MUST NOT be added again to output. When output is absent but reasoning is
reported, the known reasoning subset MAY contribute to a partial total, and
request and aggregate arithmetic MUST agree.

#### Scenario: Complete usage includes reasoning and cache
- **WHEN** a response reports input 100, cached input 40, output 50 and reasoning 30
- **THEN** its total is 150 and is complete

#### Scenario: Reasoning is the only known output subset
- **WHEN** a response reports input 100, no output count and reasoning 30
- **THEN** request and activity known totals include 130
- **AND** that total is identified as partial

### Requirement: Missing measurements remain distinguishable

The request-log API SHALL expose whether stored token usage is complete,
partial or missing based on available input/output fields. Dashboard, account,
conversation and API-key usage summaries SHALL expose coverage of their recorded
requests. Their token displays MUST NOT
present missing usage as measured zero or a partial total as the complete
expense. Folded historical requests without retained coverage metadata SHALL
be identified as unknown coverage instead of complete. An empty period MAY
show zero; a reported input/output zero MUST remain a valid complete measurement.
Completeness MUST NOT claim that usage
from unseen retries or activity outside this proxy has been recorded.

#### Scenario: Disconnect without usage
- **WHEN** a request ends without a token measurement
- **THEN** the request displays unavailable usage
- **AND** the activity summary indicates incomplete coverage

#### Scenario: Measured zero
- **WHEN** upstream reports zero input and zero output tokens
- **THEN** usage is complete with a total of zero

#### Scenario: Historical rollup lacks coverage counters
- **WHEN** an activity total includes folded requests whose completeness was not retained
- **THEN** their count is exposed as unknown coverage
- **AND** the dashboard does not claim complete measurement of that period

#### Scenario: API-key summaries preserve coverage through folding
- **WHEN** recorded requests for a key include complete, partial and missing usage
- **THEN** its usage summary exposes those coverage counts without changing enforced limits
- **AND** after folding without retained coverage metadata, those requests are marked unknown

### Requirement: Reported failure usage is settled once

Native stream reservation settlement SHALL consume reported input/output usage
on failed or incomplete terminal responses as well as successful responses.
Unknown usage MUST NOT be invented, and repeated settlement MUST NOT charge
the same reservation twice. Cancellation and cleanup ownership MUST be preserved.

#### Scenario: Incomplete response reports usage
- **WHEN** a native response ends incomplete with input and output counts
- **THEN** API-key consumption includes those actual counts exactly once

#### Scenario: Failed response has no usage
- **WHEN** a native response fails without input/output counts
- **THEN** the outstanding reservation is released without invented consumption

### Requirement: Subscription quantities reflect upstream units

Account quota displays SHALL show upstream remaining percentages and reset
times and SHALL keep separately reported credit balances in credits. They
MUST NOT label a static plan-capacity conversion as measured remaining tokens
or subscription credit balance. Aggregate displays MUST identify averages or
estimates explicitly and MUST NOT imply a measured fungible pool of tokens.

#### Scenario: Percentage without token allowance
- **WHEN** upstream reports 60 percent remaining and no absolute token allowance
- **THEN** the account shows 60 percent remaining
- **AND** no exact token allowance is inferred from the plan name

### Requirement: Measurement timing is explicit

Usage displays SHALL explain that actual token counters update after upstream
usage is received. They MUST NOT claim that visible text deltas reveal hidden
reasoning, server-side context or cache counts. No character-to-token constant
SHALL be introduced as an authoritative live usage counter.

#### Scenario: Generation is still running
- **WHEN** the upstream stream has not supplied token usage
- **THEN** the interface does not present a fabricated exact usage count
