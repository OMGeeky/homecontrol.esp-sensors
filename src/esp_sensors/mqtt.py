"""
MQTT module for ESP sensors.

This module provides functionality to connect to an MQTT broker and publish sensor data.
It supports both real hardware and simulation mode.

This module uses the MQTTClient class from mqtt_client.py for the core MQTT implementation.
"""

import time
import json
from .mqtt_client import (
    MQTTClient,
    MQTTException,
    CONNECT,
    CONNACK,
    PUBLISH,
    PUBACK,
    SUBSCRIBE,
    SUBACK,
    UNSUBSCRIBE,
    UNSUBACK,
    PINGREQ,
    PINGRESP,
    DISCONNECT,
    CONN_ACCEPTED,
    CONN_REFUSED_PROTOCOL,
    CONN_REFUSED_IDENTIFIER,
    CONN_REFUSED_SERVER,
    CONN_REFUSED_USER_PASS,
    CONN_REFUSED_AUTH,
    MQTT_PROTOCOL_LEVEL,
    MQTT_CLEAN_SESSION,
)


class ESP32MQTTClient:
    """
    A basic MQTT client implementation for ESP32 that provides:
    - Reading data from a topic with configurable wait time
    - Publishing data to a topic
    - Login to MQTT broker with credentials

    This implementation uses our custom MQTT client that doesn't rely on umqtt.
    """

    def __init__(
        self,
        client_id,
        server,
        port=1883,
        user=None,
        password=None,
        keepalive=60,
        ssl=False,
    ):
        """
        Initialize the MQTT client.

        Args:
            client_id (str): Unique client identifier
            server (str): MQTT broker address
            port (int): MQTT broker port
            user (str): Username for authentication
            password (str): Password for authentication
            keepalive (int): Keepalive interval in seconds
            ssl (bool): Whether to use SSL/TLS
        """
        self.client_id = client_id
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.keepalive = keepalive
        self.ssl = ssl
        self.client = None
        self.connected = False
        self.received_messages = {}  # Store received messages by topic

    def connect(self):
        """
        Connect to the MQTT broker.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            print(
                f"[ESP32MQTT] Connecting to {self.server}:{self.port} as {self.client_id}"
            )
            # Create our custom MQTT client
            self.client = MQTTClient(
                self.client_id,
                self.server,
                self.port,
                self.user,
                self.password,
                self.keepalive,
                self.ssl,
            )

            # Set up callback to store received messages
            self.client.set_callback(self._message_callback)

            print("[ESP32MQTT] Attempting to connect to broker...")
            # Connect to broker
            result = self.client.connect()
            if result == 0:  # 0 means success in MQTT protocol
                self.connected = True
                print("[ESP32MQTT] Connected successfully")
                return True
            else:
                print(f"[ESP32MQTT] Connection failed with result code: {result}")
                self.connected = False
                return False
        except Exception as e:
            print(f"[ESP32MQTT] Connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """
        Disconnect from the MQTT broker.
        """
        if self.client and self.connected:
            try:
                self.client.disconnect()
                self.connected = False
                print("[ESP32MQTT] Disconnected")
            except Exception as e:
                print(f"[ESP32MQTT] Error during disconnect: {e}")
                self.connected = False

    def publish(self, topic, message, retain=False, qos=0):
        """
        Publish a message to a topic.

        Args:
            topic (str): The topic to publish to
            message (str or bytes): The message to publish
            retain (bool): Whether the message should be retained
            qos (int): Quality of Service level

        Returns:
            bool: True if publishing was successful, False otherwise
        """
        if not self.connected or not self.client:
            print("[ESP32MQTT] Not connected to broker")
            return False

        try:
            # Convert message to bytes if it's not already
            if isinstance(message, str):
                message = message.encode()

            self.client.publish(topic, message, retain, qos)
            return True
        except Exception as e:
            print(f"[ESP32MQTT] Failed to publish: {e}")
            self.connected = False  # Assume connection is lost on error
            return False

    def subscribe(self, topic, qos=0):
        """
        Subscribe to a topic.

        Args:
            topic (str): The topic to subscribe to
            qos (int): Quality of Service level

        Returns:
            bool: True if subscription was successful, False otherwise
        """
        if not self.connected or not self.client:
            print("[ESP32MQTT] Not connected to broker")
            return False

        try:
            # Convert topic to bytes if it's not already
            if isinstance(topic, str):
                topic = topic.encode()

            self.client.subscribe(topic, qos)
            return True
        except Exception as e:
            print(f"[ESP32MQTT] Failed to subscribe: {e}")
            self.connected = False  # Assume connection is lost on error
            return False

    def _message_callback(self, topic, msg):
        """
        Internal callback for handling received messages.

        Args:
            topic (bytes): The topic the message was received on
            msg (bytes): The message payload
        """
        topic_str = topic.decode("utf-8") if isinstance(topic, bytes) else topic
        msg_str = msg.decode("utf-8") if isinstance(msg, bytes) else msg

        print(f"[ESP32MQTT] Message received on {topic_str}: {msg_str}")

        # Store the message
        self.received_messages[topic_str] = msg

    def read_topic(self, topic, wait_time=5):
        """
        Read data from a topic with a configurable wait time.

        Args:
            topic (str): The topic to read from
            wait_time (float): Maximum time to wait for a message in seconds

        Returns:
            bytes or None: The message payload if received within wait_time, None otherwise
        """
        if not self.connected or not self.client:
            print("[ESP32MQTT] Not connected to broker")
            return None

        # Clear any previous message for this topic
        topic_str = (
            topic
            if isinstance(topic, str)
            else topic.decode("utf-8") if isinstance(topic, bytes) else str(topic)
        )
        if topic_str in self.received_messages:
            del self.received_messages[topic_str]

        # Subscribe to the topic if not already subscribed
        self.subscribe(topic)

        # Wait for the message
        start_time = time.time()
        while time.time() - start_time < wait_time:
            try:
                # Check for new messages
                self.client.check_msg()

                # Check if we received a message on this topic
                if topic_str in self.received_messages:
                    return self.received_messages[topic_str]

                # Small delay to prevent tight loop
                time.sleep(0.1)
            except Exception as e:
                print(f"[ESP32MQTT] Error while reading topic: {e}")
                self.connected = False
                return None

        print(
            f"[ESP32MQTT] No message received on {topic_str} after {wait_time} seconds"
        )
        return None


def setup_mqtt(mqtt_config: dict) -> ESP32MQTTClient | MQTTClient | None:
    """
    Set up and connect to the MQTT broker.

    Args:
        mqtt_config: MQTT configuration dictionary

    Returns:
        ESP32MQTTClient or MQTTClient instance if enabled and connected, None otherwise
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
        use_esp32_client = mqtt_config.get("use_esp32_client", True)

        print(f"Setting up MQTT client: {client_id} -> {broker}:{port}")

        if use_esp32_client:
            # Use the new ESP32MQTTClient
            client = ESP32MQTTClient(
                client_id, broker, port, username, password, keepalive, ssl
            )

            # Try to connect
            if client.connect():
                print("MQTT connected successfully using ESP32MQTTClient")
            else:
                print("Failed to connect using ESP32MQTTClient")

            return client
            # print("Failed to connect using ESP32MQTTClient, falling back to basic MQTTClient")
            # # Fall back to basic client
            # use_esp32_client = False

        if not use_esp32_client:
            # Use the basic MQTTClient for backward compatibility
            client = MQTTClient(
                client_id, broker, port, username, password, keepalive, ssl
            )

            # Try to connect
            client.connect()
            print("MQTT connected successfully using basic MQTTClient")
            return client

    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return None


