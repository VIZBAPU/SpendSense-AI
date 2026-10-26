from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def post(name, content):
    return client.post("/uploads", files={"file": (name, content, "text/csv")})


def test_rejects_non_csv():
    assert post("statement.txt", b"hello").status_code == 415


def test_rejects_file_over_2_mb():
    assert post("big.csv", b"x" * (2 * 1024 * 1024 + 1)).status_code == 413


def test_rejects_wrong_headers():
    response = post("s.csv", b"When,What,Out,In\n")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_FAILED"


def test_bad_row_lists_row_number_and_saves_nothing():
    content = b"Date,Description,Debit,Credit\n13/45/2026,COFFEE,5.00,\n"
    response = post("s.csv", content)
    assert response.status_code == 422
    assert response.json()["error"]["details"][0]["row"] == 1
