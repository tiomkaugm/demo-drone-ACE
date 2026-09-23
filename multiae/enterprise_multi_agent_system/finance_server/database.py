from pathlib import Path
from shared.database import db_connect

DB = str(Path(__file__).parent / "data" / "finance.db")


def init_db():
    with db_connect(DB) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS ledger(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            ref TEXT,
            amount REAL NOT NULL,
            note TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        if db.execute("SELECT COUNT(*) AS n FROM ledger").fetchone()["n"] == 0:
            db.executemany(
                "INSERT INTO ledger(kind,ref,amount,note) VALUES(?,?,?,?)",
                [
                    ("revenue", "OPEN-001", 15000000, "Opening revenue"),
                    ("cost", "OPEN-002", 8000000, "Opening cost"),
                    ("expense", "OPEN-003", 1800000, "Operating expense"),
                ],
            )


def add(kind, ref, amount, note=""):
    with db_connect(DB) as db:
        cur = db.execute(
            "INSERT INTO ledger(kind,ref,amount,note) VALUES(?,?,?,?)",
            (kind, ref, float(amount), note),
        )
        return cur.lastrowid


def entries(limit=200):
    with db_connect(DB) as db:
        rows = db.execute("SELECT * FROM ledger ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def kpis():
    with db_connect(DB) as db:
        rows = db.execute(
            "SELECT kind, COALESCE(SUM(amount),0) total FROM ledger GROUP BY kind"
        ).fetchall()
    sums = {r["kind"]: float(r["total"]) for r in rows}
    revenue = sums.get("revenue", 0)
    cost = sums.get("cost", 0)
    expense = sums.get("expense", 0)
    profit = revenue - cost - expense
    margin = (profit / revenue * 100) if revenue else 0
    return {
        "revenue": revenue,
        "cost": cost,
        "expense": expense,
        "profit": profit,
        "margin_pct": margin,
    }
