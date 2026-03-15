from __future__ import annotations

from repo.models import ChargeReceipt


class GatewayTimeout(Exception):
    """Raised when the provider timed out after or during a charge attempt."""


class PaymentGateway:
    def __init__(self) -> None:
        self._charges_by_key: dict[str, str] = {}
        self.charge_attempt_log: list[dict[str, str | int | bool]] = []

    def charge(
        self,
        *,
        order_id: str,
        amount_cents: int,
        card_token: str,
        idempotency_key: str,
        simulate_timeout_after_commit: bool = False,
    ) -> ChargeReceipt:
        self.charge_attempt_log.append(
            {
                "order_id": order_id,
                "amount_cents": amount_cents,
                "card_token": card_token,
                "idempotency_key": idempotency_key,
                "simulate_timeout_after_commit": simulate_timeout_after_commit,
            }
        )

        if idempotency_key in self._charges_by_key:
            return ChargeReceipt(
                provider_reference=self._charges_by_key[idempotency_key],
                reused_existing_charge=True,
            )

        provider_reference = f"ch_{len(self._charges_by_key) + 1:04d}"
        self._charges_by_key[idempotency_key] = provider_reference

        if simulate_timeout_after_commit:
            raise GatewayTimeout("Gateway timed out after provider commit.")

        return ChargeReceipt(provider_reference=provider_reference, reused_existing_charge=False)

    @property
    def total_unique_charges(self) -> int:
        return len(self._charges_by_key)
