"""Generate a synthetic freelancer bank statement (Format B) plus an answer key.

Writes three files:
  statement.csv     the bank export to upload (Date, Description, Debit, Credit)
  ground_truth.csv  the correct category for every row
  anomalies.json    the anomalies we planted on purpose

Run from the backend folder:
  python -m scripts.generate_data --seed 42
"""

import argparse
import csv
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

START = date(2026, 1, 1)
END = date(2026, 6, 30)
DEFAULT_OUT = Path(__file__).resolve().parents[2] / "data" / "generated"


@dataclass
class Row:
    txn_date: date
    description: str
    amount: Decimal
    direction: str  # "debit" or "credit"
    category: str
    anomaly: str | None = None


def money(low: str, high: str, rng: random.Random) -> Decimal:
    """Random amount between low and high, in whole cents (never a float)."""
    cents = rng.randint(int(Decimal(low) * 100), int(Decimal(high) * 100))
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


# (category, description variants, min amount, max amount, times per week)
EVERYDAY = [
    (
        "Groceries",
        [
            "LOBLAWS #1032 TORONTO ON",
            "METRO 457 TORONTO ON",
            "NO FRILLS #3321",
            "COSTCO WHOLESALE #535",
        ],
        "25.00",
        "160.00",
        3.0,
    ),
    (
        "Dining",
        [
            "SQ *BLUE BOTTLE #1234 TORONTO ON",
            "TIM HORTONS #2231",
            "UBER *EATS",
            "DOORDASH*PIZZA PIZZA",
        ],
        "6.00",
        "45.00",
        7.0,
    ),
    (
        "Transport",
        ["UBER *TRIP", "PRESTO FARE", "SHELL 4421 TORONTO ON", "PETRO-CANADA 1188"],
        "4.00",
        "70.00",
        4.5,
    ),
    ("Shopping", ["AMAZON.CA", "WINNERS #221", "IKEA NORTH YORK"], "15.00", "120.00", 1.0),
    ("Health", ["SHOPPERS DRUG MART #1201", "REXALL 7781"], "8.00", "60.00", 0.5),
    (
        "Entertainment",
        ["CINEPLEX #1145", "STEAM PURCHASE", "TICKETMASTER CA"],
        "12.00",
        "90.00",
        0.7,
    ),
    ("Business Expense", ["STAPLES #118", "WEWORK DAY PASS", "UPWORK FEE"], "10.00", "80.00", 1.0),
    ("Other", ["CANADA POST 0112", "SERVICE ONTARIO"], "5.00", "40.00", 0.3),
]

# (day of month, description, category, min amount, max amount)
MONTHLY_BILLS = [
    (1, "PROPERTY MGMT RENT", "Rent/Housing", "1650", "1650.00"),
    (3, "HOME INSURANCE PREMIUM", "Rent/Housing", "38.50", "38.50"),
    (8, "HYDRO ONE NETWORKS", "Utilities", "55.00", "95.00"),
    (12, "ENBRIDGE GAS", "Utilities", "40.00", "110.00"),
    (15, "ROGERS WIRELESS", "Utilities", "75.00", "75.00"),
    (2, "ADOBE *CREATIVE CLOUD", "Business Expense", "29.99", "29.99"),
    (4, "GITHUB INC", "Business Expense", "4.00", "4.00"),
    (10, "FIGMA MONTHLY", "Business Expense", "20.00", "20.00"),
    (25, "TRANSFER TO SAVINGS", "Transfers", "500.00", "500.00"),
    (28, "CREDIT CARD PAYMENT", "Transfers", "300.00", "900.00"),
]

# (day of month, description, normal price, new price, month the new price starts)
SUBSCRIPTIONS = [
    (6, "NETFLIX.COM", "16.49", "18.99", 4),
    (9, "SPOTIFY P1A2B3C4", "11.99", "13.99", 5),
    (14, "DISNEY PLUS", "14.99", "16.99", 3),
    (20, "APPLE.COM/BILL ICLOUD", "3.99", "3.99", 99),
]

CLIENTS = ["CLIENT PAYMENT - ACME DESIGN", "E-TRANSFER FROM NORTHWIND LTD", "STRIPE PAYOUT"]


