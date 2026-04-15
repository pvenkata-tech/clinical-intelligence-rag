"""
FastAPI application factory and configuration
"""

from fastapi import FastAPI
from api.routes import router as query_router
from api.monitoring_routes import router as monitoring_router
from core.config import settings


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Clinical Intelligence RAG System",
        version=settings.APP_VERSION
    )
    
    # Include routers
    app.include_router(query_router)
    app.include_router(monitoring_router)
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
