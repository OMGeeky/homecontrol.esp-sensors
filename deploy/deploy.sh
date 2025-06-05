#pip install rshell
CODE_DIR="src/"
LIBS_DIR=deploy/libs/
CONFIG_FILE=deploy/config.json

LAST_UPLOAD_DIR=deploy/last_upload
UPLOAD_SOURCE_DIR=deploy/upload
ACTUAL_UPLOAD_SOURCE_DIR=deploy/actual_upload
UPLOAD_TARGET_DIR=/pyboard/

echo "preparing for deployment"
mkdir -p "$UPLOAD_SOURCE_DIR"

mkdir -p "$UPLOAD_SOURCE_DIR"
mkdir -p "$LAST_UPLOAD_DIR"
cp -r "$CODE_DIR"* "$UPLOAD_SOURCE_DIR"
cp "$CONFIG_FILE" "$UPLOAD_SOURCE_DIR"

# check if the flag -libs or -a is set and copy the libraries to the upload directory
if [[ "$1" == "-libs" || "$1" == "-a" ]]; then
  echo "Copying libraries to upload directory"
  mkdir -p "$UPLOAD_SOURCE_DIR/lib"
  cp -r "$LIBS_DIR"* "$UPLOAD_SOURCE_DIR/lib"
fi


# check what files have changed and only upload the changed files (use $ACTUAL_UPLOAD_SOURCE_DIR for the changed files)
rm -rf "$ACTUAL_UPLOAD_SOURCE_DIR"
mkdir -p "$ACTUAL_UPLOAD_SOURCE_DIR"
if [[ "$1" == "-f" || "$1" == "-a" ]]; then
  echo "Force copying all files"
  cp -r "$UPLOAD_SOURCE_DIR"/* "$ACTUAL_UPLOAD_SOURCE_DIR"
else
  echo "Checking for changes in the upload directory"
  # Use diff to find changes and copy only modified or new files
  for file in $(find "$UPLOAD_SOURCE_DIR" -type f); do
    relative_path="${file#$UPLOAD_SOURCE_DIR/}"
    last_file="$LAST_UPLOAD_DIR/$relative_path"

    if [[ ! -f "$last_file" ]] || ! diff -q "$file" "$last_file" > /dev/null; then
      echo "Copying changed file: $file"
      mkdir -p "$(dirname "$ACTUAL_UPLOAD_SOURCE_DIR/$relative_path")"
      cp "$file" "$ACTUAL_UPLOAD_SOURCE_DIR/$relative_path"
    fi
  done
  # TODO: consider removing files that are no longer in the upload directory but were in the last upload directory
#   for file in $(find "$LAST_UPLOAD_DIR" -type f); do
#     relative_path="${file#$LAST_UPLOAD_DIR/}"
#     if [[ ! -f "$UPLOAD_SOURCE_DIR/$relative_path" ]]; then
#       echo "Removing file: $file"
#     fi
#   done
fi


if [ -z "$ESP_PORT" ]; then
  echo "ESP_PORT is not set. Please set it to the correct port for your ESP32 device."
  exit 1
fi

echo "Deploying to ESP32 on port '$ESP_PORT'"
# TODO: clear storage, if -f flag is passed in?
rshell -p "$ESP_PORT" "rsync $ACTUAL_UPLOAD_SOURCE_DIR/ $UPLOAD_TARGET_DIR"
if [ $? -ne 0 ]; then
  echo "Error: Deployment failed. Please check the connection and try again."
  exit 1
fi
# move the the current upload directory to a backup to be able to compare the changes and only upload the changes
rm -rf "$LAST_UPLOAD_DIR"
mv "$UPLOAD_SOURCE_DIR" "$LAST_UPLOAD_DIR"