def days(start: date, end: date):
    """Yield every date from start to end, inclusive."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def everyday_spending(rng: random.Random) -> list[Row]:
    """Random day-to-day purchases, e.g. about 7 coffees or meals a week."""
    rows = []
    for day in days(START, END):
        for category, descriptions, low, high, per_week in EVERYDAY:
            if rng.random() < per_week / 7:
                amount = money(low, high, rng)
                rows.append(Row(day, rng.choice(descriptions), amount, "debit", category))
    return rows


def monthly_rows(rng: random.Random) -> list[Row]:
    """Rent, bills, subscriptions (with planted price increases) and client income."""
    rows = []
    for month in range(START.month, END.month + 1):
        for day, description, category, low, high in MONTHLY_BILLS:
            when = date(START.year, month, day)
            rows.append(Row(when, description, money(low, high, rng), "debit", category))

        for day, description, old_price, new_price, increase_month in SUBSCRIPTIONS:
            price = new_price if month >= increase_month else old_price
            when = date(START.year, month, day)
            row = Row(when, description, Decimal(price), "debit", "Subscriptions")
            if month == increase_month:
                row.anomaly = "subscription_increase"
            rows.append(row)

        for _ in range(rng.randint(2, 4)):
            when = date(START.year, month, rng.randint(1, 28))
            amount = money("800.00", "3200.00", rng)
            rows.append(Row(when, rng.choice(CLIENTS), amount, "credit", "Income"))
    return rows


def planted_anomalies() -> list[Row]:
    """Unusual transactions added on purpose, so we can test the detectors."""
    rows = []

    # 1. Spending spikes (z-score): far above the usual amount for the category
    for when, description, category, amount in [
        (date(2026, 3, 10), "UBER *EATS", "Dining", "185.00"),
        (date(2026, 4, 18), "TIM HORTONS #2231", "Dining", "142.50"),
        (date(2026, 5, 22), "COSTCO WHOLESALE #535", "Groceries", "640.00"),
    ]:
        rows.append(Row(when, description, Decimal(amount), "debit", category, "zscore"))

    # 2. Double charges: same merchant and amount again within 0-2 days
    for first, gap, description, category, amount in [
        (date(2026, 2, 16), 0, "AMAZON.CA", "Shopping", "89.99"),
        (date(2026, 4, 7), 1, "WINNERS #221", "Shopping", "54.20"),
        (date(2026, 5, 13), 2, "SHELL 4421 TORONTO ON", "Transport", "61.35"),
    ]:
        rows.append(Row(first, description, Decimal(amount), "debit", category))
        second = first + timedelta(days=gap)
        rows.append(Row(second, description, Decimal(amount), "debit", category, "duplicate"))

    # 3. Large first charge at a merchant we've never seen before
    for when, description, category, amount in [
        (date(2026, 2, 20), "BEST BUY #977", "Shopping", "1249.00"),
        (date(2026, 4, 3), "AIR CANADA", "Transport", "640.00"),
        (date(2026, 5, 28), "DENTAL CLINIC TORONTO", "Health", "420.00"),
    ]:
        rows.append(
            Row(when, description, Decimal(amount), "debit", category, "new_merchant_large")
        )

    return rows


def generate(seed: int = 42) -> list[Row]:
    """Build the whole statement, sorted by date. Same seed = same rows."""
    rng = random.Random(seed)
    rows = everyday_spending(rng) + monthly_rows(rng) + planted_anomalies()
    rows.sort(key=lambda row: row.txn_date)
    return rows


def write_files(rows: list[Row], out_dir: Path) -> None:
    """Write statement.csv, ground_truth.csv and anomalies.json."""
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "statement.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Description", "Debit", "Credit"])
        for row in rows:
            debit = row.amount if row.direction == "debit" else ""
            credit = row.amount if row.direction == "credit" else ""
            writer.writerow([row.txn_date.strftime("%m/%d/%Y"), row.description, debit, credit])

    with open(out_dir / "ground_truth.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row", "category"])
        for number, row in enumerate(rows, start=1):
            writer.writerow([number, row.category])

    planted = [
        {
            "row": number,
            "type": row.anomaly,
            "date": row.txn_date.isoformat(),
            "description": row.description,
            "amount": str(row.amount),
        }
        for number, row in enumerate(rows, start=1)
        if row.anomaly
    ]
    (out_dir / "anomalies.json").write_text(json.dumps(planted, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a synthetic bank statement.")
    parser.add_argument("--seed", type=int, default=42, help="random seed (default: 42)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output folder")
    args = parser.parse_args()

    rows = generate(args.seed)
    write_files(rows, args.out)
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
