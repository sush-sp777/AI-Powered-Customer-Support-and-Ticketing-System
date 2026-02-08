from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.users.models import User
from backend.app.users.schemas import UserCreate, UserLogin, TokenResponse
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.deps import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"user_id": db_user.id, "role": db_user.role}
    )

    return {"access_token": token}

from backend.app.auth.dependencies import get_current_user, require_role

@router.get("/me")
def get_profile(user=Depends(get_current_user)):
    return {
        "email": user.email,
        "role": user.role
    }

@router.get("/agent-only")
def agent_only(user=Depends(require_role("AGENT"))):
    return {"message": "Agent access granted"}
