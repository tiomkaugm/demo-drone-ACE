from datetime import datetime, timezone
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Enterprise Agent Service Directory", version="1.0")


class ServiceRegistration(BaseModel):
    agent_name: str
    department: str
    base_url: str

DIRECTORY: Dict[str, dict] = {}


@app.get("/")
def home():
    return {
        "service": "agent-service-directory",
        "registered_agents": len(DIRECTORY),
        "note": "Directory untuk endpoint komunikasi. Bukan registry untuk migrasi agent.",
    }


@app.post("/register")
def register(item: ServiceRegistration):
    DIRECTORY[item.agent_name] = {
        "agent_name": item.agent_name,
        "department": item.department,
        "base_url": item.base_url.rstrip("/"),
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"ok": True, **DIRECTORY[item.agent_name]}


@app.get("/agents")
def agents():
    return list(DIRECTORY.values())


@app.get("/agents/{agent_name}")
def agent(agent_name: str):
    if agent_name not in DIRECTORY:
        raise HTTPException(404, "Agent service tidak ditemukan")
    return DIRECTORY[agent_name]
