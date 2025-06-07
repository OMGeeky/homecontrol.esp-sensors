"""
Tests for the MQTT Client module.

This module contains tests for the MQTTClient class in the mqtt_client.py module.
"""

import pytest
import socket
import struct
from unittest.mock import patch, MagicMock, call
from src.esp_sensors.mqtt_client import (
    MQTTClient, MQTTException,
    CONNECT, CONNACK, PUBLISH, PUBACK, SUBSCRIBE, SUBACK,
    PINGREQ, PINGRESP, DISCONNECT,
    CONN_ACCEPTED
)


class TestMQTTClient:
    """Tests for the MQTTClient class."""

    @pytest.fixture
    def mqtt_client(self):
        """Fixture providing a basic MQTTClient instance."""
        return MQTTClient(
            client_id="test_client",
            server="test.mosquitto.org",
            port=1883,
            user="test_user",
            password="test_pass",
            keepalive=60,
            ssl=False
        )

    def test_init(self, mqtt_client):
        """Test that the MQTTClient initializes with the correct attributes."""
        assert mqtt_client.client_id == "test_client"
        assert mqtt_client.server == "test.mosquitto.org"
        assert mqtt_client.port == 1883
        assert mqtt_client.user == "test_user"
        assert mqtt_client.password == "test_pass"
        assert mqtt_client.keepalive == 60
        assert mqtt_client.ssl is False
        assert mqtt_client.sock is None
        assert mqtt_client.connected is False
        assert mqtt_client.callback is None
        assert mqtt_client.pid == 0
        assert mqtt_client.subscriptions == {}
        assert mqtt_client.last_ping == 0

    def test_generate_packet_id(self, mqtt_client):
        """Test that _generate_packet_id returns sequential IDs and wraps around."""
        # First call should return 1
        assert mqtt_client._generate_packet_id() == 1
        assert mqtt_client.pid == 1

        # Second call should return 2
        assert mqtt_client._generate_packet_id() == 2
        assert mqtt_client.pid == 2

        # Set pid to 65535 (max value)
        mqtt_client.pid = 65535

        # Next call should wrap around to 0
        assert mqtt_client._generate_packet_id() == 0
        assert mqtt_client.pid == 0

    def test_encode_length(self, mqtt_client):
        """Test that _encode_length correctly encodes MQTT remaining length."""
        # Test small length (< 128)
        assert list(mqtt_client._encode_length(64)) == [64]

        # Test medium length (128-16383)
        assert list(mqtt_client._encode_length(128)) == [128 & 0x7F | 0x80, 1]
        assert list(mqtt_client._encode_length(8192)) == [0x80, 0x40]

        # Test large length (16384-2097151)
        assert list(mqtt_client._encode_length(2097151)) == [0xFF, 0xFF, 0x7F]

    def test_encode_string(self, mqtt_client):
        """Test that _encode_string correctly encodes strings for MQTT packets."""
        # Test with string input
        result = mqtt_client._encode_string("test")
        assert len(result) == 6  # 2 bytes length + 4 bytes string
        assert result[0:2] == b'\x00\x04'  # Length (4) in network byte order
        assert result[2:] == b'test'  # String content

        # Test with bytes input
        result = mqtt_client._encode_string(b"test")
        assert len(result) == 6
        assert result[0:2] == b'\x00\x04'
        assert result[2:] == b'test'

    @patch('socket.socket')
    def test_connect_success(self, mock_socket, mqtt_client):
        """Test successful connection to MQTT broker."""
        # Configure the mock socket
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Mock the _recv_packet method to return a successful CONNACK
        with patch.object(mqtt_client, '_recv_packet', return_value=(CONNACK, b'\x00\x00')):
            # Call connect
            result = mqtt_client.connect()

            # Verify socket was created and connected
            mock_socket.assert_called_once()
            mock_sock.connect.assert_called_once_with(("test.mosquitto.org", 1883))

            # Verify CONNECT packet was sent
            mock_sock.send.assert_called_once()

            # Verify result
            assert result == 0
            assert mqtt_client.connected is True
            assert mqtt_client.sock is mock_sock

    @patch('socket.socket')
    def test_connect_failure(self, mock_socket, mqtt_client):
        """Test connection failure to MQTT broker."""
        # Configure the mock socket
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Mock the _recv_packet method to return a failed CONNACK
        with patch.object(mqtt_client, '_recv_packet', return_value=(CONNACK, b'\x00\x01')):
            # Call connect and verify it raises an exception
            with pytest.raises(MQTTException, match="Connection refused: 1"):
                mqtt_client.connect()

    @patch('socket.socket')
    def test_disconnect(self, mock_socket, mqtt_client):
        """Test disconnection from MQTT broker."""
        # Configure the mock socket
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Set up the client as connected
        mqtt_client.sock = mock_sock
        mqtt_client.connected = True

        # Call disconnect
        mqtt_client.disconnect()

        # Verify DISCONNECT packet was sent
        mock_sock.send.assert_called_once()

        # Verify socket was closed
        mock_sock.close.assert_called_once()

        # Verify client state
        assert mqtt_client.connected is False
        assert mqtt_client.sock is None

    @patch('socket.socket')
    def test_publish(self, mock_socket, mqtt_client):
        """Test publishing a message to a topic."""
        # Configure the mock socket
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Set up the client as connected
        mqtt_client.sock = mock_sock
        mqtt_client.connected = True
        mqtt_client.last_ping = 0

        # Call publish with QoS 0
        mqtt_client.publish("test/topic", "test message")

        # Verify PUBLISH packet was sent
        mock_sock.send.assert_called_once()

        # Test with QoS 1
        mock_sock.reset_mock()

        # Mock the _recv_packet method instead of directly mocking socket.recv
        with patch.object(mqtt_client, '_recv_packet', return_value=(PUBACK, b'\x00\x01')):
            mqtt_client.publish("test/topic", "test message", qos=1)

            # Verify PUBLISH packet was sent
            assert mock_sock.send.call_count == 1

    @patch('socket.socket')
    def test_subscribe(self, mock_socket, mqtt_client):
        """Test subscribing to a topic."""
        # Configure the mock socket
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Set up the client as connected
        mqtt_client.sock = mock_sock
        mqtt_client.connected = True
        mqtt_client.last_ping = 0

        # Mock the _recv_packet method to return a successful SUBACK
        with patch.object(mqtt_client, '_recv_packet', return_value=(SUBACK, b'\x00\x01\x00')):
            # Call subscribe
            mqtt_client.subscribe("test/topic")

            # Verify SUBSCRIBE packet was sent
            mock_sock.send.assert_called_once()

            # Verify subscription was stored
            assert "test/topic" in mqtt_client.subscriptions
            assert mqtt_client.subscriptions["test/topic"] == 0

    @patch('socket.socket')
    def test_check_msg(self, mock_socket, mqtt_client):
        """Test checking for messages."""
        # Configure the mock socket
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Set up the client as connected
        mqtt_client.sock = mock_sock
        mqtt_client.connected = True
        mqtt_client.last_ping = 0

        # Set up a mock callback
        mock_callback = MagicMock()
        mqtt_client.set_callback(mock_callback)

        # Prepare the topic and message
        topic = "test/topic"
        message = "test message"
        topic_encoded = struct.pack("!H", len(topic)) + topic.encode()
        payload = topic_encoded + message.encode()

        # Mock the _recv_packet method to return a PUBLISH packet
        with patch.object(mqtt_client, '_recv_packet', return_value=(PUBLISH, payload)):
            # Call check_msg
            mqtt_client.check_msg()

            # Verify callback was called with correct parameters
            mock_callback.assert_called_once_with(topic.encode(), message.encode())

    def test_set_callback(self, mqtt_client):
        """Test setting a callback function."""
        # Create a mock callback
        mock_callback = MagicMock()

        # Set the callback
        mqtt_client.set_callback(mock_callback)

        # Verify callback was set
        assert mqtt_client.callback is mock_callback
