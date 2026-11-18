# Observed usage, coverage and quota units

## Evidence and boundary

OpenAI documents authoritative input counting for the public Responses API at
https://developers.openai.com/api/docs/guides/token-counting and explains that
output usage includes invisible structure and reasoning. The public input count
endpoint is not assumed available through the ChatGPT OAuth backend.
The current ChatGPT usage adapter receives percentages, reset times and a
separate purchased-credit balance, not an absolute subscription-token allowance.
The limits documentation at https://learn.chatgpt.com/docs/pricing also describes
model, context, reasoning, tool use and caching as factors in allowance use.

This change uses existing measurements. It does not infer exact token totals
from characters, subscription names, percentage movement or elapsed time.

## Token arithmetic and coverage

Known total = known input + known output, with reasoning as a lower-bound output
fallback only when output is absent. Cached input is a subset, not an additional
charge. For example, input 100 and reasoning 30 with no output count yield a
known total of 130, marked partial. Input 100, output 50, cached 40, reasoning 30
yield a complete total of 150.

Coverage describes the stored total input/output measurements, not completeness
of cache detail, hidden retries, activity outside this proxy, or provider billing.
No new persisted redundant status is needed: raw rows derive coverage from their
nullable counters. Existing rollups retain arithmetic but not row completeness;
they count as unknown coverage. This avoids inventing historical certainty or
scanning all retained rows on every dashboard refresh.

## Quotas and projections

Measured account remaining percentages and purchased credits retain their
original units. Aggregate percentages are explicitly equally weighted averages
of accounts with known windows, not fungible token capacity. Existing routing
capacity heuristics remain internal compatibility behavior; any retained
capacity-based forecast must identify itself as an estimate. It must not be
presented as a measured subscription balance.

## Updates and settlement

The native finalizer already captures usage from completed, failed and incomplete
terminal events. Settlement must use full reported counts regardless of terminal
success, and release reservations when input/output is unknown. Existing
idempotency and cleanup remain responsible for charging at most once.

The dashboard continues its configured polling and refetch-on-focus behavior.
Reported tokens are recorded on receiving upstream usage and become visible on
the next refresh. There is no new SSE channel and no claim of an exact counter
while a response is still generating. External-source admission/settlement
estimates are not written as observed request-log usage by source_dispatch.

## Remaining accounting boundaries

This is completeness of stored observations, not provider billing reconciliation.
In particular, the compact SSE client converts failed/incomplete terminal events
to an error envelope before settlement and does not retain their usage. Its retry
loop shares one reservation across attempts. Fixing total spend across such
attempts requires per-attempt accounting and service-tier attribution, not
pretending the final attempt represents the whole retry sequence. That separate
transport/accounting redesign is not part of this change. Admission reservations
and external-source fallback settlement estimates retain their existing policy.
