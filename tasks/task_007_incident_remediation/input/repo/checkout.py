from __future__ import annotations

from repo.gateway import GatewayTimeout, PaymentGateway
from repo.models import Order, PaymentResult, RetryJob


def build_charge_idempotency_key(order_id: str) -> str:
    return f"charge:{order_id}"


def submit_checkout(
    order: Order,
    gateway: PaymentGateway,
    retry_queue: list[RetryJob],
    *,
    simulate_timeout_after_commit: bool = False,
) -> PaymentResult:
    idempotency_key = build_charge_idempotency_key(order.order_id)

    try:
        receipt = gateway.charge(
            order_id=order.order_id,
            amount_cents=order.amount_cents,
            card_token=order.card_token,
            idempotency_key=idempotency_key,
            simulate_timeout_after_commit=simulate_timeout_after_commit,
        )
        return PaymentResult(
            status="paid",
            provider_reference=receipt.provider_reference,
            reused_existing_charge=receipt.reused_existing_charge,
        )
    except GatewayTimeout:
        retry_queue.append(
            RetryJob(
                order_id=order.order_id,
                customer_id=order.customer_id,
                amount_cents=order.amount_cents,
                card_token=order.card_token,
                attempt=1,
                # BUG: the retry worker should reuse the original idempotency key,
                # but the current code drops it and forces the worker to mint a new one.
                original_idempotency_key=None,
            )
        )
        return PaymentResult(status="retry_scheduled", provider_reference=None)
