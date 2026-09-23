from shared.base_agent import BaseAgent
from . import database as db


class StockAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "inventory.stock",
            "inventory",
            ["CHECK_STOCK","RESERVE_STOCK","RELEASE_STOCK","RECEIVE_STOCK","INVENTORY_KPI"],
        )

    def on_check_stock(self, p):
        item = db.product(p["sku"])
        return {"ok": bool(item), "product": item} if item else {"ok": False, "error": "SKU tidak ditemukan."}

    def on_reserve_stock(self, p):
        return db.change_stock(p["sku"], -int(p["qty"]), "reserve", p.get("order_id",""))

    def on_release_stock(self, p):
        return db.change_stock(p["sku"], int(p["qty"]), "release", p.get("order_id",""))

    def on_receive_stock(self, p):
        return db.change_stock(p["sku"], int(p["qty"]), "receipt", p.get("ref",""))

    def on_inventory_kpi(self, p):
        return {"ok": True, **db.kpis()}


class ReorderAgent(BaseAgent):
    def __init__(self):
        super().__init__("inventory.reorder", "inventory", ["REORDER_SCAN"])

    def on_reorder_scan(self, p):
        low = []
        for item in db.products():
            if item["stock"] <= item["reorder_point"]:
                low.append({
                    "sku": item["sku"],
                    "name": item["name"],
                    "stock": item["stock"],
                    "reorder_point": item["reorder_point"],
                    "recommended_order_qty": max(item["reorder_point"]*2-item["stock"], item["reorder_point"]),
                })
        return {"ok": True, "count": len(low), "low_stock": low}


class ForecastAgent(BaseAgent):
    def __init__(self):
        super().__init__("inventory.forecast", "inventory", ["DEMAND_FORECAST"])

    def on_demand_forecast(self, p):
        item = db.product(p["sku"])
        if not item:
            return {"ok": False, "error": "SKU tidak ditemukan."}
        baseline = max(1, int(item["reorder_point"] * 0.7))
        return {
            "ok": True,
            "sku": item["sku"],
            "forecast_next_period": baseline,
            "method": "rule-based baseline; replaceable with ML model",
        }


class WarehouseAgent(BaseAgent):
    def __init__(self):
        super().__init__("inventory.warehouse", "inventory", ["WAREHOUSE_STATUS"])

    def on_warehouse_status(self, p):
        k = db.kpis()
        return {"ok": True, "utilization_proxy_pct": min(100, k["units_on_hand"]/5), **k}
