import os
from contextlib import contextmanager
from datetime import date, timedelta

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request

MAX_DAYS = 14


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )


def validate_borrow(payload):
    """Return (clean_payload, error). Exactly one of them is None."""
    if not isinstance(payload, dict):
        return None, "JSON body required"
    equipment_id = payload.get("equipment_id")
    borrower = payload.get("borrower")
    days = payload.get("days", 3)
    if not isinstance(equipment_id, int) or isinstance(equipment_id, bool):
        return None, "equipment_id must be an integer"
    if not isinstance(borrower, str) or not borrower.strip():
        return None, "borrower is required"
    if not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= MAX_DAYS:
        return None, f"days must be between 1 and {MAX_DAYS}"
    return {"equipment_id": equipment_id, "borrower": borrower.strip(), "days": days}, None


def compute_due_date(days, today=None):
    return (today or date.today()) + timedelta(days=days)


def create_app(conn_factory=get_conn):
    app = Flask(__name__)

    @contextmanager
    def db():
        conn = conn_factory()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="borrow-api")

    @app.get("/borrowings")
    def list_borrowings():
        with db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """SELECT b.id, e.name AS equipment, b.borrower, b.status,
                          b.borrowed_at::text AS borrowed_at,
                          b.due_date::text AS due_date,
                          b.returned_at::text AS returned_at
                   FROM borrowings b JOIN equipment e ON e.id = b.equipment_id
                   ORDER BY b.id DESC"""
            )
            return jsonify(cur.fetchall())

    @app.post("/borrowings")
    def create_borrowing():
        clean, error = validate_borrow(request.get_json(silent=True))
        if error:
            return jsonify(error=error), 400
        with db() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM equipment WHERE id = %s", (clean["equipment_id"],))
            if cur.fetchone() is None:
                return jsonify(error="equipment not found"), 404
            # Atomic decrement: only succeeds while stock remains
            cur.execute(
                "UPDATE equipment SET available = available - 1 WHERE id = %s AND available > 0 RETURNING id",
                (clean["equipment_id"],),
            )
            if cur.fetchone() is None:
                return jsonify(error="no units available"), 409
            cur.execute(
                """INSERT INTO borrowings (equipment_id, borrower, due_date)
                   VALUES (%s, %s, %s) RETURNING id""",
                (clean["equipment_id"], clean["borrower"], compute_due_date(clean["days"])),
            )
            new_id = cur.fetchone()[0]
        return jsonify(id=new_id, status="borrowed"), 201

    @app.post("/borrowings/<int:borrowing_id>/return")
    def return_borrowing(borrowing_id):
        with db() as conn, conn.cursor() as cur:
            cur.execute(
                """UPDATE borrowings SET status = 'returned', returned_at = now()
                   WHERE id = %s AND status = 'borrowed' RETURNING equipment_id""",
                (borrowing_id,),
            )
            row = cur.fetchone()
            if row is None:
                return jsonify(error="active borrowing not found"), 404
            cur.execute("UPDATE equipment SET available = available + 1 WHERE id = %s", (row[0],))
        return jsonify(id=borrowing_id, status="returned")

    @app.get("/notifications")
    def list_notifications():
        with db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, message, created_at::text AS created_at FROM notifications ORDER BY id DESC LIMIT 20"
            )
            return jsonify(cur.fetchall())

    return app
