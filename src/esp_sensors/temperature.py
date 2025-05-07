"""
Temperature sensor module for ESP-based sensors.
"""
import random
from .sensor import Sensor


class TemperatureSensor(Sensor):
    """Temperature sensor implementation."""

    def __init__(self, name: str, pin: int, interval: int = 60, unit: str = "C"):
        """
        Initialize a new temperature sensor.

        Args:
            name: The name of the sensor
            pin: The GPIO pin number the sensor is connected to
            interval: Reading interval in seconds (default: 60)
            unit: Temperature unit, either "C" for Celsius or "F" for Fahrenheit (default: "C")
        """
        super().__init__(name, pin, interval)
        if unit not in ["C", "F"]:
            raise ValueError("Unit must be either 'C' or 'F'")
        self.unit = unit

    def read(self) -> float:
        """
        Read the current temperature.

        Returns:
            The temperature reading as a float
        """
        # This is a simulation for testing purposes
        # In a real implementation, this would read from the actual sensor
        if self.unit == "C":
            self._last_reading = round(random.uniform(15.0, 30.0), 1)
        else:
            self._last_reading = round(random.uniform(59.0, 86.0), 1)
        return self._last_reading

    def get_metadata(self):
        """
        Get sensor metadata including temperature unit.

        Returns:
            A dictionary containing sensor metadata
        """
        metadata = super().get_metadata()
        metadata["unit"] = self.unit
        return metadata

    def to_fahrenheit(self) -> float | None:
        """
        Convert the last reading to Fahrenheit if it was in Celsius.

        Returns:
            The temperature in Fahrenheit
        """
        if self.unit == "F" or self._last_reading is None:
            return self._last_reading
        return (self._last_reading * 9 / 5) + 32

    def to_celsius(self) -> float | None:
        """
        Convert the last reading to Celsius if it was in Fahrenheit.

        Returns:
            The temperature in Celsius
        """
        if self.unit == "C" or self._last_reading is None:
            return self._last_reading
        return (self._last_reading - 32) * 5 / 9
