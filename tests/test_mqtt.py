"""
Tests for the MQTT module.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.esp_sensors.mqtt import setup_mqtt, publish_sensor_data, MQTTClient


class TestSensor:
    """Mock sensor class for testing."""

    __test__ = False  # Prevent pytest from treating this as a test case

    def __init__(self, name="Test Sensor", temperature_unit="C"):
        self.name = name
        self.unit = temperature_unit


@pytest.fixture
def mqtt_config():
    """Fixture providing a sample MQTT configuration."""
    return {
        "enabled": True,
        "broker": "test.mosquitto.org",
        "port": 1883,
        "client_id": "test_client",
        "username": "test_user",
        "password": "test_pass",
        "topic_prefix": "test/sensors",
        "publish_interval": 30,
        "ssl": False,
        "keepalive": 60,
        "use_esp32_client": True,
    }


@pytest.fixture
def disabled_mqtt_config():
    """Fixture providing a disabled MQTT configuration."""
    return {
        "enabled": False,
        "broker": "test.mosquitto.org",
        "use_esp32_client": True,
    }


@pytest.fixture
def mock_sensor():
    """Fixture providing a mock sensor."""
    return TestSensor(name="DHT22 Sensor", temperature_unit="C")


def test_setup_mqtt_disabled(disabled_mqtt_config):
    """Test that setup_mqtt returns None when MQTT is disabled."""
    client = setup_mqtt(disabled_mqtt_config)
    assert client is None


def test_setup_mqtt_enabled(mqtt_config):
    """Test that setup_mqtt creates and connects a client when MQTT is enabled."""
    with patch("src.esp_sensors.mqtt.ESP32MQTTClient") as mock_mqtt_client:
        # Configure the mock
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance

        # Call the function
        client = setup_mqtt(mqtt_config)

        # Verify MQTTClient was created with correct parameters
        mock_mqtt_client.assert_called_once_with(
            mqtt_config["client_id"],
            mqtt_config["broker"],
            mqtt_config["port"],
            mqtt_config["username"],
            mqtt_config["password"],
            mqtt_config["keepalive"],
            mqtt_config["ssl"],
        )

        # Verify connect was called
        mock_client_instance.connect.assert_called_once()

        # Verify the client was returned
        assert client == mock_client_instance


def test_setup_mqtt_connection_error(mqtt_config):
    """Test that setup_mqtt handles connection errors gracefully."""
    with patch("src.esp_sensors.mqtt.ESP32MQTTClient") as mock_mqtt_client:
        # Configure the mock to raise an exception on connect
        mock_client_instance = MagicMock()
        mock_client_instance.connect.side_effect = Exception("Connection failed")
        mock_mqtt_client.return_value = mock_client_instance

        # Call the function
        client = setup_mqtt(mqtt_config)

        # Verify connect was called
        mock_client_instance.connect.assert_called_once()

        # Verify None was returned due to the error
        assert client is None


def test_publish_sensor_data_success(mqtt_config, mock_sensor):
    """Test that publish_sensor_data publishes to the correct topics."""
    # Create a mock client
    mock_client = MagicMock()

    # Call the function
    temperature = 25.5
    humidity = 60.0
    result = publish_sensor_data(
        mock_client, mqtt_config, mock_sensor, temperature, humidity
    )

    # Verify the result
    assert result is True

    # Verify publish was called for temperature
    temp_topic = f"{mqtt_config['topic_prefix']}/{mock_sensor.name.lower().replace(' ', '_')}/temperature"
    mock_client.publish.assert_any_call(temp_topic, str(temperature).encode())

    # Verify publish was called for humidity
    humidity_topic = f"{mqtt_config['topic_prefix']}/{mock_sensor.name.lower().replace(' ', '_')}/humidity"
    mock_client.publish.assert_any_call(humidity_topic, str(humidity).encode())

    # Verify publish was called for combined data
    data_topic = f"{mqtt_config['topic_prefix']}/{mock_sensor.name.lower().replace(' ', '_')}/data"
    # Check that the JSON data was published
    for call_args in mock_client.publish.call_args_list:
        if call_args[0][0] == data_topic:
            # Parse the JSON data
            data = json.loads(call_args[0][1].decode())
            assert data["temperature"] == temperature
            assert data["humidity"] == humidity
            assert data["unit"] == mock_sensor.unit
            assert "timestamp" in data
            break
    else:
        pytest.fail("Data topic was not published")


def test_publish_sensor_data_no_client(mqtt_config, mock_sensor):
    """Test that publish_sensor_data returns False when client is None."""
    result = publish_sensor_data(None, mqtt_config, mock_sensor, 25.5, 60.0)
    assert result is False


def test_publish_sensor_data_error(mqtt_config, mock_sensor):
    """Test that publish_sensor_data handles errors gracefully."""
    # Create a mock client that raises an exception on publish
    mock_client = MagicMock()
    mock_client.publish.side_effect = Exception("Publish failed")

    # Call the function
    result = publish_sensor_data(mock_client, mqtt_config, mock_sensor, 25.5, 60.0)

    # Verify the result
    assert result is False
