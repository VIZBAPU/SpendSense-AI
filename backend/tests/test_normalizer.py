import pytest

from app.services.normalizer import normalize_merchant


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("SQ *BLUE BOTTLE #1234 TORONTO ON", "BLUE BOTTLE"),
        ("sq *blue bottle #1234 toronto on", "BLUE BOTTLE"),
        ("METRO 457 TORONTO ON", "METRO"),
        ("SHELL 4421 TORONTO ON", "SHELL"),
        ("COSTCO WHOLESALE #535", "COSTCO WHOLESALE"),
        ("PETRO-CANADA 1188", "PETRO-CANADA"),
        ("UBER *EATS", "UBER *EATS"),
        ("UBER *TRIP", "UBER *TRIP"),
        ("SPOTIFY P1A2B3C4", "SPOTIFY P1A2B3C4"),
        ("IKEA NORTH YORK", "IKEA NORTH YORK"),
        ("  NETFLIX.COM  ", "NETFLIX.COM"),
        ("CLIENT PAYMENT - ACME DESIGN", "CLIENT PAYMENT - ACME DESIGN"),
    ],
)
def test_normalize_merchant(raw, expected):
    assert normalize_merchant(raw) == expected
