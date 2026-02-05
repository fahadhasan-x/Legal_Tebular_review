"""
Legal Tabular Review System - Backend Application
Main FastAPI application entry point
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine, create_tables

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("application_startup", environment=settings.ENVIRONMENT)
    
    # Create database tables
    await create_tables()
    logger.info("database_tables_created")
    
    yield
    
    # Shutdown
    logger.info("application_shutdown")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="Legal Tabular Review API",
    description="AI-powered legal document extraction and comparison system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0"
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Legal Tabular Review API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
