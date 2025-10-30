#!/usr/bin/env python3
"""
MQTT Latency Monitor
Subscribes to device telemetry and calculates message latency
"""
import os
import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = os.getenv('MQTT_BROKER', 'localhost')
PORT = int(os.getenv('MQTT_PORT', 1883))
USER = os.getenv('MQTT_USER')
PASS = os.getenv('MQTT_PASS')
TOPIC = os.getenv('MQTT_TOPIC', 'devices/+/telemetry')

latencies = []

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✓ Connected to MQTT broker at {BROKER}:{PORT}")
        client.subscribe(TOPIC)
        print(f"✓ Subscribed to topic: {TOPIC}")
        print("\nMonitoring latency (press Ctrl+C to stop)...\n")
    else:
        print(f"✗ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        receive_time = time.time() * 1000  # Current time in milliseconds
        payload = json.loads(msg.payload.decode())
        
        # Extract timestamp from payload
        sent_time = payload.get('ts', 0)
        
        if sent_time > 0:
            latency_ms = receive_time - sent_time
            latencies.append(latency_ms)
            
            # Get device ID from topic (e.g., devices/sim-abc123/telemetry)
            device_id = msg.topic.split('/')[1] if '/' in msg.topic else 'unknown'
            
            print(f"[{device_id}] Latency: {latency_ms:6.2f} ms | "
                  f"Temp: {payload.get('sensors', {}).get('temperature', 'N/A')}°C")
            
            # Print statistics every 10 messages
            if len(latencies) % 10 == 0:
                avg = sum(latencies) / len(latencies)
                min_lat = min(latencies)
                max_lat = max(latencies)
                print(f"\n--- Statistics (last {len(latencies)} messages) ---")
                print(f"Avg: {avg:.2f} ms | Min: {min_lat:.2f} ms | Max: {max_lat:.2f} ms\n")
        else:
            print(f"✗ No timestamp in message from {msg.topic}")
            
    except json.JSONDecodeError:
        print(f"✗ Invalid JSON from {msg.topic}")
    except Exception as e:
        print(f"✗ Error processing message: {e}")

def main():
    client = mqtt.Client(client_id="latency-monitor", protocol=mqtt.MQTTv5)
    
    if USER:
        client.username_pw_set(USER, PASS)
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print(f"Connecting to MQTT broker at {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n--- Final Statistics ---")
        if latencies:
            avg = sum(latencies) / len(latencies)
            min_lat = min(latencies)
            max_lat = max(latencies)
            print(f"Total messages: {len(latencies)}")
            print(f"Average latency: {avg:.2f} ms")
            print(f"Min latency: {min_lat:.2f} ms")
            print(f"Max latency: {max_lat:.2f} ms")
        else:
            print("No messages received")
        client.disconnect()
    except Exception as e:
        print(f"✗ Connection error: {e}")

if __name__ == '__main__':
    main()
