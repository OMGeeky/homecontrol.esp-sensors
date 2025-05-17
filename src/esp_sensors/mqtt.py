"""
MQTT module for ESP sensors.

This module provides functionality to connect to an MQTT broker and publish sensor data.
It supports both real hardware and simulation mode.
"""

import time
import json

# Import hardware-specific modules if available (for ESP32/ESP8266)
try:
    from umqtt.simple import MQTTClient

    SIMULATION = False
except ImportError:
    # Simulation mode for development on non-ESP hardware
    SIMULATION = True
    print(
        "[MQTT] Running in simulation mode - MQTT messages will be printed to console"
    )

    # Mock MQTT client for simulation
    class MQTTClient:
        def __init__(
            self,
            client_id,
            server,
            port=0,
            user=None,
            password=None,
            keepalive=0,
            ssl=False,
        ):
            self.client_id = client_id
            self.server = server
            self.port = port
            self.user = user
            self.password = password
            self.keepalive = keepalive
            self.ssl = ssl
            self.connected = False

        def connect(self):
            print(f"[MQTT] Connecting to {self.server}:{self.port} as {self.client_id}")
            self.connected = True
            return 0

        def disconnect(self):
            print("[MQTT] Disconnected")
            self.connected = False

        def publish(self, topic, msg):
            print(f"[MQTT] Publishing to {topic}: {msg}")
            return


def setup_mqtt(mqtt_config: dict) -> MQTTClient | None:
    """
    Set up and connect to the MQTT broker.

    Args:
        mqtt_config: MQTT configuration dictionary

    Returns:
        MQTTClient instance if enabled and connected, None otherwise
    """
    if not mqtt_config.get("enabled", False):
        print("MQTT is disabled in configuration")
        return None

    try:
        client_id = mqtt_config.get("client_id", "esp_sensor")
        broker = mqtt_config.get("broker", "mqtt.example.com")
        port = mqtt_config.get("port", 1883)
        username = mqtt_config.get("username", "")
        password = mqtt_config.get("password", "")
        keepalive = mqtt_config.get("keepalive", 60)
        ssl = mqtt_config.get("ssl", False)

        print(f"Setting up MQTT client: {client_id} -> {broker}:{port}")
        client = MQTTClient(client_id, broker, port, username, password, keepalive, ssl)

        # Try to connect
        client.connect()
        print("MQTT connected successfully")
        return client
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return None


def publish_sensor_data(
    client: MQTTClient | None,
    mqtt_config: dict,
    sensor,
    temperature: float,
    humidity: float,
) -> bool:
    """
    Publish sensor data to MQTT topics.

    Args:
        client: MQTTClient instance
        mqtt_config: MQTT configuration dictionary
        sensor: Sensor instance
        temperature: Temperature reading
        humidity: Humidity reading

    Returns:
        True if publishing was successful, False otherwise
    """
    if client is None:
        return False

    try:
        topic_prefix = mqtt_config.get("topic_prefix", "esp/sensors")
        sensor_name = sensor.name.lower().replace(" ", "_")

        # Publish temperature
        temp_topic = f"{topic_prefix}/{sensor_name}/temperature"
        client.publish(temp_topic, str(temperature).encode())

        # Publish humidity
        humidity_topic = f"{topic_prefix}/{sensor_name}/humidity"
        client.publish(humidity_topic, str(humidity).encode())

        # Publish combined data as JSON
        data_topic = f"{topic_prefix}/{sensor_name}/data"
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": time.time(),
            "unit": sensor.unit,
        }
        client.publish(data_topic, json.dumps(data).encode())

        print(
            f"Published sensor data to MQTT: {temp_topic}, {humidity_topic}, {data_topic}"
        )
        return True
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")
        return False
