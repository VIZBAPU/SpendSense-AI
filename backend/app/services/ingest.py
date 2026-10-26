import hashlib
from collections import Counter
from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Transaction, Upload
from app.services.csv_formats import ParsedRow
from app.services.normalizer import normalize_merchant


def row_hashes(rows: list[ParsedRow]) -> list[str]:
    """One fingerprint per row. Identical rows in the same file get different hashes."""
    seen: Counter[tuple[str, ...]] = Counter()
    hashes = []
    for row in rows:
        key = (row.txn_date.isoformat(), row.description, row.direction, str(row.amount))
        occurrence = seen[key]
        seen[key] += 1
        raw = "|".join([*key, str(occurrence)])
        hashes.append(hashlib.sha256(raw.encode("utf-8")).hexdigest())
    return hashes


def save_upload(session: Session, filename: str, rows: list[ParsedRow]) -> Upload:
    """Save the upload and its rows in ONE transaction, skipping rows we already have."""
    upload = Upload(filename=filename, status="done", row_count=len(rows))
    session.add(upload)
    session.flush()  # sends the INSERT now, so upload.id is known

    values = [
        {
            "upload_id": upload.id,
            "txn_date": row.txn_date,
            "description_raw": row.description,
            "merchant_normalized": normalize_merchant(row.description),
            "direction": row.direction,
            "amount": row.amount,
            "row_hash": row_hash,
        }
        for row, row_hash in zip(rows, row_hashes(rows), strict=True)
    ]
    inserted = 0
    if values:
        statement = (
            insert(Transaction)
            .values(values)
            .on_conflict_do_nothing(index_elements=["row_hash"])
            .returning(Transaction.id)
        )
        inserted = len(session.execute(statement).all())

    upload.inserted_count = inserted
    upload.duplicate_count = len(rows) - inserted
    upload.finished_at = datetime.now(UTC)
    session.commit()
    return upload
