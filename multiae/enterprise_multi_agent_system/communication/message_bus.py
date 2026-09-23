from typing import Any, Dict
import requests
from .service_directory import discover_service


def send_message(message: Dict[str, Any]) -> Dict[str, Any]:
    target = discover_service(message["recipient"])
    if target is None:
        return {
            "ok": False,
            "error": f"Recipient {message['recipient']} tidak ditemukan pada Service Directory.",
        }

    try:
        response = requests.post(
            f"{target['base_url']}/agent/message",
            json=message,
            timeout=15,
        )
        return response.json()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
