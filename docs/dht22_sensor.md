# DHT22 Sensor Implementation for ESP32

This document provides information about the DHT22 sensor implementation for ESP32 microcontrollers in this project.

## Overview

The DHT22 (also known as AM2302) is a digital temperature and humidity sensor that provides high-precision temperature and humidity readings. This implementation allows you to easily integrate DHT22 sensors with your ESP32 projects using MicroPython.

## Features

- Temperature readings in Celsius or Fahrenheit
- Humidity readings as percentage
- Automatic detection of simulation vs. hardware mode
- Error handling for sensor reading failures
- Temperature unit conversion methods
- Comprehensive metadata including sensor type and last readings

## Hardware Requirements

- ESP32 microcontroller
- DHT22/AM2302 temperature and humidity sensor
- MicroPython firmware installed on the ESP32
- Appropriate wiring:
  - Connect VCC to 3.3V or 5V power supply
  - Connect GND to ground
  - Connect DATA to a GPIO pin (default is GPIO4)
  - A 10K pull-up resistor between VCC and DATA is recommended

## Software Dependencies

- MicroPython with `dht` and `machine` modules
- For simulation mode, only the standard Python libraries are required

## Usage

### Basic Usage

```python
from src.esp_sensors.dht22 import DHT22Sensor

# Initialize the sensor
sensor = DHT22Sensor("living_room", 4)  # name, GPIO pin

# Read temperature
temperature = sensor.read()
print(f"Temperature: {temperature}°C")

# Read humidity
humidity = sensor.read_humidity()
print(f"Humidity: {humidity}%")

# Get temperature in Fahrenheit
fahrenheit = sensor.to_fahrenheit()
print(f"Temperature: {fahrenheit}°F")
```

### Advanced Usage

```python
from src.esp_sensors.dht22 import DHT22Sensor
import time

# Initialize with custom parameters
sensor = DHT22Sensor(
  name="outdoor",
  pin=5,
  interval=30,  # Read every 30 seconds
  temperature_unit="F"  # Use Fahrenheit
)

# Continuous reading
try:
  while True:
    temp = sensor.read()
    humidity = sensor.read_humidity()

    # Get metadata
    metadata = sensor.get_metadata()

    print(f"Sensor: {metadata['name']}")
    print(f"Temperature: {temp}°F ({sensor.to_celsius()}°C)")
    print(f"Humidity: {humidity}%")

    time.sleep(metadata['interval'])
except KeyboardInterrupt:
  print("Monitoring stopped")
```

## API Reference

### Class: DHT22Sensor

Extends the base `Sensor` class to provide DHT22-specific functionality.

#### Constructor

```python
DHT22Sensor(name: str, pin: int, interval: int = 60, unit: str = "C")
```

- **name**: A string identifier for the sensor
- **pin**: The GPIO pin number the sensor is connected to
- **interval**: Reading interval in seconds (default: 60)
- **unit**: Temperature unit, either "C" for Celsius or "F" for Fahrenheit (default: "C")

#### Methods

- **read()**: Reads the current temperature and updates humidity
- **read_humidity()**: Returns the current humidity reading
- **to_fahrenheit()**: Converts the last reading to Fahrenheit if it was in Celsius
- **to_celsius()**: Converts the last reading to Celsius if it was in Fahrenheit
- **get_metadata()**: Returns a dictionary with sensor information including temperature unit and humidity

## Example

See the `examples/dht22_example.py` file for a complete example of how to use the DHT22 sensor with an ESP32.

## Troubleshooting

- **No readings or errors**: Check your wiring and ensure the DHT22 is properly connected
- **Inconsistent readings**: Make sure you have a pull-up resistor between VCC and DATA
- **ImportError**: Ensure you're running on MicroPython with the required modules
- **ValueError**: Check that you're using a valid temperature unit ("C" or "F")

## License

This implementation is provided under the same license as the main project.