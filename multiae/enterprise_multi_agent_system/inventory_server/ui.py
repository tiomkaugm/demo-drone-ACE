import streamlit as st
import pandas as pd
import requests
from shared.config import INVENTORY_URL

st.set_page_config(page_title="Inventory MAS", page_icon="📦", layout="wide")
st.title("📦 Inventory Department — Multi-Agent Server")
st.caption("StockAgent • ReorderAgent • ForecastAgent • WarehouseAgent")


def get(path):
    try:
        return requests.get(INVENTORY_URL+path, timeout=5).json()
    except Exception as exc:
        st.error(str(exc))
        return {}

k=get("/kpi")
a,b,c,d=st.columns(4)
a.metric("SKU",k.get("sku_count",0))
b.metric("Units on Hand",k.get("units_on_hand",0))
c.metric("Low Stock",k.get("low_stock_count",0))
d.metric("Inventory Value",f"Rp {k.get('inventory_value',0):,.0f}")

t1,t2,t3=st.tabs(["📋 Stock","🤖 Inventory Agents","🧠 Agent State"])
with t1:
    products=get("/products")
    st.dataframe(pd.DataFrame(products), width="stretch", hide_index=True)
    if products:
        with st.form("receive"):
            sku=st.selectbox("SKU",[p["sku"] for p in products])
            qty=st.number_input("Qty diterima",1,1000,10)
            if st.form_submit_button("Receive Stock"):
                msg={"sender":"inventory.ui","recipient":"inventory.stock","performative":"RECEIVE_STOCK",
                     "payload":{"sku":sku,"qty":qty,"ref":"MANUAL-RECEIPT"}}
                st.json(requests.post(INVENTORY_URL+"/agent/message", json=msg, timeout=10).json())
    st.subheader("Stock Movements")
    st.dataframe(pd.DataFrame(get("/movements")), width="stretch", hide_index=True)

with t2:
    if st.button("Run ReorderAgent", type="primary"):
        msg={"sender":"inventory.ui","recipient":"inventory.reorder","performative":"REORDER_SCAN","payload":{}}
        st.json(requests.post(INVENTORY_URL+"/agent/message",json=msg,timeout=10).json())
    sku_f=st.text_input("SKU Forecast","SKU-001")
    if st.button("Run ForecastAgent"):
        msg={"sender":"inventory.ui","recipient":"inventory.forecast","performative":"DEMAND_FORECAST","payload":{"sku":sku_f}}
        st.json(requests.post(INVENTORY_URL+"/agent/message",json=msg,timeout=10).json())

with t3:
    st.json(get("/agents"))
