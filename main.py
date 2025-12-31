import os

from fastapi import FastAPI,HTTPException
from db.api import Database
from sqlalchemy import text

app = FastAPI(debug=False if os.getenv('ENV_TYPE') == "prod" else True)
db = Database()


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.close()


@app.get("/health")
async def health():
    try:
        async with db.session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection error: {e}")
