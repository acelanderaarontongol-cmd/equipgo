"""Background worker: turns borrowing events into notification records."""
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg2

POLL_SECONDS = 3

PENDING_SQL = """
SELECT b.id, b.status, b.borrower, e.name
FROM borrowings b JOIN equipment e ON e.id = b.equipment_id
WHERE NOT EXISTS (
    SELECT 1 FROM notifications n WHERE n.borrowing_id = b.id AND n.event = b.status
)
"""


def format_message(event, borrower, equipment):
    if event == "borrowed":
        return f"{borrower} borrowed {equipment}"
    if event == "returned":
        return f"{borrower} returned {equipment}"
    return f"{borrower}: {equipment} is now {event}"


def process_pending(conn):
    """Write one notification per new (borrowing, status). Returns how many were written."""
    count = 0
    with conn.cursor() as cur:
        cur.execute(PENDING_SQL)
        for borrowing_id, status, borrower, equipment in cur.fetchall():
            cur.execute(
                "INSERT INTO notifications (borrowing_id, event, message) VALUES (%s, %s, %s)",
                (borrowing_id, status, format_message(status, borrower, equipment)),
            )
            count += 1
    conn.commit()
    return count


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if self.path == "/health" else 404)
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}' if self.path == "/health" else b"")

    def log_message(self, *args):
        pass


def main():
    server = HTTPServer(("0.0.0.0", 8000), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    while True:
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "db"),
                dbname=os.environ.get("DB_NAME"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
            )
            while True:
                n = process_pending(conn)
                if n:
                    print(f"wrote {n} notification(s)", flush=True)
                time.sleep(POLL_SECONDS)
        except psycopg2.Error as exc:
            print(f"db error, retrying: {exc}", flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()
