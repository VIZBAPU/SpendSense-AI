from datetime import date
from decimal import Decimal

from app.services.csv_formats import ParsedRow
from app.services.ingest import row_hashes


def make_row(number=1, description="AMAZON.CA", amount="89.99"):
    return ParsedRow(number, date(2026, 2, 16), description, "debit", Decimal(amount))


def test_hash_is_64_hex_characters():
    (h,) = row_hashes([make_row()])
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_identical_rows_in_one_file_get_different_hashes():
    first, second = row_hashes([make_row(1), make_row(2)])
    assert first != second


def test_same_file_gives_same_hashes():
    rows = [make_row(1), make_row(2, "NETFLIX.COM", "16.49")]
    assert row_hashes(rows) == row_hashes(rows)


def test_different_amount_gives_different_hash():
    a, b = row_hashes([make_row(amount="10.00"), make_row(amount="10.01")])
    assert a != b
