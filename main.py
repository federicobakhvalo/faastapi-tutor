import os

from fastapi import FastAPI, HTTPException, Request

from config.db_config import DBSettings

from db.api import Database
from sqlalchemy import text
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from db.db_entry import db
from routes.routes import router
from fastapi.staticfiles import StaticFiles

app = FastAPI(debug=False if os.getenv('ENV_TYPE') == "prod" else True)

app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.close()


@app.get("/health")
async def health():
    try:
        async with db.get_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection error: {e}")
