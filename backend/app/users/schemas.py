from pydantic import BaseModel, EmailStr,Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=64)   
    role: str  # USER or AGENT

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
