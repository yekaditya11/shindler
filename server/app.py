"""
Schindler SafetyConnect API
Safety data ingestion and AI insights platform
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from src.config.database import init_db
from src.config.settings import settings
from src.api.routes.dataingest_routes import router as dataingest_router
from src.api.routes.ai_insights_routes import router as ai_insights_router
from src.api.routes.unified_dashboard_routes import router as unified_dashboard_router
from src.api.routes.aws_s3_routes import s3_router
from src.api.routes.data_health_routes import router as data_health_router
from src.logs.logger import setup_logging
from src.utils.response_formatter import ResponseFormatter
from src.api.routes.conversationBI_routers import conv_bi_router
from src.api.routes.saved_charts_routes import saved_charts_router


# Environment variables are loaded by settings.py

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Schindler SafetyConnect API...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down Schindler SafetyConnect API...")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint - API health check"""
    return ResponseFormatter.success_response(
        message=f"Welcome to {settings.app_name}!",
        body={
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs"
        }
    )

# Include API routers
app.include_router(dataingest_router, prefix="/api/v1", tags=["Data Ingestion"])
app.include_router(ai_insights_router, prefix="/api/v1", tags=["AI Insights"])
app.include_router(unified_dashboard_router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(data_health_router, prefix="/api/v1", tags=["Data Health"])
app.include_router(s3_router, prefix="/s3", tags=["S3"])

app.include_router(conv_bi_router,prefix="/api/v1/conversationBI",tags=["ConversationalBI"])
app.include_router(saved_charts_router, prefix="/api/v1/saved-charts", tags=["Saved Charts"])

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
