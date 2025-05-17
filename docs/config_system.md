# Configuration System

This document explains how to use the configuration system in the ESP Sensors project.

## Overview

The configuration system allows you to change parameters like pins, display resolution, sensor names, and intervals without modifying the code. This makes it easy to adapt the project to different hardware setups and requirements.

## Configuration File

The configuration is stored in a JSON file named `config.json` in the project root directory. If this file doesn't exist, default values will be used.

### Example Configuration

```json
{
    "sensors": {
        "dht22": {
            "name": "Living Room DHT22",
            "pin": 4,
            "interval": 30,
            "temperature": {
                "name": "Living Room Temperature",
                "unit": "C"
            },
            "humidity": {
                "name": "Living Room Humidity"
            }
        }
    },
    "displays": {
        "oled": {
            "name": "Status Display",
            "scl_pin": 22,
            "sda_pin": 21,
            "width": 128,
            "height": 64,
            "address": "0x3C",
            "interval": 1
        }
    },
    "buttons": {
        "main_button": {
            "pin": 0,
            "pull_up": true
        }
    }
}
```

## Using the Configuration System

### Loading Configuration

You can load the configuration using the `load_config` function:

```python
from src.esp_sensors.config import load_config

# Load configuration from the default path (config.json)
config = load_config()

# Or specify a custom path
config = load_config("custom_config.json")
```

### Getting Sensor Configuration

To get configuration for a specific sensor type:

```python
from src.esp_sensors.config import get_sensor_config

# Get configuration for a temperature sensor
temp_config = get_sensor_config("temperature")

# Or with a custom configuration
temp_config = get_sensor_config("temperature", config)
```

### Getting Display Configuration

To get configuration for a specific display type:

```python
from src.esp_sensors.config import get_display_config

# Get configuration for an OLED display
oled_config = get_display_config("oled")

# Or with a custom configuration
oled_config = get_display_config("oled", config)
```

### Creating Sensors with Configuration

You can create sensors using the configuration system in three ways:

#### Method 1: Using sensor_config directly

```python
from src.esp_sensors.temperature import TemperatureSensor

# Get configuration
from src.esp_sensors.config import get_sensor_config
temp_config = get_sensor_config("temperature")

# Create a temperature sensor with the configuration
sensor = TemperatureSensor(sensor_config=temp_config)
```

#### Method 2: Overriding parameters directly

```python
from src.esp_sensors.temperature import TemperatureSensor

# Create a temperature sensor with direct parameters
sensor = TemperatureSensor(
    name="Custom Sensor",
    pin=5,
    interval=30,
    unit="F"
)
```

You can also combine this with a configuration dictionary:

```python
from src.esp_sensors.temperature import TemperatureSensor
from src.esp_sensors.config import get_sensor_config

# Get configuration
temp_config = get_sensor_config("temperature")

# Create a sensor with some parameters from config, others specified directly
sensor = TemperatureSensor(
    name="Custom Sensor",  # Override the name from config
    unit="F",              # Override the unit from config
    sensor_config=temp_config  # Use other parameters from config
)
```

#### Method 3: Creating a custom configuration dictionary

```python
from src.esp_sensors.temperature import TemperatureSensor

# Create a custom configuration dictionary
custom_config = {
    "name": "Custom Temperature",
    "pin": 5,
    "interval": 30,
    "unit": "F"
}

# Create a temperature sensor with the custom configuration
sensor = TemperatureSensor(sensor_config=custom_config)
```

### Creating Displays with Configuration

Similarly, you can create displays using the configuration system:

```python
from src.esp_sensors.oled_display import OLEDDisplay

# Create an OLED display using configuration
display = OLEDDisplay()

# Or override some parameters
display = OLEDDisplay(
    name="Custom Display",
    width=64,
    height=32
)
```

You can also use the display_config parameter directly:

```python
from src.esp_sensors.oled_display import OLEDDisplay
from src.esp_sensors.config import get_display_config

# Get display configuration
oled_config = get_display_config("oled")

# Create an OLED display with the configuration
display = OLEDDisplay(display_config=oled_config)

# Or create a custom configuration dictionary
custom_display_config = {
    "name": "Custom OLED",
    "scl_pin": 22,
    "sda_pin": 21,
    "width": 128,
    "height": 32,
    "address": "0x3C",
    "interval": 30
}

# Create an OLED display with the custom configuration
display = OLEDDisplay(display_config=custom_display_config)
```

## Configuration Parameters

### Common Parameters

- `name`: The name of the sensor or display
- `pin`: The GPIO pin number the sensor is connected to
- `interval`: Reading interval in seconds

### Temperature Sensor Parameters

- `unit`: Temperature unit, either "C" for Celsius or "F" for Fahrenheit

### Humidity Sensor Parameters

No additional parameters beyond the common ones.

### DHT22 Sensor Parameters

- `temperature`: A nested configuration object for temperature-specific settings
  - `name`: The name for the temperature component
  - `unit`: Temperature unit, either "C" for Celsius or "F" for Fahrenheit
- `humidity`: A nested configuration object for humidity-specific settings
  - `name`: The name for the humidity component

### OLED Display Parameters

- `scl_pin`: The GPIO pin number for the SCL (clock) line
- `sda_pin`: The GPIO pin number for the SDA (data) line
- `width`: Display width in pixels
- `height`: Display height in pixels
- `address`: I2C address of the display (in hex format, e.g., "0x3C" or as an integer)

### Button Parameters

- `pin`: The GPIO pin number the button is connected to
- `pull_up`: Whether to use internal pull-up resistor (true/false)
