# Verification

## Current-head Linux validation

Candidate `466dd50df24110792eeb7addfdcc987e7dd3aeed` passed the complete CI workflow:
https://github.com/Lok3rn3t/codexLB-up/actions/runs/43929436577

The unit slice passed 10,739 tests (7 documented skips, 1 existing expected
failure), including serialization-depth and proxy environment cases that fail
on the unchanged Windows baseline. The native wire suite passed 374 tests,
including real-worker receive-credit regressions. All integration slices,
PostgreSQL, migration, frontend, package, Docker, Helm, Nix, type and lint gates
passed. Five legacy idle-loss fixtures were updated to the real typed message
after initial CI identified a missing error attribute; their lifecycle
assertions are unchanged. No production deployment was performed.
