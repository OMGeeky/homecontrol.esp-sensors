"""
Tests for the temperature sensor module.
"""

import pytest
from src.esp_sensors.temperature import TemperatureSensor


def test_temperature_sensor_initialization():
    """Test that a temperature sensor can be initialized with valid parameters."""
    sensor = TemperatureSensor("test_sensor", 5, 30, "C")
    assert sensor.name == "test_sensor"
    assert sensor.pin == 5
    assert sensor.interval == 30
    assert sensor.unit == "C"


def test_temperature_sensor_invalid_unit():
    """Test that initializing with an invalid unit raises a ValueError."""
    with pytest.raises(ValueError):
        TemperatureSensor("test_sensor", 5, 30, "K")


def test_temperature_sensor_read():
    """Test that reading from the sensor returns a float value."""
    sensor = TemperatureSensor("test_sensor", 5)
    reading = sensor.read()
    assert isinstance(reading, float)
    # For Celsius, the reading should be between 15.0 and 30.0
    assert 15.0 <= reading <= 30.0


def test_temperature_sensor_fahrenheit():
    """Test that a sensor initialized with Fahrenheit returns appropriate values."""
    sensor = TemperatureSensor("test_sensor", 5, unit="F")
    reading = sensor.read()
    assert isinstance(reading, float)
    # For Fahrenheit, the reading should be between 59.0 and 86.0
    assert 59.0 <= reading <= 86.0


def test_temperature_conversion():
    """Test temperature conversion methods."""
    # Test Celsius to Fahrenheit
    c_sensor = TemperatureSensor("celsius_sensor", 5, unit="C")
    c_sensor._last_reading = 20.0  # Manually set for testing
    f_value = c_sensor.to_fahrenheit()
    assert f_value == 68.0  # 20°C = 68°F

    # Test Fahrenheit to Celsius
    f_sensor = TemperatureSensor("fahrenheit_sensor", 5, unit="F")
    f_sensor._last_reading = 68.0  # Manually set for testing
    c_value = f_sensor.to_celsius()
    assert c_value == 20.0  # 68°F = 20°C


def test_metadata():
    """Test that metadata includes the temperature unit."""
    sensor = TemperatureSensor("test_sensor", 5, unit="C")
    metadata = sensor.get_metadata()
    assert metadata["name"] == "test_sensor"
    assert metadata["pin"] == 5
    assert metadata["unit"] == "C"
    assert metadata["last_reading"] is None  # No reading yet

    # After a reading
    sensor.read()
    metadata = sensor.get_metadata()
    assert metadata["last_reading"] is not None
