from __future__ import annotations

from repo.gateway import PaymentGateway
from repo.models import PaymentResult, RetryJob


def process_retry(job: RetryJob, gateway: PaymentGateway) -> PaymentResult:
    idempotency_key = job.original_idempotency_key or f"retry:{job.order_id}:{job.attempt}"
    receipt = gateway.charge(
        order_id=job.order_id,
        amount_cents=job.amount_cents,
        card_token=job.card_token,
        idempotency_key=idempotency_key,
    )
    return PaymentResult(
        status="paid",
        provider_reference=receipt.provider_reference,
        reused_existing_charge=receipt.reused_existing_charge,
    )
