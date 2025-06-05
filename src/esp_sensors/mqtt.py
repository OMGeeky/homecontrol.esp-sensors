"""
MQTT module for ESP sensors.

This module provides functionality to connect to an MQTT broker and publish sensor data.
It supports both real hardware and simulation mode.

This is a custom implementation of the MQTT protocol from scratch, without relying on umqtt.
"""

import time
import json
import socket
import struct

# Determine if we're running on ESP hardware or in simulation mode
try:
    # import network
    SIMULATION = False
except ImportError:
    SIMULATION = True
    print(
        "[MQTT] Running in simulation mode - MQTT messages will be printed to console"
    )

# MQTT Protocol Constants
MQTT_PROTOCOL_LEVEL = 4  # MQTT 3.1.1
MQTT_CLEAN_SESSION = 1

# MQTT Control Packet Types
CONNECT = 0x10
CONNACK = 0x20
PUBLISH = 0x30
PUBACK = 0x40
SUBSCRIBE = 0x80
SUBACK = 0x90
UNSUBSCRIBE = 0xA0
UNSUBACK = 0xB0
PINGREQ = 0xC0
PINGRESP = 0xD0
DISCONNECT = 0xE0

# MQTT Connection Return Codes
CONN_ACCEPTED = 0
CONN_REFUSED_PROTOCOL = 1
CONN_REFUSED_IDENTIFIER = 2
CONN_REFUSED_SERVER = 3
CONN_REFUSED_USER_PASS = 4
CONN_REFUSED_AUTH = 5

class MQTTException(Exception):
    """MQTT Exception class for handling MQTT-specific errors"""
    pass

