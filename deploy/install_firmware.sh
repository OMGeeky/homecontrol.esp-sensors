#pip install esptool
FIRMWARE_FILE=ESP32_GENERIC-20250415-v1.25.0.bin

if [ -z "$ESP_PORT" ]; then
  echo "ESP_PORT is not set. Please set it to the correct port for your ESP32 device."
  exit 1
fi


esptool.py --port "$ESP_PORT" erase_flash
esptool.py --chip esp32 --port "$ESP_PORT" --baud 460800 write_flash -z 0x1000 deploy/firmware/"$FIRMWARE_FILE"
