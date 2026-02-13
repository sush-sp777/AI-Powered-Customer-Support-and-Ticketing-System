from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from backend.app.core.deps import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.users.models import User

from backend.app.tickets.models import (
    Ticket,
    TicketAIMetadata,
    TicketStatus,
    TicketMessage
)

from backend.app.tickets.schemas import (
    TicketCreate,
    TicketResponse,
    TicketReply
)

from backend.app.ai.triage import run_ai_triage
from backend.app.ai.reply_generator import (
    generate_auto_reply,
    generate_agent_draft
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    # 1️⃣ Run AI Triage FIRST
    ai_data = run_ai_triage(ticket.title, ticket.description)

    # 2️⃣ Create Ticket WITH AI category & priority
    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        category=ai_data["category"],      # ✅ FIX
        priority=ai_data["priority"],      # ✅ FIX
        status=TicketStatus.OPEN,
        created_by=current_user.id
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    # 3️⃣ Save USER message
    user_message = TicketMessage(
        ticket_id=new_ticket.id,
        sender_id=current_user.id,
        sender_role="USER",
        message=ticket.description
    )
    db.add(user_message)

    # 4️⃣ Save AI metadata
    ai_meta = TicketAIMetadata(
        ticket_id=new_ticket.id,
        category=ai_data["category"],
        priority=ai_data["priority"],
        sentiment=ai_data["sentiment"],
        risk=ai_data["risk"],
        confidence=ai_data["confidence"],
        ai_summary=ai_data["ai_summary"]
    )
    db.add(ai_meta)

    # 5️⃣ Decision Engine
    if ai_data["confidence"] >= 0.70 and ai_data["risk"] == "LOW":
        new_ticket.status = TicketStatus.AUTO_RESOLVED

        ai_reply_text = generate_auto_reply(
            ticket.title,
            ticket.description,
            ai_data
        )

        ai_message = TicketMessage(
            ticket_id=new_ticket.id,
            sender_id=None,
            sender_role="AI",
            message=ai_reply_text
        )
        db.add(ai_message)

    else:
        new_ticket.status = TicketStatus.PENDING_AGENT

    db.commit()
    db.refresh(new_ticket)

    return new_ticket
@router.get("/my", response_model=list[TicketResponse])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return (
        db.query(Ticket)
        .options(joinedload(Ticket.ai_metadata))
        .filter(Ticket.created_by == current_user.id)
        .all()
    )

@router.get("/agent/pending", response_model=list[TicketResponse])
def get_pending_tickets_for_agent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only AGENT can access
    if current_user.role != "AGENT":
        raise HTTPException(status_code=403, detail="Not authorized")

    tickets = (
        db.query(Ticket)
        .options(joinedload(Ticket.ai_metadata))
        .filter(Ticket.status == TicketStatus.PENDING_AGENT)
        .all()
    )

    return tickets

@router.post("/{ticket_id}/generate-draft")
def generate_draft_for_agent(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    if current_user.role != "AGENT":
        raise HTTPException(status_code=403, detail="Not authorized")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    messages = (
        db.query(TicketMessage)
        .filter(TicketMessage.ticket_id == ticket_id)
        .order_by(TicketMessage.created_at.asc())
        .all()
    )

    draft = generate_agent_draft(ticket, messages)

    return {"draft": draft}

@router.post("/{ticket_id}/reply")
def reply_to_ticket(
    ticket_id: int,
    reply: TicketReply,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role == "USER":

        if ticket.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        sender_role = "USER"
        ticket.status = TicketStatus.PENDING_AGENT

    elif current_user.role == "AGENT":

        sender_role = "AGENT"
        ticket.status = TicketStatus.WAITING_FOR_USER

    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_message = TicketMessage(
        ticket_id=ticket_id,
        sender_id=current_user.id,
        sender_role=sender_role,
        message=reply.message
    )

    db.add(new_message)
    db.commit()
    db.refresh(ticket)

    return {"message": "Reply added successfully"}

@router.get("/{ticket_id}/messages")
def get_ticket_messages(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # USER can only see own tickets
    if current_user.role == "USER" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    messages = (
        db.query(TicketMessage)
        .filter(TicketMessage.ticket_id == ticket_id)
        .order_by(TicketMessage.created_at.asc())
        .all()
    )

    return messages

@router.post("/{ticket_id}/close")
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role == "USER":
        if ticket.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    elif current_user.role != "AGENT":
        raise HTTPException(status_code=403, detail="Not authorized")

    ticket.status = TicketStatus.CLOSED

    db.commit()
    db.refresh(ticket)

    return {"message": "Ticket closed successfully"}
