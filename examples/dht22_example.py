"""
Example script for using the DHT22 sensor with an ESP32.

This script demonstrates how to initialize and read from a DHT22 sensor
connected to an ESP32 microcontroller.

Usage:
    - Upload this script to your ESP32 running MicroPython
    - Connect the DHT22 sensor to the specified GPIO pin
    - The script will read temperature and humidity at the specified interval
"""
import time
import sys

# Check if running on MicroPython
if sys.implementation.name == 'micropython':
    from src.esp_sensors.dht22 import DHT22Sensor
    
    # Configuration
    SENSOR_NAME = "living_room"
    SENSOR_PIN = 4  # GPIO pin where DHT22 is connected
    READ_INTERVAL = 5  # seconds between readings
    
    def main():
        print(f"Initializing DHT22 sensor on pin {SENSOR_PIN}")
        
        # Initialize the sensor
        sensor = DHT22Sensor(SENSOR_NAME, SENSOR_PIN, READ_INTERVAL)
        
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
                time.sleep(READ_INTERVAL)
                
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
    
    # Configuration
    SENSOR_NAME = "simulation"
    SENSOR_PIN = 4
    READ_INTERVAL = 2  # shorter interval for demonstration
    
    def main():
        print(f"Initializing DHT22 sensor simulation")
        
        # Initialize the sensor
        sensor = DHT22Sensor(SENSOR_NAME, SENSOR_PIN, READ_INTERVAL)
        
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
                time.sleep(READ_INTERVAL)
                
            print("Simulation complete.")
                
        except KeyboardInterrupt:
            print("Sensor readings stopped.")
        except Exception as e:
            print(f"Error: {e}")
            
    if __name__ == "__main__":
        main()