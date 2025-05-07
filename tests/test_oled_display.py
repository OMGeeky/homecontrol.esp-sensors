"""
Tests for the OLED display module.
"""

import pytest
from src.esp_sensors.oled_display import OLEDDisplay


def test_oled_display_initialization():
    """Test that an OLED display can be initialized with valid parameters."""
    display = OLEDDisplay("test_display", scl_pin=22, sda_pin=21)
    assert display.name == "test_display"
    assert display.scl_pin == 22
    assert display.sda_pin == 21
    assert display.pin == 21  # pin in base class is set to sda_pin
    assert display.width == 128
    assert display.height == 64
    assert display.address == 0x3C
    assert display.interval == 60
    assert display._values == []


def test_oled_display_custom_parameters():
    """Test that an OLED display can be initialized with custom parameters."""
    display = OLEDDisplay(
        "custom_display",
        scl_pin=22,
        sda_pin=21,
        width=64,
        height=32,
        address=0x3D,
        interval=30,
    )
    assert display.name == "custom_display"
    assert display.scl_pin == 22
    assert display.sda_pin == 21
    assert display.width == 64
    assert display.height == 32
    assert display.address == 0x3D
    assert display.interval == 30


def test_oled_display_read():
    """Test that reading from the display returns a success value."""
    display = OLEDDisplay("test_display", scl_pin=22, sda_pin=21)
    reading = display.read()
    assert reading == 1.0


def test_oled_display_metadata():
    """Test that metadata includes the display parameters."""
    display = OLEDDisplay("test_display", scl_pin=22, sda_pin=21)
    metadata = display.get_metadata()
    assert metadata["name"] == "test_display"
    assert metadata["pin"] == 21
    assert metadata["scl_pin"] == 22
    assert metadata["sda_pin"] == 21
    assert metadata["width"] == 128
    assert metadata["height"] == 64
    assert metadata["address"] == 0x3C
    assert metadata["interval"] == 60
    assert metadata["type"] == "SSD1306"
    assert metadata["values_count"] == 0


def test_oled_display_values():
    """Test that display values are stored correctly."""
    display = OLEDDisplay("test_display", scl_pin=22, sda_pin=21)

    # Test with empty values
    assert display._values == []

    # Test with string values
    test_values = ["Temperature: 25.0°C", "Humidity: 45.0%"]
    display.display_values(test_values)
    assert display._values == test_values

    # Check that metadata reflects the number of values
    metadata = display.get_metadata()
    assert metadata["values_count"] == 2


def test_oled_display_clear():
    """Test that clearing the display works in simulation mode."""
    display = OLEDDisplay("test_display", scl_pin=22, sda_pin=21)

    # This is mostly a coverage test since we can't check the actual display in tests
    display.clear()

    # Verify that clearing doesn't affect stored values
    test_values = ["Temperature: 25.0°C"]
    display.display_values(test_values)
    display.clear()
    assert display._values == test_values


def test_oled_display_text():
    """Test that displaying text works in simulation mode."""
    display = OLEDDisplay("test_display", scl_pin=22, sda_pin=21)

    # This is mostly a coverage test since we can't check the actual display in tests
    display.display_text("Hello, World!")

    # Verify that displaying text doesn't affect stored values
    test_values = ["Temperature: 25.0°C"]
    display.display_values(test_values)
    display.display_text("Hello, World!")
    assert display._values == test_values
