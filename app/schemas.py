
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    completed: bool
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    tasks: List[Task] = []

    model_config = ConfigDict(from_attributes=True)