def publish_sensor_data(
    client: ESP32MQTTClient | MQTTClient | None,
    mqtt_config: dict,
    sensor,
    temperature: float,
    humidity: float,
) -> bool:
    """
    Publish sensor data to MQTT topics.

    Args:
        client: ESP32MQTTClient or MQTTClient instance
        mqtt_config: MQTT configuration dictionary
        sensor: Sensor instance
        temperature: Temperature reading
        humidity: Humidity reading

    Returns:
        True if publishing was successful, False otherwise
    """
    if client is None:
        print("MQTT client is not connected")
        return False

    try:
        topic_data_prefix = get_data_topic(mqtt_config)
        sensor_id = getattr(sensor, "id", sensor.name.lower().replace(" ", "_"))

        # Publish temperature
        temp_topic = f"{topic_data_prefix}/{sensor_id}/temperature"
        temp_payload = str(temperature).encode()

        # Publish humidity
        humidity_topic = f"{topic_data_prefix}/{sensor_id}/humidity"
        humidity_payload = str(humidity).encode()

        # Prepare combined data as JSON
        data_topic = f"{topic_data_prefix}/{sensor_id}/data"
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "uptime": time.time(),
            "unit": sensor.unit,
        }
        data_payload = json.dumps(data).encode()

        # Both client types have compatible publish methods
        # client.publish(temp_topic, temp_payload)
        # client.publish(humidity_topic, humidity_payload)
        client.publish(data_topic, data_payload)

        print(
            f"Published sensor data to MQTT: {temp_topic}, {humidity_topic}, {data_topic}"
        )
        return True
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")
        return False


