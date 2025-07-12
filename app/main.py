
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.db import Base, engine
from app.routers import users, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

