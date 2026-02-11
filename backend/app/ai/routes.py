from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.deps import get_db
from backend.app.core.auth_deps import get_current_user
from backend.app.tickets.models import Ticket
from backend.app.ai.rag import generate_draft_reply

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate-reply/{ticket_id}")
def generate_reply(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENT":
        raise HTTPException(status_code=403, detail="Not authorized")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket or not ticket.ai_metadata:
        raise HTTPException(status_code=404, detail="Ticket or AI metadata not found")

    draft = generate_draft_reply({
        "category": ticket.ai_metadata.category
    })

    return {
        "ticket_id": ticket_id,
        "draft_reply": draft
    }
