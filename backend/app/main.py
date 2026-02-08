from fastapi import FastAPI
from backend.app.core.database import Base, engine
from backend.app.users.models import User
from backend.app.auth.routes import router as auth_router

app = FastAPI(title="SupportIQ Backend")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
