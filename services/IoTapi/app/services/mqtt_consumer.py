"""
MQTT Consumer Service
Subscribes to device telemetry and feeds unified ingestion pipeline
"""
import asyncio
from typing import Optional
import paho.mqtt.client as mqtt
from loguru import logger

from app.core.config import settings
from app.services.ingestion_pipeline import IngestionPipeline


class MQTTConsumer:
    """MQTT consumer that feeds the unified ingestion pipeline"""
    
    def __init__(self, ingestion_pipeline: IngestionPipeline):
        self.pipeline = ingestion_pipeline
        self.client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.message_count = 0
        
        if settings.MQTT_USER and settings.MQTT_PASS:
            self.client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info(f"✓ Connected to MQTT broker at {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
            client.subscribe(settings.MQTT_TOPIC)
            logger.info(f"✓ Subscribed to topic: {settings.MQTT_TOPIC}")
        else:
            logger.error(f"✗ Failed to connect to MQTT broker, code: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        if rc != 0:
            logger.warning(f"Unexpected disconnect from MQTT broker, code: {rc}")
            logger.info("Attempting to reconnect...")
    
    def on_message(self, client, userdata, msg):
        """
        Callback when message received from MQTT
        Uses unified pipeline algorithm for all device types
        """
        try:
            # Parse message using unified algorithm
            message = self.pipeline.parse_mqtt_message(msg.topic, msg.payload)
            
            if message:
                # Add to ingestion pipeline
                if not self.pipeline.ingest(message):
                    logger.warning(f"Pipeline queue full, message dropped from {message.device_id}")
                
                self.message_count += 1
                
                # Log progress periodically
                if self.message_count % 100 == 0:
                    stats = self.pipeline.get_stats()
                    logger.info(
                        f"📡 MQTT: {self.message_count} messages | "
                        f"Pipeline: {stats['total_ingested']} ingested, "
                        f"Queue: {stats['queue_size']}"
                    )
            
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def start(self):
        """Start MQTT consumer"""
        logger.info(f"Starting MQTT consumer...")
        logger.info(f"Broker: {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
        logger.info(f"Topic: {settings.MQTT_TOPIC}")
        
        self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
        self.client.loop_start()
        logger.info("✓ MQTT consumer started")
    
    def stop(self):
        """Stop MQTT consumer"""
        logger.info("Stopping MQTT consumer...")
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("✓ MQTT consumer stopped")