class MQTTClient:
    """
    A basic MQTT client implementation from scratch.
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
        if SIMULATION:
            # In simulation mode, we don't actually connect to a broker
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
            self.subscriptions = {}  # Track subscribed topics
            self.sock = None
            self.pid = 0  # Packet ID
            return

        # Real implementation for ESP hardware
        self.client_id = client_id
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.keepalive = keepalive
        self.ssl = ssl
        self.sock: socket.socket | None = None
        self.connected = False
        self.callback = None
        self.pid = 0  # Packet ID for message tracking
        self.subscriptions = {}  # Track subscribed topics
        self.last_ping = 0

    def _generate_packet_id(self):
        """Generate a unique packet ID for MQTT messages"""
        self.pid = (self.pid + 1) % 65536
        return self.pid

    def _encode_length(self, length):
        """Encode the remaining length field in the MQTT packet"""
        result = bytearray()
        while True:
            byte = length % 128
            length = length // 128
            if length > 0:
                byte |= 0x80
            result.append(byte)
            if length == 0:
                break
        return result

    def _encode_string(self, string):
        """Encode a string for MQTT packet"""
        if isinstance(string, str):
            string = string.encode('utf-8')
        return bytearray(struct.pack("!H", len(string)) + string)

    def _send_packet(self, packet_type, payload=b''):
        """Send an MQTT packet to the broker"""
        if SIMULATION:
            print(f"[MQTT SIM] Sending packet type: {packet_type:02x}, payload: {payload}")
            return

        if self.sock is None:
            raise MQTTException("Not connected to broker (_send_packet)")

        # Construct the packet
        packet = bytearray()
        packet.append(packet_type)

        # Add remaining length
        packet.extend(self._encode_length(len(payload)))

        # Add payload
        if payload:
            packet.extend(payload)

        # Send the packet
        try:
            self.sock.send(packet)
        except Exception as e:
            self.connected = False
            raise MQTTException(f"Failed to send packet: {e}")

    def _recv_packet(self, timeout=1.0):
        """Receive an MQTT packet from the broker"""
        if SIMULATION:
            # In simulation mode, we don't actually receive packets
            return None, None

        if self.sock is None:
            raise MQTTException("Not connected to broker (_recv_packet)")

        # Set socket timeout
        self.sock.settimeout(timeout)

        try:
            # Read packet type
            packet_type = self.sock.recv(1)
            if not packet_type:
                return None, None

            # Read remaining length
            remaining_length = 0
            multiplier = 1
            while True:
                byte = self.sock.recv(1)[0]
                remaining_length += (byte & 0x7F) * multiplier
                multiplier *= 128
                if not (byte & 0x80):
                    break

            # Read the payload
            payload = self.sock.recv(remaining_length) if remaining_length else b''

            return packet_type[0], payload
        except socket.timeout:
            return None, None
        except Exception as e:
            self.connected = False
            raise MQTTException(f"Failed to receive packet: {e}")

    def connect(self):
        """Connect to the MQTT broker"""
        if SIMULATION:
            print(f"[MQTT SIM] Connecting to {self.server}:{self.port} as {self.client_id}")
            self.connected = True
            return 0

        # Create socket
        try:
            self.sock = socket.socket()
            print(f"[MQTT] Connecting to Socket {self.server}:{self.port} as {self.client_id}")
            self.sock.connect((self.server, self.port))
            print(f"[MQTT] Connected to {self.server}:{self.port}")
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            raise MQTTException(f"Failed to connect to {self.server}:{self.port}: {e}")

        # Construct CONNECT packet
        payload = bytearray()

        # Protocol name and level
        payload.extend(self._encode_string("MQTT"))
        payload.append(MQTT_PROTOCOL_LEVEL)

        # Connect flags
        connect_flags = 0
        if self.user:
            connect_flags |= 0x80
        if self.password:
            connect_flags |= 0x40
        connect_flags |= MQTT_CLEAN_SESSION << 1
        payload.append(connect_flags)

        # Keepalive (in seconds)
        payload.extend(struct.pack("!H", self.keepalive))

        # Client ID
        payload.extend(self._encode_string(self.client_id))

        # Username and password if provided
        if self.user:
            payload.extend(self._encode_string(self.user))
        if self.password:
            payload.extend(self._encode_string(self.password))

        # Send CONNECT packet
        self._send_packet(CONNECT, payload)

        # Wait for CONNACK
        packet_type, payload = self._recv_packet()
        if packet_type != CONNACK:
            raise MQTTException(f"Unexpected response from broker: {packet_type}")

        # Check connection result
        if len(payload) != 2:
            raise MQTTException("Invalid CONNACK packet")

        if payload[1] != CONN_ACCEPTED:
            raise MQTTException(f"Connection refused: {payload[1]}")

        self.connected = True
        self.last_ping = time.time()
        return 0

    def disconnect(self):
        """Disconnect from the MQTT broker"""
        if SIMULATION:
            print("[MQTT SIM] Disconnected")
            self.connected = False
            return

        if self.connected:
            try:
                self._send_packet(DISCONNECT)
                self.sock.close()
            except Exception as e:
                print(f"Error during disconnect: {e}")
            finally:
                self.connected = False
                self.sock = None

    def ping(self):
        """Send PINGREQ to keep the connection alive"""
        if SIMULATION:
            return

        if self.connected:
            self._send_packet(PINGREQ)
            packet_type, _ = self._recv_packet()
            if packet_type != PINGRESP:
                self.connected = False
                raise MQTTException("No PINGRESP received")
            self.last_ping = time.time()

    def publish(self, topic, msg, retain=False, qos=0):
        """Publish a message to a topic"""
        if SIMULATION:
            retain_str = " (retained)" if retain else ""
            print(f"[MQTT SIM] Publishing to {topic}{retain_str}: {msg}")
            return

        if not self.connected:
            raise MQTTException("Not connected to broker (publish)")

        # Check if we need to ping to keep connection alive
        if self.keepalive > 0 and time.time() - self.last_ping >= self.keepalive:
            self.ping()

        # Convert topic and message to bytes if they're not already
        if isinstance(topic, str):
            topic = topic.encode('utf-8')
        if isinstance(msg, str):
            msg = msg.encode('utf-8')

        # Construct PUBLISH packet
        packet_type = PUBLISH
        if retain:
            packet_type |= 0x01
        if qos:
            packet_type |= (qos << 1)

        # Payload: topic + message
        payload = self._encode_string(topic)

        # Add packet ID for QoS > 0
        if qos > 0:
            pid = self._generate_packet_id()
            payload.extend(struct.pack("!H", pid))

        payload.extend(msg)

        # Send PUBLISH packet
        self._send_packet(packet_type, payload)

        # For QoS 1, wait for PUBACK
        if qos == 1:
            packet_type, _ = self._recv_packet()
            if packet_type != PUBACK:
                raise MQTTException(f"No PUBACK received: {packet_type}")

        return

    def subscribe(self, topic, qos=0):
        """Subscribe to a topic"""
        if SIMULATION:
            topic_str = topic.decode('utf-8') if isinstance(topic, bytes) else topic
            print(f"[MQTT SIM] Subscribed to topic: {topic_str}")
            self.subscriptions[topic_str] = qos
            return

        if not self.connected:
            raise MQTTException("Not connected to broker (subscribe)")

        # Check if we need to ping to keep connection alive
        if self.keepalive > 0 and time.time() - self.last_ping >= self.keepalive:
            self.ping()

        # Convert topic to bytes if it's not already
        if isinstance(topic, str):
            topic = topic.encode('utf-8')

        # Generate packet ID
        pid = self._generate_packet_id()

        # Construct SUBSCRIBE packet
        payload = bytearray(struct.pack("!H", pid))
        payload.extend(self._encode_string(topic))
        payload.append(qos)

        # Send SUBSCRIBE packet
        self._send_packet(SUBSCRIBE | 0x02, payload)

        # Wait for SUBACK
        packet_type, payload = self._recv_packet()
        if packet_type != SUBACK:
            raise MQTTException(f"No SUBACK received: {packet_type}")

        # Store subscription
        topic_str = topic.decode('utf-8') if isinstance(topic, bytes) else topic
        self.subscriptions[topic_str] = qos

        return

    def set_callback(self, callback):
        """Set callback for received messages"""
        self.callback = callback
        if SIMULATION:
            print(f"[MQTT SIM] Callback set")

    def check_msg(self):
        """Check for pending messages from the broker"""
        if SIMULATION:
            # In simulation mode, we simulate message checking
            if self.last_message and self.callback:
                self.callback(self.last_topic, self.last_message)
                self.last_message = None
                self.last_topic = None
            return

        if not self.connected:
            return

        # Check if we need to ping to keep connection alive
        if self.keepalive > 0 and time.time() - self.last_ping >= self.keepalive:
            self.ping()

        # Try to receive a packet with a short timeout
        packet_type, payload = self._recv_packet(timeout=0.1)

        if packet_type is None:
            return

        if packet_type & 0xF0 == PUBLISH:
            # Extract flags
            dup = (packet_type & 0x08) >> 3
            qos = (packet_type & 0x06) >> 1
            retain = packet_type & 0x01

            # Extract topic
            topic_len = struct.unpack("!H", payload[0:2])[0]
            topic = payload[2:2+topic_len]

            # Extract packet ID for QoS > 0
            if qos > 0:
                pid = struct.unpack("!H", payload[2+topic_len:2+topic_len+2])[0]
                message = payload[2+topic_len+2:]

                # Send PUBACK for QoS 1
                if qos == 1:
                    self._send_packet(PUBACK, struct.pack("!H", pid))
            else:
                message = payload[2+topic_len:]

            # Call the callback if set
            if self.callback:
                self.callback(topic, message)

        return

    # For simulation only - allows us to simulate receiving a message
    def simulate_message(self, topic, msg):
        """Simulate receiving a message (simulation mode only)"""
        if not SIMULATION:
            return

        self.last_topic = topic
        self.last_message = msg
        print(f"[MQTT SIM] Simulated message received on {topic}: {msg}")
        if self.callback:
            self.callback(topic, msg)


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
            print(f"[ESP32MQTT] Connecting to {self.server}:{self.port} as {self.client_id}")
            # Create our custom MQTT client
            self.client = MQTTClient(
                self.client_id,
                self.server,
                self.port,
                self.user,
                self.password,
                self.keepalive,
                self.ssl
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
        topic_str = topic.decode('utf-8') if isinstance(topic, bytes) else topic
        msg_str = msg.decode('utf-8') if isinstance(msg, bytes) else msg

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
        topic_str = topic if isinstance(topic, str) else topic.decode('utf-8') if isinstance(topic, bytes) else str(topic)
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

        print(f"[ESP32MQTT] No message received on {topic_str} after {wait_time} seconds")
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
            client = ESP32MQTTClient(client_id, broker, port, username, password, keepalive, ssl)

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
            client = MQTTClient(client_id, broker, port, username, password, keepalive, ssl)

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
        client.publish(temp_topic, temp_payload)
        client.publish(humidity_topic, humidity_payload)
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


def subscribe_to_config(client: ESP32MQTTClient | MQTTClient | None, mqtt_config: dict) -> bool:
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


def check_config_update(client: ESP32MQTTClient | MQTTClient | None, mqtt_config: dict, current_config: dict) -> dict:
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

            print(f"Using ESP32MQTTClient to read from config topic with wait time: {wait_time}s")
            config_msg = client.read_topic(topic_config, wait_time)

            if config_msg:
                try:
                    msg_str = config_msg.decode('utf-8') if isinstance(config_msg, bytes) else config_msg
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
                    topic_str = topic.decode('utf-8') if isinstance(topic, bytes) else topic
                    if topic_str != expected_topic:
                        print(f"Ignoring message from topic {topic_str} - not matching our config topic {expected_topic}")
                        return

                    # Parse the message as JSON
                    msg_str = msg.decode('utf-8') if isinstance(msg, bytes) else msg
                    config_data = json.loads(msg_str)
                    print(f"Received configuration from MQTT: version {config_data.get('version', 0)}")
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
        if received_config and received_config.get("version", 0) > current_config.get("version", 0):
            print(f"Found newer configuration (version {received_config.get('version')})")
            return received_config

        return current_config
    except Exception as e:
        print(f"Error checking for configuration updates: {e}")
        return current_config
