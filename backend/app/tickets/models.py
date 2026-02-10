from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.app.core.database import Base


# ---- Enums ----

class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    AUTO_RESOLVED = "AUTO_RESOLVED"
    PENDING_AGENT = "PENDING_AGENT"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TicketCategory(str, enum.Enum):
    BILLING = "BILLING"
    TECHNICAL = "TECHNICAL"
    ACCOUNT = "ACCOUNT"
    GENERAL = "GENERAL"


# ---- Ticket Model ----

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    category = Column(Enum(TicketCategory), nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ relationship
    ai_metadata = relationship(
        "TicketAIMetadata",
        back_populates="ticket",
        uselist=False,
        cascade="all, delete"
    )


class TicketAIMetadata(Base):
    __tablename__ = "ticket_ai_metadata"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), unique=True)

    category = Column(String)
    priority = Column(String)
    sentiment = Column(String)
    confidence = Column(Float)
    risk = Column(String)
    ai_summary = Column(String)

    ticket = relationship("Ticket", back_populates="ai_metadata")
