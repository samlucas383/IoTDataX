"""
Pydantic Schemas for API Request/Response Models
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class TelemetryRecord(BaseModel):
    """Single telemetry record"""
    id: int
    device_id: str
    device_type: Optional[str] = None
    topic: str
    timestamp: datetime
    payload: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DeviceInfo(BaseModel):
    """Device summary information"""
    device_id: str
    device_type: str
    last_seen: datetime
    message_count: int


class StatsResponse(BaseModel):
    """Overall system statistics"""
    total_messages: int
    total_devices: int
    device_types: Dict[str, int]
    oldest_message: Optional[datetime] = None
    newest_message: Optional[datetime] = None


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    database: str = "unknown"
    mqtt: str = "unknown"


class DeleteResponse(BaseModel):
    """Response for delete operations"""
    status: str
    deleted_records: int
    older_than_days: int


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    status_code: int
