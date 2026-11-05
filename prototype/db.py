"""Seed a small, fully synthetic business database (SQLite, in-memory or file).

No real business data, no real customers, no external service. Every row is
invented sample data for the demo/evaluation only.
"""
import sqlite3

SCHEMA = """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    segment TEXT NOT NULL
);
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price REAL NOT NULL
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL
);
"""

CUSTOMERS = [
    (1, "Ayesha Khan", "Faisalabad", "retail"),
    (2, "Bilal Ahmed", "Lahore", "wholesale"),
    (3, "Sara Malik", "Karachi", "retail"),
    (4, "Omar Farooq", "Islamabad", "wholesale"),
    (5, "Hina Raza", "Faisalabad", "retail"),
]
PRODUCTS = [
    (1, "Office Chair", "furniture", 120.0),
    (2, "Laptop Stand", "electronics", 45.0),
    (3, "Notebook Pack", "stationery", 12.0),
    (4, "Desk Lamp", "electronics", 35.0),
]
# (id, customer_id, product_id, qty, date, status)
ORDERS = [
    (1, 1, 1, 2, "2026-10-05", "delivered"),
    (2, 2, 1, 5, "2026-10-06", "delivered"),
    (3, 1, 2, 3, "2026-10-07", "delivered"),
    (4, 3, 3, 10, "2026-10-08", "pending"),
    (5, 2, 4, 4, "2026-10-09", "delivered"),
    (6, 4, 2, 2, "2026-10-10", "cancelled"),
    (7, 5, 1, 1, "2026-10-11", "delivered"),
    (8, 3, 4, 6, "2026-10-12", "delivered"),
    (9, 2, 3, 20, "2026-10-13", "delivered"),
    (10, 1, 4, 1, "2026-10-14", "pending"),
]


def seed(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO customers VALUES (?,?,?,?)", CUSTOMERS)
    conn.executemany("INSERT INTO products VALUES (?,?,?,?)", PRODUCTS)
    conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", ORDERS)
    conn.commit()


def open_db(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    seed(conn)
    return conn
