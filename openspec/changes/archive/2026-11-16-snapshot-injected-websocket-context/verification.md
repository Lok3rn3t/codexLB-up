# Verification

On the unchanged runtime baseline, the new native WebSocket route regression
failed: the third request received `response.created` from an anchorless replay
instead of a continuity failure. The incomplete-coverage admission test also
failed (`True` instead of `False`). The complete-coverage case passed.

After the snapshot fix:

- New product-route and two admission cases: **3 passed**.
- Focused existing/full-resend/continuity/idle-loss/prewarm regression selection
  plus the new tests: **37 passed**, 1557 deselected.
- Ruff check and format for the modified runtime and new tests passed.
- `ty check app/modules/proxy/_service/websocket/mixin.py` passed.
- Strict OpenSpec validation passed for the change and all **67** canonical specs.

The route test exercises an actual ASGI WebSocket with simulated upstream frames;
it does not establish the cause of production transport errors or claim a live
deployment was tested. Production was not modified.
