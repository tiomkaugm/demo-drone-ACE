from fastapi import FastAPI, HTTPException
from communication.message import AgentMessage
from communication.service_directory import register_service
from shared.config import MANAGEMENT_URL
from .agents import ExecutiveAgent, EnterpriseRiskAgent, StrategyAgent

app=FastAPI(title="Management / Board Multi-Agent Server")
AGENTS={a.name:a for a in [ExecutiveAgent(),EnterpriseRiskAgent(),StrategyAgent()]}


@app.on_event("startup")
def startup():
    for agent in AGENTS.values():
        register_service(agent.name,"management",MANAGEMENT_URL)


@app.get("/")
def home():
    return {"department":"management","agents":list(AGENTS)}


@app.get("/agents")
def agents():
    return [a.status() for a in AGENTS.values()]


@app.post("/agent/message")
def receive_message(message:AgentMessage):
    if message.recipient not in AGENTS:
        raise HTTPException(404,"Management agent tidak ditemukan.")
    return AGENTS[message.recipient].receive(message)
