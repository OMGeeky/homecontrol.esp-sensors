"""
Example usage of the OLED display with temperature and humidity sensors.
"""
import time
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.esp_sensors.oled_display import OLEDDisplay
from src.esp_sensors.dht22 import DHT22Sensor


def main():
    """
    Main function to demonstrate OLED display usage with sensors.
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

    # Display initialization message
    display.clear()
    display.display_text("Initializing...", 0, 0)
    time.sleep(2)

    # Main loop - run for 5 iterations as a demonstration
    try:
        print("Starting demonstration (5 iterations)...")
        for i in range(5):
            print(f"\nIteration {i+1}/5:")

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
                f"Demo ({i+1}/5)"
            ])

            # Print to console in simulation mode
            print(f"Updated display with: {temp_str}, {hum_str}")

            # Wait for next update
            print(f"Waiting {display.interval} second(s)...")
            time.sleep(display.interval)

    except KeyboardInterrupt:
        # Clean up on exit
        display.clear()
        display.display_text("Shutting down...", 0, 0)
        time.sleep(1)
        display.clear()
        print("Program terminated by user")


if __name__ == "__main__":
    main()
