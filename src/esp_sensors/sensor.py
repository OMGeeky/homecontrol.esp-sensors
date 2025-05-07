"""
Base sensor module for ESP-based sensors.
"""
from typing import Dict, Any, Optional
from .config import get_sensor_config


class Sensor:
    """Base class for all sensors."""

    def __init__(self, name: str = None, pin: int = None, interval: int = None, 
                 sensor_type: str = None, config: Dict[str, Any] = None):
        """
        Initialize a new sensor.

        Args:
            name: The name of the sensor (if None, loaded from config)
            pin: The GPIO pin number the sensor is connected to (if None, loaded from config)
            interval: Reading interval in seconds (if None, loaded from config)
            sensor_type: Type of the sensor for loading config (e.g., 'temperature')
            config: Configuration dictionary (if provided, used instead of loading from file)
        """
        # Load configuration if sensor_type is provided
        if sensor_type:
            sensor_config = get_sensor_config(sensor_type, config)

            # Use provided values or fall back to config values
            self.name = name if name is not None else sensor_config.get('name', 'Unnamed Sensor')
            self.pin = pin if pin is not None else sensor_config.get('pin', 0)
            self.interval = interval if interval is not None else sensor_config.get('interval', 60)
        else:
            # Use provided values or defaults
            self.name = name if name is not None else 'Unnamed Sensor'
            self.pin = pin if pin is not None else 0
            self.interval = interval if interval is not None else 60

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
