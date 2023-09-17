#
# Example cmdline:
# docker run -d --restart unless-stopped -e TZ=Europe/Helsinki -e MQTT_BROKER_HOST=XXXX -e MQTT_BROKER_USER=YYYY -e MQTT_BROKER_PASS=ZZZZ -u 1000:1000 --device=/dev/serial/by-id/usb-Devantech_Ltd._USB-RLY02._1001593-if00:/dev/ttyRELAY --group-add dialout rly02-mqtt

# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your Python script and script file into the container
COPY rly02.py .

# Install the paho-mqtt library
RUN pip install Homie4 pyserial

# Run the Python script with environment variables
CMD ["python", "rly02.py"]
