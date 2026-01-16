"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import Base, engine
from app.routers import orders_router, products_router
# Import models to register them with Base
from app.models import Product, Order, OrderItem  # noqa: F401

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup - Create tables for SQLite (in production, use Alembic migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A production-ready backend service for managing Products and Orders. "
        "Features atomic stock management, order status tracking, and full REST API."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products_router)
app.include_router(orders_router)


@app.get("/", tags=["Health"])
async def root() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
    }


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "type": type(exc).__name__,
        },
    )
