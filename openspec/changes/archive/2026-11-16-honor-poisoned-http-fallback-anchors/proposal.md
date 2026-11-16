# Honor dead-anchor fences before HTTP bridge recovery planning

## Why

A generated HTTP turn-state alias can identify an older durable record while
session acquisition falls back to its thread or legacy-session key. The latter
key can already mark the anchor dead. Planning must honor that evidence before
injecting an anchor or trimming input, and it must verify that a cumulative
resend contains the context needed to proceed without an anchor. The fork
baseline already passes the complete-history retry cases, but its quarantined
incomplete-resend case dispatches without required prior context.

## What Changes

- Check the acquisition fallback key's quarantine and abandonment tombstone
  before injecting a proxy-owned anchor or trimming complete client history.
- Keep recovery on the resolved account owner and preserve the complete input.
- Refuse incomplete history while preserving explicit-anchor checks and isolation
  between threads and API keys.
- Cover both HTTP Responses routes, cached misses, later continuations, and
  existing poison/quarantine boundaries.

## Impact

- Capability: responses-api-compat.
- Implementation: HTTP bridge request planning only.
- No production-server access, schema, migration, settings, or dependency changes.
