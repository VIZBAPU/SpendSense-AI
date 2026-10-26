import csv
import io
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


@dataclass
class ParsedRow:
    row_number: int
    txn_date: date
    description: str
    direction: str  # "debit" or "credit"
    amount: Decimal


@dataclass
class RowError:
    row: int
    field: str
    message: str


class FormatError(Exception):
    """The file as a whole is wrong (e.g. wrong headers), not just one row."""


def parse_amount(raw: str) -> Decimal | None:
    """'' -> None, '12.50' -> Decimal('12.50'). Raises ValueError if invalid."""
    if raw == "":
        return None
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        raise ValueError(f"'{raw}' is not a number") from None
    if not amount.is_finite() or amount <= 0:
        raise ValueError(f"'{raw}' must be a positive amount")
    if amount.as_tuple().exponent < -2:
        raise ValueError(f"'{raw}' has more than 2 decimals")
    return amount.quantize(Decimal("0.01"))


class FormatBAdapter:
    """Reads 'Format B' bank exports: Date (MM/DD/YYYY), Description, Debit, Credit."""

    headers = ["Date", "Description", "Debit", "Credit"]

    def parse(self, text: str) -> tuple[list[ParsedRow], list[RowError]]:
        reader = csv.reader(io.StringIO(text))
        header = next(reader, None)
        if header is None or [h.strip() for h in header] != self.headers:
            raise FormatError(f"expected headers: {', '.join(self.headers)}")

        rows: list[ParsedRow] = []
        errors: list[RowError] = []
        for number, values in enumerate(reader, start=1):
            if not any(value.strip() for value in values):
                continue  # ignore blank lines
            row, row_errors = self._parse_row(number, values)
            errors.extend(row_errors)
            if row is not None:
                rows.append(row)
        return rows, errors

    def _parse_row(self, number: int, values: list[str]) -> tuple[ParsedRow | None, list[RowError]]:
        if len(values) != len(self.headers):
            return None, [RowError(number, "row", f"expected 4 columns, got {len(values)}")]
        raw_date, description, raw_debit, raw_credit = (value.strip() for value in values)
        errors: list[RowError] = []

        txn_date = None
        try:
            txn_date = datetime.strptime(raw_date, "%m/%d/%Y").date()
        except ValueError:
            errors.append(RowError(number, "Date", f"invalid date '{raw_date}'"))

        if not description:
            errors.append(RowError(number, "Description", "must not be empty"))

        debit = credit = None
        try:
            debit = parse_amount(raw_debit)
            credit = parse_amount(raw_credit)
        except ValueError as exc:
            errors.append(RowError(number, "Debit/Credit", str(exc)))
        else:
            if (debit is None) == (credit is None):
                errors.append(
                    RowError(number, "Debit/Credit", "exactly one of Debit or Credit is required")
                )

        if errors:
            return None, errors
        if debit is not None:
            return ParsedRow(number, txn_date, description, "debit", debit), []
        return ParsedRow(number, txn_date, description, "credit", credit), []
