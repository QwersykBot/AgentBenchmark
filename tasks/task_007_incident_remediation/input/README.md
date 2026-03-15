# Incident Remediation Fixture

This task simulates a production payments incident where retries may create duplicate external charges and where the internal reconciliation layer may still leave the order in the wrong state after a retry.

Useful files:
- `incident_report.md` summarizes the customer-visible issue
- `logs/payments.log` contains the event timeline
- `docs/architecture.md` explains the payment flow
- `docs/runbook.md` describes the expected timeout/retry behavior
- `repo/reconciliation.py` contains the downstream state update logic
- `repo/` contains the checkout and retry code
- `tests/test_incident.py` contains public regression coverage

Recommended approach:
- read the incident report and logs first
- confirm the intended idempotency behavior from the docs
- inspect both the retry path and the downstream reconciliation path
- make a focused end-to-end fix
- run the public tests
