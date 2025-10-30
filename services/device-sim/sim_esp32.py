"""
ESP32 Simulator - Mimics ESP32 microcontroller behavior
- WiFi signal strength (RSSI)
- Temperature, humidity, pressure sensors
- Battery voltage monitoring
- Deep sleep cycles simulation
"""
import os
import time
import json
import random
import uuid
import threading
import paho.mqtt.client as mqtt

BROKER = os.environ.get('MQTT_BROKER', 'mosquitto')
PORT = int(os.environ.get('MQTT_PORT', 1883))
USER = os.environ.get('MQTT_USER')
PASS = os.environ.get('MQTT_PASS')
NUM_DEVICES = int(os.environ.get('NUM_DEVICES', 2))
INTERVAL = float(os.environ.get('INTERVAL', 10.0))

class ESP32Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.battery_voltage = 3.7  # Starting voltage
        self.sleep_counter = 0
        self.boot_count = 0
        
    def get_telemetry(self):
        """Generate ESP32-style telemetry data"""
        # Battery drains slowly
        self.battery_voltage = max(3.0, self.battery_voltage - random.uniform(0.001, 0.005))
        
        # Simulate occasional deep sleep (resets boot counter)
        if random.random() < 0.05:  # 5% chance
            self.boot_count += 1
            self.battery_voltage = min(4.2, self.battery_voltage + 0.1)  # "Recharged"
        
        return {
            "device_type": "ESP32",
            "device_id": self.device_id,
            "ts": int(time.time() * 1000),
            "sensors": {
                "temperature": round(random.uniform(18.0, 28.0), 2),
                "humidity": round(random.uniform(35.0, 65.0), 2),
                "pressure": round(random.uniform(980.0, 1020.0), 2),
            },
            "system": {
                "rssi": random.randint(-90, -30),  # WiFi signal strength
                "battery_voltage": round(self.battery_voltage, 2),
                "heap_free": random.randint(50000, 150000),  # Free heap memory
                "boot_count": self.boot_count,
                "uptime_sec": int(time.time() - (self.boot_count * 300))
            }
        }

def device_loop(device):
    client = mqtt.Client(client_id=device.device_id)
    if USER:
        client.username_pw_set(USER, PASS)
    
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        
        while True:
            payload = device.get_telemetry()
            topic = f"devices/{device.device_id}/telemetry"
            client.publish(topic, json.dumps(payload))
            print(f"[ESP32-{device.device_id}] Temp: {payload['sensors']['temperature']}°C | "
                  f"Battery: {payload['system']['battery_voltage']}V | "
                  f"RSSI: {payload['system']['rssi']}dBm")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

def main():
    print(f"Starting {NUM_DEVICES} ESP32 device simulators...")
    threads = []
    
    for i in range(NUM_DEVICES):
        device_id = f"esp32-{uuid.uuid4().hex[:8]}"
        device = ESP32Device(device_id)
        t = threading.Thread(target=device_loop, args=(device,), daemon=True)
        t.start()
        threads.append(t)
        print(f"✓ Started {device_id}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping ESP32 simulators...')

if __name__ == '__main__':
    main()
