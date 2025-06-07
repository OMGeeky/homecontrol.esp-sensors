"""
Humidity sensor module for ESP-based sensors.
"""

from .dummy_sensor import read_dummy  # Dummy sensor for simulation purposes
from .sensor import Sensor
from .config import get_sensor_config


class HumiditySensor(Sensor):
    """Humidity sensor implementation."""

    def __init__(
        self,
        name: str = None,
        pin: int = None,
        interval: int = None,
        sensor_config: dict | None = None,
        **kwargs,
    ):
        """
        Initialize a new humidity sensor.

        Args:
            name: The name of the sensor (if None, loaded from config)
            pin: The GPIO pin number the sensor is connected to (if None, loaded from config)
            interval: Reading interval in seconds (if None, loaded from config)
            sensor_config: Sensor-Configuration dictionary (if provided, used instead of loading from file)
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        if sensor_config is None:
            sensor_config = {}
        # Initialize base class with sensor_config for configuration
        super().__init__(name, pin, interval, sensor_config=sensor_config)
        self._last_humidity = None

    def read_humidity(self) -> float:
        """
        Read the current humidity.

        Returns:
            The humidity reading as a float (percentage)
        """
        self._last_humidity = read_dummy("humidity", unit="%")
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
