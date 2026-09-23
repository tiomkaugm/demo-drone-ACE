from fastapi import FastAPI, HTTPException
from communication.message import AgentMessage
from communication.service_directory import register_service
from shared.config import INVENTORY_URL
from . import database as db
from .agents import StockAgent, ReorderAgent, ForecastAgent, WarehouseAgent

app = FastAPI(title="Inventory Multi-Agent Server")
AGENTS = {a.name:a for a in [StockAgent(),ReorderAgent(),ForecastAgent(),WarehouseAgent()]}


@app.on_event("startup")
def startup():
    db.init_db()
    for agent in AGENTS.values():
        register_service(agent.name, "inventory", INVENTORY_URL)


@app.get("/")
def home():
    return {"department":"inventory","agents":list(AGENTS)}


@app.get("/products")
def products():
    return db.products()


@app.get("/kpi")
def kpi():
    return db.kpis()


@app.get("/movements")
def movements():
    return db.movements()


@app.get("/agents")
def agents():
    return [a.status() for a in AGENTS.values()]


@app.post("/agent/message")
def receive_message(message:AgentMessage):
    if message.recipient not in AGENTS:
        raise HTTPException(404,"Inventory agent tidak ditemukan.")
    return AGENTS[message.recipient].receive(message)
