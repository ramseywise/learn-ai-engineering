-- Seed schema for top-orders-per-user.md. Runs in SQLite 3.25+ and DuckDB.
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
  order_id   INTEGER PRIMARY KEY,
  user_id    INTEGER NOT NULL,
  ordered_at TEXT    NOT NULL,  -- ISO date
  amount     NUMERIC NOT NULL
);
INSERT INTO orders VALUES
  (1, 1, '2026-01-03', 40),
  (2, 1, '2026-01-10', 15),
  (3, 1, '2026-02-01', 40),
  (4, 1, '2026-02-14', 90),
  (5, 2, '2026-01-05', 20),
  (6, 2, '2026-03-01', 20),
  (7, 3, '2026-01-20', 70),
  (8, 3, '2026-01-21', 10),
  (9, 3, '2026-02-02', 55),
  (10, 3, '2026-02-28', 5);
