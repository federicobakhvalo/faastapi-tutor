from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, Request, APIRouter
from forms._forms import *

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def main(request: Request):
    items = [
        {'title': 'Все книги', 'url': '#'},
        {'title': 'Предложить книгу', 'url': '#'},
        {'title': 'Создать читателя', 'url': '#'},
        {'title': 'Выдача книг', 'url': '#'},
        {'title': "Создать читательский билет", 'url': "#"}
    ]
    return templates.TemplateResponse("main.html", {"request": request, "items": items})


@router.get('/create_reader/', response_class=HTMLResponse)
async def create_reader_form(request: Request):
    return templates.TemplateResponse(
        "forms/form.html",
        {"request": request, "title": "Создать читателя", "form": ReaderForm()}
    )


@router.post("/create_reader/",response_class=HTMLResponse)
async def create_reader(request: Request):
    data = dict(await request.form())
    form = ReaderForm(data)
    if not form.is_valid():
        return templates.TemplateResponse(
            "forms/form.html",
            {
                "request": request,
                "title": "Создать читателя",
                "form": form
            }
        )

    print(form.cleaned_data.model_dump())

    return '<h1>HelloWorld</h1>'
