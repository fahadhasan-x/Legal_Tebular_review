"""
API v1 Router
Aggregates all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import projects, documents, extraction, review, field_templates

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(field_templates.router, prefix="/field-templates", tags=["Field Templates"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(extraction.router, prefix="/extraction", tags=["Extraction"])
api_router.include_router(review.router, prefix="/review", tags=["Review"])
