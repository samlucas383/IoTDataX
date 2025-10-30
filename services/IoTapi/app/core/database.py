"""
Database Connection Management
Handles PostgreSQL connection pool and table initialization
"""
import asyncpg
from loguru import logger
from typing import Optional

from app.core.config import settings


class Database:
    """Database connection pool manager"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Initialize database connection pool"""
        logger.info("Initializing database connection pool...")
        self.pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE
        )
        logger.info(f"✓ Database pool created (min={settings.DB_POOL_MIN_SIZE}, max={settings.DB_POOL_MAX_SIZE})")
        await self._create_tables()
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("✓ Database pool closed")
    
    async def _create_tables(self):
        """Create database tables and indexes if they don't exist"""
        async with self.pool.acquire() as conn:
            # Create device_telemetry table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS device_telemetry (
                    id SERIAL PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    device_type VARCHAR(100),
                    topic VARCHAR(255),
                    timestamp TIMESTAMP,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes for better query performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_device_telemetry_device_id 
                ON device_telemetry(device_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_device_telemetry_timestamp 
                ON device_telemetry(timestamp DESC)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_device_telemetry_device_type 
                ON device_telemetry(device_type)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_device_telemetry_created_at 
                ON device_telemetry(created_at DESC)
            """)
            
            logger.info("✓ Database tables and indexes ready")
    
    def get_pool(self) -> asyncpg.Pool:
        """Get the connection pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        return self.pool


# Global database instance
db = Database()
