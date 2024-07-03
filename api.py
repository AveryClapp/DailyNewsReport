from fastapi import APIRouter, HTTPException
import pandas as pd

router = APIRouter()

@router.get("/register")
async def test(email):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    df = pd.read_csv("./Users/users.csv")
    # If the email is already stored in the CSV
    if email in df['emails'].values:
        return {"Email Already Registered"}
    else:
        new_row = pd.DataFrame([{'emails': email}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv("./Users/users.csv", index=False)
        return {f"Successfully Registered Email: {email}"}

