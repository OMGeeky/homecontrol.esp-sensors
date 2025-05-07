"""
Main application for ESP32 sensor display that activates on button press or at regular intervals.

This program:
1. Sets up a button input
2. Uses low-power sleep mode to conserve energy
3. Wakes up and reads sensor data when the button is pressed or at regular intervals
4. Displays the data on an OLED screen
5. Publishes sensor data to MQTT broker (if enabled)
"""

import time
import sys

from esp_sensors.oled_display import OLEDDisplay
from esp_sensors.dht22 import DHT22Sensor
from esp_sensors.mqtt import setup_mqtt, publish_sensor_data
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
    SIMULATION = False
except ImportError:
    # Simulation mode for development on non-ESP hardware
    SIMULATION = True
    print("Running in simulation mode - hardware functions will be simulated")


def simulate_button_press(timeout=None):
    """
    Simulate a button press in simulation mode.

    Args:
        timeout: Time in seconds to wait for input before returning.
                If None, wait indefinitely.

    Returns:
        True if button was pressed or timeout occurred, False to exit
    """
    import select
    import sys

    if timeout is not None:
        print(
            f"\nPress Enter to simulate a button press (or 'q' to quit, Ctrl+C to exit)..."
            f"\nWill automatically continue in {timeout} seconds..."
        )
    else:
        print(
            "\nPress Enter to simulate a button press (or 'q' to quit, Ctrl+C to exit)..."
        )

    try:
        # Set up select to monitor stdin with timeout
        if timeout is not None:
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if not rlist:
                # Timeout occurred, no input
                print("Timeout reached, continuing automatically...")
                return True

        # If we get here, either there was input or timeout was None
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
    last_read_time = 0  # Track the last time sensors were read

    # Set up button using configuration
    button_pin = button_config.get("pin", 0)
    if not SIMULATION:
        pull_up = button_config.get("pull_up", True)
        button = Pin(button_pin, Pin.IN, Pin.PULL_UP if pull_up else None)

    # Display initialization message
    display.clear()
    display.display_text("Ready - Auto & Button", 0, 0)
    print(f"System initialized. Will run every {mqtt_publish_interval} seconds or on button press...")

    # Main loop - sleep until button press, then read and display sensor data
    try:
        while True:
            # Calculate time until next scheduled reading
            current_time = time.time()
            time_since_last_read = current_time - last_read_time
            time_until_next_read = max(0, mqtt_publish_interval - int(time_since_last_read))

            # Wait for button press or until next scheduled reading
            button_pressed = False

            if SIMULATION:
                # In simulation mode, wait for Enter key with timeout
                if not simulate_button_press(timeout=time_until_next_read if last_read_time > 0 else None):
                    break  # Exit if 'q' was pressed or Ctrl+C

                # If we get here, either button was pressed or timeout occurred
                button_pressed = True
            else:
                # In hardware mode, check if button is pressed (active low)
                if button.value() == 0:  # Button is pressed
                    button_pressed = True
                elif time_since_last_read >= mqtt_publish_interval:
                    # Time for scheduled reading
                    button_pressed = True
                else:
                    # Go to light sleep mode to save power
                    # Wake up on pin change (button press) or timer
                    print(f"Entering light sleep mode for {time_until_next_read:.1f} seconds or until button press...")

                    # Set up wake on button press
                    esp32.wake_on_ext0(pin=button, level=0)  # Wake on button press (low)

                    # Set up wake on timer
                    if last_read_time > 0:  # Skip timer on first run
                        # Convert seconds to milliseconds for sleep
                        esp32.wake_on_timer(time_until_next_read * 1000)

                    # Enter light sleep
                    esp32.light_sleep()  # Light sleep preserves RAM but saves power

                    # When we get here, either the button was pressed or the timer expired
                    button_pressed = True

            # Determine if this was triggered by a button press or scheduled interval
            if SIMULATION:
                trigger_source = "user input or scheduled interval"
            else:
                trigger_source = "button press" if button.value() == 0 else "scheduled interval"
            print(f"Reading sensor data (triggered by {trigger_source})...")

            # Read sensor values
            temperature = dht_sensor.read_temperature()
            humidity = dht_sensor.read_humidity()

            # Update last read time
            last_read_time = time.time()

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
            display.display_text("Ready - Auto & Button", 0, 0)

            if SIMULATION:
                print(f"Display cleared. Will run again in {mqtt_publish_interval - (time.time() - last_read_time):.1f} seconds or on button press.")

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