def get_data_topic(mqtt_config):
    return mqtt_config.get("topic_data_prefix", "/homecontrol/device/data")


def subscribe_to_config(
    client: ESP32MQTTClient | MQTTClient | None, mqtt_config: dict
) -> bool:
    """
    Subscribe to the configuration topic.

    Args:
        client: ESP32MQTTClient or MQTTClient instance
        mqtt_config: MQTT configuration dictionary

    Returns:
        True if subscription was successful, False otherwise
    """
    if client is None:
        print("MQTT client is not connected (subscribe)")
        return False

    try:
        topic_config = mqtt_config.get("topic_config")
        if not topic_config:
            print("No configuration topic specified")
            return False

        print(f"Subscribing to configuration topic: {topic_config}")

        # Both client types have compatible subscribe methods
        client.subscribe(topic_config.encode())
        return True
    except Exception as e:
        print(f"Failed to subscribe to configuration topic: {e}")
        return False


def check_config_update(
    client: ESP32MQTTClient | MQTTClient | None, mqtt_config: dict, current_config: dict
) -> dict:
    """
    Check for configuration updates from MQTT.

    Args:
        client: ESP32MQTTClient or MQTTClient instance
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

        if isinstance(client, ESP32MQTTClient):
            print("Using ESP32MQTTClient to check for configuration updates")

            topic_config = mqtt_config.get("topic_config")
            wait_time = mqtt_config.get("config_wait_time", 1.0)

            print(
                f"Using ESP32MQTTClient to read from config topic with wait time: {wait_time}s"
            )
            config_msg = client.read_topic(topic_config, wait_time)

            if config_msg:
                try:
                    msg_str = (
                        config_msg.decode("utf-8")
                        if isinstance(config_msg, bytes)
                        else config_msg
                    )
                    received_config = json.loads(msg_str)
                except Exception as e:
                    print(f"Error parsing configuration message: {e}")
        else:

            # Define callback function to handle incoming messages
            def config_callback(topic, msg):
                nonlocal received_config
                try:
                    # Verify that the topic matches our expected topic
                    expected_topic = mqtt_config.get("topic_config")
                    topic_str = (
                        topic.decode("utf-8") if isinstance(topic, bytes) else topic
                    )
                    if topic_str != expected_topic:
                        print(
                            f"Ignoring message from topic {topic_str} - not matching our config topic {expected_topic}"
                        )
                        return

                    # Parse the message as JSON
                    msg_str = msg.decode("utf-8") if isinstance(msg, bytes) else msg
                    config_data = json.loads(msg_str)
                    print(
                        f"Received configuration from MQTT: version {config_data.get('version', 0)}"
                    )
                    received_config = config_data
                except Exception as e:
                    print(f"Error parsing configuration message: {e}")

            # Set the callback
            client.set_callback(config_callback)

            # Subscribe to the configuration topic
            if not subscribe_to_config(client, mqtt_config):
                print("Failed to subscribe to configuration topic")
                return current_config

            # Check for retained messages (will be processed by the callback)
            print("Checking for retained configuration messages...")
            client.check_msg()

            # For basic MQTTClient, use the original approach
            print("Waiting for configuration updates...")
            # Wait a short time for any retained messages to be processed
            time.sleep(0.5)
            client.check_msg()
            print("done waiting for configuration updates")

        # If we received a configuration and its version is newer, return it
        if received_config and received_config.get("version", 0) > current_config.get(
            "version", 0
        ):
            print(
                f"Found newer configuration (version {received_config.get('version')})"
            )
            return received_config

        return current_config
    except Exception as e:
        print(f"Error checking for configuration updates: {e}")
        return current_config
