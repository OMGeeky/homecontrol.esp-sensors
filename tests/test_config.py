"""
Tests for the configuration module.
"""

import os
import json
import tempfile
import pytest
from src.esp_sensors.config import (
    load_config,
    save_config,
    get_sensor_config,
    get_display_config,
    create_default_config,
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


def test_save_and_load_config():
    """Test saving and loading configuration."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Create a test configuration
        test_config = {
            "sensors": {
                "test_sensor": {"name": "Test Sensor", "pin": 10, "interval": 30}
            }
        }

        # Save the configuration
        result = save_config(test_config, temp_path)
        assert result is True

        # Load the configuration
        loaded_config = load_config(temp_path)

        # Check that the loaded configuration matches the saved one
        assert loaded_config == test_config
        assert loaded_config["sensors"]["test_sensor"]["name"] == "Test Sensor"
        assert loaded_config["sensors"]["test_sensor"]["pin"] == 10
        assert loaded_config["sensors"]["test_sensor"]["interval"] == 30

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


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


def test_create_default_config():
    """Test creating a default configuration file."""
    # Create a temporary file path
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Remove the file (we just want the path)
        os.unlink(temp_path)

        # Create the default configuration
        result = create_default_config(temp_path)
        assert result is True

        # Check that the file exists
        assert os.path.exists(temp_path)

        # Load the configuration and check it matches the default
        with open(temp_path, "r") as f:
            config = json.load(f)

        assert config == DEFAULT_CONFIG

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
