# Plan against the key used for session acquisition

Reuse `_turn_keys` to derive the same API-key-scoped fallback identity as session
acquisition. Load the retry circuit for that key only for generated HTTP turn
states outside account-neutral replay. Include the key with the canonical
durable key in quarantine and abandonment checks.

Suppress anchor injection and prefix trimming only when the complete resend has
the existing proof that it carries enough fresh context. Otherwise fail closed.
Delta-only requests consult the same fences before dispatch. Explicit client
anchors retain their validation path. Submission-time fences remain necessary
because a circuit can change after planning.

This does not select a different account or reconcile historical database rows.
The existing scope, ownership, and replay contracts remain in force.
