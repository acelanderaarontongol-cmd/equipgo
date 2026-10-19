-- Runs only the first time the named volume is empty.
CREATE TABLE IF NOT EXISTS equipment (
    id        SERIAL PRIMARY KEY,
    name      TEXT NOT NULL,
    category  TEXT NOT NULL DEFAULT 'general',
    quantity  INTEGER NOT NULL CHECK (quantity >= 0),
    available INTEGER NOT NULL CHECK (available >= 0)
);

CREATE TABLE IF NOT EXISTS borrowings (
    id           SERIAL PRIMARY KEY,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    borrower     TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'borrowed',
    borrowed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    due_date     DATE NOT NULL,
    returned_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS notifications (
    id           SERIAL PRIMARY KEY,
    borrowing_id INTEGER NOT NULL REFERENCES borrowings(id),
    event        TEXT NOT NULL,
    message      TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (borrowing_id, event)
);

INSERT INTO equipment (name, category, quantity, available) VALUES
    ('Digital Oscilloscope', 'electronics', 3, 3),
    ('Arduino Uno Kit',      'electronics', 10, 10),
    ('Digital Multimeter',   'electronics', 8, 8),
    ('Laptop (loaner)',      'computing',   5, 5);
