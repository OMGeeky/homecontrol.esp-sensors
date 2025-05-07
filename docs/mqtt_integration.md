# MQTT Integration

This document describes how to use the MQTT integration in the ESP Sensors project.

## Overview

The ESP Sensors project now supports publishing sensor data to an MQTT broker. This allows you to integrate your ESP sensors with home automation systems, dashboards, and other IoT platforms that support MQTT.

## Configuration

MQTT functionality is configured in the `config.json` file. Here's an example configuration:

```json
{
  "mqtt": {
    "enabled": true,
    "broker": "mqtt.example.com",
    "port": 1883,
    "client_id": "esp_sensor",
    "username": "your_username",
    "password": "your_password",
    "topic_prefix": "esp/sensors",
    "publish_interval": 60,
    "ssl": false,
    "keepalive": 60
  }
}
```

### Configuration Options

- `enabled`: Set to `true` to enable MQTT publishing, `false` to disable it.
- `broker`: The address of your MQTT broker.
- `port`: The port of your MQTT broker (typically 1883 for non-SSL, 8883 for SSL).
- `client_id`: A unique identifier for this ESP device.
- `username` and `password`: Credentials for authenticating with the MQTT broker (if required).
- `topic_prefix`: The prefix for all MQTT topics published by this device.
- `publish_interval`: How often to publish data (in seconds).
- `ssl`: Set to `true` to use SSL/TLS for the connection.
- `keepalive`: The keepalive interval for the MQTT connection (in seconds).

## MQTT Topics

The ESP Sensors project publishes data to the following MQTT topics:

- `{topic_prefix}/{sensor_name}/temperature`: The temperature reading.
- `{topic_prefix}/{sensor_name}/humidity`: The humidity reading.
- `{topic_prefix}/{sensor_name}/data`: A JSON payload containing all sensor data.

For example, with the default configuration and a DHT22 sensor, the topics would be:
- `esp/sensors/dht22_sensor/temperature`
- `esp/sensors/dht22_sensor/humidity`
- `esp/sensors/dht22_sensor/data`

## JSON Payload Format

The JSON payload published to the `data` topic has the following format:

```json
{
  "temperature": 25.5,
  "humidity": 60.2,
  "timestamp": 1617123456,
  "unit": "C"
}
```

## Usage

Once configured, the ESP device will automatically publish sensor data to the MQTT broker at the specified interval. No additional code is required.

To enable MQTT publishing:

1. Edit the `config.json` file to set `mqtt.enabled` to `true`.
2. Configure the MQTT broker address and credentials.
3. Restart the ESP device.

## Simulation Mode

In simulation mode, MQTT messages are not actually sent to a broker but are printed to the console. This allows you to test your code without an actual MQTT broker.

## Dependencies

This feature requires the `micropython-umqtt.simple` package, which is included in the project's dependencies.