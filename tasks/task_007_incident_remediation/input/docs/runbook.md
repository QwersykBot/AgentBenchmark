# Timeout Runbook

When the payment gateway times out:
- Assume the provider may already have committed the charge.
- Schedule a retry only if the order still needs reconciliation.
- Preserve the original idempotency key on the retry job.
- The retry worker must replay the original key, not mint a new one.
- If the provider confirms the original charge on retry, reconciliation should mark the same order as `paid`.

Why:
- The provider deduplicates by idempotency key only.
- Reusing the key returns the original provider reference instead of creating a second charge.
- A reused provider reference for the same order is expected in this flow and should not trigger a duplicate-warning state for that order.

Safe rollout notes:
- Patch the retry path first.
- Patch reconciliation in the same deploy if it still misclassifies reused provider references.
- Re-run the public regression suite.
- After deploy, monitor for new duplicate provider references on the same order id.
- Also monitor orders stuck in `pending_manual_review` after a successful deduplicated retry.
