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
    # record start time
    last_read_time = time.time()  # this is to make sure, the sleep time is correct

    # Load configuration
    config = load_config()
    # print('config: ', config)

    # button_config = get_button_config("main_button", config)
    mqtt_config = get_mqtt_config(config)
    dht_config = get_sensor_config("dht22", config)
    display_config = get_display_config("oled", config)
    network_config = config.get("network", {})

    # Initialize a DHT22 sensor using configuration
    dht_sensor = DHT22Sensor(sensor_config=dht_config)

    connect_wifi(network_config)

    # Initialize an OLED display using configuration
    display = OLEDDisplay(display_config=display_config)

    # Set up MQTT client if enabled
    mqtt_client = setup_mqtt(mqtt_config)
    mqtt_publish_interval = mqtt_config.get("publish_interval", 60)

    # # Set up button using configuration
    # button_pin = button_config.get("pin", 0)
    # if not SIMULATION:
    #     pull_up = button_config.get("pull_up", True)
    #     button = Pin(button_pin, Pin.IN, Pin.PULL_UP if pull_up else None)
    #
    # # Display initialization message
    display.clear()
    display.display_text("Ready - Auto & Button", 0, 0)
    print(f"System initialized. Will run every {mqtt_publish_interval} seconds or on button press...")

    # Main loop - sleep until button press, then read and display sensor data
    try:
        # while True:
        print('sleeping for 5 seconds for debugging')
        time.sleep(5)

        # Read sensor values
        temperature = dht_sensor.read_temperature()
        humidity = dht_sensor.read_humidity()
        #
        # # Format values for display
        temp_str = f"Temp: {temperature:.1f} C"
        hum_str = f"Humidity: {humidity:.1f}%"
        time_str = f"Time: {time.time():.0f}"
        name_str = f"Sensor: {dht_sensor.name}"

        # Display values
        # TODO: only display values, if the button has been clicked
        display.display_values(
            [name_str, temp_str, hum_str, time_str, "Press button again"]
        )
        time.sleep(3)

        # Print to console
        print('='*20)
        print(f"Sensor data: {temp_str}, {hum_str}")
        print('='*20)

        # Publish to MQTT
        publish_sensor_data(mqtt_client, mqtt_config, dht_sensor, temperature, humidity)

        if mqtt_client:
            try:
                mqtt_client.disconnect()
                print("MQTT client disconnected")
            except Exception as e:
                print(f"Error disconnecting MQTT client: {e}")

        time_until_next_read = mqtt_publish_interval - (time.time() - last_read_time)
        print('sleeping for', time_until_next_read, 'seconds')
        if not SIMULATION:
            deepsleep(time_until_next_read * 1000)
        else:
            # Simulate deep sleep
            print(f"Simulated deep sleep for {time_until_next_read:.1f} seconds")
            time.sleep(time_until_next_read)


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


def connect_wifi(network_config: dict):
    import network
    ssid = network_config.get("ssid")
    password = network_config.get("password")
    timeout = network_config.get("timeout", 10)
    if not ssid or not password:
        print("SSID and password are required for WiFi connection")
        return False

    print(f'Connecting to WIFI: "{ssid}"')
    # Connect to your network
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    connection_start_time = time.time()
    while not station.isconnected():
        # Check if connection attempt has timed out
        if time.time() - connection_start_time > timeout:
            print("Connection timed out")
            return False
        pass
    print('Connection successful')
    print(station.ifconfig())
    return True


if __name__ == "__main__":
    main()
