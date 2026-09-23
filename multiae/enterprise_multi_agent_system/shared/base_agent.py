from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List
from communication.message import AgentMessage
from communication.message_bus import send_message


class BaseAgent:
    """
    Agent tetap (stationary agent) pada server departemennya.
    Kelas ini tidak mempunyai kemampuan migrasi host.
    """

    def __init__(self, name: str, department: str, capabilities: List[str]):
        self.name = name
        self.department = department
        self.capabilities = capabilities
        self.beliefs: Dict[str, Any] = {}
        self.goals: List[str] = []
        self.intentions: List[str] = []
        self.memory = deque(maxlen=200)

    def perceive(self, event: Dict[str, Any]) -> Dict[str, Any]:
        perception = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
        }
        self.memory.append({"phase": "perception", **perception})
        return perception

    def update_belief(self, perception: Dict[str, Any]) -> None:
        self.beliefs["last_perception"] = perception
        self.beliefs["updated_at"] = datetime.now(timezone.utc).isoformat()

    def select_goal(self, performative: str, payload: Dict[str, Any]) -> str:
        goal = f"complete::{performative}"
        self.goals.append(goal)
        return goal

    def form_intention(self, goal: str) -> str:
        intention = f"commit::{goal}"
        self.intentions.append(intention)
        return intention

    def create_plan(self, performative: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "step": 1,
                "name": "reason",
                "action": "reason",
                "status": "pending",
                "input": {"performative": performative, "payload": payload},
            },
            {
                "step": 2,
                "name": "act",
                "action": performative,
                "status": "pending",
                "input": payload,
            },
        ]

    def reason(self, performative: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        allowed = performative in self.capabilities
        return {
            "allowed": allowed,
            "decision": "execute" if allowed else "reject",
            "matched_capability": performative if allowed else None,
        }

    def act(self, performative: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        handler = getattr(self, f"on_{performative.lower()}", None)
        if handler is None:
            return {
                "ok": False,
                "error": f"{self.name} tidak mempunyai capability {performative}",
            }
        return handler(payload)

    def communicate(self, recipient: str, performative: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        message = AgentMessage(
            sender=self.name,
            recipient=recipient,
            performative=performative,
            payload=payload,
        )
        self.memory.append({"phase": "communication", "direction": "out", "message": message.model_dump()})
        return send_message(message.model_dump())

    def reflect(self, result: Dict[str, Any]) -> str:
        if result.get("ok", False):
            text = "Aksi berhasil; belief diperbarui dari hasil eksekusi."
        else:
            text = f"Aksi gagal; agent perlu revisi plan atau menjalankan compensation action. Penyebab: {result.get('error', 'unknown')}"
        self.memory.append({"phase": "reflection", "text": text})
        return text

    def receive(self, message: AgentMessage) -> Dict[str, Any]:
        perception = self.perceive(message.model_dump())
        self.update_belief(perception)

        goal = self.select_goal(message.performative, message.payload)
        intention = self.form_intention(goal)
        plan = self.create_plan(message.performative, message.payload)

        reasoning = self.reason(message.performative, message.payload)
        plan[0]["status"] = "done"
        plan[0]["result"] = reasoning

        if not reasoning["allowed"]:
            result = {"ok": False, "error": "Capability tidak diizinkan."}
        else:
            result = self.act(message.performative, message.payload)

        plan[1]["status"] = "done" if result.get("ok", False) else "failed"
        plan[1]["result"] = result

        reflection = self.reflect(result)
        self.beliefs["last_result"] = result

        return {
            "ok": result.get("ok", False),
            "agent": self.name,
            "department": self.department,
            "goal": goal,
            "intention": intention,
            "plan": plan,
            "data": result,
            "reflection": reflection,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "department": self.department,
            "capabilities": self.capabilities,
            "beliefs": self.beliefs,
            "goals": self.goals[-10:],
            "intentions": self.intentions[-10:],
            "memory_size": len(self.memory),
            "memory_tail": list(self.memory)[-10:],
            "mobility": "disabled / not implemented",
        }
