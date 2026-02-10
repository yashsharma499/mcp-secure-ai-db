from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    
    user_id: int

    
    session_id: Optional[str] = None

    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    text: str
    data: Optional[List[Dict[str, Any]]] = None


class MemoryState(BaseModel):
    last_intent: Optional[str] = None
    last_tables: List[str] = Field(default_factory=list)
    last_filters: Dict[str, Any] = Field(default_factory=dict)
    last_summary: Optional[str] = None


class PlannedAction(BaseModel):
    tool: str
    sql: Optional[str] = None
    reason: Optional[str] = None


class Plan(BaseModel):
    intent: str
    actions: List[PlannedAction]
