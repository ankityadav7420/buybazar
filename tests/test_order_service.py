import pytest

from app.models.order_models import OrderStatus
from app.services.order_service import can_transition_order_status, normalize_order_status


@pytest.mark.parametrize(
    ("current_status", "next_status"),
    [
        (OrderStatus.PENDING, OrderStatus.CONFIRMED),
        (OrderStatus.PENDING, OrderStatus.CANCELLED),
        (OrderStatus.CONFIRMED, OrderStatus.SHIPPED),
        (OrderStatus.CONFIRMED, OrderStatus.CANCELLED),
        (OrderStatus.SHIPPED, OrderStatus.DELIVERED),
    ],
)
def test_allowed_order_status_transitions(current_status, next_status):
    assert can_transition_order_status(current_status, next_status) is True


@pytest.mark.parametrize(
    ("current_status", "next_status"),
    [
        (OrderStatus.PENDING, OrderStatus.SHIPPED),
        (OrderStatus.SHIPPED, OrderStatus.CANCELLED),
        (OrderStatus.DELIVERED, OrderStatus.CANCELLED),
        (OrderStatus.CANCELLED, OrderStatus.CONFIRMED),
    ],
)
def test_rejected_order_status_transitions(current_status, next_status):
    assert can_transition_order_status(current_status, next_status) is False


def test_normalize_order_status_accepts_database_strings():
    assert normalize_order_status("PENDING") == OrderStatus.PENDING
    assert normalize_order_status("confirmed") == OrderStatus.CONFIRMED
