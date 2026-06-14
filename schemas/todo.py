from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---------- Request schemas ----------

class TodoCreate(BaseModel):
    category_id: int | None = None
    task_name: str
    description: str | None = None
    deadline: datetime | None = None


class TodoUpdate(BaseModel):
    category_id: int | None = None
    task_name: str | None = None
    description: str | None = None
    deadline: datetime | None = None


# ---------- Response schemas ----------

class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None
    task_name: str
    description: str | None
    deadline: datetime | None
    created_at: datetime
    category_name: str | None = None


class TodoListResponse(BaseModel):
    message: str
    data: list[TodoResponse]


class TodoSingleResponse(BaseModel):
    message: str
    data: TodoResponse


class TodoDeleteResponse(BaseModel):
    message: str
    deleted_id: int
