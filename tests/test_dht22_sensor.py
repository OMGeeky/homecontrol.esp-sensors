"""
Tests for the DHT22 sensor module.
"""

import pytest
from src.esp_sensors.dht22 import DHT22Sensor
from src.esp_sensors.config import get_sensor_config


def test_dht22_sensor_initialization():
    """Test that a DHT22 sensor can be initialized with valid parameters."""
    # Test direct parameter initialization
    sensor = DHT22Sensor(name="test_sensor", pin=5, interval=30, temperature_unit="C")
    assert sensor.name == "test_sensor"
    assert sensor.pin == 5
    assert sensor.interval == 30
    assert sensor.unit == "C"
    assert sensor._last_humidity is None

    # Test initialization with custom config
    test_config = {
        "name": "config_sensor",
        "pin": 6,
        "interval": 40,
        "temperature": {"name": "Config Temperature", "unit": "F"},
        "humidity": {"name": "Config Humidity"},
    }

    config_sensor = DHT22Sensor(sensor_config=test_config)
    assert config_sensor.name == "config_sensor"
    assert config_sensor.pin == 6
    assert config_sensor.interval == 40
    assert config_sensor.unit == "F"
    assert config_sensor._last_humidity is None


def test_dht22_sensor_invalid_unit():
    """Test that initializing with an invalid unit raises a ValueError."""
    with pytest.raises(ValueError):
        DHT22Sensor(name="test_sensor", pin=5, interval=30, temperature_unit="K")


def test_dht22_sensor_read_temperature():
    """Test that reading temperature from the sensor returns a float value."""
    sensor = DHT22Sensor(name="test_sensor", pin=5)
    reading = sensor.read()
    assert isinstance(reading, float)
    # For Celsius, the reading should be between 15.0 and 30.0
    assert 15.0 <= reading <= 30.0


def test_dht22_sensor_read_humidity():
    """Test that reading humidity from the sensor returns a float value."""
    sensor = DHT22Sensor(name="test_sensor", pin=5)
    humidity = sensor.read_humidity()
    assert isinstance(humidity, float)
    # Humidity should be between 30.0% and 90.0%
    assert 30.0 <= humidity <= 90.0


def test_dht22_sensor_fahrenheit():
    """Test that a sensor initialized with Fahrenheit returns appropriate values."""
    sensor = DHT22Sensor(name="test_sensor", pin=5, temperature_unit="F")
    reading = sensor.read()
    assert isinstance(reading, float)
    # For Fahrenheit, the reading should be between 59.0 and 86.0
    assert 59.0 <= reading <= 86.0


def test_dht22_temperature_conversion():
    """Test temperature conversion methods."""
    # Test Celsius to Fahrenheit
    c_sensor = DHT22Sensor(name="celsius_sensor", pin=5, temperature_unit="C")
    c_sensor._last_reading = 20.0  # Manually set for testing
    f_value = c_sensor.to_fahrenheit()
    assert f_value == 68.0  # 20°C = 68°F

    # Test Fahrenheit to Celsius
    f_sensor = DHT22Sensor(name="fahrenheit_sensor", pin=5, temperature_unit="F")
    f_sensor._last_reading = 68.0  # Manually set for testing
    c_value = f_sensor.to_celsius()
    assert c_value == 20.0  # 68°F = 20°C


def test_dht22_metadata():
    """Test that metadata includes the temperature unit, humidity, and type."""
    sensor = DHT22Sensor(name="test_sensor", pin=5, temperature_unit="C")
    metadata = sensor.get_metadata()
    assert metadata["name"] == "test_sensor"
    assert metadata["pin"] == 5
    assert metadata["unit"] == "C"
    assert metadata["last_reading"] is None  # No reading yet
    assert metadata["last_humidity"] is None  # No reading yet
    assert metadata["type"] == "DHT22"

    # After a reading
    sensor.read()
    metadata = sensor.get_metadata()
    assert metadata["last_reading"] is not None
    assert metadata["last_humidity"] is not None


def test_dht22_read_updates_both_values():
    """Test that reading temperature also updates humidity."""
    sensor = DHT22Sensor(name="test_sensor", pin=5)
    assert sensor._last_humidity is None

    # Reading temperature should also update humidity
    sensor.read()
    assert sensor._last_humidity is not None

    # Reset humidity to test read_humidity
    old_temp = sensor._last_reading
    sensor._last_humidity = None

    # Reading humidity should not change temperature
    humidity = sensor.read_humidity()
    assert sensor._last_reading == old_temp
    assert humidity is not None
