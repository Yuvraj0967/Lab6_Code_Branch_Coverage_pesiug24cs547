"""Retail order pricing application used for the Lab 6 coverage exercise.

Run the tests with:
    coverage run --branch -m pytest test_application.py
    coverage report -m
"""

FREE_SHIPPING_THRESHOLD = 2000.0
STANDARD_SHIPPING = 99.0
EXPRESS_SHIPPING = 199.0
GST_RATE = 0.18


def calculate_subtotal(items):
    """Return the order subtotal for a list of {price, quantity} items."""
    if not items:
        raise ValueError("Order must contain at least one item")

    subtotal = 0.0
    for item in items:
        if item["quantity"] <= 0:
            raise ValueError("Quantity must be a positive integer")
        if item["price"] < 0:
            raise ValueError("Price cannot be negative")
        subtotal += item["price"] * item["quantity"]
    return round(subtotal, 2)


def membership_rate(tier):
    """Return the membership discount rate for a customer tier."""
    if tier == "platinum":
        return 0.15
    if tier == "gold":
        return 0.10
    if tier == "silver":
        return 0.05
    return 0.0


def coupon_discount(subtotal, coupon):
    """Return the coupon discount amount that applies to the subtotal."""
    if coupon is None:
        return 0.0
    if coupon == "SAVE10":
        return round(subtotal * 0.10, 2) if subtotal >= 500 else 0.0
    if coupon == "SAVE20":
        return round(subtotal * 0.20, 2) if subtotal >= 1500 else 0.0
    if coupon == "FLAT200":
        return 200.0 if subtotal >= 1000 else 0.0
    return 0.0


def shipping_charge(payable, delivery):
    """Return the shipping charge for the requested delivery method."""
    if delivery == "pickup":
        return 0.0
    if delivery not in ("standard", "express"):
        raise ValueError("Unsupported delivery option")

    charge = EXPRESS_SHIPPING if delivery == "express" else STANDARD_SHIPPING
    return 0.0 if payable >= FREE_SHIPPING_THRESHOLD else charge


def loyalty_points(total):
    """Return the loyalty points earned on a paid total."""
    if total >= 5000:
        return 100
    if total >= 2000:
        return 50
    if total >= 500:
        return 20
    return 5


def price_order(items, tier="bronze", coupon=None, delivery="standard"):
    """Price an order and return every component of the final bill."""
    subtotal = calculate_subtotal(items)
    member_discount = round(subtotal * membership_rate(tier), 2)
    promo_discount = coupon_discount(subtotal, coupon)

    discount = min(member_discount + promo_discount, subtotal)
    taxable = subtotal - discount
    shipping = shipping_charge(taxable, delivery)
    gst = round(taxable * GST_RATE, 2)
    total = round(taxable + gst + shipping, 2)

    return {
        "subtotal": subtotal,
        "discount": round(discount, 2),
        "taxable": round(taxable, 2),
        "gst": gst,
        "shipping": shipping,
        "total": total,
        "loyalty_points": loyalty_points(total),
    }
