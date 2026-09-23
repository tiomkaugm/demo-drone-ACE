from fastapi import FastAPI, HTTPException
from communication.message import AgentMessage
from communication.service_directory import register_service
from shared.config import FINANCE_URL
from . import database as db
from .agents import PaymentAgent, ProfitAgent, FinanceRiskAgent

app = FastAPI(title="Finance Multi-Agent Server")
AGENTS = {a.name: a for a in [PaymentAgent(), ProfitAgent(), FinanceRiskAgent()]}


@app.on_event("startup")
def startup():
    db.init_db()
    for agent in AGENTS.values():
        register_service(agent.name, "finance", FINANCE_URL)


@app.get("/")
def home():
    return {"department": "finance", "agents": list(AGENTS)}


@app.get("/kpi")
def kpi():
    return db.kpis()


@app.get("/ledger")
def ledger():
    return db.entries()


@app.get("/agents")
def agents():
    return [a.status() for a in AGENTS.values()]


@app.post("/agent/message")
def receive_message(message: AgentMessage):
    if message.recipient not in AGENTS:
        raise HTTPException(404, "Finance agent tidak ditemukan.")
    return AGENTS[message.recipient].receive(message)
