"""
API Dependencies
Dependency injection for services
"""
from fastapi import Request

from app.services.telemetry_service import TelemetryService


def get_telemetry_service(request: Request) -> TelemetryService:
    """Get telemetry service instance from app state"""
    return request.app.state.telemetry_service
