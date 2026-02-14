from fastapi import FastAPI
from backend.app.core.database import Base, engine
from backend.app.users.models import User
from backend.app.auth.routes import router as auth_router
from backend.app.tickets.models import Ticket,TicketAIMetadata
from backend.app.tickets.routes import router as ticket_router
import logging
from backend.app.core import logging_config

logger = logging.getLogger(__name__)


app = FastAPI(title="SupportIQ Backend")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(ticket_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
