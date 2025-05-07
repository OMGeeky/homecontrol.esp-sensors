# ESP Sensors Project Guidelines

This document provides guidelines and instructions for developing and maintaining the ESP Sensors project.

## Build and Configuration Instructions

### Environment Setup

1. **Python Version**: This project uses Python 3.12. Ensure you have this version installed.

2. **Virtual Environment**: Always use a virtual environment for development:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Dependencies**: Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Project Structure

The project follows this structure:
```
esp-sensors/
├── src/
│   └── esp_sensors/       # Main package
│       ├── __init__.py
│       ├── sensor.py      # Base sensor class
│       └── temperature.py # Temperature sensor implementation
├── tests/                 # Test directory
├── .junie/                # Project documentation
├── pyproject.toml         # Project configuration
└── requirements.txt       # Dependencies
```

## Testing Information

### Running Tests

1. **Basic Test Run**:
   ```bash
   python -m pytest
   ```

2. **Verbose Output**:
   ```bash
   python -m pytest -v
   ```

3. **With Coverage**:
   ```bash
   python -m pytest --cov=src.esp_sensors
   ```

4. **Generate Coverage Report**:
   ```bash
   python -m pytest --cov=src.esp_sensors --cov-report=html
   ```
   This will create a `htmlcov` directory with an HTML coverage report.

### Adding New Tests

1. Create test files in the `tests` directory with the naming pattern `test_*.py`.
2. Test functions should be named with the prefix `test_`.
3. Use pytest fixtures for common setup and teardown operations.

### Example Test

Here's a simple example of a test for a temperature sensor:

```python
import pytest
from src.esp_sensors.temperature import TemperatureSensor

def test_temperature_sensor_initialization():
    """Test that a temperature sensor can be initialized with valid parameters."""
    sensor = TemperatureSensor("test_sensor", 5, 30, "C")
    assert sensor.name == "test_sensor"
    assert sensor.pin == 5
    assert sensor.interval == 30
    assert sensor.unit == "C"
```

## Code Style and Development Guidelines

### Code Formatting

This project uses [Black](https://black.readthedocs.io/) for code formatting:

```bash
# Check if files need formatting
black --check .

# Format files
black .
```

### Type Hints

Always use type hints in function signatures and variable declarations:

```python
from typing import Dict, Any, Optional

def process_reading(value: float, metadata: Dict[str, Any]) -> Optional[float]:
    # Function implementation
    pass
```

### Documentation

- Use docstrings for all modules, classes, and functions.
- Follow the Google docstring style.
- Include examples in docstrings where appropriate.

Example:
```python
def read(self) -> float:
    """
    Read the current sensor value.

    Returns:
        The sensor reading as a float
    """
    # Implementation
```

### Error Handling

- Use specific exception types rather than generic exceptions.
- Handle exceptions at the appropriate level.
- Log exceptions with context information.

### Development Workflow

1. Create a new branch for each feature or bug fix.
2. Write tests before implementing features (Test-Driven Development).
3. Ensure all tests pass before submitting changes.
4. Format code with Black before committing.
5. Update documentation as needed.

## ESP-Specific Development Notes

When developing for actual ESP hardware:

1. This project is designed to work with MicroPython on ESP32/ESP8266 devices.
2. For hardware testing, you'll need to flash MicroPython to your device.
3. Use tools like `ampy` or `rshell` to upload code to the device.
4. Consider memory constraints when developing for ESP devices.
5. For production, optimize code to reduce memory usage and power consumption.