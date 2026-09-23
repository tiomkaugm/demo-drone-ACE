import streamlit as st
import requests
import pandas as pd
from shared.config import MANAGEMENT_URL, FINANCE_URL, INVENTORY_URL, SALES_URL, DIRECTORY_URL

st.set_page_config(page_title="Board MAS", page_icon="🏢", layout="wide")
st.title("🏢 Board of Directors — Multi-Agent Enterprise Cockpit")
st.caption("ExecutiveAgent • EnterpriseRiskAgent • StrategyAgent")


def get(url):
    try:
        return requests.get(url,timeout=5).json()
    except Exception:
        return {}

fin=get(FINANCE_URL+"/kpi")
inv=get(INVENTORY_URL+"/kpi")
sales=get(SALES_URL+"/kpi")

a,b,c,d=st.columns(4)
a.metric("Profit",f"Rp {fin.get('profit',0):,.0f}")
b.metric("Margin",f"{fin.get('margin_pct',0):.1f}%")
c.metric("Low Stock",inv.get("low_stock_count",0))
d.metric("Paid Orders",sales.get("orders_count",0))

t1,t2,t3,t4=st.tabs(["📊 Executive","⚠️ Risk","🧭 Strategy","🌐 Agent Directory"])

with t1:
    if st.button("Generate Executive Briefing",type="primary"):
        msg={"sender":"management.ui","recipient":"management.executive","performative":"EXECUTIVE_BRIEFING","payload":{}}
        result=requests.post(MANAGEMENT_URL+"/agent/message",json=msg,timeout=15).json()
        for line in result.get("data",{}).get("briefing",[]):
            st.write("•",line)
        st.json(result)

with t2:
    if st.button("Run EnterpriseRiskAgent"):
        msg={"sender":"management.ui","recipient":"management.risk","performative":"ENTERPRISE_RISK","payload":{}}
        st.json(requests.post(MANAGEMENT_URL+"/agent/message",json=msg,timeout=15).json())

with t3:
    if st.button("Run StrategyAgent"):
        msg={"sender":"management.ui","recipient":"management.strategy","performative":"STRATEGY_ACTIONS","payload":{}}
        st.json(requests.post(MANAGEMENT_URL+"/agent/message",json=msg,timeout=15).json())

with t4:
    directory=get(DIRECTORY_URL+"/agents")
    if directory:
        st.dataframe(pd.DataFrame(directory),width="stretch",hide_index=True)
    else:
        st.warning("Service Directory belum berisi agent.")
    st.subheader("Management Agent State")
    st.json(get(MANAGEMENT_URL+"/agents"))
