"""Initial test case shipped with the Lab 6 exercise."""

from application import price_order


def test_platinum_express_order():
    """A platinum member buys 2000 worth of goods with SAVE10 and express delivery."""
    items = [
        {"price": 1500.0, "quantity": 1},
        {"price": 500.0, "quantity": 1},
    ]

    result = price_order(items, tier="platinum", coupon="SAVE10", delivery="express")

    assert result["subtotal"] == 2000.0
    assert result["discount"] == 500.0
    assert result["taxable"] == 1500.0
    assert result["gst"] == 270.0
    assert result["shipping"] == 199.0
    assert result["total"] == 1969.0
    assert result["loyalty_points"] == 20
