## Why

The keepalive iterator treats an upstream read timeout as its own elapsed heartbeat interval. The completed read can then yield heartbeats indefinitely.

## What Changes

Identify expiry of the heartbeat deadline separately from a source read failure. Keep the existing cancellation and shared-future ownership.

## Impact

HTTP Responses and other streams using the SSE keepalive iterator.
