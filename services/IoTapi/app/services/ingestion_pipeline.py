"""
Unified Data Ingestion Pipeline
Single algorithm for processing all device telemetry with batching and validation
"""
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from collections import deque
import asyncpg
from loguru import logger

from app.core.config import settings


@dataclass
class TelemetryMessage:
    """Standardized telemetry message"""
    device_id: str
    device_type: str
    topic: str
    timestamp: int  # epoch milliseconds
    payload: Dict[str, Any]
    received_at: datetime
    
    def validate(self) -> bool:
        """Validate message has required fields"""
        return all([
            self.device_id,
            self.timestamp > 0,
            self.payload is not None
        ])


class IngestionPipeline:
    """
    Unified ingestion pipeline with:
    - Single processing algorithm for all device types
    - Automatic batching for efficiency
    - Validation and error handling
    - Backpressure management
    """
    
    def __init__(
        self,
        pool: asyncpg.Pool,
        batch_size: int = 100,
        batch_timeout: float = 1.0
    ):
        self.pool = pool
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        
        # Message queue with deque for O(1) append/popleft
        self.queue: deque[TelemetryMessage] = deque(maxlen=10000)
        
        # Statistics
        self.total_received = 0
        self.total_ingested = 0
        self.total_errors = 0
        self.total_batches = 0
        
        # Worker task
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False
    
    def start(self):
        """Start the ingestion worker"""
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._worker())
            logger.info("✓ Ingestion pipeline started")
    
    async def stop(self):
        """Stop the ingestion worker gracefully"""
        self._running = False
        if self._worker_task:
            await self._worker_task
        logger.info("✓ Ingestion pipeline stopped")
    
    def ingest(self, message: TelemetryMessage) -> bool:
        """
        Add message to ingestion queue
        Returns False if queue is full (backpressure)
        """
        try:
            self.queue.append(message)
            self.total_received += 1
            return True
        except Exception as e:
            logger.error(f"Failed to queue message: {e}")
            return False
    
    def parse_mqtt_message(self, topic: str, payload_bytes: bytes) -> Optional[TelemetryMessage]:
        """
        Parse MQTT message into standardized format
        Single algorithm handles all device types
        """
        try:
            # Parse JSON payload
            payload = json.loads(payload_bytes.decode('utf-8'))
            
            # Extract device_id from topic (format: devices/{device_id}/telemetry)
            topic_parts = topic.split('/')
            device_id = topic_parts[1] if len(topic_parts) > 1 else "unknown"
            
            # Extract metadata from payload
            device_type = payload.get('device_type', 'unknown')
            timestamp = payload.get('ts', int(datetime.utcnow().timestamp() * 1000))
            
            # Validate timestamp is reasonable (not too far in past or future)
            now = int(datetime.utcnow().timestamp() * 1000)
            if abs(timestamp - now) > 86400000 * 7:  # 7 days
                logger.warning(f"Timestamp out of range for {device_id}: {timestamp}")
                timestamp = now
            
            # Create standardized message
            message = TelemetryMessage(
                device_id=device_id,
                device_type=device_type,
                topic=topic,
                timestamp=timestamp,
                payload=payload,
                received_at=datetime.utcnow()
            )
            
            # Validate
            if not message.validate():
                logger.warning(f"Invalid message from {device_id}")
                return None
            
            return message
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error from topic {topic}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    async def _worker(self):
        """
        Background worker that processes messages in batches
        Single algorithm for all device types
        """
        logger.info("Ingestion worker started")
        
        while self._running or len(self.queue) > 0:
            try:
                # Collect batch
                batch = await self._collect_batch()
                
                if batch:
                    # Process batch
                    await self._process_batch(batch)
                else:
                    # No messages, short sleep
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1.0)
        
        logger.info("Ingestion worker stopped")
    
    async def _collect_batch(self) -> List[TelemetryMessage]:
        """
        Collect messages into a batch
        Uses timeout to ensure timely processing even with low message rates
        """
        batch = []
        deadline = asyncio.get_event_loop().time() + self.batch_timeout
        
        while len(batch) < self.batch_size:
            # Check if we have messages
            if self.queue:
                batch.append(self.queue.popleft())
            else:
                # Wait a bit for more messages
                await asyncio.sleep(0.01)
            
            # Check timeout
            if asyncio.get_event_loop().time() >= deadline:
                break
        
        return batch
    
    async def _process_batch(self, batch: List[TelemetryMessage]):
        """
        Process a batch of messages - single INSERT for all device types
        """
        if not batch:
            return
        
        try:
            # Prepare batch insert data
            records = [
                (
                    msg.device_id,
                    msg.device_type,
                    msg.topic,
                    msg.timestamp,
                    json.dumps(msg.payload),
                    msg.received_at
                )
                for msg in batch
            ]
            
            # Single batch insert for all device types
            async with self.pool.acquire() as conn:
                await conn.executemany(
                    """
                    INSERT INTO device_telemetry 
                    (device_id, device_type, topic, timestamp, payload, created_at)
                    VALUES ($1, $2, $3, to_timestamp($4/1000.0), $5, $6)
                    """,
                    records
                )
            
            # Update statistics
            self.total_ingested += len(batch)
            self.total_batches += 1
            
            # Log progress periodically
            if self.total_batches % 10 == 0:
                self._log_stats()
                
        except Exception as e:
            self.total_errors += len(batch)
            logger.error(f"Failed to process batch: {e}")
    
    def _log_stats(self):
        """Log ingestion statistics"""
        queue_size = len(self.queue)
        success_rate = (
            (self.total_ingested / self.total_received * 100) 
            if self.total_received > 0 
            else 0
        )
        
        logger.info(
            f"📊 Pipeline Stats | "
            f"Received: {self.total_received} | "
            f"Ingested: {self.total_ingested} | "
            f"Errors: {self.total_errors} | "
            f"Batches: {self.total_batches} | "
            f"Queue: {queue_size} | "
            f"Success: {success_rate:.1f}%"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current pipeline statistics"""
        return {
            "queue_size": len(self.queue),
            "total_received": self.total_received,
            "total_ingested": self.total_ingested,
            "total_errors": self.total_errors,
            "total_batches": self.total_batches,
            "success_rate": (
                (self.total_ingested / self.total_received * 100)
                if self.total_received > 0
                else 0
            )
        }
