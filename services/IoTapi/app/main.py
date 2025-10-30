"""
FastAPI Application Factory
Main application setup and configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import db
from app.api.routes import router as telemetry_router
from app.services.telemetry_service import TelemetryService
from app.services.mqtt_consumer import MQTTConsumer
from app.models.schemas import HealthCheck


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    
    # Initialize database
    await db.connect()
    
    # Initialize unified ingestion pipeline
    from app.services.ingestion_pipeline import IngestionPipeline
    ingestion_pipeline = IngestionPipeline(
        pool=db.get_pool(),
        batch_size=100,
        batch_timeout=1.0
    )
    ingestion_pipeline.start()
    app.state.ingestion_pipeline = ingestion_pipeline
    
    # Initialize services
    telemetry_service = TelemetryService(db.get_pool())
    app.state.telemetry_service = telemetry_service
    
    # Start MQTT consumer with unified pipeline
    mqtt_consumer = MQTTConsumer(ingestion_pipeline)
    mqtt_consumer.start()
    app.state.mqtt_consumer = mqtt_consumer
    
    logger.info("=" * 60)
    logger.info("🚀 Application started successfully")
    logger.info(f"📡 MQTT: {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
    logger.info(f"🗄️  Database: Connected")
    logger.info(f"⚡ Pipeline: Unified ingestion with batching")
    logger.info(f"🌐 API: http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📚 Docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("Shutting down application...")
    logger.info("=" * 60)
    
    if hasattr(app.state, 'mqtt_consumer'):
        app.state.mqtt_consumer.stop()
    
    if hasattr(app.state, 'ingestion_pipeline'):
        await app.state.ingestion_pipeline.stop()
    
    await db.disconnect()
    
    logger.info("✓ Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="REST API for IoT device telemetry data with MQTT ingestion",
        version=settings.APP_VERSION,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(
        telemetry_router,
        prefix=settings.API_V1_PREFIX,
        tags=["Telemetry"]
    )
    
    # Health check endpoint
    @app.get("/", response_model=HealthCheck)
    async def health_check():
        """Health check endpoint"""
        mqtt_status = "connected" if hasattr(app.state, 'mqtt_consumer') else "disconnected"
        db_status = "connected" if db.pool else "disconnected"
        
        return HealthCheck(
            status="healthy",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            database=db_status,
            mqtt=mqtt_status
        )
    
    @app.get("/health")
    async def health():
        """Simple health check"""
        return {"status": "ok"}
    
    return app


# Create application instance
app = create_app()
