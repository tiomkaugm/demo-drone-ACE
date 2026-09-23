from pathlib import Path
from shared.database import db_connect

DB = str(Path(__file__).parent / "data" / "inventory.db")
SEED = [
    ("SKU-001","Premium Melon A",95,20,85000,120000),
    ("SKU-002","Premium Melon B",42,15,92000,135000),
    ("SKU-003","Nutrient Pack",18,25,120000,175000),
    ("SKU-004","Smart EC Sensor",12,10,325000,475000),
    ("SKU-005","Smart pH Sensor",8,10,280000,420000),
]


def init_db():
    with db_connect(DB) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS products(
            sku TEXT PRIMARY KEY,
            name TEXT,
            stock INTEGER,
            reorder_point INTEGER,
            cost REAL,
            sell_price REAL
        )""")
        if db.execute("SELECT COUNT(*) AS n FROM products").fetchone()["n"] == 0:
            db.executemany("INSERT INTO products VALUES(?,?,?,?,?,?)", SEED)
        db.execute("""CREATE TABLE IF NOT EXISTS stock_movements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT,
            kind TEXT,
            qty INTEGER,
            ref TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")


def products():
    with db_connect(DB) as db:
        return [dict(r) for r in db.execute("SELECT * FROM products ORDER BY sku").fetchall()]


def product(sku):
    with db_connect(DB) as db:
        row = db.execute("SELECT * FROM products WHERE sku=?", (sku,)).fetchone()
        return dict(row) if row else None


def change_stock(sku, delta, kind, ref=""):
    with db_connect(DB) as db:
        row = db.execute("SELECT stock FROM products WHERE sku=?", (sku,)).fetchone()
        if not row:
            return {"ok": False, "error": "SKU tidak ditemukan."}
        new_stock = int(row["stock"]) + int(delta)
        if new_stock < 0:
            return {"ok": False, "error": "Stok tidak mencukupi.", "available": int(row["stock"])}
        db.execute("UPDATE products SET stock=? WHERE sku=?", (new_stock, sku))
        db.execute(
            "INSERT INTO stock_movements(sku,kind,qty,ref) VALUES(?,?,?,?)",
            (sku, kind, abs(int(delta)), ref),
        )
        return {"ok": True, "sku": sku, "new_stock": new_stock}


def movements():
    with db_connect(DB) as db:
        return [dict(r) for r in db.execute(
            "SELECT * FROM stock_movements ORDER BY id DESC LIMIT 100"
        ).fetchall()]


def kpis():
    items = products()
    return {
        "sku_count": len(items),
        "units_on_hand": sum(i["stock"] for i in items),
        "low_stock_count": sum(i["stock"] <= i["reorder_point"] for i in items),
        "inventory_value": sum(i["stock"] * i["cost"] for i in items),
    }
