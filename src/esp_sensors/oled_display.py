"""
OLED display module for ESP32 using SSD1306 controller.
"""

LINE_HEIGHT = 8  # Height of each line in pixels

HEADER_LINE = 0
STATUS_LINE = 1
VALUE_LINES_START = 2

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
        display_config=None,
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
                print("Initializing OLED display...")
                print(f"  SCL pin: {self.scl_pin}, SDA pin: {self.sda_pin}")
                # print('initializing scl pin', type(self.scl_pin), self.scl_pin)
                scl = Pin(self.scl_pin)
                # print('initializing sda pin', type(self.sda_pin), self.sda_pin)
                sda = Pin(self.sda_pin)
                # print('initializing i2c')
                i2c = I2C(scl=scl, sda=sda)
                print(f"  I2C bus: {i2c}")
                # print('i2c scan:', i2c.scan())
                print(f"  I2C address: {self.address}")
                self._display = ssd1306.SSD1306_I2C(
                    self.width, self.height, i2c, addr=self.address
                )
                print(f"  Display initialized: {self._display}")
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

    # region basic display methods
    def power_off(self):
        """
        Turn off the display to save power.
        """
        if SIMULATION:
            print("Simulated OLED display powered off")
        else:
            if self._display:
                self._display.poweroff()

    def power_on(self):
        """
        Turn on the display.
        """
        if SIMULATION:
            print("Simulated OLED display powered on")
        else:
            if self._display:
                self._display.poweron()

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

    def set_line_text(self, i, value):
        if SIMULATION:
            print(f"Simulated OLED display line {i}: {value}")
        else:
            if self._display:
                y = i * LINE_HEIGHT
                if y < self.height:  # Make sure we don't go off the screen
                    x = 0
                    self._display.fill_rect(
                        x, y, self.width, LINE_HEIGHT, 0
                    )  # Clear the line
                    self._display.text(str(value), x, y, 1)
                else:
                    print(f"Line {i} exceeds display height, skipping")

    # endregion

    # region easy setter methods

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
                # self._display.fill(0)  # Clear the display
                x = 0
                y = VALUE_LINES_START * LINE_HEIGHT
                self._display.fill_rect(
                    x, y, self.width, self.height - y, 0
                )  # Clear the line
                # Display each value on a new line (8 pixels per line)
                for i, value in enumerate(values):
                    self.set_line_text(VALUE_LINES_START + i, value)

                self._display.show()

    def set_header(self, value):
        """
        Display a header on the OLED screen.

        Args:
            value: The header to display
        """
        self.set_line_text(HEADER_LINE, value)

    def set_status(self, status: str):
        """
        Display a status message on the OLED screen.

        Args:
            status: The status message to display
        """
        self.set_line_text(STATUS_LINE, status)
        if self._display:
            self._display.show()

    # endregion

    # region Sensor interface methods
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

    # endregion
