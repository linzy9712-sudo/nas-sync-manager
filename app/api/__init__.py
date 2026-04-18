from fastapi import APIRouter
from app.api.targets import router as targets_router
from app.api.tasks import router as tasks_router
from app.api.logs import router as logs_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(targets_router)
api_router.include_router(tasks_router)
api_router.include_router(logs_router)