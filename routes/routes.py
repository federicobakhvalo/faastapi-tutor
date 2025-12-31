from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI,HTTPException,Request,APIRouter

templates = Jinja2Templates(directory="templates")
router=APIRouter()



@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная страница"})