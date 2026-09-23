from pathlib import Path
from shared.database import db_connect

DB = str(Path(__file__).parent / "data" / "sales.db")


def init_db():
    with db_connect(DB) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            sku TEXT,
            qty INTEGER,
            unit_price REAL,
            total REAL,
            customer TEXT,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")


def add_order(order_id, sku, qty, unit_price, total, customer, status):
    with db_connect(DB) as db:
        db.execute(
            """INSERT INTO orders(order_id,sku,qty,unit_price,total,customer,status)
               VALUES(?,?,?,?,?,?,?)""",
            (order_id,sku,qty,unit_price,total,customer,status),
        )


def orders():
    with db_connect(DB) as db:
        return [dict(r) for r in db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()]


def kpis():
    with db_connect(DB) as db:
        row=db.execute("""SELECT COUNT(*) orders_count,
                                COALESCE(SUM(qty),0) units_sold,
                                COALESCE(SUM(total),0) gross_sales
                         FROM orders WHERE status='paid'""").fetchone()
        return dict(row)
