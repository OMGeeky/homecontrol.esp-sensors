"""
OLED display module for ESP32 using SSD1306 controller.
"""

import time
from typing import Dict, Any, Optional

try:
    from machine import Pin, I2C
    import ssd1306

    SIMULATION = False
except ImportError:
    SIMULATION = True

from .sensor import Sensor
from .config import get_display_config


class OLEDDisplay(Sensor):
    """SSD1306 OLED display implementation."""

    def __init__(
        self,
        name: str = None,
        scl_pin: int = None,
        sda_pin: int = None,
        width: int = None,
        height: int = None,
        address: int | str = None,
        interval: int = None,
        on_time: int = None,
        display_config: Dict[str, Any] = None,
    ):
        """
        Initialize a new OLED display.

        Args:
            name: The name of the display (if None, loaded from config)
            scl_pin: The GPIO pin number for the SCL (clock) line (if None, loaded from config)
            sda_pin: The GPIO pin number for the SDA (data) line (if None, loaded from config)
            width: Display width in pixels (if None, loaded from config)
            height: Display height in pixels (if None, loaded from config)
            address: I2C address of the display (if None, loaded from config)
            interval: Refresh interval in seconds (if None, loaded from config)
            on_time: The time, the display should stay on (if None, loaded from config)
            display_config: Configuration dictionary
        """

        if display_config is None:
            display_config = {}

        # Get parameters from config if not provided
        name = name if name is not None else display_config.get("name", "OLED Display")
        sda_pin = sda_pin if sda_pin is not None else display_config.get("sda_pin", 21)
        interval = (
            interval if interval is not None else display_config.get("interval", 60)
        )

        # Initialize base class with the pin parameter
        super().__init__(name=name, pin=sda_pin, interval=interval)

        # Set display-specific parameters
        self.scl_pin = (
            scl_pin if scl_pin is not None else display_config.get("scl_pin", 22)
        )
        self.sda_pin = sda_pin  # Already set above
        self.width = width if width is not None else display_config.get("width", 128)
        self.height = height if height is not None else display_config.get("height", 64)
        self.on_time = (
            on_time if on_time is not None else display_config.get("on_time", 5)
        )

        # Handle address (could be string in config)
        if address is None:
            address = display_config.get("address", "0x3C")

        # Convert address to int if it's a hex string
        if isinstance(address, str) and address.startswith("0x"):
            self.address = int(address, 16)
        else:
            self.address = address

        self._values = []

        # Initialize the display if not in simulation mode
        if not SIMULATION:
            try:
                i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))
                self._display = ssd1306.SSD1306_I2C(width, height, i2c, addr=address)
                self._display.fill(0)  # Clear the display
                self._display.text("Initialized", 0, 0, 1)
                self._display.show()
            except Exception as e:
                print(f"Error initializing OLED display: {e}")
                self._display = None
        else:
            # In simulation mode, just print to console
            print(f"Simulated OLED display initialized: {width}x{height}")
            self._display = None

    def clear(self):
        """
        Clear the display.
        """
        if SIMULATION:
            print("Simulated OLED display cleared")
        else:
            if self._display:
                self._display.fill(0)
                self._display.show()

    def display_text(self, text: str, x: int = 0, y: int = 0, color: int = 1):
        """
        Display text at the specified position.

        Args:
            text: The text to display
            x: X coordinate (default: 0)
            y: Y coordinate (default: 0)
            color: Pixel color (1 for white, 0 for black, default: 1)
        """
        if SIMULATION:
            print(f"Simulated OLED display text at ({x}, {y}): {text}")
        else:
            if self._display:
                self._display.text(text, x, y, color)
                self._display.show()

    def display_values(self, values: list):
        """
        Display a list of values on the OLED screen.

        Args:
            values: List of values to display (strings or objects with __str__ method)
        """
        self._values = values

        if SIMULATION:
            print("Simulated OLED display values:")
            for i, value in enumerate(values):
                print(f"  Line {i}: {value}")
        else:
            if self._display:
                self._display.fill(0)  # Clear the display

                # Display each value on a new line (8 pixels per line)
                for i, value in enumerate(values):
                    if i * 10 < self.height:  # Make sure we don't go off the screen
                        self._display.text(str(value), 0, i * 10, 1)

                self._display.show()

    def read(self) -> float:
        """
        Update the display (placeholder to satisfy Sensor interface).

        Returns:
            Always returns 1.0 to indicate success
        """
        # This method is required by the Sensor interface but doesn't make sense for a display
        # We'll just return a constant value
        return 1.0

    def get_metadata(self):
        """
        Get display metadata.

        Returns:
            A dictionary containing display metadata
        """
        metadata = super().get_metadata()
        metadata["scl_pin"] = self.scl_pin
        metadata["sda_pin"] = self.sda_pin
        metadata["width"] = self.width
        metadata["height"] = self.height
        metadata["address"] = self.address
        metadata["type"] = "SSD1306"
        metadata["values_count"] = len(self._values)
        return metadata
