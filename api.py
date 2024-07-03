from fastapi import APIRouter

router = APIRouter()

@router.get("/register")
async def test(email):
    return {"message": "Successfulll Registered"}

