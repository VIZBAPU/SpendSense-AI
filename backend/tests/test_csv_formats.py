from decimal import Decimal

import pytest

from app.services.csv_formats import FormatBAdapter, FormatError, parse_amount

HEADER = "Date,Description,Debit,Credit\n"


def test_parses_a_debit_and_a_credit():
    text = HEADER + "03/02/2026,SQ *BLUE BOTTLE,6.75,\n03/02/2026,CLIENT PAYMENT,,2500.00\n"
    rows, errors = FormatBAdapter().parse(text)
    assert errors == []
    assert [(r.direction, r.amount) for r in rows] == [
        ("debit", Decimal("6.75")),
        ("credit", Decimal("2500.00")),
    ]


def test_wrong_headers_raise_format_error():
    with pytest.raises(FormatError):
        FormatBAdapter().parse("When,What,Out,In\n")


def test_collects_every_row_error():
    text = HEADER + "13/45/2026,COFFEE,5.00,\n03/02/2026,,5.00,\n03/02/2026,BOTH,1.00,2.00\n"
    _, errors = FormatBAdapter().parse(text)
    assert [(e.row, e.field) for e in errors] == [
        (1, "Date"),
        (2, "Description"),
        (3, "Debit/Credit"),
    ]


def test_blank_lines_are_ignored():
    rows, errors = FormatBAdapter().parse(HEADER + "\n03/02/2026,COFFEE,5.00,\n\n")
    assert len(rows) == 1 and errors == []


@pytest.mark.parametrize("raw", ["abc", "-5.00", "0", "1.234", "NaN"])
def test_invalid_amounts_are_rejected(raw):
    with pytest.raises(ValueError):
        parse_amount(raw)


def test_amount_gets_two_decimals():
    assert parse_amount("12.5").as_tuple().exponent == -2
