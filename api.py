from fastapi import APIRouter, HTTPException
import pandas as pd

router = APIRouter()

@router.post("/register")
async def register(email: str, general_news: bool = True, business_news: bool = True, finance_report: bool = True):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    df = pd.read_csv("./Users/users.csv")
    if email in df['email'].values:
        return {"message": "Email Already Registered"}
    else:
        new_row = pd.DataFrame([{
            'email': email,
            'general_news': int(general_news),
            'business_news': int(business_news),
            'finance_report': int(finance_report)
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv("./Users/users.csv", index=False)
        return {"message": f"Successfully Registered Email: {email} with custom preferences"}

@router.put("/update_preferences")
async def update_preferences(email: str, general_news: bool = None, business_news: bool = None, finance_report: bool = None):
    df = pd.read_csv("./Users/users.csv")
    if email not in df['email'].values:
        raise HTTPException(status_code=404, detail="Email not found")
    
    user = df.loc[df['email'] == email].iloc[0]
    if general_news is not None:
        user['general_news'] = int(general_news)
    if business_news is not None:
        user['business_news'] = int(business_news)
    if finance_report is not None:
        user['finance_report'] = int(finance_report)
    
    df.loc[df['email'] == email] = user
    df.to_csv("./Users/users.csv", index=False)
    
    return {"message": f"Successfully updated preferences for {email}"}
    