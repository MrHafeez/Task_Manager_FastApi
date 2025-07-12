
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import models, auth
from jose import JWTError

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        username = auth.decode_access_token(token)
        return db.query(models.User).filter(models.User.username == username).first()
    except JWTError:
        return None

@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
    tasks = db.query(models.Task).filter(models.Task.owner_id == user.id).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "tasks": tasks})

@router.post("/add-task")
def add_task(request: Request, title: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
    task = models.Task(title=title, description=description, owner_id=user.id)
    db.add(task)
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=302)

@router.get("/delete-task/{task_id}")
def delete_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user.id).first()
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse(url="/dashboard")

@router.post("/update-task/{task_id}")
def update_task(task_id: int, request: Request, title: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user.id).first()
    if task:
        task.title = title
        task.description = description
        db.commit()
    return RedirectResponse(url="/dashboard")
