"""Code coverage tests for application.py.

These tests are written to execute the pricing logic and every statement in
the main flow at least once. The store-pickup path and the invalid-delivery
guard are left to the branch coverage suite, so this suite reaches >90% line
coverage while branch coverage still shows gaps.

Run:
    coverage run -m pytest CodeCoverageTest_pesiug24cs547_application.py
    coverage report -m
"""

import pytest

from application import price_order


def test_empty_order_is_rejected():
    with pytest.raises(ValueError, match="at least one item"):
        price_order([])


def test_non_positive_quantity_is_rejected():
    items = [{"price": 250.0, "quantity": 0}]
    with pytest.raises(ValueError, match="positive integer"):
        price_order(items)


def test_negative_price_is_rejected():
    items = [{"price": -10.0, "quantity": 2}]
    with pytest.raises(ValueError, match="Price cannot be negative"):
        price_order(items)


@pytest.mark.parametrize(
    "tier, expected_discount, expected_total",
    [
        ("platinum", 900.0, 6018.0),
        ("gold", 600.0, 6372.0),
        ("silver", 300.0, 6726.0),
        ("bronze", 0.0, 7080.0),
    ],
)
def test_every_membership_tier(tier, expected_discount, expected_total):
    items = [{"price": 6000.0, "quantity": 1}]

    result = price_order(items, tier=tier, delivery="express")

    assert result["discount"] == expected_discount
    assert result["shipping"] == 0.0
    assert result["total"] == expected_total
    assert result["loyalty_points"] == 100


def test_standard_paid_shipping_for_a_small_order():
    items = [{"price": 100.0, "quantity": 1}]

    result = price_order(items, delivery="standard")

    assert result["taxable"] == 100.0
    assert result["shipping"] == 99.0
    assert result["gst"] == 18.0
    assert result["total"] == 217.0
    assert result["loyalty_points"] == 5


def test_save10_coupon_above_threshold():
    items = [{"price": 600.0, "quantity": 1}]

    result = price_order(items, coupon="SAVE10", delivery="standard")

    assert result["discount"] == 60.0
    assert result["shipping"] == 99.0
    assert result["total"] == 736.2
    assert result["loyalty_points"] == 20


def test_save20_coupon_above_threshold():
    items = [{"price": 2500.0, "quantity": 1}]

    result = price_order(items, coupon="SAVE20", delivery="standard")

    assert result["discount"] == 500.0
    assert result["shipping"] == 0.0
    assert result["total"] == 2360.0
    assert result["loyalty_points"] == 50


def test_flat200_coupon_above_threshold():
    items = [{"price": 1200.0, "quantity": 1}]

    result = price_order(items, coupon="FLAT200", delivery="standard")

    assert result["discount"] == 200.0
    assert result["shipping"] == 99.0
    assert result["total"] == 1279.0


def test_unknown_coupon_is_ignored():
    items = [{"price": 700.0, "quantity": 1}]

    result = price_order(items, coupon="WELCOME5", delivery="standard")

    assert result["discount"] == 0.0
    assert result["total"] == 925.0
