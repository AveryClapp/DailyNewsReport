from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import db

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    general_news: bool = True
    business_news: bool = True
    finance_report: bool = True
    sports_news: bool = True

class UpdateRequest(BaseModel):
    email: EmailStr
    token: str
    general_news: Optional[bool] = None
    business_news: Optional[bool] = None
    finance_report: Optional[bool] = None
    sports_news: Optional[bool] = None

class AuthRequest(BaseModel):
    email: EmailStr
    token: str

@router.post("/register", status_code=201)
async def register(req: RegisterRequest):
    try:
        token = db.add_user(req.email, req.model_dump(exclude={"email"}))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {
        "message": f"Registered {req.email}",
        "token": token,
        "note": "Save this token — you'll need it to update or remove your preferences."
    }

@router.put("/update_preferences")
async def update_preferences(req: UpdateRequest):
    if not db.verify_token(req.email, req.token):
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        db.update_user(req.email, req.model_dump(exclude={"email", "token"}, exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Updated preferences for {req.email}"}

@router.delete("/unregister")
async def unregister(req: AuthRequest):
    if not db.verify_token(req.email, req.token):
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        db.delete_user(req.email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Unregistered {req.email}"}
