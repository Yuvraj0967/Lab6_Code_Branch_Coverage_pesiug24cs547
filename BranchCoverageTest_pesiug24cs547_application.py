"""Branch coverage tests for application.py.

This suite is a superset of the code coverage tests. It exercises both
outcomes of every decision: all membership tiers, valid/invalid delivery,
pickup, free/paid shipping, every coupon at and below its threshold, and
all loyalty-point brackets.

Run:
    coverage run --branch -m pytest BranchCoverageTest_pesiug24cs547_application.py
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


def test_unsupported_delivery_is_rejected():
    items = [{"price": 100.0, "quantity": 1}]
    with pytest.raises(ValueError, match="Unsupported delivery"):
        price_order(items, delivery="drone")


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


def test_store_pickup_has_no_shipping_charge():
    items = [{"price": 100.0, "quantity": 1}]

    result = price_order(items, delivery="pickup")

    assert result["shipping"] == 0.0
    assert result["total"] == 118.0


def test_save10_coupon_above_threshold():
    items = [{"price": 600.0, "quantity": 1}]

    result = price_order(items, coupon="SAVE10", delivery="standard")

    assert result["discount"] == 60.0
    assert result["shipping"] == 99.0
    assert result["total"] == 736.2
    assert result["loyalty_points"] == 20


def test_save10_coupon_below_threshold():
    items = [{"price": 499.0, "quantity": 1}]

    result = price_order(items, coupon="SAVE10", delivery="pickup")

    assert result["discount"] == 0.0
    assert result["total"] == 588.82
    assert result["loyalty_points"] == 20


def test_save20_coupon_above_threshold():
    items = [{"price": 2500.0, "quantity": 1}]

    result = price_order(items, coupon="SAVE20", delivery="standard")

    assert result["discount"] == 500.0
    assert result["shipping"] == 0.0
    assert result["total"] == 2360.0
    assert result["loyalty_points"] == 50


def test_save20_coupon_below_threshold():
    items = [{"price": 1499.0, "quantity": 1}]

    result = price_order(items, coupon="SAVE20", delivery="pickup")

    assert result["discount"] == 0.0
    assert result["total"] == 1768.82


def test_flat200_coupon_above_threshold():
    items = [{"price": 1200.0, "quantity": 1}]

    result = price_order(items, coupon="FLAT200", delivery="standard")

    assert result["discount"] == 200.0
    assert result["shipping"] == 99.0
    assert result["total"] == 1279.0


def test_flat200_coupon_below_threshold():
    items = [{"price": 999.0, "quantity": 1}]

    result = price_order(items, coupon="FLAT200", delivery="pickup")

    assert result["discount"] == 0.0
    assert result["total"] == 1178.82


def test_unknown_coupon_is_ignored():
    items = [{"price": 700.0, "quantity": 1}]

    result = price_order(items, coupon="WELCOME5", delivery="standard")

    assert result["discount"] == 0.0
    assert result["total"] == 925.0
