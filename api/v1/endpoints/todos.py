from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.deps import get_db
from schemas.todo import TodoSingleResponse, TodoCreate, TodoListResponse, TodoUpdate, TodoDeleteResponse
from services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def get_service(db: DbDep) -> TodoService:
    return TodoService(db)


ServiceDep = Annotated[TodoService, Depends(get_service)]


@router.post("", response_model=TodoSingleResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate, svc: ServiceDep):
    data = await svc.create_todo(payload)
    return TodoSingleResponse(message="success", data=data)


@router.get("", response_model=TodoListResponse)
async def list_todos(svc: ServiceDep, category_id: int | None = None):
    data = await svc.list_todos(category_id)
    return TodoListResponse(message="success", data=data)


@router.get("/{todo_id}", response_model=TodoSingleResponse)
async def get_todo(todo_id: int, svc: ServiceDep):
    data = await svc.get_todo(todo_id)
    return TodoSingleResponse(message="success", data=data)


@router.patch("/{todo_id}", response_model=TodoSingleResponse)
async def update_todo(todo_id: int, payload: TodoUpdate, svc: ServiceDep):
    data = await svc.update_todo(todo_id, payload)
    return TodoSingleResponse(message="success", data=data)


@router.delete("/{todo_id}", response_model=TodoDeleteResponse)
async def delete_todo(todo_id: int, svc: ServiceDep):
    deleted_id = await svc.delete_todo(todo_id)
    return TodoDeleteResponse(message="success", deleted_id=deleted_id)
