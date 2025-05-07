# Button-Triggered Sensor Display

This document explains how to use the button-triggered sensor display example, which demonstrates an energy-efficient approach to reading and displaying sensor data on ESP32/ESP8266 devices.

## Overview

The button-triggered display example shows how to:

1. Set up a button input on an ESP device
2. Use low-power sleep mode to conserve energy
3. Wake up and read sensor data when the button is pressed
4. Display the data on an OLED screen

This approach is ideal for battery-powered applications where energy conservation is important.

## Hardware Requirements

- ESP32 or ESP8266 development board
- DHT22 temperature and humidity sensor
- SSD1306 OLED display (128x64 pixels recommended)
- Pushbutton
- 10K pull-up resistor (if your button doesn't have an internal pull-up)
- Breadboard and jumper wires

## Wiring

1. **DHT22 Sensor**:
   - Connect VCC to 3.3V
   - Connect GND to ground
   - Connect DATA to GPIO4 (or change the pin in the code)

2. **OLED Display**:
   - Connect VCC to 3.3V
   - Connect GND to ground
   - Connect SCL to GPIO22 (or change the pin in the code)
   - Connect SDA to GPIO21 (or change the pin in the code)

3. **Button**:
   - Connect one side to GPIO0 (or change the pin in the code)
   - Connect the other side to ground
   - Connect a 10K pull-up resistor between GPIO0 and 3.3V (if not using internal pull-up)

## Running the Example

1. Flash MicroPython to your ESP device if you haven't already
2. Upload the `button_triggered_display.py` script to your device
3. Run the script

```python
import button_triggered_display
button_triggered_display.main()
```

## How It Works

### Energy Conservation

The example uses ESP32's light sleep mode to conserve energy when not actively reading or displaying data. In light sleep mode:

- The CPU is paused
- RAM is preserved
- Peripherals can be configured to wake the device
- Power consumption is significantly reduced

### Button Wake-Up

The device is configured to wake up from sleep when the button is pressed. This is done using the `wake_on_ext0` function, which allows an external pin to trigger a wake-up event.

### Simulation Mode

The example includes a simulation mode that runs when not on actual ESP hardware. This allows you to test the functionality on a development computer before deploying to the ESP device.

## Customization

You can customize the example by:

1. Changing the GPIO pins for the sensor, display, or button
2. Adjusting the display time before going back to sleep
3. Adding additional sensors
4. Modifying the information displayed on the OLED screen

## Power Consumption

Typical power consumption in different states:

- Active mode (reading sensors and updating display): ~80-120mA
- Light sleep mode: ~0.8-1.5mA

This represents a power saving of approximately 98% during idle periods, significantly extending battery life.