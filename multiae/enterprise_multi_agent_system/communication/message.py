from typing import Any, Dict
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone


class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    sender: str
    recipient: str
    performative: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
