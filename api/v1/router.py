from fastapi import APIRouter

from api.v1.endpoints import todos

api_router = APIRouter(prefix="/v1")
api_router.include_router(todos.router)
