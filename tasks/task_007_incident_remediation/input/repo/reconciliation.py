from __future__ import annotations

from repo.models import PaymentResult


def reconcile_retry_result(
    order_id: str,
    result: PaymentResult,
    order_statuses: dict[str, str],
) -> str:
    if result.status != "paid":
        order_statuses[order_id] = "retry_scheduled"
        return order_statuses[order_id]

    if result.reused_existing_charge:
        # BUG: a reused provider reference for the same order is expected after
        # a timeout-after-commit replay and should settle to paid, not remain stuck.
        order_statuses[order_id] = "pending_manual_review"
        return order_statuses[order_id]

    order_statuses[order_id] = "paid"
    return order_statuses[order_id]
