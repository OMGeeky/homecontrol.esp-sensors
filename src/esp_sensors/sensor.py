"""
Base sensor module for ESP-based sensors.
"""


class Sensor:
    """Base class for all sensors."""

    def __init__(
        self,
        name: str = None,
        pin: int = None,
        interval: int = None,
        sensor_config=None,
    ):
        """
        Initialize a new sensor.

        Args:
            name: The name of the sensor (if None, loaded from config)
            pin: The GPIO pin number the sensor is connected to (if None, loaded from config)
            interval: Reading interval in seconds (if None, loaded from config)
            sensor_config: Sensor-Configuration dictionary (if provided, used instead of loading from file)
        """

        if sensor_config is None:
            sensor_config = {}

        self.name = (
            name if name is not None else sensor_config.get("name", "Unnamed Sensor")
        )
        self.id = sensor_config.get(
            "id", "sensor_" + self.name.lower().replace(" ", "_")
        )
        self.pin = pin if pin is not None else sensor_config.get("pin", 0)
        self.interval = (
            interval if interval is not None else sensor_config.get("interval", 60)
        )

        self._last_reading = None

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

    def get_metadata(self):
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
