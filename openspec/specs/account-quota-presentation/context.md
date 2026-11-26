# Subscription labels

Subscription status labels follow the user-selected official Codex implementation:
https://github.com/openai/codex/blob/ca21fe65d18a9b6326759fb4263c65dfbb645aa5/codex-rs/tui/src/subscription.rs#L11-L39.

The dashboard keeps the subscription identifier separate from its readable name.
For example, `self_serve_business_prolite` displays as Business Premium, while
personal `prolite` displays as Pro 100. `business` displays as Enterprise in
status, as in the selected source. Status is used for account rows, cards,
details, account selection and request snapshots. The explicit analytics mode
uses the broader upstream labels but does not alter telemetry grouping.

Historical `prolite` metadata is ambiguous after earlier normalization; it stays
Pro 100 until an accepted upstream observation restores a more specific plan.
Changing a display name does not establish or modify subscription allowances.

See the [subscription-label requirement](spec.md#requirement-account-labels-follow-codex-subscription-display-names).

## Observed quota units

The upstream quota percentage and reset time are measurements. Static capacities
such as 37,800 multiplied by a reported 96 percent yield 36,288 model credits,
not an upstream subscription balance or a known remaining-token allowance.
The dashboard account list shows measured percentages in Quota, the plan-based
estimate in Subscription credits (est.), and the upstream balance in Purchased.
For example, the same account can show 36,288 estimated model credits and zero
purchased credits.

Overview donuts show equally weighted percentages of accounts with a known
window. For example, 0 percent and 80 percent remaining average to 40 percent;
an unreported third account is excluded and the reporting-account count is two.
This is not a fungible pool of tokens. Capacity-based forecasts remain explicitly
labelled estimates and do not establish subscription entitlements.

An unknown refresh does not become zero or a current stale percentage. Existing
row continuity is retained, with the old value used only as an animation starting
point when a new observation arrives. Upstream observation freshness remains
separate from the dashboard polling time.
