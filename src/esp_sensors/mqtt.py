"""
MQTT module for ESP sensors.

This module provides functionality to connect to an MQTT broker and publish sensor data.
It supports both real hardware and simulation mode.
"""

import time
import json

# Import hardware-specific modules if available (for ESP32/ESP8266)
try:
    from umqtt.robust import MQTTClient

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
            self.callback = None
            self.last_message = None
            self.last_topic = None

        def connect(self):
            print(f"[MQTT] Connecting to {self.server}:{self.port} as {self.client_id}")
            self.connected = True
            return 0

        def disconnect(self):
            print("[MQTT] Disconnected")
            self.connected = False

        def publish(self, topic, msg, retain=False):
            retain_str = " (retained)" if retain else ""
            print(f"[MQTT] Publishing to {topic}{retain_str}: {msg}")
            return

        def set_callback(self, callback):
            self.callback = callback
            print(f"[MQTT] Callback set")

        def check_msg(self):
            """Simulate checking for messages"""
            if self.last_message and self.callback:
                self.callback(self.last_topic, self.last_message)
                self.last_message = None
                self.last_topic = None
            return

        # For simulation only - allows us to simulate receiving a message
        def simulate_message(self, topic, msg):
            self.last_topic = topic
            self.last_message = msg
            print(f"[MQTT] Simulated message received on {topic}: {msg}")
            if self.callback:
                self.callback(topic, msg)


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
        topic_data_prefix = mqtt_config.get("topic_data_prefix", "/homecontrol/device/data")
        sensor_id = getattr(sensor, "id", sensor.name.lower().replace(" ", "_"))

        # Publish temperature
        temp_topic = f"{topic_data_prefix}/{sensor_id}/temperature"
        client.publish(temp_topic, str(temperature).encode())

        # Publish humidity
        humidity_topic = f"{topic_data_prefix}/{sensor_id}/humidity"
        client.publish(humidity_topic, str(humidity).encode())

        # Publish combined data as JSON
        data_topic = f"{topic_data_prefix}/{sensor_id}/data"
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "uptime": time.time(),
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


def subscribe_to_config(client: MQTTClient | None, mqtt_config: dict) -> bool:
    """
    Subscribe to the configuration topic.

    Args:
        client: MQTTClient instance
        mqtt_config: MQTT configuration dictionary

    Returns:
        True if subscription was successful, False otherwise
    """
    if client is None:
        return False

    try:
        topic_config = mqtt_config.get("topic_config")
        if not topic_config:
            print("No configuration topic specified")
            return False

        print(f"Subscribing to configuration topic: {topic_config}")
        client.subscribe(topic_config.encode())
        return True
    except Exception as e:
        print(f"Failed to subscribe to configuration topic: {e}")
        return False


def check_config_update(client: MQTTClient | None, mqtt_config: dict, current_config: dict) -> dict:
    """
    Check for configuration updates from MQTT.

    Args:
        client: MQTTClient instance
        mqtt_config: MQTT configuration dictionary
        current_config: Current configuration dictionary

    Returns:
        Updated configuration dictionary if an update was found, otherwise the current configuration
    """
    if client is None or not mqtt_config.get("load_config_from_mqtt", False):
        return current_config

    try:
        # Variable to store the received configuration
        received_config = None

        # Define callback function to handle incoming messages
        def config_callback(topic, msg):
            nonlocal received_config
            try:
                # Parse the message as JSON
                config_data = json.loads(msg.decode('utf-8'))
                print(f"Received configuration from MQTT: version {config_data.get('version', 0)}")
                received_config = config_data
            except Exception as e:
                print(f"Error parsing configuration message: {e}")

        # Set the callback
        client.set_callback(config_callback)

        # Subscribe to the configuration topic
        if not subscribe_to_config(client, mqtt_config):
            return current_config

        # Check for retained messages (will be processed by the callback)
        print("Checking for retained configuration messages...")
        client.check_msg()

        # Wait a short time for any retained messages to be processed
        time.sleep(0.5)
        client.check_msg()

        # If we received a configuration and its version is newer, return it
        if received_config and received_config.get("version", 0) > current_config.get("version", 0):
            print(f"Found newer configuration (version {received_config.get('version')})")
            return received_config

        return current_config
    except Exception as e:
        print(f"Error checking for configuration updates: {e}")
        return current_config
