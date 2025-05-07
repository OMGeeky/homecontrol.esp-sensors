# ESP32 Deployment Guide for Button-Triggered Display Example

This guide provides step-by-step instructions for setting up and deploying the `button_triggered_display.py` example to an ESP32 microcontroller.

## Required Hardware Components

1. **ESP32 Development Board** - Any ESP32-based board (like NodeMCU-32S, WEMOS LOLIN32, etc.)
2. **DHT22 Sensor** - Temperature and humidity sensor
3. **SSD1306 OLED Display** - 128x64 pixel I2C OLED display
4. **Push Button** - Momentary push button
5. **Breadboard and Jumper Wires** - For connecting components
6. **Micro USB Cable** - For connecting ESP32 to your computer

## Wiring Instructions

Connect the components to your ESP32 as follows:

### DHT22 Sensor
- VCC pin → 3.3V on ESP32
- GND pin → GND on ESP32
- DATA pin → GPIO 4 on ESP32

### SSD1306 OLED Display (I2C)
- VCC pin → 3.3V on ESP32
- GND pin → GND on ESP32
- SCL pin → GPIO 22 on ESP32
- SDA pin → GPIO 21 on ESP32

### Push Button
- Connect one terminal to GPIO 0 on ESP32
- Connect the other terminal to GND on ESP32
- (The internal pull-up resistor will be enabled in the code)

## Setting Up MicroPython on ESP32

1. **Install Python and required tools**:
   ```bash
   pip install esptool
   ```

2. **Download MicroPython firmware**:
   - Visit the [MicroPython downloads page](https://micropython.org/download/esp32/)
   - Download the latest stable firmware (.bin file)

3. **Erase the ESP32 flash**:
   ```bash
   esptool.py --port /dev/ttyUSB0 erase_flash
   ```
   Note: Replace `/dev/ttyUSB0` with your ESP32's port (on Windows, it might be `COM3` or similar)

4. **Flash MicroPython firmware**:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20230426-v1.20.0.bin
   ```
   Note: Replace the firmware filename with the one you downloaded

## Installing Required Libraries on ESP32

You'll need to install the following libraries on your ESP32:
- `ssd1306.py` for the OLED display
- `dht.py` for the DHT22 sensor

You can use a tool like `ampy` or `rshell` to upload these libraries:

1. **Install ampy**:
   ```bash
   pip install adafruit-ampy
   ```

2. **Download the required libraries**:
   - SSD1306 library: [micropython-ssd1306](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py)
   - DHT library: This is usually included in MicroPython firmware for ESP32

3. **Upload the SSD1306 library** (if not already included in firmware):
   ```bash
   ampy --port /dev/ttyUSB0 put ssd1306.py
   ```

## Deploying the Code to ESP32

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/yourusername/esp-sensors.git
   cd esp-sensors
   ```

2. **Create a deployment directory**:
   ```bash
   mkdir deploy
   ```

3. **Copy the necessary files**:
   ```bash
   cp -r src/esp_sensors deploy/
   cp examples/button_triggered_display.py deploy/main.py
   ```

4. **Modify the imports in main.py**:
   Edit `deploy/main.py` to change the import statements:
   ```python
   # Replace these lines:
   sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
   from src.esp_sensors.oled_display import OLEDDisplay
   from src.esp_sensors.dht22 import DHT22Sensor
   
   # With these lines:
   from esp_sensors.oled_display import OLEDDisplay
   from esp_sensors.dht22 import DHT22Sensor
   ```

5. **Upload the files to ESP32**:
   ```bash
   # Upload the esp_sensors package
   ampy --port /dev/ttyUSB0 mkdir esp_sensors
   ampy --port /dev/ttyUSB0 put deploy/esp_sensors/__init__.py esp_sensors/__init__.py
   ampy --port /dev/ttyUSB0 put deploy/esp_sensors/sensor.py esp_sensors/sensor.py
   ampy --port /dev/ttyUSB0 put deploy/esp_sensors/temperature.py esp_sensors/temperature.py
   ampy --port /dev/ttyUSB0 put deploy/esp_sensors/humidity.py esp_sensors/humidity.py
   ampy --port /dev/ttyUSB0 put deploy/esp_sensors/dht22.py esp_sensors/dht22.py
   ampy --port /dev/ttyUSB0 put deploy/esp_sensors/oled_display.py esp_sensors/oled_display.py
   
   # Upload the main script (will run automatically on boot)
   ampy --port /dev/ttyUSB0 put deploy/main.py
   ```

## Running the Example

1. **Reset your ESP32** by pressing the reset button or disconnecting and reconnecting power.

2. **Monitor the output** (optional):
   ```bash
   ampy --port /dev/ttyUSB0 run main.py
   ```
   Or use a serial monitor:
   ```bash
   screen /dev/ttyUSB0 115200
   ```
   (Press Ctrl+A, then K to exit screen)

3. **Interact with the device**:
   - The OLED display should show "Ready - Press Button"
   - Press the button connected to GPIO 0
   - The ESP32 will wake up, read temperature and humidity from the DHT22 sensor, and display the values on the OLED screen
   - After 5 seconds, the display will clear and show "Ready - Press Button" again
   - The ESP32 will enter light sleep mode to save power until the button is pressed again

## Troubleshooting Common Issues

### Display Not Working
- Check I2C connections (SCL and SDA pins)
- Verify the I2C address (default is 0x3C, but some displays use 0x3D)
- Try running an I2C scanner script to detect the display

### DHT22 Sensor Not Reading
- Check the data pin connection
- Ensure the sensor is powered correctly (3.3V)
- Try adding a 10kΩ pull-up resistor between the data pin and VCC
- DHT22 sensors can be sensitive to timing; try reducing the reading frequency

### ESP32 Not Entering Sleep Mode
- Ensure the button is connected to GPIO 0
- Check that the button is properly grounded
- Try using a different GPIO pin and update the code accordingly

### Upload Errors
- Make sure the ESP32 is in the correct mode for uploading
- Try pressing the BOOT button while connecting power
- Check USB cable and port connections
- Verify you have the correct port in your commands

## Advanced Configuration

### Changing Pin Assignments
If you need to use different GPIO pins, modify the pin numbers in the `main.py` file:

```python
# Initialize a DHT22 sensor
dht_sensor = DHT22Sensor(
    name="Living Room",
    pin=4,  # Change this to your DHT22 data pin
    interval=5,
    unit="C"
)

# Initialize an OLED display
display = OLEDDisplay(
    name="Status Display",
    scl_pin=22,  # Change this to your SCL pin
    sda_pin=21,  # Change this to your SDA pin
    width=128,
    height=64,
    interval=1
)

# Set up button on GPIO pin 0
button_pin = 0  # Change this to your button pin
```

### Power Optimization
For battery-powered applications, you can increase the sleep duration by modifying the code. Look for the `time.sleep(5)` line and adjust as needed.

## Further Resources

- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 Technical Reference Manual](https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf)
- [SSD1306 OLED Display Guide](https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html)
- [DHT22 Sensor Guide](https://randomnerdtutorials.com/esp32-dht11-dht22-temperature-humidity-sensor-micropython/)