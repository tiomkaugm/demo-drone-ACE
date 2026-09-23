import requests
from shared.base_agent import BaseAgent
from shared.config import FINANCE_URL, INVENTORY_URL, SALES_URL


def safe_get(url):
    try:
        return requests.get(url,timeout=5).json()
    except Exception as exc:
        return {"error":str(exc)}


class ExecutiveAgent(BaseAgent):
    def __init__(self):
        super().__init__("management.executive","management",["ENTERPRISE_KPI","EXECUTIVE_BRIEFING"])

    def on_enterprise_kpi(self,p):
        return {
            "ok":True,
            "finance":safe_get(FINANCE_URL+"/kpi"),
            "inventory":safe_get(INVENTORY_URL+"/kpi"),
            "sales":safe_get(SALES_URL+"/kpi"),
        }

    def on_executive_briefing(self,p):
        fin=safe_get(FINANCE_URL+"/kpi")
        inv=safe_get(INVENTORY_URL+"/kpi")
        sales=safe_get(SALES_URL+"/kpi")
        briefing=[]
        briefing.append("Company profitable." if fin.get("profit",0)>0 else "Profit membutuhkan perhatian.")
        if inv.get("low_stock_count",0)>0:
            briefing.append(f"{inv['low_stock_count']} SKU berada pada kondisi low stock.")
        briefing.append(f"Paid orders tercatat: {sales.get('orders_count',0)}.")
        return {"ok":True,"briefing":briefing,"finance":fin,"inventory":inv,"sales":sales}


class EnterpriseRiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("management.risk","management",["ENTERPRISE_RISK"])

    def on_enterprise_risk(self,p):
        fin=safe_get(FINANCE_URL+"/kpi")
        inv=safe_get(INVENTORY_URL+"/kpi")
        alerts=[]
        if fin.get("margin_pct",100)<10:
            alerts.append({"domain":"finance","severity":"high","text":"Margin di bawah 10%."})
        if inv.get("low_stock_count",0)>0:
            alerts.append({"domain":"inventory","severity":"medium","text":"Low-stock SKU terdeteksi."})
        return {"ok":True,"risk_score":len(alerts),"alerts":alerts}


class StrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__("management.strategy","management",["STRATEGY_ACTIONS"])

    def on_strategy_actions(self,p):
        inv=safe_get(INVENTORY_URL+"/kpi")
        fin=safe_get(FINANCE_URL+"/kpi")
        actions=[]
        if inv.get("low_stock_count",0)>0:
            actions.append("Prioritaskan replenishment untuk SKU low-stock.")
        if fin.get("margin_pct",0)<20:
            actions.append("Review pricing dan operating cost untuk meningkatkan margin.")
        if not actions:
            actions.append("Pertahankan kebijakan operasi saat ini dan monitor KPI.")
        return {"ok":True,"recommended_actions":actions}
