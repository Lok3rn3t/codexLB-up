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

## Full-suite fixture correction

The first complete bridge CI run found one additional fixture inconsistency:
the positive silent-reattach quarantine test supplied a Responses-Lite bundle
after an earlier user item, a prefix already classified as unverified by the
existing Lite tests. It also omitted the actual completed assistant output.
Its old success expectation therefore depended on the removed unsafe bypass.

The positive test now uses a normal completed assistant response, deliberately
omits that output in the second request to exercise anchored reattachment and
quarantine, then supplies the actual returned output in the third request.
The third request still must complete successfully without an anchor. The
separate incomplete-history test still requires refusal before dispatch.
Both focused tests pass. The broader quarantine, split-record and Responses-Lite
classification selection passes 57 cases (209 deselected). Ruff, formatting,
and Ty pass. Runtime and normative contracts are unchanged by this correction.
