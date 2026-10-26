from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.models import Upload
from app.db.session import get_session
from app.services.csv_formats import FormatBAdapter, FormatError
from app.services.ingest import save_upload

router = APIRouter(tags=["uploads"])

MAX_BYTES = 2 * 1024 * 1024  # 2 MB
MAX_ROWS = 5000


def error(status: int, code: str, message: str, details: list | None = None) -> JSONResponse:
    """The one error shape every endpoint uses (09-api-spec)."""
    body = {"error": {"code": code, "message": message, "details": details or []}}
    return JSONResponse(status_code=status, content=body)


def upload_json(upload: Upload) -> dict:
    return {
        "id": upload.id,
        "filename": upload.filename,
        "status": upload.status,
        "row_count": upload.row_count,
        "inserted_count": upload.inserted_count,
        "duplicate_count": upload.duplicate_count,
        "error": upload.error,
    }


@router.post("/uploads", status_code=201)
def create_upload(file: UploadFile, session: Annotated[Session, Depends(get_session)]):
    if not (file.filename or "").lower().endswith(".csv"):
        return error(415, "UNSUPPORTED_TYPE", "only .csv files are accepted")

    content = file.file.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        return error(413, "FILE_TOO_LARGE", "file is larger than 2 MB")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return error(422, "VALIDATION_FAILED", "file must be UTF-8 text")

    try:
        rows, row_errors = FormatBAdapter().parse(text)
    except FormatError as exc:
        return error(422, "VALIDATION_FAILED", str(exc))

    if row_errors:
        details = [{"row": e.row, "field": e.field, "message": e.message} for e in row_errors]
        return error(422, "VALIDATION_FAILED", f"{len(row_errors)} rows failed validation", details)
    if len(rows) > MAX_ROWS:
        return error(413, "FILE_TOO_LARGE", f"more than {MAX_ROWS} rows")

    upload = save_upload(session, file.filename, rows)
    return upload_json(upload)


@router.get("/uploads/{upload_id}")
def get_upload(upload_id: int, session: Annotated[Session, Depends(get_session)]):
    upload = session.get(Upload, upload_id)
    if upload is None:
        return error(404, "NOT_FOUND", f"upload {upload_id} not found")
    body = upload_json(upload)
    body["created_at"] = upload.created_at.isoformat()
    body["finished_at"] = upload.finished_at.isoformat() if upload.finished_at else None
    return body
