# Payments Architecture

Checkout flow:
1. API receives an order request.
2. `submit_checkout(...)` builds the provider payload and an idempotency key.
3. The gateway uses the idempotency key as the deduplication boundary for external charges.
4. On a transport timeout, the API schedules a retry job if the provider outcome is uncertain.
5. The retry worker replays the charge attempt.
6. The reconciliation layer updates the internal order status after the retry outcome is known.

Important invariant:
- A retry for the same logical order must reuse the original provider idempotency key.
- If a new idempotency key is generated on retry, the gateway will treat the retry as a brand-new charge.
- If the retry reuses the original provider reference, reconciliation should still resolve the order to `paid` for the same order, not flag it as a duplicate anomaly.

Expected operational behavior:
- One logical order should map to one provider charge, even if the first attempt times out after the provider already committed.
- One logical order should also converge to one terminal internal state: `paid` after reconciliation succeeds.
