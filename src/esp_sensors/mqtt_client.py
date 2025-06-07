"""
MQTT Client module for ESP sensors.

This module provides a basic MQTT client implementation from scratch,
without relying on umqtt. It handles the low-level details of the MQTT protocol
and provides a simple interface for connecting to an MQTT broker, publishing
messages, and subscribing to topics.
"""

import time
import json
import socket
import struct

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

    This class implements the MQTT protocol directly using socket communication.
    It provides functionality for connecting to an MQTT broker, publishing messages,
    subscribing to topics, and receiving messages.

    Attributes:
        client_id (str): Unique identifier for this client
        server (str): MQTT broker address
        port (int): MQTT broker port
        user (str): Username for authentication
        password (str): Password for authentication
        keepalive (int): Keepalive interval in seconds
        ssl (bool): Whether to use SSL/TLS
        sock (socket.socket): Socket connection to the broker
        connected (bool): Whether the client is connected to the broker
        callback (callable): Callback function for received messages
        pid (int): Packet ID for message tracking
        subscriptions (dict): Dictionary of subscribed topics
        last_ping (float): Timestamp of the last ping
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
            client_id (str): Unique identifier for this client
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
        self.sock: socket.socket | None = None
        self.connected = False
        self.callback = None
        self.pid = 0  # Packet ID for message tracking
        self.subscriptions = {}  # Track subscribed topics
        self.last_ping = 0

    def _generate_packet_id(self):
        """
        Generate a unique packet ID for MQTT messages.

        Returns:
            int: A unique packet ID between 1 and 65535
        """
        self.pid = (self.pid + 1) % 65536
        return self.pid

    def _encode_length(self, length):
        """
        Encode the remaining length field in the MQTT packet.

        Args:
            length (int): The length to encode

        Returns:
            bytearray: The encoded length
        """
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
        """
        Encode a string for MQTT packet.

        Args:
            string (str or bytes): The string to encode

        Returns:
            bytearray: The encoded string
        """
        if isinstance(string, str):
            string = string.encode("utf-8")
        return bytearray(struct.pack("!H", len(string)) + string)

    def _send_packet(self, packet_type, payload=b""):
        """
        Send an MQTT packet to the broker.

        Args:
            packet_type (int): The MQTT packet type
            payload (bytes): The packet payload

        Raises:
            MQTTException: If the client is not connected or sending fails
        """
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
        """
        Receive an MQTT packet from the broker.

        Args:
            timeout (float): Socket timeout in seconds

        Returns:
            tuple: (packet_type, payload) or (None, None) if no packet received

        Raises:
            MQTTException: If the client is not connected or receiving fails
        """
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
            payload = self.sock.recv(remaining_length) if remaining_length else b""

            return packet_type[0], payload
        except socket.timeout:
            return None, None
        except Exception as e:
            self.connected = False
            raise MQTTException(f"Failed to receive packet: {e}")

    def connect(self):
        """
        Connect to the MQTT broker.

        Returns:
            int: 0 if successful, otherwise an error code

        Raises:
            MQTTException: If connection fails
        """
        # Create socket
        try:
            self.sock = socket.socket()
            print(
                f"[MQTT] Connecting to Socket {self.server}:{self.port} as {self.client_id}"
            )
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
        """
        Disconnect from the MQTT broker.
        """
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
        """
        Send PINGREQ to keep the connection alive.

        Raises:
            MQTTException: If no PINGRESP is received
        """
        if self.connected:
            self._send_packet(PINGREQ)
            packet_type, _ = self._recv_packet()
            if packet_type != PINGRESP:
                self.connected = False
                raise MQTTException("No PINGRESP received")
            self.last_ping = time.time()

    def publish(self, topic, msg, retain=False, qos=0):
        """
        Publish a message to a topic.

        Args:
            topic (str or bytes): The topic to publish to
            msg (str or bytes): The message to publish
            retain (bool): Whether the message should be retained by the broker
            qos (int): Quality of Service level (0 or 1)

        Raises:
            MQTTException: If the client is not connected or publishing fails
        """
        if not self.connected:
            raise MQTTException("Not connected to broker (publish)")

        # Check if we need to ping to keep connection alive
        if self.keepalive > 0 and time.time() - self.last_ping >= self.keepalive:
            self.ping()

        # Convert topic and message to bytes if they're not already
        if isinstance(topic, str):
            topic = topic.encode("utf-8")
        if isinstance(msg, str):
            msg = msg.encode("utf-8")

        # Construct PUBLISH packet
        packet_type = PUBLISH
        if retain:
            packet_type |= 0x01
        if qos:
            packet_type |= qos << 1

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
        """
        Subscribe to a topic.

        Args:
            topic (str or bytes): The topic to subscribe to
            qos (int): Quality of Service level

        Raises:
            MQTTException: If the client is not connected or subscription fails
        """
        if not self.connected:
            raise MQTTException("Not connected to broker (subscribe)")

        # Check if we need to ping to keep connection alive
        if self.keepalive > 0 and time.time() - self.last_ping >= self.keepalive:
            self.ping()

        # Convert topic to bytes if it's not already
        if isinstance(topic, str):
            topic = topic.encode("utf-8")

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
        topic_str = topic.decode("utf-8") if isinstance(topic, bytes) else topic
        self.subscriptions[topic_str] = qos

        return

    def set_callback(self, callback):
        """
        Set callback for received messages.

        Args:
            callback (callable): Function to call when a message is received.
                                The callback should accept two parameters:
                                topic (bytes) and message (bytes).
        """
        self.callback = callback

    def check_msg(self):
        """
        Check for pending messages from the broker.

        This method should be called regularly to process incoming messages.
        If a callback is set, it will be called with the topic and message.
        """
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
            topic = payload[2 : 2 + topic_len]

            # Extract packet ID for QoS > 0
            if qos > 0:
                pid = struct.unpack("!H", payload[2 + topic_len : 2 + topic_len + 2])[0]
                message = payload[2 + topic_len + 2 :]

                # Send PUBACK for QoS 1
                if qos == 1:
                    self._send_packet(PUBACK, struct.pack("!H", pid))
            else:
                message = payload[2 + topic_len :]

            # Call the callback if set
            if self.callback:
                self.callback(topic, message)

        return
