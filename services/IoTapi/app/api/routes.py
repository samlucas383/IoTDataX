"""
Telemetry API Routes
REST endpoints for querying device telemetry data
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional

from app.models.schemas import (
    TelemetryRecord, 
    DeviceInfo, 
    StatsResponse, 
    DeleteResponse
)
from app.services.telemetry_service import TelemetryService
from app.api.deps import get_telemetry_service

router = APIRouter()


@router.get("/telemetry", response_model=List[TelemetryRecord])
async def get_telemetry(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: TelemetryService = Depends(get_telemetry_service)
):
    """
    Get telemetry data with optional filters
    
    - **device_id**: Filter by specific device ID
    - **device_type**: Filter by device type (ESP32, Arduino, etc.)
    - **limit**: Maximum records to return (1-1000)
    - **offset**: Offset for pagination
    """
    return await service.get_telemetry(device_id, device_type, limit, offset)


@router.get("/devices", response_model=List[DeviceInfo])
async def get_devices(
    service: TelemetryService = Depends(get_telemetry_service)
):
    """
    Get list of all devices with their latest activity
    
    Returns summary information for each device including:
    - Device ID and type
    - Last seen timestamp
    - Total message count
    """
    return await service.get_devices()


@router.get("/device/{device_id}/latest")
async def get_latest_telemetry(
    device_id: str,
    service: TelemetryService = Depends(get_telemetry_service)
):
    """
    Get the latest telemetry data for a specific device
    
    - **device_id**: The unique device identifier
    """
    result = await service.get_latest_telemetry(device_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return result


@router.get("/device/{device_id}/history")
async def get_device_history(
    device_id: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve"),
    service: TelemetryService = Depends(get_telemetry_service)
):
    """
    Get historical telemetry data for a specific device
    
    - **device_id**: The unique device identifier
    - **hours**: Number of hours of history (1-168)
    """
    return await service.get_device_history(device_id, hours)


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    service: TelemetryService = Depends(get_telemetry_service)
):
    """
    Get overall statistics about telemetry data
    
    Returns:
    - Total message count
    - Total device count
    - Breakdown by device type
    - Timestamp range (oldest/newest)
    """
    return await service.get_stats()


@router.delete("/telemetry", response_model=DeleteResponse)
async def delete_old_telemetry(
    days: int = Query(30, ge=1, le=365, description="Delete data older than N days"),
    service: TelemetryService = Depends(get_telemetry_service)
):
    """
    Delete telemetry data older than specified days
    
    - **days**: Delete records older than this many days (1-365)
    
    ⚠️ **Warning**: This operation is irreversible
    """
    deleted = await service.delete_old_telemetry(days)
    return DeleteResponse(
        status="success",
        deleted_records=deleted,
        older_than_days=days
    )


@router.get("/pipeline/stats")
async def get_pipeline_stats(request: Request):
    """
    Get ingestion pipeline statistics
    
    Shows real-time metrics for the unified ingestion algorithm:
    - Queue size
    - Total messages received
    - Total messages ingested
    - Error count
    - Success rate
    """
    if hasattr(request.app.state, 'ingestion_pipeline'):
        return request.app.state.ingestion_pipeline.get_stats()
    return {"error": "Pipeline not available"}
