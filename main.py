from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
import db

db.init_db()

app = FastAPI(title="Daily News Report API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Daily News API. Visit /docs for documentation."}
