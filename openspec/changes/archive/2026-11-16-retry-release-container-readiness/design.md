# Bounded startup probing

Keep readiness as a read-only HTTP GET and use curl's retry implementation.
`--retry-all-errors` covers connection resets from a container port that becomes
reachable before its application finishes startup. `--retry-max-time 180` bounds
the retry window; each request retains its five-second timeout.

Continue to fail on exhausted readiness retries. The existing EXIT trap keeps
the failing status, emits container logs, and removes the temporary container.
No application validation is retried or weakened. The image pull also has a
separate five-attempt bound for transient registry failures.

Regression coverage runs the real shell script with mocked Docker operations.
A local HTTP server first resets the connection, then returns a successful
readiness response. Separate cases verify cleanup after failed readiness and
the image-pull attempt limit.
