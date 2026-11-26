## Why

The proxy forwards Ultrafast to eligible accounts. PR #5 adds Standard and Fast pricing for GPT-6.2, but Ultrafast usage still takes the Standard pricing path.

## What Changes

Use explicit catalog Ultrafast rates and the documented OpenAI schedule for supported models. Account for the GPT-6.2 promotion by request time in USD estimates and API-key limits.

## Impact

Affected capabilities are API-key accounting and upstream metadata. Existing account discovery determines eligibility.
