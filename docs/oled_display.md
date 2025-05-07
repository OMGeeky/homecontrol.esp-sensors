# OLED Display Module

This module provides a class for interfacing with SSD1306 OLED displays via I2C on ESP32/ESP8266 microcontrollers.

## Features

- Compatible with SSD1306 OLED displays
- I2C interface support
- Display text at specific coordinates
- Display a list of values (e.g., sensor readings)
- Simulation mode for testing without hardware
- Integration with the ESP Sensors framework

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

#### Constructor

```python
OLEDDisplay(name, scl_pin, sda_pin, width=128, height=64, address=0x3C, interval=60)
```

Parameters:
- `name` (str): The name of the display
- `scl_pin` (int): The GPIO pin number for the SCL (clock) line
- `sda_pin` (int): The GPIO pin number for the SDA (data) line
- `width` (int): Display width in pixels (default: 128)
- `height` (int): Display height in pixels (default: 64)
- `address` (int): I2C address of the display (default: 0x3C)
- `interval` (int): Refresh interval in seconds (default: 60)

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

##### get_metadata()

Returns a dictionary containing display metadata.

```python
metadata = display.get_metadata()
print(metadata)
```

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