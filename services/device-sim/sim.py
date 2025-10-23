import os
import time
import json
import random
import uuid
import threading
import paho.mqtt.client as mqtt
import requests

BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
PORT = int(os.getenv('MQTT_PORT', 1883))
USER = os.getenv('MQTT_USER') or None
PASS = os.getenv('MQTT_PASS') or None
API_URL = os.getenv('API_URL')  # optional endpoint to POST telemetry
NUM_DEVICES = int(os.getenv('NUM_DEVICES', 1))
INTERVAL = float(os.getenv('INTERVAL', 5.0))

def connect_with_backoff(client, host, port, max_wait=30):
    """Keep trying until connected, with exponential backoff."""
    wait = 1
    while True:
        try:
            client.connect(host, port, keepalive=60)
            print(f"[{client._client_id.decode()}] connected to {host}:{port}", flush=True)
            return
        except Exception as e:
            print(f"[{client._client_id.decode()}] connect error: {e}; retrying in {wait}s", flush=True)
            time.sleep(wait)
            wait = min(wait * 2, max_wait)

def device_loop(device_id: str):
    client = mqtt.Client(client_id=device_id)

    if USER and PASS:
        client.username_pw_set(USER, PASS)

    # Make client resilient to temporary disconnects
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_disconnect(c, u, rc):
        # rc != 0: unexpected disconnect → paho will auto-reconnect with backoff
        print(f"[{device_id}] disconnected (rc={rc})", flush=True)

    client.on_disconnect = on_disconnect

    # Initial connect with backoff (don’t exit the thread on first failure)
    connect_with_backoff(client, BROKER, PORT)

    client.loop_start()
    try:
        while True:
            payload = {
                "ts": int(time.time() * 1000),
                "sensors": {
                    "temperature": round(random.uniform(20, 30), 2),
                    "humidity": round(random.uniform(40, 55), 2),
                    "voltage": round(random.uniform(3.1, 3.7), 2),
                },
            }
            topic = f"devices/{device_id}/telemetry"
            # publish() returns (result, mid); result==0 is success
            rc = client.publish(topic, json.dumps(payload))[0]
            if rc == 0:
                print(f"[{device_id}] sent: {payload}", flush=True)
            else:
                print(f"[{device_id}] publish failed (rc={rc})", flush=True)

            if API_URL:
                try:
                    requests.post(API_URL + '/telemetry', json=payload, timeout=2)
                except Exception:
                    pass

            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass

def main():
    print(f"broker={BROKER} port={PORT} devices={NUM_DEVICES} interval={INTERVAL}", flush=True)
    threads = []
    for _ in range(NUM_DEVICES):
        device_id = f"sim-{uuid.uuid4().hex[:6]}"
        t = threading.Thread(target=device_loop, args=(device_id,), daemon=True)
        t.start()
        threads.append(t)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping simulator', flush=True)

if __name__ == '__main__':
    main()
