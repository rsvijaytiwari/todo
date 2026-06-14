from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.todo import Todo
from schemas.todo import TodoCreate, TodoUpdate


class TodoRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: TodoCreate) -> Todo:
        todo = Todo(**payload.model_dump())
        self.db.add(todo)
        await self.db.flush()
        await self.db.refresh(todo)
        return todo

    async def get_by_id(self, todo_id: int) -> Todo | None:
        stmt = (
            select(Todo)
            .options(joinedload(Todo.category))
            .where(Todo.id == todo_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().one_or_none()

    async def list_all(self, category_id: int | None = None) -> list[Todo]:
        stmt = select(Todo).options(joinedload(Todo.category))
        if category_id is not None:
            stmt = stmt.where(Todo.category_id == category_id)
        stmt = stmt.order_by(Todo.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, todo: Todo, payload: TodoUpdate) -> Todo:
        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(todo, field, value)
        await self.db.flush()
        await self.db.refresh(todo)
        return todo

    async def delete(self, todo: Todo) -> int:
        todo_id = todo.id
        await self.db.delete(todo)
        await self.db.flush()
        return todo_id
