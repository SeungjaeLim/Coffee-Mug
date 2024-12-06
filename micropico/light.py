"""
Light Sensor Module
Handles light intensity readings and day detection.
"""

from machine import ADC, Pin

class LightSensor:
    def __init__(self, pin, threshold):
        """
        Initializes the light sensor.

        Parameters:
        - pin: int - GPIO pin connected to the light sensor.
        - threshold: int - Light threshold for day/night detection.
        """
        self.adc = ADC(Pin(pin))
        self.threshold = threshold

    def read(self):
        """
        Reads the light intensity.

        Returns:
        - int: Light intensity value (0-65535).
        """
        return self.adc.read_u16()

    def is_light(self):
        """
        Determines if it's 'Day' based on light sensor reading.

        Returns:
        - bool: True if light intensity is above the threshold, False otherwise.
        """
        return self.read() >= self.threshold
