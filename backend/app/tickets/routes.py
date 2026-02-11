from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from backend.app.core.deps import get_db
from backend.app.core.auth_deps import get_current_user
from backend.app.tickets.models import (
    Ticket,
    TicketAIMetadata,
    TicketStatus
)
from backend.app.tickets.schemas import TicketCreate, TicketResponse
from backend.app.ai.triage import run_ai_triage

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 1️⃣ Create ticket (initially OPEN)
    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        status=TicketStatus.OPEN,
        created_by=current_user["user_id"]
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    # 2️⃣ Run AI Triage
    ai_data = run_ai_triage(ticket.title, ticket.description)

    # 3️⃣ Save AI metadata
    ai_meta = TicketAIMetadata(
        ticket_id=new_ticket.id,
        **ai_data
    )

    db.add(ai_meta)

    # 4️⃣ Decision Engine
    if ai_data["confidence"] >= 0.85 and ai_data["risk"] == "LOW":
        new_ticket.status = TicketStatus.AUTO_RESOLVED
    else:
        new_ticket.status = TicketStatus.PENDING_AGENT

    db.commit()
    db.refresh(new_ticket)

    return new_ticket


@router.get("/my", response_model=list[TicketResponse])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return (
        db.query(Ticket)
        .options(joinedload(Ticket.ai_metadata))
        .filter(Ticket.created_by == current_user["user_id"])
        .all()
    )


@router.get("/all", response_model=list[TicketResponse])
def get_all_tickets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENT":
        raise HTTPException(status_code=403, detail="Not authorized")

    return (
        db.query(Ticket)
        .options(joinedload(Ticket.ai_metadata))
        .all()
    )
