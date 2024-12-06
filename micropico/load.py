"""
Load Sensor Module
Handles load (weight) readings and coffee detection.
"""

from machine import ADC, Pin

class LoadSensor:
    def __init__(self, pin, threshold):
        """
        Initializes the load sensor.

        Parameters:
        - pin: int - GPIO pin connected to the load sensor.
        - threshold: int - Load threshold for coffee detection.
        """
        self.adc = ADC(Pin(pin))
        self.threshold = threshold

    def read(self):
        """
        Reads the load sensor value.

        Returns:
        - int: Load sensor value (0-65535).
        """
        return self.adc.read_u16()

    def is_load(self):
        """
        Determines if a coffee load is detected.

        Returns:
        - bool: True if load sensor value is above the threshold, False otherwise.
        """
        return self.read() >= self.threshold
