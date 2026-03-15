Title: Duplicate charges and stuck pending orders after gateway timeout

Summary:
- Customer support escalated a case where order `ord_1842` was charged twice.
- The checkout API returned a timeout to the caller and the retry worker later processed the same order again.
- Finance confirmed two different provider references for a single order.
- A later replay in staging showed that even when the retry reused the original provider reference, the internal order state could remain `pending_manual_review` instead of closing as `paid`.

What we know:
- The gateway supports idempotency keys.
- The retry path is supposed to reuse the original idempotency key if the first attempt may already have committed upstream.
- The reconciliation layer should treat a reused provider reference for the same logical order as a successful paid state, not a new anomaly.
- The incident appears limited to orders that hit the timeout-after-commit path.

What we need:
- Fix the code path that causes the duplicate charge.
- Fix any downstream state transition that would still leave the order in the wrong status after a safe retry.
- Add a regression test.
- Keep the rollout safe and easy to explain to on-call staff.
