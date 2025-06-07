"""
MQTT Example for ESP32

This example demonstrates how to use the ESP32MQTTClient class to:
1. Connect to an MQTT broker with credentials
2. Publish data to a topic
3. Read data from a topic with a configurable wait time

Usage:
- Run this script on an ESP32 device with MicroPython installed
- For simulation mode, run on a regular computer
"""

import time
import json
from src.esp_sensors.mqtt import ESP32MQTTClient, SIMULATION

# MQTT Configuration
MQTT_CONFIG = {
    "client_id": "esp32_example",
    "broker": "mqtt.fritz.box",  # Replace with your MQTT broker address
    "port": 1883,
    "username": "geeky",  # Replace with your MQTT username
    "password": "geeky",  # Replace with your MQTT password
    "topic_data": "esp32/example/data",
    "topic_control": "esp32/example/control",
}


def main():
    print("Starting MQTT Example")

    # Create and connect MQTT client
    client = ESP32MQTTClient(
        MQTT_CONFIG["client_id"],
        MQTT_CONFIG["broker"],
        MQTT_CONFIG["port"],
        MQTT_CONFIG["username"],
        MQTT_CONFIG["password"],
    )

    # Connect to the broker
    if not client.connect():
        print("Failed to connect to MQTT broker")
        return

    print("Connected to MQTT broker")

    try:
        # Subscribe to the control topic
        client.subscribe(MQTT_CONFIG["topic_control"])
        print(f"Subscribed to {MQTT_CONFIG['topic_control']}")

        # Publish some data
        data = {"temperature": 25.5, "humidity": 60.2, "timestamp": time.time()}

        print(f"Publishing data to {MQTT_CONFIG['topic_data']}")
        client.publish(MQTT_CONFIG["topic_data"], json.dumps(data), retain=True)

        # Read from the control topic with a timeout
        print(f"Waiting for messages on {MQTT_CONFIG['topic_control']} (timeout: 10s)")
        message = client.read_topic(MQTT_CONFIG["topic_control"], 10)

        if message:
            # Process the message
            if isinstance(message, bytes):
                message = message.decode("utf-8")

            try:
                control_data = json.loads(message)
                print(f"Received control message: {control_data}")

                # Example of processing a command
                if "command" in control_data:
                    command = control_data["command"]
                    value = control_data.get("value")
                    print(f"Processing command: {command} with value: {value}")

                    # Here you would handle different commands
                    if command == "set_led":
                        print(f"Setting LED to {value}")
                    elif command == "reboot":
                        print("Rebooting device...")
                    else:
                        print(f"Unknown command: {command}")
            except json.JSONDecodeError:
                print(f"Received non-JSON message: {message}")
        else:
            print("No control message received within timeout period")

        # Disconnect from the broker
        client.disconnect()
        print("Disconnected from MQTT broker")

    except Exception as e:
        print(f"Error in MQTT example: {e}")
        client.disconnect()


if __name__ == "__main__":
    main()
