"""
STM32 Simulator - Mimics industrial-grade STM32 microcontroller
- High precision ADC readings
- Industrial sensor suite
- CAN bus simulation
- Modbus-like data structure
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
INTERVAL = float(os.environ.get('INTERVAL', 5.0))

class STM32Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.machine_state = "idle"
        self.cycle_count = 0
        self.error_count = 0
        
    def get_telemetry(self):
        """Generate STM32-style industrial telemetry data"""
        # Simulate machine state changes
        if random.random() < 0.1:
            self.machine_state = random.choice(["idle", "running", "maintenance", "error"])
            if self.machine_state == "running":
                self.cycle_count += 1
            elif self.machine_state == "error":
                self.error_count += 1
        
        return {
            "device_type": "STM32_Industrial",
            "device_id": self.device_id,
            "ts": int(time.time() * 1000),
            "sensors": {
                "temperature": round(random.uniform(15.0, 85.0), 3),
                "pressure": round(random.uniform(0.0, 10.0), 3),  # Bar
                "flow_rate": round(random.uniform(0.0, 100.0), 2),  # L/min
                "vibration": round(random.uniform(0.0, 5.0), 3),  # mm/s
            },
            "analog_inputs": {
                "ai0": random.randint(0, 4095),  # 12-bit ADC
                "ai1": random.randint(0, 4095),
                "ai2": random.randint(0, 4095),
                "ai3": random.randint(0, 4095),
            },
            "digital_inputs": {
                "di0": random.choice([True, False]),
                "di1": random.choice([True, False]),
                "emergency_stop": False,
            },
            "machine_state": {
                "status": self.machine_state,
                "cycle_count": self.cycle_count,
                "error_count": self.error_count,
                "runtime_hours": round(random.uniform(100, 5000), 1),
            },
            "system": {
                "core_temp": round(random.uniform(40.0, 70.0), 2),
                "vdd": round(random.uniform(3.25, 3.35), 3),  # Supply voltage
                "cpu_usage": random.randint(10, 95),
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
            state_icon = {"idle": "⏸️", "running": "▶️", "maintenance": "🔧", "error": "❌"}
            print(f"[STM32-{device.device_id}] {state_icon.get(payload['machine_state']['status'], '?')} "
                  f"{payload['machine_state']['status'].upper()} | "
                  f"Temp: {payload['sensors']['temperature']}°C | "
                  f"Pressure: {payload['sensors']['pressure']}bar | "
                  f"Cycles: {payload['machine_state']['cycle_count']}")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

def main():
    print(f"Starting {NUM_DEVICES} STM32 industrial simulators...")
    threads = []
    
    for i in range(NUM_DEVICES):
        device_id = f"stm32-{uuid.uuid4().hex[:8]}"
        device = STM32Device(device_id)
        t = threading.Thread(target=device_loop, args=(device,), daemon=True)
        t.start()
        threads.append(t)
        print(f"✓ Started {device_id}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping STM32 simulators...')

if __name__ == '__main__':
    main()
