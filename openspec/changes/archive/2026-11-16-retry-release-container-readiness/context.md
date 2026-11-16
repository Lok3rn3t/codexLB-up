# Readiness recovery

Release run 43796661942 downloaded the Docker image, then failed with curl exit
56 before checking application health. Docker port forwarding can become
reachable before the application is ready. Retrying the read-only readiness GET
is safe; the original validation and failure exit remain required.

Curl now retries all readiness errors for at most 180 seconds, with a five-second
limit per request. A final request can finish up to five seconds after the retry
window. This does not retry application validation failures or bypass native
worker, migration, or dashboard checks.

Verification: three regression tests passed. A real local HTTP server resets
the first readiness connection (curl exit 56), then returns HTTP 200; the complete
shell script recovers, reaches in-container validation, and removes the mock
container. Failed readiness preserves exit 56, prints logs, and cleans up without
running validation. Repeated image-pull failure stops after five attempts. Ruff,
Bash syntax, and strict OpenSpec validation passed. Docker itself was not run
locally; released architecture validation remains a workflow gate.
