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

from esp_sensors.dht22 import DHT22Sensor
from esp_sensors.mqtt import (
    setup_mqtt,
    publish_sensor_data,
    check_config_update,
    get_data_topic,
)
from esp_sensors.oled_display import OLEDDisplay
from esp_sensors.config import Config

# Import hardware-specific modules if available (for ESP32/ESP8266)
from machine import Pin, deepsleep
import esp32


def main():
    """
    Main function to demonstrate button-triggered sensor display with MQTT publishing.
    """
    # record start time
    last_read_time = time.time()  # this is to make sure, the sleep time is correct

    # Load configuration
    config = Config()

    # Initialize an OLED display using configuration
    display = OLEDDisplay(display_config=config.display_config)

    # Check if display is enabled in config
    display_enabled = config.display_config.get("enabled", True)
    display_always_on = config.display_config.get("always_on", False)

    if display_enabled:
        display.power_on()  # Explicitly power on the display
        display.clear()
        display.set_header(f"Device: {config.device_name}")
        display.set_status("Initializing...")
    else:
        print("Display disabled in config, not initializing")

    # Initialize a DHT22 sensor using configuration
    dht_sensor = DHT22Sensor(sensor_config=config.dht_config)

    # Update display header with sensor name
    name_str = f"N: {dht_sensor.name}"
    display.set_header(name_str)

    # Set up MQTT
    mqtt_enabled = config.mqtt_config.get("enabled", False)
    load_config_from_mqtt = config.mqtt_config.get("load_config_from_mqtt", False)

    print(f"System initialized. Will run every {config.update_interval} seconds...")
    mqtt_client = None
    # Main loop - sleep until button press, then read and display sensor data
    try:
        # while True:
        # print('sleeping for 5 seconds for debugging')
        # display.set_status('debug sleeping')
        # time.sleep(5)

        # Read sensor values
        display.set_status("Reading sensor values...")
        temperature = dht_sensor.read_temperature()
        humidity = dht_sensor.read_humidity()

        # # Format values for display
        temp_str = f"Temp: {temperature:.1f} C"
        hum_str = f"Humidity: {humidity:.1f}%"
        time_str = f"Time: {time.time():.0f}"

        # Print to console
        print("=" * 20)
        print(f"{temp_str}, {hum_str}")
        print("=" * 20)

        # Display values
        ## TODO: only display values, if the button has been clicked
        display.display_values([temp_str, hum_str, time_str])

        display.set_status("")

        # Publish to MQTT
        if mqtt_enabled:
            # Initialize Wi-Fi connection
            display.set_status("Connecting WiFi...")
            wifi_connected, station = connect_wifi(
                config.network_config, config.network_fallback_config
            )

            if not wifi_connected:
                display.set_status("WiFi connection failed")
                print("Failed to connect to WiFi, skipping MQTT operations")
            else:
                # Set up MQTT client if enabled
                display.set_status("Setting up MQTT...")
                print(
                    f"MQTT enabled: {mqtt_enabled}, broker: {config.mqtt_config.get('broker')}"
                )
                mqtt_client = setup_mqtt(config.mqtt_config)

                if mqtt_client:
                    if not mqtt_client.connected:
                        try:
                            mqtt_client.connect()
                            display.set_status("MQTT connected")
                            print("MQTT client connected")
                        except Exception as e:
                            print(f"Error connecting MQTT client: {e}")
                            mqtt_client = None

                    if mqtt_client and mqtt_client.connected:
                        # First publish sensor data (most important task)
                        display.set_status("Publishing to MQTT...")
                        print(
                            f"Publishing sensor data to MQTT at {config.mqtt_config.get('broker')}:{config.mqtt_config.get('port')}"
                        )
                        publish_success = publish_sensor_data(
                            mqtt_client,
                            config.mqtt_config,
                            dht_sensor,
                            temperature,
                            humidity,
                        )
                        if publish_success:
                            print("Sensor data published to MQTT")
                            display.set_status("Published to MQTT")
                        else:
                            print("Failed to publish sensor data to MQTT")
                            display.set_status("MQTT publish failed")

                        # Only check for config updates if publishing was successful
                        if publish_success and load_config_from_mqtt:
                            display.set_status("Checking MQTT config...")
                            print("Checking for configuration updates...")
                            updated_config = check_config_update(
                                mqtt_client, config.mqtt_config, config.config
                            )

                            # If we got an updated configuration with a newer version, save it
                            if (
                                updated_config != config.config
                                and updated_config.get("version", 0)
                                > config.current_version
                            ):
                                display.set_status("Updating config...")
                                print(
                                    f"Found newer configuration (version {updated_config.get('version')}), updating..."
                                )
                                config.save_config(updated_config)
                                mqtt_client.publish(
                                    get_data_topic(config.mqtt_config)
                                    + "/config_status",
                                    "Configuration updated",
                                )
                                # Note: We continue with the current config for this cycle
                                # The updated config will be used after the next reboot
                            else:
                                print(
                                    f"No configuration updates found or no newer version available (local version: {config.current_version})"
                                )

                        # Disconnect MQTT client after operations
                        try:
                            mqtt_client.disconnect()
                            display.set_status("MQTT disconnected")
                            print("MQTT client disconnected")
                        except Exception as e:
                            print(f"Error disconnecting MQTT client: {e}")

                    if mqtt_client:
                        # Save the updated reconnection state to the configuration
                        config.save_config()

                # Disconnect WiFi to save power
                disconnect_wifi(station)
        else:
            print("MQTT is disabled, not publishing data")

        # sleep, to be able to do something, before going into deepsleep
        # time.sleep(display.on_time)

        time_until_next_read = config.update_interval - (time.time() - last_read_time)
        if time_until_next_read < 0:
            time_until_next_read = config.update_interval

        display.set_status(f"Sleeping {time_until_next_read}s")
        print("sleeping for", time_until_next_read, "seconds")

        # Power off display to save battery before going to sleep
        # Only if display is enabled and not set to always_on
        if display_enabled and not display_always_on:
            display.power_off()
            print("Display powered off to save battery")
        elif display_enabled and display_always_on:
            print("Display kept on as per always_on setting")

        deepsleep(time_until_next_read * 1000)

    except KeyboardInterrupt:
        # Clean up on exit
        if display_enabled:
            display.clear()
            display.display_text("Shutting down...", 0, 0)

        # Disconnect MQTT if connected
        if "mqtt_client" in locals() and mqtt_client:
            try:
                mqtt_client.disconnect()
                print("MQTT client disconnected")
            except Exception as e:
                print(f"Error disconnecting MQTT client: {e}")

        # Disconnect WiFi if connected
        if "station" in locals() and station:
            disconnect_wifi(station)

        # Power off display to save battery if it's enabled and not set to always_on
        if display_enabled and not display_always_on:
            display.power_off()
            print("Display powered off during shutdown")
        elif display_enabled and display_always_on:
            print("Display kept on during shutdown as per always_on setting")

        print("Program terminated by user")


def connect_wifi(network_config: dict, fallback_config: dict = None):
    import network

    ssid = network_config.get("ssid")
    password = network_config.get("password")
    timeout = network_config.get("timeout", 5)  # Reduced timeout for faster failure
    if not ssid or not password:
        print("SSID and password are required for WiFi connection")
        return False, None

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

            # Try fallback network if available
            if fallback_config:
                print("Trying fallback network")
                return connect_wifi(fallback_config)
            return False, None

        time.sleep(0.5)  # Reduced sleep time for faster checking

    print("Connection successful")
    print(station.ifconfig())
    return True, station


def disconnect_wifi(station):
    """
    Disconnect from WiFi to save power.

    Args:
        station: The WiFi station interface
    """
    if station:
        station.active(False)
        print("WiFi disconnected to save power")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # this should never really be reachable. But if it is, just reset the system
        print(f"An error occurred: {e}")
        time.sleep(5)  # give time to read the error message and respond
        deepsleep(60)  # dummy deepsleep to basically reset the system
