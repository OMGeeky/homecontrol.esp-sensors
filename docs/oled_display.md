# OLED Display Module

This module provides a class for interfacing with SSD1306 OLED displays via I2C on ESP32/ESP8266 microcontrollers.

## Features

- Compatible with SSD1306 OLED displays
- I2C interface support
- Display text at specific coordinates
- Display a list of values (e.g., sensor readings)
- Simulation mode for testing without hardware
- Integration with the ESP Sensors framework
- Configuration-based initialization
- Inherits from the Sensor class for consistent API
- Support for both integer and hex string I2C addresses

## Hardware Requirements

- ESP32 or ESP8266 microcontroller
- SSD1306 OLED display (common sizes: 128x64, 128x32, 64x48)
- I2C connection (2 pins: SCL and SDA)

## Installation

The OLED display module is part of the ESP Sensors package. No additional installation is required if you have already installed the package.

## Usage

### Basic Initialization

```python
from esp_sensors.oled_display import OLEDDisplay

# Initialize the display
display = OLEDDisplay(
    name="Status Display",
    scl_pin=22,  # GPIO pin for I2C clock
    sda_pin=21,  # GPIO pin for I2C data
    width=128,   # Display width in pixels
    height=64,   # Display height in pixels
    address=0x3C # I2C address (default: 0x3C)
)
```

### Configuration-Based Initialization

```python
from esp_sensors.oled_display import OLEDDisplay

# Initialize using configuration
display_config = {
    "name": "Status Display",
    "scl_pin": 22,
    "sda_pin": 21,
    "width": 128,
    "height": 64,
    "address": "0x3C",  # Can be a hex string
    "interval": 30
}

display = OLEDDisplay(display_config=display_config)
```

### Displaying Text

```python
# Clear the display
display.clear()

# Display text at specific coordinates
display.display_text("Hello, World!", x=0, y=0)
display.display_text("Line 2", x=0, y=10)
display.display_text("ESP32", x=64, y=30)
```

### Displaying Multiple Values

```python
# Display a list of values (e.g., sensor readings)
display.display_values([
    "Temperature: 25.5°C",
    "Humidity: 45%",
    "Pressure: 1013 hPa",
    "Time: 12:34:56"
])
```

### Integration with Sensors

```python
from esp_sensors.dht22 import DHT22Sensor

# Initialize a DHT22 sensor
sensor = DHT22Sensor("Living Room", pin=4)

# Read sensor values
temperature = sensor.read_temperature()
humidity = sensor.read_humidity()

# Display sensor values
display.display_values([
    f"Temp: {temperature:.1f}°C",
    f"Humidity: {humidity:.1f}%"
])
```

## API Reference

### Class: OLEDDisplay

Extends the base `Sensor` class to provide OLED display functionality.

#### Constructor

```python
OLEDDisplay(
    name: str = None,
    scl_pin: int = None,
    sda_pin: int = None,
    width: int = None,
    height: int = None,
    address: int | str = None,
    interval: int = None,
    display_config: Dict[str, Any] = None
)
```

Parameters:
- `name` (str): The name of the display (if None, loaded from config)
- `scl_pin` (int): The GPIO pin number for the SCL (clock) line (if None, loaded from config)
- `sda_pin` (int): The GPIO pin number for the SDA (data) line (if None, loaded from config)
- `width` (int): Display width in pixels (if None, loaded from config)
- `height` (int): Display height in pixels (if None, loaded from config)
- `address` (int | str): I2C address of the display, can be an integer or a hex string (if None, loaded from config)
- `interval` (int): Refresh interval in seconds (if None, loaded from config)
- `display_config` (Dict[str, Any]): Configuration dictionary (if provided, used instead of loading from file)

#### Methods

##### clear()

Clears the display.

```python
display.clear()
```

##### display_text(text, x=0, y=0, color=1)

Displays text at the specified position.

Parameters:
- `text` (str): The text to display
- `x` (int): X coordinate (default: 0)
- `y` (int): Y coordinate (default: 0)
- `color` (int): Pixel color (1 for white, 0 for black, default: 1)

```python
display.display_text("Hello", x=10, y=20)
```

##### display_values(values)

Displays a list of values on the OLED screen.

Parameters:
- `values` (list): List of values to display (strings or objects with __str__ method)

```python
display.display_values(["Line 1", "Line 2", "Line 3"])
```

##### read()

Updates the display (placeholder to satisfy Sensor interface).

```python
display.read()  # Always returns 1.0 to indicate success
```

##### get_metadata()

Returns a dictionary containing display metadata.

```python
metadata = display.get_metadata()
print(metadata)
```

The metadata includes:
- `name`: The name of the display
- `pin`: The SDA pin number (inherited from Sensor)
- `interval`: Refresh interval in seconds
- `scl_pin`: The SCL pin number
- `sda_pin`: The SDA pin number
- `width`: Display width in pixels
- `height`: Display height in pixels
- `address`: I2C address of the display
- `type`: Always "SSD1306"
- `values_count`: Number of values currently displayed

## Troubleshooting

### Display Not Working

1. Check the I2C address (common addresses are 0x3C and 0x3D)
2. Verify the SCL and SDA pin connections
3. Ensure the display is powered correctly (usually 3.3V)
4. Try a different I2C bus speed if available

### Text Not Displaying Correctly

1. Check that the coordinates are within the display dimensions
2. Ensure the text doesn't exceed the display width
3. Try using smaller font or breaking text into multiple lines

## Example

See the `examples/oled_display_example.py` file for a complete example of using the OLED display with sensors.
