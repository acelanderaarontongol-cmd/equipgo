from datetime import date

from app import compute_due_date, create_app, validate_borrow


def test_health_endpoint():
    client = create_app(conn_factory=None).test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_validate_borrow_accepts_valid_payload():
    clean, error = validate_borrow({"equipment_id": 1, "borrower": " Ana ", "days": 5})
    assert error is None
    assert clean == {"equipment_id": 1, "borrower": "Ana", "days": 5}


def test_validate_borrow_defaults_days():
    clean, _ = validate_borrow({"equipment_id": 2, "borrower": "Ben"})
    assert clean["days"] == 3


def test_validate_borrow_rejects_bad_input():
    assert validate_borrow({"borrower": "Ana"})[1]
    assert validate_borrow({"equipment_id": 1, "borrower": ""})[1]
    assert validate_borrow({"equipment_id": 1, "borrower": "Ana", "days": 99})[1]
    assert validate_borrow("nope")[1]


def test_compute_due_date():
    assert compute_due_date(3, today=date(2026, 1, 1)) == date(2026, 1, 4)


def test_post_borrowings_rejects_invalid_before_touching_db():
    client = create_app(conn_factory=None).test_client()
    res = client.post("/borrowings", json={"borrower": "Ana"})
    assert res.status_code == 400
