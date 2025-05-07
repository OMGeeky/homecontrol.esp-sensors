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
        "temperature": {
            "name": "Living Room Temperature",
            "pin": 4,
            "interval": 60,
            "unit": "C"
        },
        "humidity": {
            "name": "Living Room Humidity",
            "pin": 4,
            "interval": 60
        },
        "dht22": {
            "name": "Living Room DHT22",
            "pin": 4,
            "interval": 30,
            "unit": "C"
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

You can create sensors using the configuration system in two ways:

#### Method 1: Using sensor_type parameter

```python
from src.esp_sensors.temperature import TemperatureSensor

# Create a temperature sensor using configuration
sensor = TemperatureSensor(sensor_type="temperature")
```

#### Method 2: Overriding some parameters

```python
from src.esp_sensors.temperature import TemperatureSensor

# Create a temperature sensor with custom name but other parameters from config
sensor = TemperatureSensor(
    name="Custom Sensor",
    sensor_type="temperature"
)
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

## Saving Configuration

You can save a configuration to a file using the `save_config` function:

```python
from src.esp_sensors.config import save_config

# Save configuration to the default path (config.json)
save_config(config)

# Or specify a custom path
save_config(config, "custom_config.json")
```

## Creating Default Configuration

To create a default configuration file:

```python
from src.esp_sensors.config import create_default_config

# Create a default configuration file at the default path (config.json)
create_default_config()

# Or specify a custom path
create_default_config("custom_config.json")
```

## Configuration Parameters

### Common Parameters

- `name`: The name of the sensor or display
- `pin`: The GPIO pin number the sensor is connected to
- `interval`: Reading interval in seconds

### Temperature Sensor Parameters

- `unit`: Temperature unit, either "C" for Celsius or "F" for Fahrenheit

### OLED Display Parameters

- `scl_pin`: The GPIO pin number for the SCL (clock) line
- `sda_pin`: The GPIO pin number for the SDA (data) line
- `width`: Display width in pixels
- `height`: Display height in pixels
- `address`: I2C address of the display (in hex format, e.g., "0x3C")

### Button Parameters

- `pin`: The GPIO pin number the button is connected to
- `pull_up`: Whether to use internal pull-up resistor (true/false)