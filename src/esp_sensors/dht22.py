"""
DHT22 temperature and humidity sensor module for ESP32.
"""

import time
from typing import Dict, Any, Optional

try:
    import dht
    from machine import Pin

    SIMULATION = False
except ImportError:
    import random

    SIMULATION = True

from .temperature import TemperatureSensor
from .humidity import HumiditySensor
from .config import get_sensor_config


class DHT22Sensor(TemperatureSensor, HumiditySensor):
    """DHT22 temperature and humidity sensor implementation."""

    def __init__(
        self,
        name: str = None,
        pin: int = None,
        interval: int = None,
        temperature_unit: str = None,
        sensor_config: Dict[str, Any] = None,
    ):
        """
        Initialize a new DHT22 sensor.

        Args:
            name: The name of the sensor (if None, loaded from config)
            pin: The GPIO pin number the sensor is connected to (if None, loaded from config)
            interval: Reading interval in seconds (if None, loaded from config)
            temperature_unit: Temperature unit, either "C" or "F" (if None, loaded from config)
            sensor_config: Sensor-Configuration dictionary (if provided, used instead of loading from file)
        """
        if sensor_config is None:
            sensor_config = {}

        self.apply_parameters(interval, name, pin, sensor_config)

        # Get sensor configurations
        temp_config = sensor_config.get("temperature", {})
        humidity_config = sensor_config.get("humidity", {})

        # Initialize both parent classes
        TemperatureSensor.__init__(
            self,
            pin=self.pin,
            interval=self.interval,
            sensor_config=temp_config,
            unit=temperature_unit,
        )
        HumiditySensor.__init__(
            self, sensor_config=humidity_config, pin=self.pin, interval=self.interval
        )

        # Re-apply parameters to ensure they are not overridden by parent classes
        self.apply_parameters(interval, name, pin, sensor_config)

        # Initialize the sensor if not in simulation mode
        if not SIMULATION:
            self._sensor = dht.DHT22(Pin(pin))

    def apply_parameters(self, interval, name, pin, sensor_config):
        # Get main parameters from config if not provided
        self.name = (
            name if name is not None else sensor_config.get("name", "DHT22 Sensor")
        )
        self.pin = pin if pin is not None else sensor_config.get("pin", 0)
        self.interval = (
            interval if interval is not None else sensor_config.get("interval", 60)
        )

    def read_temperature(self) -> float:
        """
        Read the current temperature.

        Returns:
            The temperature reading as a float
        """
        if SIMULATION:
            # Use parent class simulation for temperature
            temp_reading = super().read_temperature()
            # Also update humidity in simulation mode
            self._last_humidity = super().read_humidity()
            return temp_reading
        else:
            # Actual hardware reading
            try:
                self._sensor.measure()
                temp = self._sensor.temperature()

                # Convert to Fahrenheit if needed
                if self.unit == "F":
                    temp = (temp * 9 / 5) + 32

                self._last_reading = round(temp, 1)
                # Also read humidity while we're at it
                self._last_humidity = round(self._sensor.humidity(), 1)
            except Exception as e:
                print(f"Error reading DHT22 sensor: {e}")
                # Return last reading if available, otherwise default value
                if self._last_reading is None:
                    self._last_reading = 0.0
                if self._last_humidity is None:
                    self._last_humidity = 0.0

        return self._last_reading

    def read(self) -> float:
        """
        Read the current temperature (wrapper for read_temperature).

        Returns:
            The temperature reading as a float
        """
        return self.read_temperature()

    def read_humidity(self) -> float:
        """
        Read the current humidity.

        Returns:
            The humidity reading as a float (percentage)
        """
        # If we haven't read yet, read only humidity
        if self._last_humidity is None:
            if SIMULATION:
                # Use parent class simulation
                return super().read_humidity()
            else:
                # Actual hardware reading
                try:
                    self._sensor.measure()
                    self._last_humidity = round(self._sensor.humidity(), 1)
                except Exception as e:
                    print(f"Error reading DHT22 humidity: {e}")
                    # Return default value if no previous reading
                    self._last_humidity = 0.0
        return self._last_humidity

    def get_metadata(self):
        """
        Get sensor metadata including temperature unit and humidity.

        Returns:
            A dictionary containing sensor metadata
        """
        # Get metadata from TemperatureSensor
        temp_metadata = TemperatureSensor.get_metadata(self)
        # Get metadata from HumiditySensor
        humidity_metadata = HumiditySensor.get_metadata(self)

        # Combine metadata from both parent classes
        metadata = {**temp_metadata, **humidity_metadata}
        # Ensure the name is the main sensor name, not the humidity sensor name
        metadata["name"] = self.name
        metadata["type"] = "DHT22"
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
