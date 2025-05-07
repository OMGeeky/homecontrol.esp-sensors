"""
Temperature sensor module for ESP-based sensors.
"""

import random
from typing import Dict, Any, Optional
from .sensor import Sensor
from .config import get_sensor_config


class TemperatureSensor(Sensor):
    """Temperature sensor implementation."""

    def __init__(
        self,
        name: str = None,
        pin: int = None,
        interval: int = None,
        unit: str = None,
        sensor_config: Dict[str, Any] = None,
    ):
        """
        Initialize a new temperature sensor.

        Args:
            name: The name of the sensor (if None, loaded from config)
            pin: The GPIO pin number the sensor is connected to (if None, loaded from config)
            interval: Reading interval in seconds (if None, loaded from config)
            unit: Temperature unit, either "C" or "F" (if None, loaded from config)
            sensor_config: Sensor-Configuration dictionary (if provided, used instead of loading from file)
        """
        if sensor_config is None:
            sensor_config = {}
        # Initialize base class with sensor_config for configuration
        super().__init__(name, pin, interval, sensor_config=sensor_config)

        # Load configuration if not provided in parameters
        if unit is None:
            unit = sensor_config.get("unit", "C")

        # Validate unit
        if unit not in ["C", "F"]:
            raise ValueError("Unit must be either 'C' or 'F'")

        self.unit = unit

    def read_temperature(self) -> float:
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

    def read(self) -> float:
        """
        Read the current temperature (wrapper for read_temperature).

        Returns:
            The temperature reading as a float
        """
        return self.read_temperature()

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
