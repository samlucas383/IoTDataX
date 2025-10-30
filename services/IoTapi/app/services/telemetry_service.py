"""
Telemetry Service
Business logic for handling device telemetry data
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncpg
from loguru import logger

from app.models.schemas import TelemetryRecord, DeviceInfo, StatsResponse


class TelemetryService:
    """Service for telemetry data operations"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def get_telemetry(
        self,
        device_id: Optional[str] = None,
        device_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TelemetryRecord]:
        """Get telemetry data with optional filters"""
        query = """
            SELECT id, device_id, device_type, topic, timestamp, payload, created_at
            FROM device_telemetry
            WHERE 1=1
        """
        params = []
        param_count = 1
        
        if device_id:
            query += f" AND device_id = ${param_count}"
            params.append(device_id)
            param_count += 1
        
        if device_type:
            query += f" AND device_type = ${param_count}"
            params.append(device_type)
            param_count += 1
        
        query += f" ORDER BY timestamp DESC LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, offset])
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
            return [
                TelemetryRecord(
                    id=row['id'],
                    device_id=row['device_id'],
                    device_type=row['device_type'],
                    topic=row['topic'],
                    timestamp=row['timestamp'],
                    payload=json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
    
    async def get_devices(self) -> List[DeviceInfo]:
        """Get list of all devices with their latest activity"""
        query = """
            SELECT 
                device_id,
                device_type,
                MAX(timestamp) as last_seen,
                COUNT(*) as message_count
            FROM device_telemetry
            GROUP BY device_id, device_type
            ORDER BY last_seen DESC
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            
            return [
                DeviceInfo(
                    device_id=row['device_id'],
                    device_type=row['device_type'] or 'unknown',
                    last_seen=row['last_seen'],
                    message_count=row['message_count']
                )
                for row in rows
            ]
    
    async def get_latest_telemetry(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest telemetry data for a specific device"""
        query = """
            SELECT id, device_id, device_type, topic, timestamp, payload, created_at
            FROM device_telemetry
            WHERE device_id = $1
            ORDER BY timestamp DESC
            LIMIT 1
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, device_id)
            
            if not row:
                return None
            
            return {
                "id": row['id'],
                "device_id": row['device_id'],
                "device_type": row['device_type'],
                "topic": row['topic'],
                "timestamp": row['timestamp'],
                "payload": json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload'],
                "created_at": row['created_at']
            }
    
    async def get_device_history(self, device_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical telemetry data for a specific device"""
        query = """
            SELECT id, device_id, device_type, topic, timestamp, payload, created_at
            FROM device_telemetry
            WHERE device_id = $1 
            AND timestamp > NOW() - INTERVAL '1 hour' * $2
            ORDER BY timestamp DESC
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, device_id, hours)
            
            return [
                {
                    "id": row['id'],
                    "device_id": row['device_id'],
                    "device_type": row['device_type'],
                    "topic": row['topic'],
                    "timestamp": row['timestamp'],
                    "payload": json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload'],
                    "created_at": row['created_at']
                }
                for row in rows
            ]
    
    async def get_stats(self) -> StatsResponse:
        """Get overall statistics about telemetry data"""
        async with self.pool.acquire() as conn:
            # Total messages
            total = await conn.fetchval("SELECT COUNT(*) FROM device_telemetry")
            
            # Total devices
            devices = await conn.fetchval("SELECT COUNT(DISTINCT device_id) FROM device_telemetry")
            
            # Device types breakdown
            types = await conn.fetch("""
                SELECT device_type, COUNT(*) as count
                FROM device_telemetry
                GROUP BY device_type
            """)
            device_types = {row['device_type'] or 'unknown': row['count'] for row in types}
            
            # Timestamp range
            oldest = await conn.fetchval("SELECT MIN(timestamp) FROM device_telemetry")
            newest = await conn.fetchval("SELECT MAX(timestamp) FROM device_telemetry")
            
            return StatsResponse(
                total_messages=total,
                total_devices=devices,
                device_types=device_types,
                oldest_message=oldest,
                newest_message=newest
            )
    
    async def delete_old_telemetry(self, days: int) -> int:
        """Delete telemetry data older than specified days"""
        query = """
            DELETE FROM device_telemetry
            WHERE timestamp < NOW() - INTERVAL '1 day' * $1
        """
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, days)
            # Extract number of deleted rows from result string like "DELETE 123"
            deleted = int(result.split()[-1]) if result.split()[-1].isdigit() else 0
            
            logger.info(f"Deleted {deleted} records older than {days} days")
            return deleted
    
    async def save_telemetry(
        self,
        device_id: str,
        device_type: str,
        topic: str,
        timestamp: int,
        payload: dict
    ) -> bool:
        """Save telemetry data to database"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO device_telemetry 
                    (device_id, device_type, topic, timestamp, payload, created_at)
                    VALUES ($1, $2, $3, to_timestamp($4/1000.0), $5, NOW())
                """, device_id, device_type, topic, timestamp, json.dumps(payload))
                
            return True
        except Exception as e:
            logger.error(f"Failed to save telemetry: {e}")
            return False
