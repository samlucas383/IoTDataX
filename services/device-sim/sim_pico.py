"""
Raspberry Pi Pico W Simulator - Mimics Pico W behavior
- Lower power consumption simulation
- GPIO state monitoring
- Temperature sensor
- Simple binary sensors (motion, door, etc.)
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
INTERVAL = float(os.environ.get('INTERVAL', 8.0))

class PicoDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.gpio_states = {i: random.choice([True, False]) for i in [15, 16, 17, 18]}
        self.motion_detected = False
        
    def get_telemetry(self):
        """Generate Raspberry Pi Pico W-style telemetry data"""
        # Randomly toggle motion detection
        if random.random() < 0.1:
            self.motion_detected = not self.motion_detected
        
        # Occasionally toggle GPIO states
        if random.random() < 0.15:
            pin = random.choice(list(self.gpio_states.keys()))
            self.gpio_states[pin] = not self.gpio_states[pin]
        
        return {
            "device_type": "RaspberryPi_Pico_W",
            "device_id": self.device_id,
            "ts": int(time.time() * 1000),
            "sensors": {
                "temperature": round(random.uniform(20.0, 30.0), 2),
                "motion": self.motion_detected,
                "door_open": random.choice([True, False]) if random.random() < 0.05 else False,
                "light_level": random.randint(0, 65535),  # 16-bit ADC
            },
            "gpio": self.gpio_states.copy(),
            "system": {
                "cpu_temp": round(random.uniform(35.0, 50.0), 2),
                "vsys": round(random.uniform(4.8, 5.2), 2),  # System voltage
                "uptime_sec": int(time.time() % 86400),
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
            motion_str = "🚶 MOTION" if payload['sensors']['motion'] else "       "
            print(f"[Pico-{device.device_id}] {motion_str} | "
                  f"Temp: {payload['sensors']['temperature']}°C | "
                  f"Light: {payload['sensors']['light_level']}")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

def main():
    print(f"Starting {NUM_DEVICES} Raspberry Pi Pico W simulators...")
    threads = []
    
    for i in range(NUM_DEVICES):
        device_id = f"pico-{uuid.uuid4().hex[:8]}"
        device = PicoDevice(device_id)
        t = threading.Thread(target=device_loop, args=(device,), daemon=True)
        t.start()
        threads.append(t)
        print(f"✓ Started {device_id}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping Pico simulators...')

if __name__ == '__main__':
    main()
