# Provenance and validation scope

Adapted from [Soju06/codex-lb PR #2628](https://github.com/Soju06/codex-lb/pull/2628),
head `63da9eea0ebaf1673b8670dc7ec6581f5a94d77f`. The fork already contains the
related #2627 backoff-selection fix and #2731/#2581 continuity protections.

Example: generated turn state T resolves to historical row A, but acquisition
falls back to thread B on the same account and API-key scope. B marks the old
anchor dead. A complete client resend should retain its full input and reach the
same owner without that proxy-injected anchor. A delta cannot supply the missing
history and remains refused; another thread or API key does not inherit B's fence.

All evidence comes from repository code and isolated tests with fake upstream
transports. No production logs, provider requests, database changes, or server
operations are part of this change.

On the current fork baseline, all 48 split-record cases already passed. They
are compatibility coverage, not evidence that this patch newly fixes all retry
loops. The incomplete-resend quarantine case did reproduce a different failure:
the baseline dispatched without required prior context instead of refusing the
unsafe fresh request. The adopted checks preserve known fallback fences and
prevent that context loss. No claim is made that the specific production
requests supplied in chat have been diagnosed without their server-side evidence.

Verified local results: the baseline run has 48 passing split-record cases and
one failing incomplete-resend expectation; after the change, the combined route
run passes all 49 selected cases. Related poison/quarantine/tombstone unit
coverage passes 98 cases. These counts refer to the targeted runs, not the full
suite or a deployed server.
