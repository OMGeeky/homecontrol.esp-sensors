"""
OLED display module for ESP32 using SSD1306 controller.
"""
import time
try:
    from machine import Pin, I2C
    import ssd1306
    SIMULATION = False
except ImportError:
    SIMULATION = True

from .sensor import Sensor


class OLEDDisplay(Sensor):
    """SSD1306 OLED display implementation."""

    def __init__(self, name: str, scl_pin: int, sda_pin: int, width: int = 128, height: int = 64, 
                 address: int = 0x3C, interval: int = 60):
        """
        Initialize a new OLED display.

        Args:
            name: The name of the display
            scl_pin: The GPIO pin number for the SCL (clock) line
            sda_pin: The GPIO pin number for the SDA (data) line
            width: Display width in pixels (default: 128)
            height: Display height in pixels (default: 64)
            address: I2C address of the display (default: 0x3C)
            interval: Refresh interval in seconds (default: 60)
        """
        # Use sda_pin as the pin parameter for the Sensor base class
        super().__init__(name, sda_pin, interval)
        
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.width = width
        self.height = height
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