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
    general_news: Optional[bool] = None
    business_news: Optional[bool] = None
    finance_report: Optional[bool] = None
    sports_news: Optional[bool] = None

class EmailRequest(BaseModel):
    email: EmailStr

@router.post("/register", status_code=201)
async def register(req: RegisterRequest):
    try:
        db.add_user(req.email, req.model_dump(exclude={"email"}))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"message": f"Registered {req.email}"}

@router.put("/update_preferences")
async def update_preferences(req: UpdateRequest):
    try:
        db.update_user(req.email, req.model_dump(exclude={"email"}, exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Updated preferences for {req.email}"}

@router.delete("/unregister")
async def unregister(req: EmailRequest):
    try:
        db.delete_user(req.email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Unregistered {req.email}"}
