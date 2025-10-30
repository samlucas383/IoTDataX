"""
Application Configuration
Centralized configuration management using environment variables
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    APP_NAME: str = "IoT Data API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql://iotuser:iotpass@postgres:5432/iotdb",
        env="DATABASE_URL"
    )
    DB_POOL_MIN_SIZE: int = Field(default=2, env="DB_POOL_MIN_SIZE")
    DB_POOL_MAX_SIZE: int = Field(default=10, env="DB_POOL_MAX_SIZE")
    
    # MQTT Settings
    MQTT_BROKER: str = Field(default="mosquitto", env="MQTT_BROKER")
    MQTT_PORT: int = Field(default=1883, env="MQTT_PORT")
    MQTT_USER: str = Field(default="", env="MQTT_USER")
    MQTT_PASS: str = Field(default="", env="MQTT_PASS")
    MQTT_TOPIC: str = Field(default="devices/+/telemetry", env="MQTT_TOPIC")
    MQTT_CLIENT_ID: str = Field(default="iot-consumer", env="MQTT_CLIENT_ID")
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]  # In production, specify allowed origins
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
