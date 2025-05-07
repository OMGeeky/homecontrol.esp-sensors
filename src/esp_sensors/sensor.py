"""
Base sensor module for ESP-based sensors.
"""
from typing import Dict, Any, Optional


class Sensor:
    """Base class for all sensors."""

    def __init__(self, name: str, pin: int, interval: int = 60):
        """
        Initialize a new sensor.

        Args:
            name: The name of the sensor
            pin: The GPIO pin number the sensor is connected to
            interval: Reading interval in seconds (default: 60)
        """
        self.name = name
        self.pin = pin
        self.interval = interval
        self._last_reading: Optional[float] = None

    def read(self) -> float:
        """
        Read the current sensor value.

        Returns:
            The sensor reading as a float
        """
        # This is a placeholder that would be overridden by subclasses
        # In a real implementation, this would interact with the hardware
        self._last_reading = 0.0
        return self._last_reading

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get sensor metadata.

        Returns:
            A dictionary containing sensor metadata
        """
        return {
            "name": self.name,
            "pin": self.pin,
            "interval": self.interval,
            "last_reading": self._last_reading,
        }
