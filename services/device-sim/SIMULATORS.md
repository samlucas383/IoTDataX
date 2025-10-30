# IoT Device Simulators

Multiple microcontroller simulators for testing your IoT platform with realistic device behavior.

## Available Simulators

### 1. ESP32 Simulator (`sim_esp32.py`)
**Mimics:** ESP32 WiFi-enabled microcontroller
**Features:**
- Environmental sensors (temperature, humidity, pressure)
- WiFi RSSI (signal strength)
- Battery voltage monitoring
- Heap memory tracking
- Deep sleep cycles simulation
- Boot counter

**Sample Output:**
```json
{
  "device_type": "ESP32",
  "device_id": "esp32-a1b2c3d4",
  "ts": 1698451234567,
  "sensors": {
    "temperature": 24.5,
    "humidity": 48.2,
    "pressure": 1013.2
  },
  "system": {
    "rssi": -65,
    "battery_voltage": 3.65,
    "heap_free": 98432,
    "boot_count": 5,
    "uptime_sec": 3600
  }
}
```

### 2. Arduino Nano 33 IoT Simulator (`sim_arduino.py`)
**Mimics:** Arduino Nano 33 IoT with IMU
**Features:**
- 9-axis IMU (accelerometer, gyroscope, magnetometer)
- Environmental sensors
- Analog inputs (10-bit ADC)
- Free RAM monitoring

**Sample Output:**
```json
{
  "device_type": "Arduino_Nano_33_IoT",
  "device_id": "arduino-e5f6a7b8",
  "ts": 1698451234567,
  "sensors": {
    "temperature": 22.3,
    "humidity": 52.1
  },
  "imu": {
    "accel_x": 0.05,
    "accel_y": -0.02,
    "accel_z": 9.81,
    "gyro_x": 0.15,
    "gyro_y": -0.08,
    "gyro_z": 0.02
  },
  "analog": {
    "a0": 512,
    "a1": 768
  }
}
```

### 3. Raspberry Pi Pico W Simulator (`sim_pico.py`)
**Mimics:** Raspberry Pi Pico W
**Features:**
- Motion detection (PIR sensor)
- Door/window sensors
- Light level (16-bit ADC)
- GPIO state monitoring
- CPU temperature
- System voltage (VSYS)

**Sample Output:**
```json
{
  "device_type": "RaspberryPi_Pico_W",
  "device_id": "pico-c9d0e1f2",
  "ts": 1698451234567,
  "sensors": {
    "temperature": 25.1,
    "motion": true,
    "door_open": false,
    "light_level": 45231
  },
  "gpio": {
    "15": true,
    "16": false,
    "17": true,
    "18": false
  }
}
```

### 4. STM32 Industrial Simulator (`sim_stm32.py`)
**Mimics:** Industrial-grade STM32 microcontroller
**Features:**
- High-precision sensors (temperature, pressure, flow, vibration)
- 12-bit analog inputs (4 channels)
- Digital inputs with emergency stop
- Machine state tracking (idle, running, maintenance, error)
- Cycle counter and error counter
- Runtime hours tracking

**Sample Output:**
```json
{
  "device_type": "STM32_Industrial",
  "device_id": "stm32-a3b4c5d6",
  "ts": 1698451234567,
  "sensors": {
    "temperature": 45.235,
    "pressure": 6.842,
    "flow_rate": 72.45,
    "vibration": 2.156
  },
  "machine_state": {
    "status": "running",
    "cycle_count": 1247,
    "error_count": 3,
    "runtime_hours": 2345.6
  }
}
```

### 5. Generic Simulator (`sim.py`)
**Mimics:** Basic IoT device
**Features:**
- Simple temperature, humidity, voltage sensors
- Lightweight and fast

## Usage

### Run Individual Simulator

```bash
# ESP32
python sim_esp32.py

# Arduino
python sim_arduino.py

# Pico
python sim_pico.py

# STM32
python sim_stm32.py
```

### Run All Simulators

```bash
python run_simulators.py
```

This will show a menu where you can:
- Run individual simulators
- Run all simulators simultaneously
- See device counts and intervals

### Environment Variables

All simulators support these environment variables:

```bash
export MQTT_BROKER=mosquitto      # MQTT broker hostname
export MQTT_PORT=1883              # MQTT port
export MQTT_USER=username          # MQTT username (optional)
export MQTT_PASS=password          # MQTT password (optional)
export NUM_DEVICES=3               # Number of devices to simulate
export INTERVAL=5                  # Seconds between messages
```

### Docker Compose

You can add individual simulators to `docker-compose.yml`:

```yaml
esp32-sim:
  build:
    context: ./services/device-sim
  image: device-sim:latest
  container_name: esp32-sim
  environment:
    - MQTT_BROKER=mosquitto
    - MQTT_PORT=1883
    - NUM_DEVICES=2
    - INTERVAL=10
  command: ["python", "sim_esp32.py"]
  networks:
    - iot-network
```

## MQTT Topics

All simulators publish to:
```
devices/{device_id}/telemetry
```

Example:
- `devices/esp32-a1b2c3d4/telemetry`
- `devices/arduino-e5f6a7b8/telemetry`
- `devices/pico-c9d0e1f2/telemetry`
- `devices/stm32-a3b4c5d6/telemetry`

## Monitoring

### View All Messages
```bash
docker exec -it mosquitto mosquitto_sub -h localhost -t "devices/+/telemetry" -v
```

### View Specific Device Type
```bash
# ESP32 devices only
docker exec -it mosquitto mosquitto_sub -h localhost -t "devices/esp32-+/telemetry" -v

# Arduino devices only
docker exec -it mosquitto mosquitto_sub -h localhost -t "devices/arduino-+/telemetry" -v
```

### Check Latency
```bash
python mqtt_latency_check.py
```

## Dependencies

```bash
pip install paho-mqtt requests
```

Or:
```bash
pip install -r requirements.txt
```

## Customization

Each simulator is a standalone Python file that you can customize:
- Modify sensor ranges and behaviors
- Add new sensor types
- Change publish intervals
- Adjust device characteristics
- Add error conditions or anomalies

## Testing Different Scenarios

### Low Battery Scenario (ESP32)
The ESP32 simulator gradually drains battery. Watch for low voltage warnings.

### Motion Detection (Pico)
The Pico simulator randomly triggers motion events. Use for testing alert systems.

### Machine Failures (STM32)
The STM32 simulator enters error states. Test your fault detection and logging.

### IMU Data (Arduino)
The Arduino provides 9-axis motion data. Test orientation and movement tracking.
