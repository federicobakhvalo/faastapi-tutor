from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import FastAPI, HTTPException, Request, APIRouter
from sqlalchemy.exc import IntegrityError

from forms._forms import *
from db.repositories import *

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def main(request: Request):
    items = [
        {'title': 'Все книги', 'url': '#'},
        {'title': 'Предложить книгу', 'url': '/create_book/'},
        {'title': 'Создать читателя', 'url': '/create_reader/'},
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


@router.get("/create_book/", response_class=HTMLResponse)
async def create_book_form(request: Request):
    author_choices = await BookAuthorRepository().list_choices()
    form = BookForm(author_choices=author_choices)
    return templates.TemplateResponse("forms/form.html", {"request": request, "title": "Создать книгу", "form": form})


@router.post('/create_book/', response_class=HTMLResponse)
async def create_book(request: Request):
    author_choices = await BookAuthorRepository().list_choices()
    data = dict(await request.form())
    form = BookForm(data, author_choices=author_choices)
    if not form.is_valid():
        return templates.TemplateResponse("forms/form.html",
                                          {'request': request, 'title': "Создать книгу", "form": form})
    # print(form.cleaned_data.model_dump())

    repo = BookRepository()
    try:
        await repo.create(form.cleaned_data.model_dump(mode='json'))
    except ValueError as e:
        form.add_error('__all__', str(e))
        return templates.TemplateResponse(
            "forms/form.html",
            {
                "request": request,
                "title": "Создать читателя",
                "form": form,
            }
        )

    return RedirectResponse("/", status_code=303)


@router.post("/create_reader/", response_class=HTMLResponse)
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
    repo = ReaderRepository()
    try:
        await repo.create(form.cleaned_data.model_dump())
    except IntegrityError:
        form.add_error(
            "__all__",
            "Не удалось сохранить данные. Возможно, такие данные уже существуют."
        )
        return templates.TemplateResponse(
            "forms/form.html",
            {
                "request": request,
                "title": "Создать читателя",
                "form": form,
            }
        )
    return RedirectResponse("/", status_code=303)
