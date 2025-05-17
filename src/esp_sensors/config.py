"""
Configuration module for ESP sensors.

This module provides functionality to load and save configuration settings
from/to a file, making it easy to change parameters like pins, display resolution,
sensor names, and intervals without modifying the code.
"""

import json

# Default configuration file path
DEFAULT_CONFIG_PATH = "config.json"

# Default configuration values
DEFAULT_CONFIG = {
    "sensors": {
        "dht22": {
            "name": "DHT22 Sensor",
            "pin": 4,
            "interval": 60,
            "temperature": {"name": "DHT22 Temperature", "unit": "C"},
            "humidity": {"name": "DHT22 Humidity"},
        }
    },
    "displays": {
        "oled": {
            "name": "OLED Display",
            "scl_pin": 22,
            "sda_pin": 21,
            "width": 128,
            "height": 64,
            "address": "0x3C",
            "interval": 1,
        }
    },
    "buttons": {"main_button": {"pin": 0, "pull_up": True}},
    "mqtt": {
        "enabled": False,
        "broker": "mqtt.example.com",
        "port": 1883,
        "client_id": "esp_sensor",
        "username": "",
        "password": "",
        "topic_prefix": "esp/sensors",
        "publish_interval": 60,  # seconds
        "ssl": False,
        "keepalive": 60,
    },
    "network": {
        "ssid": "<your ssid>",
        "password": "<your password>",
        "timeout": 10,
    }
}


def load_config(config_path: str = DEFAULT_CONFIG_PATH) :
    """
    Load configuration from a JSON file.

    Args:
        config_path: Path to the configuration file (default: config.json)

    Returns:
        A dictionary containing the configuration

    If the file doesn't exist or can't be read, returns the default configuration.
    """
    try:
        with open(config_path, "r") as f:
            print(f"Loading configuration from '{config_path}'")
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}. Using default configuration.")
        return DEFAULT_CONFIG


def get_sensor_config(
    sensor_type: str, config: dict | None = None
) -> dict:
    """
    Get configuration for a specific sensor type.

    Args:
        sensor_type: Type of the sensor (e.g., 'temperature', 'humidity', 'dht22')
        config: Configuration dictionary (if None, loads from default path)

    Returns:
        A dictionary containing the sensor configuration
    """
    if config is None:
        config = load_config()

    # Try to get the sensor configuration, fall back to default if not found
    sensor_config = config.get("sensors", {}).get(sensor_type)
    if sensor_config is None:
        sensor_config = DEFAULT_CONFIG.get("sensors", {}).get(sensor_type, {})

    return sensor_config


def get_display_config(
    display_type: str, config: dict | None = None
) -> dict:
    """
    Get configuration for a specific display type.

    Args:
        display_type: Type of the display (e.g., 'oled')
        config: Configuration dictionary (if None, loads from default path)

    Returns:
        A dictionary containing the display configuration
    """
    if config is None:
        config = load_config()

    # Try to get the display configuration, fall back to default if not found
    display_config = config.get("displays", {}).get(display_type)
    if display_config is None:
        display_config = DEFAULT_CONFIG.get("displays", {}).get(display_type, {})

    return display_config


def get_button_config(
    button_name: str = "main_button", config: dict | None = None
) -> dict:
    """
    Get configuration for a specific button.

    Args:
        button_name: Name of the button (e.g., 'main_button')
        config: Configuration dictionary (if None, loads from default path)

    Returns:
        A dictionary containing the button configuration
    """
    if config is None:
        config = load_config()

    # Try to get the button configuration, fall back to default if not found
    button_config = config.get("buttons", {}).get(button_name)
    if button_config is None:
        button_config = DEFAULT_CONFIG.get("buttons", {}).get(button_name, {})

    return button_config


def get_mqtt_config(config: dict | None = None) -> dict:
    """
    Get MQTT configuration.

    Args:
        config: Configuration dictionary (if None, loads from default path)

    Returns:
        A dictionary containing the MQTT configuration
    """
    if config is None:
        config = load_config()

    # Try to get the MQTT configuration, fall back to default if not found
    mqtt_config = config.get("mqtt")
    if mqtt_config is None:
        mqtt_config = DEFAULT_CONFIG.get("mqtt", {})

    return mqtt_config
