try:
    import machine

    SIMULATION = False
except ModuleNotFoundError:
    SIMULATION = True  # We're in a test environment
    import random  # For generating random values in tests


def read_dummy(name: str, unit: str) -> float:
    """
    Dummy function to simulate reading a sensor value.

    Args:
        name: The name of the sensor (e.g., "temperature", "humidity")
        unit: The unit of the data to generate (one of ['F', 'C', '%'])

    Returns:
        A simulated sensor reading as a float
    """

    if SIMULATION:
        # Simulation mode - generate random values for testing
        if unit == "F":
            # Simulate a temperature reading in Fahrenheit
            return round(random.uniform(59.0, 86.0), 1)
        elif unit == "%":
            # Simulate a humidity reading in percentage
            return round(random.uniform(30.0, 90.0), 1)
        elif unit == "C":
            return round(random.uniform(15.0, 30.0), 1)
        else:
            raise ValueError(f"Unsupported unit for dummy sensor: {unit}")
    else:
        # This method should be overridden by subclasses to implement
        # actual temperature reading from hardware
        raise NotImplementedError(f"Subclasses must implement read_{name}()")
