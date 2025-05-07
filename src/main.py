"""
Main application for ESP32 sensor display that activates on button press.

This program:
1. Sets up a button input
2. Uses low-power sleep mode to conserve energy
3. Wakes up and reads sensor data when the button is pressed
4. Displays the data on an OLED screen
5. Publishes sensor data to MQTT broker (if enabled)
"""

import time
import sys

from esp_sensors.oled_display import OLEDDisplay
from esp_sensors.dht22 import DHT22Sensor
from esp_sensors.config import (
    load_config,
    get_button_config,
    get_sensor_config,
    get_display_config,
    get_mqtt_config,
)

# Import hardware-specific modules if available (for ESP32/ESP8266)
try:
    from machine import Pin, deepsleep
    import esp32
    from umqtt.simple import MQTTClient

    SIMULATION = False
except ImportError:
    # Simulation mode for development on non-ESP hardware
    SIMULATION = True
    print("Running in simulation mode - hardware functions will be simulated")

    # Mock MQTT client for simulation
    class MQTTClient:
        def __init__(self, client_id, server, port=0, user=None, password=None, keepalive=0, ssl=False):
            self.client_id = client_id
            self.server = server
            self.port = port
            self.user = user
            self.password = password
            self.keepalive = keepalive
            self.ssl = ssl
            self.connected = False

        def connect(self):
            print(f"[MQTT] Connecting to {self.server}:{self.port} as {self.client_id}")
            self.connected = True
            return 0

        def disconnect(self):
            print("[MQTT] Disconnected")
            self.connected = False

        def publish(self, topic, msg):
            print(f"[MQTT] Publishing to {topic}: {msg}")
            return


def setup_mqtt(mqtt_config):
    """
    Set up and connect to the MQTT broker.

    Args:
        mqtt_config: MQTT configuration dictionary

    Returns:
        MQTTClient instance if enabled and connected, None otherwise
    """
    if not mqtt_config.get("enabled", False):
        print("MQTT is disabled in configuration")
        return None

    try:
        client_id = mqtt_config.get("client_id", "esp_sensor")
        broker = mqtt_config.get("broker", "mqtt.example.com")
        port = mqtt_config.get("port", 1883)
        username = mqtt_config.get("username", "")
        password = mqtt_config.get("password", "")
        keepalive = mqtt_config.get("keepalive", 60)
        ssl = mqtt_config.get("ssl", False)

        print(f"Setting up MQTT client: {client_id} -> {broker}:{port}")
        client = MQTTClient(client_id, broker, port, username, password, keepalive, ssl)

        # Try to connect
        client.connect()
        print("MQTT connected successfully")
        return client
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return None


def publish_sensor_data(client, mqtt_config, sensor, temperature, humidity):
    """
    Publish sensor data to MQTT topics.

    Args:
        client: MQTTClient instance
        mqtt_config: MQTT configuration dictionary
        sensor: Sensor instance
        temperature: Temperature reading
        humidity: Humidity reading
    """
    if client is None:
        return

    try:
        topic_prefix = mqtt_config.get("topic_prefix", "esp/sensors")
        sensor_name = sensor.name.lower().replace(" ", "_")

        # Publish temperature
        temp_topic = f"{topic_prefix}/{sensor_name}/temperature"
        client.publish(temp_topic, str(temperature).encode())

        # Publish humidity
        humidity_topic = f"{topic_prefix}/{sensor_name}/humidity"
        client.publish(humidity_topic, str(humidity).encode())

        # Publish combined data as JSON
        import json
        data_topic = f"{topic_prefix}/{sensor_name}/data"
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": time.time(),
            "unit": sensor.temperature_unit
        }
        client.publish(data_topic, json.dumps(data).encode())

        print(f"Published sensor data to MQTT: {temp_topic}, {humidity_topic}, {data_topic}")
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")


def simulate_button_press():
    """Simulate a button press in simulation mode."""
    print(
        "\nPress Enter to simulate a button press (or 'q' to quit, Ctrl+C to exit)..."
    )
    try:
        user_input = input()
        if user_input.lower() == "q":
            return False
        return True
    except KeyboardInterrupt:
        return False


def main():
    """
    Main function to demonstrate button-triggered sensor display with MQTT publishing.
    """
    # Load configuration
    config = load_config()
    button_config = get_button_config("main_button", config)
    mqtt_config = get_mqtt_config(config)

    # Initialize a DHT22 sensor using configuration
    dht_sensor = DHT22Sensor(
        sensor_config=get_sensor_config("dht22", config)  # Pass the loaded config
    )

    # Initialize an OLED display using configuration
    display = OLEDDisplay(
        display_config=get_display_config("oled", config)  # Pass the loaded config
    )

    # Set up MQTT client if enabled
    mqtt_client = setup_mqtt(mqtt_config)
    mqtt_publish_interval = mqtt_config.get("publish_interval", 60)
    last_publish_time = 0

    # Set up button using configuration
    button_pin = button_config.get("pin", 0)
    if not SIMULATION:
        pull_up = button_config.get("pull_up", True)
        button = Pin(button_pin, Pin.IN, Pin.PULL_UP if pull_up else None)

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
                    esp32.wake_on_ext0(
                        pin=button, level=0
                    )  # Wake on button press (low)
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
            display.display_values(
                [name_str, temp_str, hum_str, time_str, "Press button again"]
            )

            # Print to console
            print(f"Updated display with: {temp_str}, {hum_str}")

            # Publish to MQTT if enabled and interval has elapsed
            current_time = time.time()
            if mqtt_client and (current_time - last_publish_time >= mqtt_publish_interval):
                publish_sensor_data(mqtt_client, mqtt_config, dht_sensor, temperature, humidity)
                last_publish_time = current_time
                print(f"Next MQTT publish in {mqtt_publish_interval} seconds")

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

        # Disconnect MQTT if connected
        if mqtt_client:
            try:
                mqtt_client.disconnect()
                print("MQTT client disconnected")
            except Exception as e:
                print(f"Error disconnecting MQTT client: {e}")

        time.sleep(1)
        display.clear()
        print("Program terminated by user")


if __name__ == "__main__":
    main()
