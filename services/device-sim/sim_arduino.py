"""
Arduino Nano 33 IoT Simulator - Mimics Arduino behavior
- 9-axis IMU (accelerometer, gyroscope, magnetometer)
- Environmental sensors
- Simple analog inputs
- Lower frequency updates
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
INTERVAL = float(os.environ.get('INTERVAL', 15.0))

class ArduinoDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.accel_offset = [random.uniform(-0.1, 0.1) for _ in range(3)]
        
    def get_telemetry(self):
        """Generate Arduino Nano 33-style telemetry data"""
        return {
            "device_type": "Arduino_Nano_33_IoT",
            "device_id": self.device_id,
            "ts": int(time.time() * 1000),
            "sensors": {
                "temperature": round(random.uniform(19.0, 26.0), 2),
                "humidity": round(random.uniform(40.0, 60.0), 2),
            },
            "imu": {
                "accel_x": round(random.uniform(-0.5, 0.5) + self.accel_offset[0], 3),
                "accel_y": round(random.uniform(-0.5, 0.5) + self.accel_offset[1], 3),
                "accel_z": round(random.uniform(9.5, 10.0) + self.accel_offset[2], 3),  # Gravity
                "gyro_x": round(random.uniform(-2.0, 2.0), 3),
                "gyro_y": round(random.uniform(-2.0, 2.0), 3),
                "gyro_z": round(random.uniform(-2.0, 2.0), 3),
            },
            "analog": {
                "a0": random.randint(0, 1023),  # 10-bit ADC
                "a1": random.randint(0, 1023),
            },
            "system": {
                "uptime_ms": int(time.time() * 1000),
                "free_ram": random.randint(10000, 30000),
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
            print(f"[Arduino-{device.device_id}] Temp: {payload['sensors']['temperature']}°C | "
                  f"Accel Z: {payload['imu']['accel_z']}m/s² | "
                  f"A0: {payload['analog']['a0']}")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

def main():
    print(f"Starting {NUM_DEVICES} Arduino Nano 33 IoT simulators...")
    threads = []
    
    for i in range(NUM_DEVICES):
        device_id = f"arduino-{uuid.uuid4().hex[:8]}"
        device = ArduinoDevice(device_id)
        t = threading.Thread(target=device_loop, args=(device,), daemon=True)
        t.start()
        threads.append(t)
        print(f"✓ Started {device_id}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping Arduino simulators...')

if __name__ == '__main__':
    main()
