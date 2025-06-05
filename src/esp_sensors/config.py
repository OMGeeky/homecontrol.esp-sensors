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
    "device_id": "livingroom",
    "device_name": "Wohnzimmer",
    "update_interval": 60,
    "version": 1,
    "sensors": {
        "dht22": {
            "id": "wohnzimmer-dht22",
            "name": "Wohnzimmer",
            "pin": 16,
            "interval": 60,
            "temperature": {"name": "DHT22 Temperature", "unit": "C"},
            "humidity": {"name": "DHT22 Humidity"},
        }
    },
    "displays": {
        "oled": {
            "name": "OLED Display",
            "enabled": True,
            "always_on": False,
            "scl_pin": 22,
            "sda_pin": 21,
            "width": 128,
            "height": 64,
            "address": "0x3C",
            "interval": 5,
        }
    },
    "buttons": {"main_button": {"pin": 0, "pull_up": True}},
    "mqtt": {
        "enabled": False,
        "broker": "mqtt.example.com",
        "port": 1883,
        "client_id": "{device_id}",
        "username": "",
        "password": "",
        "load_config_from_mqtt": True,
        "topic_config": "/homecontrol/{device_id}/config",
        "topic_data_prefix": "/homecontrol/{device_id}/data",
        "ssl": False,
        "keepalive": 60,
    },
    "network": {
        "ssid": "<your ssid>",
        "password": "<your password>",
        "timeout": 10,
    },
    "network_fallback": {
        "ssid": "<your fallback ssid>",
        "password": "<your fallback password>",
        "timeout": 10,
    }
}

class Config:
    """
    Configuration class to manage loading and saving configuration settings.
    """

    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        self.current_version = None
        self.update_interval = None
        self.device_name = None
        self.device_id = None
        self.network_fallback_config = None
        self.network_config = None
        self.display_config = None
        self.dht_config = None
        self.mqtt_config = None

        self.config_path = config_path
        self.config = self.load_config()

        # Get configuration sections
        config = self.config
        self.update_configs(config)

    def update_configs(self, config):
        self.mqtt_config = get_mqtt_config(config)
        self.dht_config = get_sensor_config("dht22", config)
        self.display_config = get_display_config("oled", config)
        self.network_config = config.get("network", {})
        self.network_fallback_config = config.get("network_fallback", {})
        # Get device information and update interval
        self.device_id = config.get("device_id", "esp_sensor")
        self.device_name = config.get("device_name", "ESP Sensor")
        self.update_interval = config.get("update_interval", 60)
        self.current_version = config.get("version", 0)

    def load_config(self) -> dict:
        """
        Load configuration from the specified file.

        Returns:
            A dictionary containing the configuration
        """
        return load_config(self.config_path)

    def save_config(self, config: dict) -> bool:
        """
        Save the provided configuration to the file.

        Args:
            config: Configuration dictionary to save

        Returns:
            True if saving was successful, False otherwise
        """
        self.config = config
        self.update_configs(config)
        return save_config_to_file(config, self.config_path)

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

    # Replace {device_id} placeholders in MQTT configuration
    device_id = config.get("device_id", DEFAULT_CONFIG.get("device_id", "esp_sensor"))
    mqtt_config = replace_device_id_placeholders(mqtt_config, device_id)

    return mqtt_config


def replace_device_id_placeholders(config_section: dict, device_id: str) -> dict:
    """
    Replace {device_id} placeholders in configuration values.

    Args:
        config_section: Configuration section to process
        device_id: Device ID to use for replacement

    Returns:
        Configuration section with placeholders replaced
    """
    result = {}
    for key, value in config_section.items():
        if isinstance(value, str) and "{device_id}" in value:
            result[key] = value.replace("{device_id}", device_id)
        else:
            result[key] = value
    return result


def save_config_to_file(config: dict, config_path: str = DEFAULT_CONFIG_PATH) -> bool:
    """
    Save configuration to a JSON file.

    Args:
        config: Configuration dictionary to save
        config_path: Path to the configuration file (default: config.json)

    Returns:
        True if saving was successful, False otherwise
    """
    try:
        config_json = json.dumps(config)
        with open(config_path, "w") as f:
            f.write(config_json)
        print(f"Configuration saved to '{config_path}'")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def check_and_update_config_from_mqtt(mqtt_client, mqtt_config: dict, current_config: dict) -> dict:
    """
    Check for configuration updates from MQTT and update local configuration if needed.

    Args:
        mqtt_client: MQTT client instance
        mqtt_config: MQTT configuration dictionary
        current_config: Current configuration dictionary

    Returns:
        Updated configuration dictionary if an update was found, otherwise the current configuration
    """
    if not mqtt_config.get("load_config_from_mqtt", False):
        print("Loading config from MQTT is disabled")
        return current_config

    try:
        # Get the configuration topic
        topic_config = mqtt_config.get("topic_config")
        if not topic_config:
            print("No configuration topic specified")
            return current_config

        # Subscribe to the configuration topic
        print(f"Subscribing to configuration topic: {topic_config}")

        # This is a simplified implementation - in a real implementation, we would
        # set up a callback to handle the message and wait for it to be received
        # For now, we'll just return the current configuration

        # In a real implementation, we would:
        # 1. Subscribe to the topic
        # 2. Wait for a message (with timeout)
        # 3. Parse the message as JSON
        # 4. Check if the version is newer than the current version
        # 5. If it is, update the local configuration and save it

        print("MQTT configuration update check not implemented yet")
        return current_config
    except Exception as e:
        print(f"Error checking for configuration updates: {e}")
        return current_config
