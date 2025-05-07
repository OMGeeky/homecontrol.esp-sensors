"""
DHT22 temperature and humidity sensor module for ESP32.
"""
import time
try:
    import dht
    from machine import Pin
    SIMULATION = False
except ImportError:
    import random
    SIMULATION = True

from .sensor import Sensor


class DHT22Sensor(Sensor):
    """DHT22 temperature and humidity sensor implementation."""

    def __init__(self, name: str, pin: int, interval: int = 60, unit: str = "C"):
        """
        Initialize a new DHT22 sensor.

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
        self._last_humidity = None

        # Initialize the sensor if not in simulation mode
        if not SIMULATION:
            self._sensor = dht.DHT22(Pin(pin))

    def read(self) -> float:
        """
        Read the current temperature.

        Returns:
            The temperature reading as a float
        """
        if SIMULATION:
            # Simulate temperature reading
            if self.unit == "C":
                self._last_reading = round(random.uniform(15.0, 30.0), 1)
            else:
                self._last_reading = round(random.uniform(59.0, 86.0), 1)

            # Simulate humidity reading (between 30% and 90%)
            self._last_humidity = round(random.uniform(30.0, 90.0), 1)
        else:
            # Actual hardware reading
            try:
                self._sensor.measure()
                temp = self._sensor.temperature()

                # Convert to Fahrenheit if needed
                if self.unit == "F":
                    temp = (temp * 9 / 5) + 32

                self._last_reading = round(temp, 1)
                self._last_humidity = round(self._sensor.humidity(), 1)
            except Exception as e:
                print(f"Error reading DHT22 sensor: {e}")
                # Return last reading if available, otherwise default value
                if self._last_reading is None:
                    self._last_reading = 0.0
                if self._last_humidity is None:
                    self._last_humidity = 0.0

        return self._last_reading

    def read_humidity(self) -> float:
        """
        Read the current humidity.

        Returns:
            The humidity reading as a float (percentage)
        """
        # If we haven't read yet, read only humidity
        if self._last_humidity is None:
            if SIMULATION:
                # Simulate humidity reading (between 30% and 90%)
                self._last_humidity = round(random.uniform(30.0, 90.0), 1)
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
        metadata = super().get_metadata()
        metadata["unit"] = self.unit
        metadata["last_humidity"] = self._last_humidity
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
