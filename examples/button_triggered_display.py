"""
Example of an energy-efficient sensor display that activates on button press.

This example demonstrates how to:
1. Set up a button input
2. Use low-power sleep mode to conserve energy
3. Wake up and read sensor data when the button is pressed
4. Display the data on an OLED screen
"""
import time
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.esp_sensors.oled_display import OLEDDisplay
from src.esp_sensors.dht22 import DHT22Sensor

# Import hardware-specific modules if available (for ESP32/ESP8266)
try:
    from machine import Pin, deepsleep
    import esp32
    SIMULATION = False
except ImportError:
    # Simulation mode for development on non-ESP hardware
    SIMULATION = True
    print("Running in simulation mode - hardware functions will be simulated")


def simulate_button_press():
    """Simulate a button press in simulation mode."""
    print("\nPress Enter to simulate a button press (or 'q' to quit, Ctrl+C to exit)...")
    try:
        user_input = input()
        if user_input.lower() == 'q':
            return False
        return True
    except KeyboardInterrupt:
        return False


def main():
    """
    Main function to demonstrate button-triggered sensor display.
    """
    # Initialize a DHT22 sensor
    dht_sensor = DHT22Sensor(
        name="Living Room",
        pin=4,  # GPIO pin for DHT22 data
        interval=5,  # Read every 5 seconds
        unit="C"  # Celsius
    )

    # Initialize an OLED display
    display = OLEDDisplay(
        name="Status Display",
        scl_pin=22,  # GPIO pin for I2C clock
        sda_pin=21,  # GPIO pin for I2C data
        width=128,   # Display width in pixels
        height=64,   # Display height in pixels
        interval=1   # Update every second
    )

    # Set up button on GPIO pin 0 (common button pin on many ESP boards)
    button_pin = 0
    if not SIMULATION:
        button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

    # Display initialization message
    display.clear()
    display.display_text("Ready - Press Button", 0, 0)
    print("System initialized. Waiting for button press...")

    # Main loop - sleep until button press, then read and display sensor data
    try:
        while True:
            # Wait for button press
            if SIMULATION:
                # In simulation mode, wait for Enter key
                if not simulate_button_press():
                    break  # Exit if Ctrl+C was pressed
            else:
                # In hardware mode, check if button is pressed (active low)
                if button.value() == 1:  # Button not pressed
                    # Go to light sleep mode to save power
                    # Wake up on pin change (button press)
                    print("Entering light sleep mode...")
                    esp32.wake_on_ext0(pin=button, level=0)  # Wake on button press (low)
                    esp32.light_sleep()  # Light sleep preserves RAM but saves power
                    # When we get here, the button was pressed

            print("Button pressed! Reading sensor data...")

            # Read sensor values
            temperature = dht_sensor.read_temperature()
            humidity = dht_sensor.read_humidity()

            # Format values for display
            temp_str = f"Temp: {temperature:.1f} C"
            hum_str = f"Humidity: {humidity:.1f}%"
            time_str = f"Time: {time.time():.0f}"
            name_str = f"Sensor: {dht_sensor.name}"

            # Display values
            display.display_values([
                name_str,
                temp_str,
                hum_str,
                time_str,
                "Press button again"
            ])

            # Print to console
            print(f"Updated display with: {temp_str}, {hum_str}")

            # Keep display on for a few seconds before going back to sleep
            time.sleep(5)

            # Clear display to save power
            display.clear()
            display.display_text("Ready - Press Button", 0, 0)

            if SIMULATION:
                print("Display cleared. Ready for next button press.")

    except KeyboardInterrupt:
        # Clean up on exit
        display.clear()
        display.display_text("Shutting down...", 0, 0)
        time.sleep(1)
        display.clear()
        print("Program terminated by user")


if __name__ == "__main__":
    main()
