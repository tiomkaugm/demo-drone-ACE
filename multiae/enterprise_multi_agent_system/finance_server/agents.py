from shared.base_agent import BaseAgent
from . import database as db


class PaymentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "finance.payment",
            "finance",
            ["CHARGE_PAYMENT", "RECORD_EXPENSE", "PAYMENT_STATUS"],
        )

    def on_charge_payment(self, p):
        amount = float(p["amount"])
        if amount <= 0:
            return {"ok": False, "error": "Nilai pembayaran harus positif."}
        if amount > 100_000_000:
            return {"ok": False, "error": "Pembayaran > Rp100 juta memerlukan approval manual."}
        entry_id = db.add(
            "revenue",
            p.get("order_id", "SALE"),
            amount,
            "Payment captured by Finance PaymentAgent",
        )
        return {"ok": True, "entry_id": entry_id, "captured": amount}

    def on_record_expense(self, p):
        entry_id = db.add("expense", p.get("ref", "EXP"), p["amount"], p.get("note", ""))
        return {"ok": True, "entry_id": entry_id}

    def on_payment_status(self, p):
        return {"ok": True, "policy": "Auto capture <= Rp100 juta."}


class ProfitAgent(BaseAgent):
    def __init__(self):
        super().__init__("finance.profit", "finance", ["FINANCE_KPI", "PROFIT_ANALYSIS"])

    def on_finance_kpi(self, p):
        return {"ok": True, **db.kpis()}

    def on_profit_analysis(self, p):
        k = db.kpis()
        signal = "healthy" if k["profit"] > 0 and k["margin_pct"] >= 10 else "watch"
        return {"ok": True, "signal": signal, **k}


class FinanceRiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("finance.risk", "finance", ["FINANCE_RISK"])

    def on_finance_risk(self, p):
        k = db.kpis()
        alerts = []
        if k["profit"] < 0:
            alerts.append("Profit negatif.")
        if k["margin_pct"] < 10:
            alerts.append("Margin di bawah 10%.")
        return {
            "ok": True,
            "risk_level": "high" if alerts else "low",
            "alerts": alerts,
            "kpi": k,
        }
