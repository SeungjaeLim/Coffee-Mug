"""
Main Module: Coffee Sensor System
Classifies coffee as 'Day Coffee' or 'Night Coffee' based on sensor readings.
"""
import os
print(os.getcwd())  # Should print D:\micropico
print(os.listdir())

from light import LightSensor
from load import LoadSensor
import time

# Initialize sensors
light_sensor = LightSensor(pin=27, threshold=30000)  # Set light threshold
load_sensor = LoadSensor(pin=26, threshold=15000)    # Set load threshold

def classify_coffee(light_sensor, load_sensor):
    """
    Classifies coffee based on light and load sensor readings.

    Parameters:
    - light_sensor: LightSensor - Instance of LightSensor.
    - load_sensor: LoadSensor - Instance of LoadSensor.

    Returns:
    - str: 'Night Coffee', 'Day Coffee', or 'No Coffee Detected'
    """
    if load_sensor.is_load():
        if light_sensor.is_light():
            return "Day Coffee"
        else:
            return "Night Coffee"
    return "No Coffee Detected"

# Main loop
if __name__ == "__main__":
    while True:
        coffee_type = classify_coffee(light_sensor, load_sensor)
        print(f"Light: {light_sensor.read()}, Load: {load_sensor.read()}, Coffee Type: {coffee_type}")
        time.sleep(1)  # Delay to avoid spamming
