import streamlit as st
import pandas as pd
import requests
from shared.config import FINANCE_URL

st.set_page_config(page_title="Finance MAS", page_icon="💰", layout="wide")
st.title("💰 Finance Department — Multi-Agent Server")
st.caption("Agent tetap di Finance Server: PaymentAgent • ProfitAgent • FinanceRiskAgent")


def get(path):
    try:
        return requests.get(FINANCE_URL + path, timeout=5).json()
    except Exception as exc:
        st.error(f"Finance API tidak tersedia: {exc}")
        return {}

k = get("/kpi")
a,b,c,d = st.columns(4)
a.metric("Revenue", f"Rp {k.get('revenue',0):,.0f}")
b.metric("Cost", f"Rp {k.get('cost',0):,.0f}")
c.metric("Profit", f"Rp {k.get('profit',0):,.0f}")
d.metric("Margin", f"{k.get('margin_pct',0):.1f}%")

t1,t2 = st.tabs(["📒 Ledger", "🤖 Finance Agents"])
with t1:
    st.dataframe(pd.DataFrame(get("/ledger")), width="stretch", hide_index=True)
with t2:
    agent = st.selectbox("Agent", ["finance.profit", "finance.risk", "finance.payment"])
    perf = {
        "finance.profit":"PROFIT_ANALYSIS",
        "finance.risk":"FINANCE_RISK",
        "finance.payment":"PAYMENT_STATUS",
    }[agent]
    if st.button("Jalankan Agent", type="primary"):
        message = {"sender":"finance.ui","recipient":agent,"performative":perf,"payload":{}}
        st.json(requests.post(FINANCE_URL+"/agent/message", json=message, timeout=10).json())
    st.subheader("Internal Agent State")
    st.json(get("/agents"))
