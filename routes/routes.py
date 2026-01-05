from fastapi.params import Query
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
        {'title': 'Все книги', 'url': '/books/'},
        {'title': 'Предложить книгу', 'url': '/create_book/'},
        {'title': 'Создать читателя', 'url': '/create_reader/'},
        {'title': 'Выдача книг', 'url': '/bookloan/'},
        {'title': "Создать читательский билет", 'url': "/readerticket/"}
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


@router.get('/books/', response_class=HTMLResponse)
async def books_list(request: Request, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
                     q: str | None = Query(None)):
    repo = BookRepository()
    books, pagination = await  repo.list(page=page, page_size=page_size, search=q)
    return templates.TemplateResponse(
        "books/book_list.html",
        {
            "request": request,
            "books": books,
            "pagination": pagination,
            "q": q,
        }
    )


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


@router.get('/bookloan/', response_class=HTMLResponse)
async def bookloan_list(request: Request, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    repo = BookLoanRepository()
    loans, pagination = await repo.list(page=page, page_size=page_size)
    return templates.TemplateResponse(
        "books/bookloan.html",
        {
            "request": request,
            "loans": loans,
            "pagination": pagination,

        }
    )


@router.get("/create_bookloan/", response_class=HTMLResponse)
async def create_bookloan_form(
        request: Request,
        book_id: int | None = Query(None),
):
    book_repo = BookRepository()
    initial = {}
    if book_id is not None:
        if await book_repo.exists(book_id):
            print("Существует книга такая")
            initial["book_id"] = book_id

    form = BookLoanForm(
        book_choices=await book_repo.list_choices(),
        reader_choices=await ReaderRepository().list_choices(),
        librarian_choices=await LibrarianRepository().list_choices(),
        initial=initial,
    )

    return templates.TemplateResponse(
        "forms/form.html",
        {
            "request": request,
            "title": "Выдача книги",
            "form": form,
        }
    )


@router.post('/create_bookloan/', response_class=HTMLResponse)
async def create_bookloan(request: Request):
    data = dict(await request.form())
    form = BookLoanForm(data, book_choices=await BookRepository().list_choices(),
                        reader_choices=await ReaderRepository().list_choices(),
                        librarian_choices=await LibrarianRepository().list_choices())

    if not form.is_valid():
        return templates.TemplateResponse(
            "forms/form.html",
            {
                "request": request,
                "title": "Выдача книги",
                "form": form,
            }
        )

    repo = BookLoanRepository()

    try:
        await repo.create(form.cleaned_data.model_dump())
    except ValueError as e:
        form.add_error(BaseForm.NON_FIELD_ERRORS, str(e))
        return templates.TemplateResponse(
            "forms/form.html",
            {
                "request": request,
                "title": "Выдача книги",
                "form": form,
            }
        )
    return RedirectResponse("/books/", status_code=303)


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


@router.get("/bookloan/{loan_id}/", response_class=HTMLResponse)
async def update_bookloan_form(request: Request, loan_id: int):
    repo = BookLoanRepository()
    loan = await repo.get(loan_id)
    if not loan:
        return RedirectResponse("/bookloan/")

    form = BookLoanUpdateForm(initial={"due_date": loan.due_date,
                                       "returned_at": loan.returned_at.date() if loan.returned_at else None})

    print(loan.due_date, loan.returned_at)

    return templates.TemplateResponse(
        "forms/form.html",
        {
            "request": request,
            "title": "Обновление выдачи",
            "form": form,
        }
    )


@router.post("/bookloan/{loan_id}/", response_class=HTMLResponse)
async def update_bookloan(
        request: Request,
        loan_id: int,
):
    data = dict(await request.form())
    form = BookLoanUpdateForm(data)

    if not form.is_valid():
        return templates.TemplateResponse(
            "forms/form.html",
            {
                "request": request,
                "title": "Обновление выдачи",
                "form": form,
            }
        )

    repo = BookLoanRepository()

    try:
        await repo.update(loan_id, form.cleaned_data.model_dump())
    except ValueError as e:
        form.add_error(form.NON_FIELD_ERRORS, str(e))
        return templates.TemplateResponse(
            "forms/form.html",
            {
                "request": request,
                "title": "Обновление выдачи",
                "form": form,
            }
        )

    return RedirectResponse("/bookloan/", status_code=303)


@router.get('/readerticket/', response_class=HTMLResponse)
async def readerticket_form(request: Request):
    reader_choices = await ReaderRepository().list_choices()
    form = ReaderTicketForm(reader_choices=reader_choices)
    return templates.TemplateResponse(
        "forms/form.html",
        {
            "request": request,
            "title": "Создать читательский билет",
            "form": form,
        }
    )


@router.post("/readerticket/", response_class=HTMLResponse)
async def create_reader_ticket(request: Request):
    data = dict(await request.form())
    reader_choices = await ReaderRepository().list_choices()
    form = ReaderTicketForm(data, reader_choices=reader_choices)

    if not form.is_valid():
        return templates.TemplateResponse(
            "forms/form.html",
            {"request": request, "title": "Создать читательский билет", "form": form},
        )

    repo = ReaderTicketRepository()
    try:
        await repo.create(form.cleaned_data.model_dump().get('reader_id', None))
    except ValueError as e:
        form.add_error("__all__", str(e))
        return templates.TemplateResponse(
            "forms/form.html",
            {"request": request, "title": "Создать читательский билет", "form": form},
        )

    return RedirectResponse("/", status_code=303)
    pass
