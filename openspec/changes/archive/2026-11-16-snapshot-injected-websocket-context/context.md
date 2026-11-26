# Context

Adapted from [upstream PR #2731](https://github.com/Soju06/codex-lb/pull/2731),
commit `ace4d91eb8523b21fd253b0ef91821b8e9991f44`. The fork additionally snapshots
coverage when the anchor is selected, before capability routing and API-key
reservation can suspend execution.

Example: a client-anchored request contains only two new messages. It completes,
then the proxy injects that completion into a request restating those messages
plus another one. The injected request must retain incomplete coverage. A later
explicitly anchored resend of that prefix cannot authorize a fresh replay that
would omit the original history.
