# MQTT Implementation for ESP32

This document describes the MQTT implementation for ESP32 devices in the ESP Sensors project.

## Overview

The MQTT implementation provides a simple and reliable way to connect ESP32 devices to MQTT brokers, publish sensor data, and receive commands or configuration updates. It supports both real hardware and simulation mode for development and testing.

This implementation is built from scratch without relying on external libraries like umqtt, providing full control over the MQTT protocol implementation.

## Features

The implementation provides the following features:

- Connect to an MQTT broker with credentials
- Publish data to topics
- Subscribe to topics
- Read data from topics with configurable wait times
- Handle received messages
- Socket-based communication with MQTT brokers
- Quality of Service (QoS) support (levels 0 and 1)
- Ping/keepalive mechanism to maintain connections
- Simulation mode for development on non-ESP hardware

## Classes

### MQTTClient

The `MQTTClient` class is the core implementation of the MQTT protocol. It handles the low-level details of the MQTT protocol, including packet formatting, socket communication, and protocol state management.

#### Methods

- `__init__(client_id, server, port=1883, user=None, password=None, keepalive=60, ssl=False)`: Initialize the client
- `connect()`: Connect to the MQTT broker
- `disconnect()`: Disconnect from the MQTT broker
- `publish(topic, msg, retain=False, qos=0)`: Publish a message to a topic
- `subscribe(topic, qos=0)`: Subscribe to a topic
- `set_callback(callback)`: Set a callback function for received messages
- `check_msg()`: Check for pending messages from the broker
- `ping()`: Send a ping request to keep the connection alive

#### Implementation Details

The `MQTTClient` class implements the MQTT protocol from scratch using socket communication. It includes:

- MQTT packet encoding and decoding
- Connection establishment with authentication
- Topic subscription and message publishing
- QoS levels 0 and 1 support
- Ping/keepalive mechanism
- Message callback handling

In simulation mode, the class provides a mock implementation that simulates MQTT behavior without actually connecting to a broker.

### ESP32MQTTClient

The `ESP32MQTTClient` class is the main interface for MQTT operations. It provides a high-level API for common MQTT tasks.

#### Methods

- `__init__(client_id, server, port=1883, user=None, password=None, keepalive=60, ssl=False)`: Initialize the client
- `connect()`: Connect to the MQTT broker
- `disconnect()`: Disconnect from the MQTT broker
- `publish(topic, message, retain=False, qos=0)`: Publish a message to a topic
- `subscribe(topic, qos=0)`: Subscribe to a topic
- `read_topic(topic, wait_time=5)`: Read data from a topic with a configurable wait time

## Usage

### Using ESP32MQTTClient (Recommended)

The `ESP32MQTTClient` class provides a high-level, easy-to-use interface for MQTT operations:

```python
from esp_sensors.mqtt import ESP32MQTTClient

# Create client
client = ESP32MQTTClient(
    "esp32_client",
    "mqtt.example.com",
    1883,
    "username",
    "password"
)

# Connect to broker
if client.connect():
    # Publish a message
    client.publish("esp32/data", "Hello, MQTT!")

    # Subscribe to a topic
    client.subscribe("esp32/commands")

    # Read from a topic with a 10-second timeout
    message = client.read_topic("esp32/commands", 10)
    if message:
        print(f"Received: {message}")

    # Disconnect
    client.disconnect()
```

### Using MQTTClient Directly

For more control over the MQTT protocol, you can use the `MQTTClient` class directly:

```python
from esp_sensors.mqtt import MQTTClient
import time

# Create client
client = MQTTClient(
    "esp32_client",
    "mqtt.example.com",
    1883,
    "username",
    "password",
    keepalive=60
)

# Set up a callback for received messages
def message_callback(topic, msg):
    topic_str = topic.decode('utf-8') if isinstance(topic, bytes) else topic
    msg_str = msg.decode('utf-8') if isinstance(msg, bytes) else msg
    print(f"Message received on {topic_str}: {msg_str}")

client.set_callback(message_callback)

# Connect to broker
try:
    client.connect()

    # Subscribe to a topic
    client.subscribe("esp32/commands")

    # Publish a message
    client.publish("esp32/data", "Hello from direct MQTT client!")

    # Check for messages for 10 seconds
    start_time = time.time()
    while time.time() - start_time < 10:
        client.check_msg()
        time.sleep(0.1)

    # Disconnect
    client.disconnect()
except Exception as e:
    print(f"MQTT error: {e}")
```

### Configuration

The MQTT implementation can be configured using a dictionary with the following keys:

```python
mqtt_config = {
    "enabled": True,                      # Enable/disable MQTT
    "client_id": "esp32_sensor",          # Client ID
    "broker": "mqtt.example.com",         # Broker address
    "port": 1883,                         # Broker port
    "username": "username",               # Username for authentication
    "password": "password",               # Password for authentication
    "keepalive": 60,                      # Keepalive interval in seconds
    "ssl": False,                         # Whether to use SSL/TLS
    "use_esp32_client": True,             # Whether to use ESP32MQTTClient (vs basic MQTTClient)
    "topic_data_prefix": "/homecontrol/device/data",  # Prefix for data topics
    "topic_config": "/homecontrol/device/config",     # Topic for configuration
    "load_config_from_mqtt": True,        # Whether to load config from MQTT
    "config_wait_time": 1.0               # Wait time for config updates in seconds
}
```

### Using the setup_mqtt Function

The `setup_mqtt` function provides a convenient way to set up an MQTT client from a configuration dictionary:

```python
from esp_sensors.mqtt import setup_mqtt

mqtt_config = {
    "enabled": True,
    "client_id": "esp32_sensor",
    "broker": "mqtt.example.com",
    "username": "username",
    "password": "password"
}

client = setup_mqtt(mqtt_config)
if client:
    # MQTT is enabled and connected
    # Use the client for MQTT operations
    pass
```

## Examples

See the `examples/mqtt_example.py` file for a complete example of using the MQTT implementation.

## Simulation Mode

When running on non-ESP hardware, the implementation automatically switches to simulation mode. In this mode:

- MQTT messages are printed to the console instead of being sent to a broker
- You can simulate receiving messages using the `simulate_message` method

This is useful for development and testing without actual hardware.

## Integration with Sensor Data

The `publish_sensor_data` function provides a convenient way to publish sensor data to MQTT topics:

```python
from esp_sensors.mqtt import setup_mqtt, publish_sensor_data

mqtt_config = {...}  # MQTT configuration
client = setup_mqtt(mqtt_config)

# Publish sensor data
if client:
    publish_sensor_data(client, mqtt_config, sensor, temperature, humidity)
```

## Configuration Updates

The `check_config_update` function allows devices to receive configuration updates from MQTT:

```python
from esp_sensors.mqtt import setup_mqtt, check_config_update

mqtt_config = {...}  # MQTT configuration
current_config = {...}  # Current device configuration
client = setup_mqtt(mqtt_config)

# Check for configuration updates
if client:
    updated_config = check_config_update(client, mqtt_config, current_config)
    if updated_config != current_config:
        # Configuration was updated
        # Apply the new configuration
        pass
```
