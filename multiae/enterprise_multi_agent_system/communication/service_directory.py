from typing import Any, Dict, Optional
import requests
from shared.config import DIRECTORY_URL


def register_service(agent_name: str, department: str, base_url: str) -> Dict[str, Any]:
    try:
        response = requests.post(
            f"{DIRECTORY_URL}/register",
            json={
                "agent_name": agent_name,
                "department": department,
                "base_url": base_url,
            },
            timeout=3,
        )
        return response.json()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def discover_service(agent_name: str) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f"{DIRECTORY_URL}/agents/{agent_name}", timeout=3)
        if response.ok:
            return response.json()
    except Exception:
        return None
    return None
