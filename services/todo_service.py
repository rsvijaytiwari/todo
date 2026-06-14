from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.todo_repository import TodoRepository
from schemas.todo import TodoResponse, TodoCreate, TodoUpdate


def _to_response(todo) -> TodoResponse:
    """Map ORM Todo (with joined category) to TodoResponse."""
    return TodoResponse(
        id=todo.id,
        category_id=todo.category_id,
        task_name=todo.task_name,
        description=todo.description,
        deadline=todo.deadline,
        created_at=todo.created_at,
        category_name=todo.category.name if todo.category else None,
    )


class TodoService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = TodoRepository(db)

    async def create_todo(self, payload: TodoCreate) -> TodoResponse:
        todo = await self.repo.create(payload)
        return _to_response(todo)

    async def get_todo(self, todo_id: int) -> TodoResponse:
        todo = await self.repo.get_by_id(todo_id)
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo {todo_id} not found",
            )
        return _to_response(todo)

    async def list_todos(self, category_id: int | None = None) -> list[TodoResponse]:
        todos = await self.repo.list_all(category_id)
        return [_to_response(t) for t in todos]

    async def update_todo(self, todo_id: int, payload: TodoUpdate) -> TodoResponse:
        if not payload.model_dump(exclude_unset=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided to update",
            )
        todo = await self.repo.get_by_id(todo_id)
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo {todo_id} not found",
            )
        updated = await self.repo.update(todo, payload)
        return _to_response(updated)

    async def delete_todo(self, todo_id: int) -> int:
        todo = await self.repo.get_by_id(todo_id)
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo {todo_id} not found",
            )
        return await self.repo.delete(todo)
