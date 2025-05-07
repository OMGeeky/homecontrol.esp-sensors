"""
Example script for using the DHT22 sensor with an ESP32.

This script demonstrates how to initialize and read from a DHT22 sensor
connected to an ESP32 microcontroller using the configuration system.

Usage:
    - Upload this script to your ESP32 running MicroPython
    - Ensure config.json is properly set up with DHT22 sensor configuration
    - The script will read temperature and humidity at the specified interval
"""

import time
import sys
import os

# Add the src directory to the Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Check if running on MicroPython
if sys.implementation.name == "micropython":
    from src.esp_sensors.dht22 import DHT22Sensor
    from src.esp_sensors.config import load_config, get_sensor_config

    def main():
        # Load configuration
        config = load_config()
        dht_config = get_sensor_config("dht22", config)

        print(f"Initializing DHT22 sensor from configuration")
        print(f"Sensor name: {dht_config.get('name')}")
        print(f"Sensor pin: {dht_config.get('pin')}")

        # Initialize the sensor using configuration
        sensor = DHT22Sensor(sensor_config=config)

        print("Starting sensor readings. Press Ctrl+C to stop.")

        try:
            while True:
                # Read temperature
                temperature = sensor.read()
                # Read humidity
                humidity = sensor.read_humidity()

                # Get the current timestamp
                timestamp = time.time()

                # Print readings
                print(f"Time: {timestamp}")
                print(f"Temperature: {temperature}°C ({sensor.to_fahrenheit()}°F)")
                print(f"Humidity: {humidity}%")
                print("-" * 30)

                # Wait for the next reading
                time.sleep(sensor.interval)

        except KeyboardInterrupt:
            print("Sensor readings stopped.")
        except Exception as e:
            print(f"Error: {e}")

    if __name__ == "__main__":
        main()
else:
    print("This script is designed to run on MicroPython on an ESP32.")
    print("Running in simulation mode for demonstration purposes.")

    # Import for simulation mode
    from src.esp_sensors.dht22 import DHT22Sensor
    from src.esp_sensors.config import load_config, get_sensor_config

    def main():
        # Load configuration
        config = load_config()
        dht_config = get_sensor_config("dht22", config)

        print(f"Initializing DHT22 sensor simulation from configuration")
        print(f"Sensor name: {dht_config.get('name')}")
        print(f"Sensor pin: {dht_config.get('pin')}")

        # Initialize the sensor using configuration
        sensor = DHT22Sensor(sensor_config=config)

        print("Starting simulated sensor readings. Press Ctrl+C to stop.")

        try:
            for _ in range(5):  # Just do 5 readings for the simulation
                # Read temperature
                temperature = sensor.read()
                # Read humidity
                humidity = sensor.read_humidity()

                # Get the current timestamp
                timestamp = time.time()

                # Print readings
                print(f"Time: {timestamp}")
                print(f"Temperature: {temperature}°C ({sensor.to_fahrenheit()}°F)")
                print(f"Humidity: {humidity}%")
                print("-" * 30)

                # Wait for the next reading
                time.sleep(sensor.interval)

            print("Simulation complete.")

        except KeyboardInterrupt:
            print("Sensor readings stopped.")
        except Exception as e:
            print(f"Error: {e}")

    if __name__ == "__main__":
        main()
