FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY sim.py sim_esp32.py sim_arduino.py sim_pico.py sim_stm32.py ./
ENV MQTT_BROKER=mosquitto
ENV MQTT_PORT=1883
ENV NUM_DEVICES=5
ENV INTERVAL=5
CMD ["python", "sim.py"]
