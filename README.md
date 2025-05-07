# ESP Sensors

A Python library for interfacing with various sensors on ESP32/ESP8266 microcontrollers using MicroPython.

## Overview

This library provides a simple and consistent interface for working with different types of sensors connected to ESP32/ESP8266 microcontrollers. It includes both real hardware implementations and simulation capabilities for testing without physical hardware.

## Features

- Base sensor class with common functionality
- Temperature sensor implementation
- DHT22 temperature and humidity sensor implementation
- Simulation mode for testing without hardware
- Comprehensive test suite
- Example scripts for each sensor type

## Installation

1. Install MicroPython on your ESP32/ESP8266 device
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/esp-sensors.git
   cd esp-sensors
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Temperature Sensor

```python
from src.esp_sensors.temperature import TemperatureSensor

# Initialize a temperature sensor on GPIO pin 5
sensor = TemperatureSensor("room_temp", 5, unit="C")

# Read temperature
temp = sensor.read()
print(f"Temperature: {temp}°C")

# Convert to Fahrenheit
temp_f = sensor.to_fahrenheit()
print(f"Temperature: {temp_f}°F")
```

### DHT22 Sensor

```python
from src.esp_sensors.dht22 import DHT22Sensor

# Initialize a DHT22 sensor on GPIO pin 4
sensor = DHT22Sensor("living_room", 4)

# Read temperature
temp = sensor.read()
print(f"Temperature: {temp}°C")

# Read humidity
humidity = sensor.read_humidity()
print(f"Humidity: {humidity}%")
```

## Available Sensors

| Sensor | Description | Features |
|--------|-------------|----------|
| Temperature | Basic temperature sensor | Temperature in C/F |
| DHT22 | Digital temperature and humidity sensor | Temperature in C/F, Humidity % |

## Examples

Example scripts are provided in the `examples/` directory:

- `examples/dht22_example.py`: Demonstrates how to use the DHT22 sensor

## Documentation

Detailed documentation for each sensor is available in the `docs/` directory:

- [DHT22 Sensor Documentation](docs/dht22_sensor.md)

## Development

### Setup Development Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running Tests

```bash
python -m pytest
```

### Code Style

This project uses Black for code formatting:

```bash
black .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.