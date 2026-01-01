from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI,HTTPException,Request,APIRouter

templates = Jinja2Templates(directory="templates")
router=APIRouter()



@router.get("/", response_class=HTMLResponse)
async def main(request: Request):
    items=[
        {'title': 'Все книги', 'url': '#'},
        {'title': 'Предложить книгу', 'url': '#'},
        {'title': 'Создать читателя', 'url': '#'},
        {'title': 'Выдача книг', 'url': '#'},
        {'title': "Создать читательский билет", 'url': "#"}
    ]
    return templates.TemplateResponse("main.html", {"request": request, "items": items})