from uuid import uuid4
import requests
from shared.base_agent import BaseAgent
from shared.config import INVENTORY_URL
from . import database as db


class CatalogAgent(BaseAgent):
    def __init__(self):
        super().__init__("sales.catalog","sales",["CATALOG"])

    def on_catalog(self,p):
        try:
            products=requests.get(INVENTORY_URL+"/products",timeout=5).json()
            return {"ok":True,"products":[x for x in products if x["stock"]>0]}
        except Exception as exc:
            return {"ok":False,"error":str(exc)}


class PricingAgent(BaseAgent):
    def __init__(self):
        super().__init__("sales.pricing","sales",["PRICE_RECOMMENDATION"])

    def on_price_recommendation(self,p):
        cost=float(p["cost"])
        current=float(p["current_price"])
        stock=int(p["stock"])
        reorder=int(p["reorder_point"])
        min_margin=float(p.get("min_margin_pct",25))/100
        floor=cost*(1+min_margin)
        scarcity_factor=1.08 if stock<=reorder else 1.0
        recommended=max(floor,current*scarcity_factor)
        return {
            "ok":True,
            "recommended_price":round(recommended,2),
            "minimum_floor":round(floor,2),
            "reason":"stock scarcity uplift" if scarcity_factor>1 else "normal stock policy",
        }


class CustomerAgent(BaseAgent):
    def __init__(self):
        super().__init__("sales.customer","sales",["CUSTOMER_SEGMENT"])

    def on_customer_segment(self,p):
        total=float(p.get("lifetime_value",0))
        if total>=10_000_000:
            segment="VIP"
        elif total>=2_000_000:
            segment="Loyal"
        else:
            segment="Standard"
        return {"ok":True,"segment":segment}


class OrderAgent(BaseAgent):
    def __init__(self):
        super().__init__("sales.order","sales",["CREATE_SALE","SALES_KPI"])

    def on_create_sale(self,p):
        order_id=p.get("order_id") or f"ORD-{uuid4().hex[:8].upper()}"
        sku=p["sku"]
        qty=int(p["qty"])
        unit_price=float(p["unit_price"])
        total=qty*unit_price

        reserve=self.communicate(
            "inventory.stock",
            "RESERVE_STOCK",
            {"sku":sku,"qty":qty,"order_id":order_id},
        )
        reserve_data=reserve.get("data",{}) if isinstance(reserve,dict) else {}
        if not reserve.get("ok",False) or not reserve_data.get("ok",False):
            return {"ok":False,"error":"Reserve stock gagal.","stage":"inventory","detail":reserve}

        payment=self.communicate(
            "finance.payment",
            "CHARGE_PAYMENT",
            {"order_id":order_id,"amount":total,"customer":p.get("customer","Walk-in")},
        )
        payment_data=payment.get("data",{}) if isinstance(payment,dict) else {}
        if not payment.get("ok",False) or not payment_data.get("ok",False):
            self.communicate(
                "inventory.stock",
                "RELEASE_STOCK",
                {"sku":sku,"qty":qty,"order_id":order_id},
            )
            return {"ok":False,"error":"Payment gagal; stock reservation dibatalkan.","stage":"finance","detail":payment}

        db.add_order(order_id,sku,qty,unit_price,total,p.get("customer","Walk-in"),"paid")
        return {
            "ok":True,
            "order_id":order_id,
            "sku":sku,
            "qty":qty,
            "unit_price":unit_price,
            "total":total,
            "inventory_confirmation":reserve_data,
            "payment_confirmation":payment_data,
        }

    def on_sales_kpi(self,p):
        return {"ok":True,**db.kpis()}
