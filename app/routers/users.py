
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from app import models, schemas, auth
from app.db import SessionLocal
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        return templates.TemplateResponse("register.html", {"request": request, "msg": "User already exists"})
    hashed = auth.get_password_hash(password)
    new_user = models.User(username=username, email=email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid credentials"})
    token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
    response.set_cookie("access_token", token, httponly=True)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
