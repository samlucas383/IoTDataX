# Docker-Based Device Simulators

## Overview
Each device simulator type runs in its own dedicated Docker container, creating a realistic distributed IoT environment where MQTT must handle connections from multiple network endpoints.

## Active Simulator Containers

| Container Name | Device Type | # Devices | Publish Interval | Status |
|---------------|-------------|-----------|------------------|---------|
| `device-sim` | Generic IoT | 2 | 10s | ✅ Running |
| `device-sim-esp32` | ESP32 WiFi | 2 | 8s | ✅ Running |
| `device-sim-arduino` | Arduino Nano 33 IoT | 2 | 6s | ✅ Running |
| `device-sim-pico` | Raspberry Pi Pico W | 2 | 7s | ✅ Running |
| `device-sim-stm32` | STM32 Industrial | 1 | 5s | ✅ Running |

**Total Active Devices:** 9 simulated IoT devices across 5 containers

## Architecture Benefits

### Distributed Network Topology
- Each simulator runs in an isolated container with its own network endpoint
- Mosquitto broker receives connections from 5 different sources
- Simulates real-world scenarios with devices at different locations

### Independent Lifecycle Management
- Start/stop individual device types without affecting others
- Scale specific device types by adjusting `NUM_DEVICES` environment variable
- Different publish intervals simulate various device characteristics

### Resource Isolation
- Each container has its own CPU/memory allocation
- Python interpreter isolation prevents cross-contamination
- Independent restart policies for fault tolerance

## Docker Commands

### View All Simulator Containers
```bash
docker ps --filter "name=device-sim"
```

### View Live Logs from All Simulators
```bash
docker compose logs -f device-sim device-sim-esp32 device-sim-arduino device-sim-pico device-sim-stm32
```

### View Logs from Specific Simulator
```bash
docker logs device-sim-esp32 -f
```

### Restart Specific Simulator
```bash
docker compose restart device-sim-arduino
```

### Stop All Simulators
```bash
docker compose stop device-sim device-sim-esp32 device-sim-arduino device-sim-pico device-sim-stm32
```

### Start All Simulators
```bash
docker compose up -d device-sim device-sim-esp32 device-sim-arduino device-sim-pico device-sim-stm32
```

### Scale Individual Simulator (Example: Run 5 ESP32 devices)
Edit `docker-compose.yml` and change the ESP32 `NUM_DEVICES` environment variable:
```yaml
device-sim-esp32:
  environment:
    - NUM_DEVICES=5
```
Then restart:
```bash
docker compose restart device-sim-esp32
```

## MQTT Monitoring

### Subscribe to All Device Telemetry
```bash
docker exec -it mosquitto mosquitto_sub -h localhost -t "devices/+/telemetry" -v
```

### Count Messages per Second
```bash
docker exec -it mosquitto mosquitto_sub -h localhost -t "devices/+/telemetry" | pv -l -i 1
```

### Monitor Specific Device Type (Example: ESP32 only)
```bash
docker exec -it mosquitto mosquitto_sub -h localhost -t "devices/esp32-+/telemetry" -v
```

### Check MQTT Connection Count
```bash
docker exec -it mosquitto mosquitto_sub -h localhost -t '$SYS/broker/clients/connected' -C 1
```

## Device Details

### Generic IoT Devices (2 devices)
- **Sensors:** Temperature, humidity, voltage
- **Interval:** 10 seconds
- **Container:** `device-sim`

### ESP32 Devices (2 devices)
- **Sensors:** Temperature, humidity, pressure
- **System:** WiFi RSSI, battery voltage, heap memory, boot count
- **Interval:** 8 seconds
- **Container:** `device-sim-esp32`

### Arduino Nano 33 IoT (2 devices)
- **Sensors:** Temperature, humidity
- **IMU:** 9-axis (accelerometer, gyroscope)
- **Analog:** 2 channels (10-bit ADC)
- **Interval:** 6 seconds
- **Container:** `device-sim-arduino`

### Raspberry Pi Pico W (2 devices)
- **Sensors:** Temperature, motion detection, door sensor, light level
- **GPIO:** 4 digital pins (15-18)
- **System:** CPU temperature, system voltage
- **Interval:** 7 seconds
- **Container:** `device-sim-pico`

### STM32 Industrial (1 device)
- **Sensors:** Temperature, pressure, flow rate, vibration
- **Analog:** 4 channels (12-bit ADC)
- **Digital:** 2 inputs + emergency stop
- **Machine State:** status, cycle count, error count, runtime hours
- **Interval:** 5 seconds
- **Container:** `device-sim-stm32`

## Network Configuration

All simulator containers connect to the same Docker network (`iot-network`) but maintain separate network identities:
- Each container resolves `mosquitto` hostname to the broker
- Mosquitto sees 5 different client connection sources
- Simulates distributed IoT deployment across multiple locations

## Troubleshooting

### Container Keeps Restarting
Check logs for errors:
```bash
docker logs device-sim-esp32 --tail 50
```

### No Messages Appearing in MQTT
1. Check container is running: `docker ps --filter "name=device-sim-esp32"`
2. Verify Mosquitto is healthy: `docker ps --filter "name=mosquitto"`
3. Check container logs: `docker logs device-sim-esp32`

### Modify Simulator Code
After editing simulator Python files:
1. Rebuild image: `docker compose build device-sim`
2. Recreate containers: `docker compose up -d --force-recreate device-sim device-sim-esp32 device-sim-arduino device-sim-pico device-sim-stm32`

## Environment Variables

Each simulator container supports these environment variables (set in `docker-compose.yml`):

- `MQTT_BROKER` - Hostname of MQTT broker (default: `mosquitto`)
- `MQTT_PORT` - MQTT port (default: `1883`)
- `MQTT_USER` - MQTT username (optional)
- `MQTT_PASS` - MQTT password (optional)
- `NUM_DEVICES` - Number of simulated devices in this container
- `INTERVAL` - Seconds between telemetry messages
- `PYTHONUNBUFFERED` - Set to `1` for immediate log output

## Performance Considerations

### Current Load
- **9 devices total** publishing at intervals ranging from 5-10 seconds
- Approximately **1.2 messages/second** to MQTT broker
- Minimal CPU and network overhead

### Scaling Up
To simulate larger deployments, increase `NUM_DEVICES` per container:
- 100 devices @ 10s interval = ~10 msg/sec
- 1000 devices @ 30s interval = ~33 msg/sec

Monitor Mosquitto resource usage:
```bash
docker stats mosquitto
```
