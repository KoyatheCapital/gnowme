from pydantic import BaseModel
from typing import List, Optional

class AgentContextPayload(BaseModel):
    user_id: str
    agent_id: str
    work_summary: str
    detected_human_state: List[str] = []
    current_activity_type: str = "general"
    domain: str = "general"
    confidence: float = 0.75
    urgency: str = "normal"  # low | normal | high
