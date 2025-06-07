"""
Tests for the configuration update functionality.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from src.esp_sensors.mqtt import check_config_update, ESP32MQTTClient


@pytest.fixture
def mqtt_config():
    """Fixture providing a sample MQTT configuration with version and data topics."""
    return {
        "enabled": True,
        "broker": "test.mosquitto.org",
        "port": 1883,
        "client_id": "test_client",
        "username": "test_user",
        "password": "test_pass",
        "load_config_from_mqtt": True,
        "topic_config_version": "test/config/version",
        "topic_config_data": "test/config/data",
        "topic_data_prefix": "test/sensors",
        "publish_interval": 30,
        "ssl": False,
        "keepalive": 60,
        "use_esp32_client": True,
    }


@pytest.fixture
def current_config():
    """Fixture providing a sample current configuration."""
    return {
        "device_id": "test_device",
        "device_name": "Test Device",
        "version": 5,
        "sensors": {
            "dht22": {
                "id": "test-dht22",
                "name": "Test Sensor",
                "pin": 16,
                "interval": 60,
            }
        },
    }


@pytest.fixture
def new_config():
    """Fixture providing a sample new configuration."""
    return {
        "device_id": "test_device",
        "device_name": "Test Device Updated",
        "version": 6,
        "sensors": {
            "dht22": {
                "id": "test-dht22",
                "name": "Test Sensor Updated",
                "pin": 16,
                "interval": 30,
            }
        },
    }


def test_check_config_update_no_client(mqtt_config, current_config):
    """Test that check_config_update returns the current config when client is None."""
    result = check_config_update(None, mqtt_config, current_config)
    assert result == current_config


def test_check_config_update_disabled(mqtt_config, current_config):
    """Test that check_config_update returns the current config when load_config_from_mqtt is False."""
    mqtt_config["load_config_from_mqtt"] = False
    mock_client = MagicMock()
    result = check_config_update(mock_client, mqtt_config, current_config)
    assert result == current_config


def test_check_config_update_esp32_newer_version(
    mqtt_config, current_config, new_config
):
    """Test that check_config_update returns the new config when a newer version is available (ESP32MQTTClient)."""
    # Create a mock ESP32MQTTClient
    mock_client = MagicMock(spec=ESP32MQTTClient)

    # Configure the mock to return a version and then the new config
    mock_client.read_topic.side_effect = [
        str(new_config["version"]),  # First call returns the version
        json.dumps(new_config),  # Second call returns the config data
    ]

    # Call the function
    result = check_config_update(mock_client, mqtt_config, current_config)

    # Verify the result
    assert result == new_config

    # Verify read_topic was called for both topics
    assert mock_client.read_topic.call_count == 2
    mock_client.read_topic.assert_any_call(mqtt_config["topic_config_version"], 5.0)
    mock_client.read_topic.assert_any_call(mqtt_config["topic_config_data"], 5.0)


def test_check_config_update_esp32_same_version(mqtt_config, current_config):
    """Test that check_config_update returns the current config when the version is the same (ESP32MQTTClient)."""
    # Create a mock ESP32MQTTClient
    mock_client = MagicMock(spec=ESP32MQTTClient)

    # Configure the mock to return the same version
    mock_client.read_topic.return_value = str(current_config["version"])

    # Call the function
    result = check_config_update(mock_client, mqtt_config, current_config)

    # Verify the result
    assert result == current_config

    # Verify read_topic was called only for the version topic
    mock_client.read_topic.assert_called_once_with(
        mqtt_config["topic_config_version"], 5.0
    )


def test_check_config_update_esp32_older_version(mqtt_config, current_config):
    """Test that check_config_update returns the current config when the version is older (ESP32MQTTClient)."""
    # Create a mock ESP32MQTTClient
    mock_client = MagicMock(spec=ESP32MQTTClient)

    # Configure the mock to return an older version
    mock_client.read_topic.return_value = str(current_config["version"] - 1)

    # Call the function
    result = check_config_update(mock_client, mqtt_config, current_config)

    # Verify the result
    assert result == current_config

    # Verify read_topic was called only for the version topic
    mock_client.read_topic.assert_called_once_with(
        mqtt_config["topic_config_version"], 5.0
    )


def test_check_config_update_esp32_no_version(mqtt_config, current_config):
    """Test that check_config_update returns the current config when no version is available (ESP32MQTTClient)."""
    # Create a mock ESP32MQTTClient
    mock_client = MagicMock(spec=ESP32MQTTClient)

    # Configure the mock to return None for the version
    mock_client.read_topic.return_value = None

    # Call the function
    result = check_config_update(mock_client, mqtt_config, current_config)

    # Verify the result
    assert result == current_config

    # Verify read_topic was called only for the version topic
    mock_client.read_topic.assert_called_once_with(
        mqtt_config["topic_config_version"], 5.0
    )
