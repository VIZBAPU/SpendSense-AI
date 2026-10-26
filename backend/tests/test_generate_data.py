import csv
import json
import re
from datetime import datetime
from decimal import Decimal

from scripts.generate_data import END, START, generate, write_files

CATEGORIES = {
    "Groceries",
    "Dining",
    "Transport",
    "Rent/Housing",
    "Utilities",
    "Subscriptions",
    "Shopping",
    "Health",
    "Entertainment",
    "Income",
    "Transfers",
    "Business Expense",
    "Other",
}


def test_same_seed_gives_same_rows():
    assert generate(42) == generate(42)


def test_different_seed_gives_different_rows():
    assert generate(42) != generate(7)


def test_about_600_rows_within_six_months():
    rows = generate(42)
    assert 500 <= len(rows) <= 700
    assert min(row.txn_date for row in rows) >= START
    assert max(row.txn_date for row in rows) <= END


def test_every_row_is_valid():
    for row in generate(42):
        assert row.category in CATEGORIES
        assert row.direction in ("debit", "credit")
        assert isinstance(row.amount, Decimal)
        assert row.amount > 0
        assert row.amount.as_tuple().exponent == -2  # exactly 2 decimal places


def test_no_account_or_card_numbers():
    for row in generate(42):
        assert not re.search(r"\d{8,}", row.description)


def test_at_least_three_of_each_planted_anomaly():
    rows = generate(42)
    for kind in ["zscore", "duplicate", "new_merchant_large", "subscription_increase"]:
        assert sum(row.anomaly == kind for row in rows) >= 3


def test_files_are_written_in_format_b(tmp_path):
    rows = generate(42)
    write_files(rows, tmp_path)

    with open(tmp_path / "statement.csv", newline="", encoding="utf-8") as f:
        statement = list(csv.DictReader(f))
    assert list(statement[0].keys()) == ["Date", "Description", "Debit", "Credit"]
    assert len(statement) == len(rows)
    for line in statement:
        datetime.strptime(line["Date"], "%m/%d/%Y")  # raises if the format is wrong
        assert (line["Debit"] == "") != (line["Credit"] == "")  # exactly one is filled

    with open(tmp_path / "ground_truth.csv", newline="", encoding="utf-8") as f:
        assert len(list(csv.DictReader(f))) == len(rows)

    planted = json.loads((tmp_path / "anomalies.json").read_text(encoding="utf-8"))
    assert len(planted) == sum(1 for row in rows if row.anomaly)
