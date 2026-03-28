"""Route aggregation."""

from fastapi import APIRouter

from backend.api.routes.overview import router as overview_router
from backend.api.routes.processes import router as processes_router
from backend.api.routes.opportunities import router as opportunities_router
from backend.api.routes.workflow import router as workflow_router
from backend.api.routes.copilot import router as copilot_router

api_router = APIRouter()

api_router.include_router(overview_router, tags=["Overview"])
api_router.include_router(processes_router, tags=["Processes"])
api_router.include_router(opportunities_router, tags=["Opportunities"])
api_router.include_router(workflow_router, tags=["Workflow"])
api_router.include_router(copilot_router, tags=["Copilot"])
