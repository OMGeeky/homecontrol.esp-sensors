"""
Humidity sensor module for ESP-based sensors.
"""
import random
from .sensor import Sensor


class HumiditySensor(Sensor):
    """Humidity sensor implementation."""

    def __init__(self, name: str, pin: int, interval: int = 60):
        """
        Initialize a new humidity sensor.

        Args:
            name: The name of the sensor
            pin: The GPIO pin number the sensor is connected to
            interval: Reading interval in seconds (default: 60)
        """
        super().__init__(name, pin, interval)
        self._last_humidity = None

    def read_humidity(self) -> float:
        """
        Read the current humidity.

        Returns:
            The humidity reading as a float (percentage)
        """
        # This is a simulation for testing purposes
        # In a real implementation, this would read from the actual sensor
        self._last_humidity = round(random.uniform(30.0, 90.0), 1)
        return self._last_humidity

    def get_metadata(self):
        """
        Get sensor metadata including humidity information.

        Returns:
            A dictionary containing sensor metadata
        """
        metadata = super().get_metadata()
        metadata["last_humidity"] = self._last_humidity
        return metadata