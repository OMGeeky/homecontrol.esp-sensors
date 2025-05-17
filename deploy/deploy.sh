#pip install adafruit-ampy
CODE_DIR="src/"
LIBS_DIR=deploy/upload

UPLOAD_SOURCE_DIR=deploy/upload
CONFIG_FILE=deploy/config.json
ACTUAL_UPLOAD_SOURCE_DIR=deploy/actual_upload
LAST_UPLOAD_DIR=deploy/last_upload
UPLOAD_TARGET_DIR=

echo "preparing for deployment"
mkdir -p "$UPLOAD_SOURCE_DIR"
# move the last upload directory to a backup to be able to compare the changes and only upload the changes
rm -rf "$LAST_UPLOAD_DIR"
mv "$UPLOAD_SOURCE_DIR" "$LAST_UPLOAD_DIR"

mkdir -p "$UPLOAD_SOURCE_DIR"
mkdir -p "$LAST_UPLOAD_DIR"
cp -r "$CODE_DIR"* "$UPLOAD_SOURCE_DIR"
cp "$CONFIG_FILE" "$UPLOAD_SOURCE_DIR"

# check if the flag -libs is set and copy the libraries to the upload directory
if [[ "$1" == "-libs" ]]; then
  echo "Copying libraries to upload directory"
  mkdir -p "$UPLOAD_SOURCE_DIR/lib"
  cp -r "$LIBS_DIR"* "$UPLOAD_SOURCE_DIR/lib"
fi


# check what files have changed and only upload the changed files (use $ACTUAL_UPLOAD_SOURCE_DIR for the changed files)
echo "Checking for changes in the upload directory"
rm -rf "$ACTUAL_UPLOAD_SOURCE_DIR"
mkdir -p "$ACTUAL_UPLOAD_SOURCE_DIR"
#rsync -a --delete --ignore-existing "$UPLOAD_SOURCE_DIR/" "$LAST_UPLOAD_DIR/" "$ACTUAL_UPLOAD_SOURCE_DIR/"
# TODO: use diff or rsync to check for changes and only upload the changed files (and delete the files, that are no longer there)
cp -r "$UPLOAD_SOURCE_DIR"/* "$ACTUAL_UPLOAD_SOURCE_DIR"


if [ -z "$ESP_PORT" ]; then
  echo "ESP_PORT is not set. Please set it to the correct port for your ESP32 device."
  exit 1
fi

echo "Deploying to ESP32 on port '$ESP_PORT'"
ampy --port "$ESP_PORT" put "$ACTUAL_UPLOAD_SOURCE_DIR"/ "$UPLOAD_TARGET_DIR"/
