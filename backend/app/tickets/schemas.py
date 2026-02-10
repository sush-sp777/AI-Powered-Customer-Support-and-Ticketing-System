from pydantic import BaseModel
from datetime import datetime
from backend.app.tickets.models import TicketCategory, TicketPriority, TicketStatus

class TicketCreate(BaseModel):
    title: str
    description: str
    category: TicketCategory

from typing import Optional

class TicketAIMetadataResponse(BaseModel):
    category: str
    priority: str
    sentiment: str
    confidence: float
    risk: str
    ai_summary: str

    class Config:
        orm_mode = True

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    ai_metadata: Optional[TicketAIMetadataResponse]
    class Config:
        orm_mode = True
