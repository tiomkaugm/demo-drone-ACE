from fastapi import FastAPI, HTTPException
from communication.message import AgentMessage
from communication.service_directory import register_service
from shared.config import SALES_URL
from . import database as db
from .agents import CatalogAgent, PricingAgent, CustomerAgent, OrderAgent

app=FastAPI(title="Sales Multi-Agent Server")
AGENTS={a.name:a for a in [CatalogAgent(),PricingAgent(),CustomerAgent(),OrderAgent()]}


@app.on_event("startup")
def startup():
    db.init_db()
    for agent in AGENTS.values():
        register_service(agent.name,"sales",SALES_URL)


@app.get("/")
def home():
    return {"department":"sales","agents":list(AGENTS)}


@app.get("/orders")
def orders():
    return db.orders()


@app.get("/kpi")
def kpi():
    return db.kpis()


@app.get("/agents")
def agents():
    return [a.status() for a in AGENTS.values()]


@app.post("/agent/message")
def receive_message(message:AgentMessage):
    if message.recipient not in AGENTS:
        raise HTTPException(404,"Sales agent tidak ditemukan.")
    return AGENTS[message.recipient].receive(message)
