from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.deps import get_db
from backend.app.core.auth_deps import get_current_user
from backend.app.tickets.models import Ticket
from backend.app.tickets.schemas import TicketCreate, TicketResponse

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        created_by=current_user["user_id"]
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket

@router.get("/my", response_model=list[TicketResponse])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    tickets = db.query(Ticket).filter(
        Ticket.created_by == current_user["user_id"]
    ).all()

    return tickets

from fastapi import HTTPException

@router.get("/all", response_model=list[TicketResponse])
def get_all_tickets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENT":
        raise HTTPException(status_code=403, detail="Not authorized")


    tickets = db.query(Ticket).all()
    return tickets
