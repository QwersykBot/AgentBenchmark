from repo.checkout import build_charge_idempotency_key, submit_checkout
from repo.gateway import PaymentGateway
from repo.models import Order
from repo.reconciliation import reconcile_retry_result
from repo.retry_worker import process_retry


def make_order() -> Order:
    return Order(
        order_id="ord_1842",
        customer_id="cus_77",
        amount_cents=12_900,
        card_token="tok_live_abc",
    )


def test_happy_path_creates_one_provider_charge():
    gateway = PaymentGateway()
    retry_queue = []

    result = submit_checkout(make_order(), gateway, retry_queue)

    assert result.status == "paid"
    assert result.provider_reference == "ch_0001"
    assert retry_queue == []
    assert gateway.total_unique_charges == 1


def test_timeout_schedules_a_retry_job():
    gateway = PaymentGateway()
    retry_queue = []

    result = submit_checkout(
        make_order(),
        gateway,
        retry_queue,
        simulate_timeout_after_commit=True,
    )

    assert result.status == "retry_scheduled"
    assert len(retry_queue) == 1
    assert retry_queue[0].order_id == "ord_1842"


def test_timeout_retry_reuses_original_key_and_settles_order_to_paid():
    gateway = PaymentGateway()
    retry_queue = []
    order = make_order()
    order_statuses = {order.order_id: "retry_scheduled"}

    first_result = submit_checkout(
        order,
        gateway,
        retry_queue,
        simulate_timeout_after_commit=True,
    )

    assert first_result.status == "retry_scheduled"
    assert len(retry_queue) == 1
    assert retry_queue[0].original_idempotency_key == build_charge_idempotency_key(order.order_id)

    retry_result = process_retry(retry_queue[0], gateway)
    final_status = reconcile_retry_result(order.order_id, retry_result, order_statuses)

    assert retry_result.status == "paid"
    assert retry_result.provider_reference == "ch_0001"
    assert retry_result.reused_existing_charge is True
    assert gateway.total_unique_charges == 1
    assert final_status == "paid"
    assert order_statuses[order.order_id] == "paid"
