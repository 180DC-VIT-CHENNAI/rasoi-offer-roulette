"""ISSUE-02: this fails while the budget helper ignores redemption probability."""

from rasoi.assignment.budget import expected_discount_cost


def test_expected_discount_uses_redemption_probability():
    assert expected_discount_cost(20.0, 500.0, 0.5) == 50.0
    assert expected_discount_cost(10.0, 420.0, 0.0) == 0.0
    assert expected_discount_cost(10.0, 420.0, 1.0) == 42.0
