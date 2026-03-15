from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Order:
    order_id: str
    customer_id: str
    amount_cents: int
    card_token: str


@dataclass(slots=True)
class RetryJob:
    order_id: str
    customer_id: str
    amount_cents: int
    card_token: str
    attempt: int = 1
    original_idempotency_key: str | None = None


@dataclass(slots=True)
class PaymentResult:
    status: str
    provider_reference: str | None
    reused_existing_charge: bool = False


@dataclass(slots=True)
class ChargeReceipt:
    provider_reference: str
    reused_existing_charge: bool = False
