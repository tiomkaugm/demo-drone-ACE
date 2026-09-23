import streamlit as st
import pandas as pd
import requests
from shared.config import SALES_URL, INVENTORY_URL

st.set_page_config(page_title="Sales MAS", page_icon="🛒", layout="wide")
st.title("🛒 Sales Department — Multi-Agent Server")
st.caption("OrderAgent • PricingAgent • CatalogAgent • CustomerAgent")


def get(url):
    try:
        return requests.get(url, timeout=5).json()
    except Exception as exc:
        st.error(str(exc))
        return {}

k=get(SALES_URL+"/kpi")
a,b,c=st.columns(3)
a.metric("Paid Orders",k.get("orders_count",0))
b.metric("Units Sold",k.get("units_sold",0))
c.metric("Gross Sales",f"Rp {k.get('gross_sales',0):,.0f}")

products=get(INVENTORY_URL+"/products") or []
t1,t2,t3=st.tabs(["🛍️ Penjualan","🏷️ Pricing Agent","🧠 Orders & Agents"])

with t1:
    if products:
        sku=st.selectbox("Produk",[p["sku"] for p in products],
                         format_func=lambda s: next(f"{p['sku']} — {p['name']} | stock {p['stock']}" for p in products if p["sku"]==s))
        item=next(p for p in products if p["sku"]==sku)
        c1,c2,c3=st.columns(3)
        qty=c1.number_input("Qty",1,max(1,int(item["stock"])),1)
        price=c2.number_input("Unit Price",0.0,value=float(item["sell_price"]),step=1000.0)
        customer=c3.text_input("Customer","Customer Demo")
        st.info(f"Total transaksi: Rp {qty*price:,.0f}")
        if st.button("Execute Multi-Agent Sale",type="primary",width="stretch"):
            msg={"sender":"sales.ui","recipient":"sales.order","performative":"CREATE_SALE",
                 "payload":{"sku":sku,"qty":qty,"unit_price":price,"customer":customer}}
            result=requests.post(SALES_URL+"/agent/message",json=msg,timeout=20).json()
            st.json(result)
    else:
        st.warning("Data Inventory belum tersedia.")

with t2:
    if products:
        sku2=st.selectbox("SKU",[p["sku"] for p in products],key="pricing")
        item=next(p for p in products if p["sku"]==sku2)
        if st.button("Ask PricingAgent"):
            msg={"sender":"sales.ui","recipient":"sales.pricing","performative":"PRICE_RECOMMENDATION",
                 "payload":{"cost":item["cost"],"current_price":item["sell_price"],"stock":item["stock"],
                            "reorder_point":item["reorder_point"],"min_margin_pct":25}}
            st.json(requests.post(SALES_URL+"/agent/message",json=msg,timeout=10).json())

with t3:
    st.dataframe(pd.DataFrame(get(SALES_URL+"/orders")),width="stretch",hide_index=True)
    st.subheader("Internal Agent State")
    st.json(get(SALES_URL+"/agents"))
