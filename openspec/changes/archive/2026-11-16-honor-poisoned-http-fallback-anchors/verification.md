# Verification

## Behavior and contract

- `streaming.py` derives fallback identities through the existing `_turn_keys`
  helper and loads their scoped retry-circuit state before anchor planning.
- A known fence permits anchor suppression only when the existing durable
  full-resend verification proves the request carries required context.
- A cumulative resend without that proof is refused during planning, before
  upstream dispatch. The contract does not require an anchor to be submitted.
- Delta-only refusal consults the same fallback evidence. Existing explicit
  anchor validation, account ownership and API-key/thread scope remain in place.
- The canonical quarantine requirement and the added fallback requirement are
  synchronized with the change delta. The old scenario allowing a cumulative
  resend without prior output to proceed unanchored has been replaced.

## Evidence

- Baseline targeted comparison: 48 passed and 1 failed. The failure is the
  incomplete-resend route expectation; all split-record cases already passed.
- Updated combined route selection: 49 passed, 217 deselected.
- Related poison, quarantine and tombstone unit selection: 98 passed,
  966 deselected.
- `openspec validate honor-poisoned-http-fallback-anchors --strict`: passed.
- `openspec validate --specs --strict`: 67 passed, 0 failed.
- Scoped Ruff and Ty checks: passed.
- `git diff --check`: passed.

The route/unit counts refer to the targeted run logs reviewed during this
change. Strict specification validation and diff checks were rerun after the
canonical specification was synchronized. No production behavior was measured.
