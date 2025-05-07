"""
Example usage of the OLED display with temperature and humidity sensors.
This example demonstrates how to use the configuration system to initialize sensors and displays.
"""
import time
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.esp_sensors.oled_display import OLEDDisplay
from src.esp_sensors.dht22 import DHT22Sensor
from src.esp_sensors.config import load_config, get_sensor_config, get_display_config


def main():
    """
    Main function to demonstrate OLED display usage with sensors.
    """
    # Load configuration from file
    print("Loading configuration from config.json...")
    config = load_config()

    # Method 1: Initialize sensors using configuration directly
    print("\nMethod 1: Initialize using configuration directly")

    # Get configuration for DHT22 sensor
    dht_config = get_sensor_config("dht22", config)
    print(f"DHT22 config: {dht_config}")

    # Initialize a DHT22 sensor with configuration
    dht_sensor = DHT22Sensor(
        sensor_type="dht22",  # This will load config for this sensor type
        config=config         # Pass the loaded config
    )
    print(f"Created DHT22 sensor: {dht_sensor.name}, pin: {dht_sensor.pin}, interval: {dht_sensor.interval}s")

    # Method 2: Initialize with some parameters from config, others specified directly
    print("\nMethod 2: Override some config parameters")

    # Initialize an OLED display with some custom parameters
    display = OLEDDisplay(
        # These parameters will override the config values
        name="Custom Display",
        interval=1,  # Update every second

        # Other parameters will be loaded from config
        config=config
    )
    print(f"Created OLED display: {display.name}, size: {display.width}x{display.height}, interval: {display.interval}s")

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
