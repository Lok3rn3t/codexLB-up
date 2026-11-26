## REMOVED Requirements

### Requirement: Zero-credit assigned accounts are omitted from 5h and weekly donut totals

**Reason**: Static plan credits are not a measured allowance and must no longer
decide which measured account percentages participate in the display.

**Migration**: Use the measured-window eligibility requirement below. Known zero
percent is a depleted window and participates; unknown percentage is omitted.

## ADDED Requirements

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

## MODIFIED Requirements

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
