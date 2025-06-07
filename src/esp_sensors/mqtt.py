"""
MQTT module for ESP sensors.

This module provides functionality to connect to an MQTT broker and publish sensor data.

This module uses the MQTTClient class from mqtt_client.py for the core MQTT implementation.
"""

import json
import time

from .mqtt_client import (
    MQTTClient,
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
            # self.connected = False  # Assume connection is lost on error
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
            # self.connected = False  # Assume connection is lost on error
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

        print(f"[ESP32MQTT] Message received on '{topic_str}': len: {len(msg_str)}")

        # Store the message
        self.received_messages[topic_str] = msg

    def read_topic(self, topic, wait_time=5.0):
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
        if not self.subscribe(topic):
            print("[ESP32MQTT] Failed to subscribe to topic")
            return None

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
                # self.connected = False
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

        # Get reconnection configuration
        reconnect_config = mqtt_config.get("reconnect", {})
        reconnect_enabled = reconnect_config.get("enabled", True)

        print(f"Setting up MQTT client: {client_id} -> {broker}:{port}")

        # Use the new ESP32MQTTClient
        client = ESP32MQTTClient(
            client_id, broker, port, username, password, keepalive, ssl
        )

        # Check if we should attempt to connect based on reconnection strategy
        if reconnect_enabled and not should_attempt_connection(reconnect_config):
            print("Skipping MQTT connection attempt based on reconnection strategy")
            return client

        # Try to connect
        if client.connect():
            print("MQTT connected successfully using ESP32MQTTClient")
            # Reset reconnection attempt counter on successful connection
            if reconnect_enabled:
                update_reconnection_state(reconnect_config, True)
        else:
            print("Failed to connect using ESP32MQTTClient")
            # Update reconnection attempt counter
            if reconnect_enabled:
                update_reconnection_state(reconnect_config, False)

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

        # Prepare combined data as JSON
        data_topic = f"{topic_data_prefix}/{sensor_id}/data"
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "uptime": time.time(),
            "unit": sensor.unit,
        }
        data_payload = json.dumps(data).encode()

        # Publish the data and check the result
        publish_success = client.publish(data_topic, data_payload)
        if publish_success:
            print(f"Published sensor data to MQTT: '{data_topic}'")
            return True
        else:
            print("Failed to publish sensor data to MQTT")
            return False
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")
        return False


def get_data_topic(mqtt_config):
    return mqtt_config.get("topic_data_prefix", "/homecontrol/device/data")


def subscribe_to_config(
    client: ESP32MQTTClient | MQTTClient | None, mqtt_config: dict
) -> bool:
    """
    Subscribe to the configuration version topic.

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
        topic_config_version = mqtt_config.get("topic_config_version")
        if not topic_config_version:
            print("No configuration version topic specified")
            return False

        print(f"Subscribing to configuration version topic: {topic_config_version}")

        # Both client types have compatible subscribe methods
        client.subscribe(topic_config_version.encode())
        return True
    except Exception as e:
        print(f"Failed to subscribe to configuration version topic: {e}")
        return False


def should_attempt_connection(reconnect_config: dict) -> bool:
    """
    Determine if a connection attempt should be made based on the reconnection strategy.

    Args:
        reconnect_config: Reconnection configuration dictionary

    Returns:
        True if a connection attempt should be made, False otherwise
    """
    # If reconnection is disabled, always attempt to connect
    if not reconnect_config.get("enabled", True):
        return True

    # Get reconnection parameters
    attempt_count = reconnect_config.get("attempt_count", 0)
    max_attempts = reconnect_config.get("max_attempts", 3)
    last_attempt_time = reconnect_config.get("last_attempt_time", 0)
    backoff_factor = reconnect_config.get("backoff_factor", 2)
    min_interval = reconnect_config.get("min_interval", 3600)  # 1 hour default
    max_interval = reconnect_config.get("max_interval", 21600)  # 6 hours default

    # If we haven't reached max attempts, always try to connect
    if attempt_count < max_attempts:
        return True

    # Calculate the backoff interval based on attempt count
    # Use exponential backoff with a maximum interval
    interval = min(
        min_interval * (backoff_factor ** (attempt_count - max_attempts)), max_interval
    )

    # Check if enough time has passed since the last attempt
    current_time = time.time()
    time_since_last_attempt = current_time - last_attempt_time

    # If we've waited long enough, allow another attempt
    if time_since_last_attempt >= interval:
        print(
            f"Allowing reconnection attempt after {time_since_last_attempt:.1f}s (interval: {interval:.1f}s)"
        )
        return True
    else:
        print(
            f"Skipping reconnection attempt, next attempt in {interval - time_since_last_attempt:.1f}s"
        )
        return False


def update_reconnection_state(reconnect_config: dict, success: bool) -> None:
    """
    Update the reconnection state based on the connection attempt result.

    Args:
        reconnect_config: Reconnection configuration dictionary
        success: Whether the connection attempt was successful
    """
    current_time = time.time()

    if success:
        # Reset attempt counter on successful connection
        reconnect_config["attempt_count"] = 0
        print("Connection successful, reset reconnection attempt counter")
    else:
        # Increment attempt counter on failed connection
        attempt_count = reconnect_config.get("attempt_count", 0) + 1
        reconnect_config["attempt_count"] = attempt_count
        print(f"Connection failed, reconnection attempt count: {attempt_count}")

    # Update last attempt time
    reconnect_config["last_attempt_time"] = current_time

    # Update the configuration in the parent dictionary
    # This will be saved to the config file in the main application


def check_config_update(
    client: ESP32MQTTClient | MQTTClient | None, mqtt_config: dict, current_config: dict
) -> dict:
    """
    Check for configuration updates from MQTT.

    First checks the version topic to see if a new version is available.
    If a new version is detected, fetches the full configuration from the data topic.

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
        # Get the version and data topics
        topic_config_version = mqtt_config.get("topic_config_version")
        topic_config_data = mqtt_config.get("topic_config_data")

        if not topic_config_version or not topic_config_data:
            print("Configuration version or data topic not specified")
            return current_config

        # Variable to store the received version and configuration
        received_version = None
        received_config = None
        wait_time = mqtt_config.get("config_wait_time", 1.0)

        # Step 1: Check the version topic for updates
        print(
            f"Reading from version topic: {topic_config_version} with wait time: {wait_time}s"
        )
        version_msg = client.read_topic(topic_config_version, wait_time)

        if version_msg:
            try:
                msg_str = (
                    version_msg.decode("utf-8")
                    if isinstance(version_msg, bytes)
                    else version_msg
                )
                received_version = int(msg_str.strip())
                print(f"Received version: {received_version}")
            except Exception as e:
                print(f"Error parsing version message: {e}")

        # Step 2: If we received a version and it's newer, fetch the full config from the data topic
        current_version = current_config.get("version", 0)

        if received_version is not None and received_version > current_version:
            print(
                f"Found newer version ({received_version} > {current_version}), fetching full configuration"
            )

            print(
                f"Reading from data topic: {topic_config_data} with wait time: {wait_time}s"
            )
            config_msg = client.read_topic(topic_config_data, wait_time)

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

            # If we received a configuration and its version matches what we expected, return it
            if (
                received_config
                and received_config.get("version", 0) == received_version
            ):
                print(f"Successfully fetched configuration version {received_version}")
                return received_config
            else:
                print("Failed to fetch the full configuration or version mismatch")

        return current_config
    except Exception as e:
        print(f"Error checking for configuration updates: {e}")
        return current_config
