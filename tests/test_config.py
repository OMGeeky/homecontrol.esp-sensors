"""
Tests for the configuration module.
"""

import os
import json
import tempfile
import pytest
from src.esp_sensors.config import (
    load_config,
    get_sensor_config,
    get_display_config,
    DEFAULT_CONFIG,
)


def test_load_default_config():
    """Test that default configuration is loaded when file doesn't exist."""
    # Use a non-existent file path
    config = load_config("non_existent_file.json")

    # Check that the default configuration was loaded
    assert config == DEFAULT_CONFIG
    assert "sensors" in config
    assert "displays" in config


def test_get_sensor_config():
    """Test getting sensor configuration."""
    # Create a test configuration
    test_config = {
        "sensors": {"test_sensor": {"name": "Test Sensor", "pin": 10, "interval": 30}}
    }

    # Get configuration for an existing sensor
    sensor_config = get_sensor_config("test_sensor", test_config)
    assert sensor_config["name"] == "Test Sensor"
    assert sensor_config["pin"] == 10
    assert sensor_config["interval"] == 30

    # Get configuration for a non-existent sensor (should return default or empty dict)
    non_existent_config = get_sensor_config("non_existent", test_config)
    assert isinstance(non_existent_config, dict)


def test_get_display_config():
    """Test getting display configuration."""
    # Create a test configuration
    test_config = {
        "displays": {
            "test_display": {"name": "Test Display", "width": 64, "height": 32}
        }
    }

    # Get configuration for an existing display
    display_config = get_display_config("test_display", test_config)
    assert display_config["name"] == "Test Display"
    assert display_config["width"] == 64
    assert display_config["height"] == 32

    # Get configuration for a non-existent display (should return default or empty dict)
    non_existent_config = get_display_config("non_existent", test_config)
    assert isinstance(non_existent_config, dict)
